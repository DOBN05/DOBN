"""
Sinh báo cáo phân tích AI cho MỘT mã cổ phiếu bất kỳ trên thị trường -
thay thế cho các file PDF làm sẵn trong pdf/{code}.pdf.

Khác với /api/recommend (dùng dữ liệu cache để nhanh), route này gọi
`vnstock` SỐNG cho đúng 1 mã (vài request, vài giây) vì chỉ phục vụ 1 mã
tại một thời điểm - hoàn toàn khả thi real-time, và đảm bảo dữ liệu mới
nhất khi user xem báo cáo.
"""

import json
import logging
from typing import Optional

import anthropic

from app.config import settings
from app.services import vnstock_data

logger = logging.getLogger(__name__)

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> Optional[anthropic.Anthropic]:
    global _client
    if not settings.ANTHROPIC_API_KEY:
        return None
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _gather_live_data(symbol: str) -> dict:
    """Gom toàn bộ dữ liệu sống cần thiết để viết báo cáo cho 1 mã."""
    return {
        "symbol": symbol,
        "overview": vnstock_data.get_company_overview(symbol),
        "ratios": vnstock_data.get_financial_snapshot(symbol),
        "income_statement": vnstock_data.get_income_statement(symbol)[:4],  # 4 kỳ gần nhất
        "balance_sheet": vnstock_data.get_balance_sheet(symbol)[:4],
        "recent_price_history": vnstock_data.get_price_history(symbol, days=180)[-30:],  # 30 phiên gần nhất
        "last_price": vnstock_data.get_latest_price(symbol),
    }


def _build_report_prompt(symbol: str, data: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return f"""Bạn là nhà phân tích tài chính của DOBN Capital. Viết một báo cáo phân
tích cổ phiếu {symbol} bằng tiếng Việt, dựa HOÀN TOÀN trên dữ liệu JSON dưới
đây.

QUY TẮC BẮT BUỘC:
- CHỈ dùng số liệu có trong JSON. KHÔNG tự suy đoán hay dùng số liệu bạn nhớ
  từ dữ liệu huấn luyện (có thể đã cũ hoặc sai).
- Nếu một phần dữ liệu bị thiếu/rỗng, ghi rõ "không có đủ dữ liệu để đánh giá
  mục này" thay vì bịa ra.
- Giọng điệu khách quan, thận trọng, chuyên nghiệp. KHÔNG đưa ra khuyến nghị
  "mua/bán" chắc chắn, không cam kết lợi nhuận.
- CHỈ trả về JSON hợp lệ theo đúng format bên dưới, không thêm text/markdown khác.

Dữ liệu:
{data_json}

Format trả về:
{{
  "company_overview": "2-4 câu giới thiệu doanh nghiệp, ngành nghề, vị thế",
  "financial_health": "3-5 câu phân tích sức khỏe tài chính dựa trên các chỉ số đã cho (PE, PB, ROE, ROA, EPS...)",
  "valuation_commentary": "2-4 câu nhận định về định giá hiện tại (so P/E, P/B với thông lệ ngành nếu có thể suy luận từ dữ liệu, nếu không đủ dữ liệu thì nói rõ)",
  "risks": "2-4 câu về rủi ro cần lưu ý (dựa trên xu hướng giá, biến động, hoặc điểm thiếu dữ liệu)",
  "outlook_note": "1-2 câu tổng kết thận trọng, nhắc rõ đây không phải khuyến nghị đầu tư chắc chắn",
  "key_metrics": {{"pe": ..., "pb": ..., "roe": ..., "roa": ..., "eps": ..., "last_price": ...}}
}}
"""


def generate_report(symbol: str) -> dict:
    symbol = symbol.upper()
    data = _gather_live_data(symbol)

    if not data["overview"] and not data["ratios"] and not data["recent_price_history"]:
        raise ValueError(f"Không tìm thấy dữ liệu cho mã {symbol}")

    client = _get_client()
    if client is None:
        return {
            "symbol": symbol,
            "company_overview": "Chưa cấu hình ANTHROPIC_API_KEY nên chưa thể sinh báo cáo AI.",
            "financial_health": "",
            "valuation_commentary": "",
            "risks": "",
            "outlook_note": "Vui lòng cấu hình API key trong backend/.env để dùng tính năng này.",
            "key_metrics": data["ratios"],
            "raw_data": data,
            "ai_generated": False,
        }

    prompt = _build_report_prompt(symbol, data)

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[-1] if "\n" in text else text
        parsed = json.loads(text)
    except Exception as e:
        logger.error("Lỗi sinh báo cáo AI cho %s: %s", symbol, e)
        raise RuntimeError(f"Lỗi khi gọi AI để sinh báo cáo: {e}")

    return {
        "symbol": symbol,
        "company_overview": parsed.get("company_overview", ""),
        "financial_health": parsed.get("financial_health", ""),
        "valuation_commentary": parsed.get("valuation_commentary", ""),
        "risks": parsed.get("risks", ""),
        "outlook_note": parsed.get("outlook_note", ""),
        "key_metrics": parsed.get("key_metrics", data["ratios"]),
        "raw_data": data,
        "ai_generated": True,
    }
