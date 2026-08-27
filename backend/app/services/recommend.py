"""
Luồng recommend (bản nâng cấp — cover toàn thị trường):

1. Map risk_type -> ngưỡng lọc (max_pe, min_market_cap...) — tương tự logic
   risk profile trước đây.
2. Query trực tiếp trong SQLite cache (đã được `scripts/sync_market_data.py`
   đồng bộ định kỳ) để lấy ~30-40 mã ứng viên thoả ngưỡng — CỰC NHANH, vì
   không gọi vnstock trong lúc phục vụ request.
3. Gửi ứng viên (kèm số liệu cache) cho Claude API xếp hạng lại + viết lý
   do, đa dạng hoá ngành, chọn ra 5 mã.
4. Fallback 2 lớp:
   - Nếu cache RỖNG (chưa chạy sync lần nào) -> quay về pool 39 mã tĩnh cũ
     (stock_pool.json) với thuật toán rule-based cũ, để tính năng không
     bao giờ bị sập.
   - Nếu Claude lỗi -> vẫn trả kết quả rule-based (không có AI reasoning).

Đây KHÔNG phải lời khuyên đầu tư - chỉ là logic sản phẩm demo/học thuật.
"""

import json
import logging
from typing import Optional

import anthropic

from app.config import settings
from app.market_cache import count_cached, query_universe
from app.services.vnstock_data import load_stock_pool

logger = logging.getLogger(__name__)

_client: Optional[anthropic.Anthropic] = None

# Map risk_type -> ngưỡng lọc rule-based, áp trực tiếp lên toàn thị trường qua SQL
RISK_THRESHOLDS = {
    "Conservative": {"max_pe": 18, "min_market_cap": 5_000_000_000_000},   # >5,000 tỷ
    "Balanced":     {"max_pe": 25, "min_market_cap": 1_000_000_000_000},   # >1,000 tỷ
    "Aggressive":   {"max_pe": 40, "min_market_cap": 200_000_000_000},     # >200 tỷ
}


def _get_client() -> Optional[anthropic.Anthropic]:
    global _client
    if not settings.ANTHROPIC_API_KEY:
        return None
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _fallback_static(risk_type: str, horizon: str, total_score: int) -> list[dict]:
    """Fallback khi cache toàn thị trường còn rỗng (chưa chạy sync lần nào):
    dùng lại pool 39 mã tĩnh + thuật toán rule-based cũ."""
    pool = load_stock_pool()
    candidates = [p for p in pool if p.get("horizon") == horizon]
    if len(candidates) < 5:
        extra = [p for p in pool if p.get("type") == risk_type]
        seen = {p["code"] for p in candidates}
        candidates += [p for p in extra if p["code"] not in seen]

    candidates.sort(key=lambda p: abs(int(p.get("score", 0)) - total_score))

    sector_count: dict[str, int] = {}
    result = []
    for p in candidates:
        if len(result) >= 5:
            break
        sector = p.get("sector")
        if sector_count.get(sector, 0) < 2:
            result.append(p)
            sector_count[sector] = sector_count.get(sector, 0) + 1

    return [
        {
            "code": p["code"],
            "name": p.get("name"),
            "sector": p.get("sector"),
            "logo": p.get("logo"),
            "match_score": 50,
            "reason": "Được chọn theo bộ lọc tĩnh (cache thị trường chưa được đồng bộ - "
                      "chạy `python -m scripts.sync_market_data` để bật tính năng cover toàn thị trường).",
            "key_metrics": {},
        }
        for p in result
    ]


def _build_prompt(risk_type: str, horizon: str, total_score: int, candidates: list[dict]) -> str:
    candidates_json = json.dumps(candidates, ensure_ascii=False, indent=2, default=str)
    return f"""Bạn là trợ lý phân tích tài chính cho DOBN Capital. Chọn ra 5 mã cổ phiếu
PHÙ HỢP NHẤT từ danh sách ứng viên dưới đây (lấy từ toàn bộ thị trường
HOSE/HNX/UPCOM, đã qua lọc sơ bộ theo chỉ số tài chính) cho một nhà đầu tư
có hồ sơ:

- Điểm rủi ro: {total_score}
- Nhóm rủi ro: {risk_type} (Conservative = thận trọng, Balanced = cân bằng, Aggressive = mạo hiểm)
- Thời gian đầu tư: {horizon}

QUY TẮC BẮT BUỘC:
- CHỈ dùng số liệu có trong JSON dưới đây (pe, pb, eps, roe, roa,
  dividend_yield, market_cap, last_price). KHÔNG tự suy đoán hay dùng số
  liệu bạn nhớ từ dữ liệu huấn luyện.
- Nếu chỉ số bị thiếu (null), có thể ghi chú "thiếu dữ liệu" nếu cần, không bịa số.
- Ưu tiên đa dạng ngành (sector) trong 5 mã chọn ra, tối đa 2 mã/ngành.
- Giọng điệu khách quan, thận trọng, không đảm bảo lợi nhuận.
- CHỈ trả về JSON hợp lệ, không thêm text/markdown nào khác.

Danh sách ứng viên:
{candidates_json}

Format trả về:
{{
  "recommendations": [
    {{
      "code": "MÃ",
      "match_score": 0-100,
      "reason": "2-3 câu giải thích dựa trên số liệu đã cho"
    }}
  ]
}}
"""


def get_recommendations(total_score: int, risk_type: str, horizon: str) -> list[dict]:
    if count_cached() == 0:
        logger.warning("Cache thị trường rỗng, dùng fallback tĩnh (pool 39 mã).")
        return _fallback_static(risk_type, horizon, total_score)

    thresholds = RISK_THRESHOLDS.get(risk_type, RISK_THRESHOLDS["Balanced"])
    candidates = query_universe(
        max_pe=thresholds["max_pe"],
        min_market_cap=thresholds["min_market_cap"],
        limit=40,
    )

    if not candidates:
        logger.warning("Không có mã nào khớp ngưỡng lọc, nới lỏng bộ lọc.")
        candidates = query_universe(limit=40)  # bỏ hết ngưỡng, lấy theo vốn hóa

    if not candidates:
        return _fallback_static(risk_type, horizon, total_score)

    client = _get_client()
    if client is None:
        logger.warning("Chưa cấu hình ANTHROPIC_API_KEY, trả top ứng viên theo vốn hóa (không có AI reasoning).")
        return [
            {
                "code": c["symbol"],
                "name": c.get("name"),
                "sector": c.get("sector"),
                "logo": None,
                "match_score": 50,
                "reason": "Chưa cấu hình AI - xếp theo vốn hóa trong nhóm rủi ro phù hợp.",
                "key_metrics": {"pe": c.get("pe"), "roe": c.get("roe"), "last_price": c.get("last_price")},
            }
            for c in candidates[:5]
        ]

    prompt = _build_prompt(risk_type, horizon, total_score, candidates)

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[-1] if "\n" in text else text
        parsed = json.loads(text)
    except Exception as e:
        logger.error("Lỗi gọi Claude hoặc parse JSON: %s", e)
        return [
            {
                "code": c["symbol"],
                "name": c.get("name"),
                "sector": c.get("sector"),
                "logo": None,
                "match_score": 50,
                "reason": "AI reasoning tạm thời lỗi - xếp theo vốn hóa trong nhóm rủi ro phù hợp.",
                "key_metrics": {"pe": c.get("pe"), "roe": c.get("roe"), "last_price": c.get("last_price")},
            }
            for c in candidates[:5]
        ]

    candidates_by_code = {c["symbol"]: c for c in candidates}
    output = []
    for r in parsed.get("recommendations", [])[:5]:
        code = r.get("code")
        live = candidates_by_code.get(code, {})
        output.append(
            {
                "code": code,
                "name": live.get("name"),
                "sector": live.get("sector"),
                "logo": None,  # logo chỉ có sẵn cho 39 mã pool cũ, mã khác dùng icon mặc định ở frontend
                "match_score": int(r.get("match_score", 0)),
                "reason": r.get("reason", ""),
                "key_metrics": {
                    "pe": live.get("pe"),
                    "roe": live.get("roe"),
                    "last_price": live.get("last_price"),
                },
            }
        )

    return output or _fallback_static(risk_type, horizon, total_score)
