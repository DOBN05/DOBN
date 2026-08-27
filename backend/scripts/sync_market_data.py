"""
Quét chỉ số tài chính (P/E, P/B, ROE, ROA, EPS, vốn hóa, cổ tức...) cho
TOÀN BỘ mã trên HOSE/HNX/UPCOM, lưu vào SQLite cache (backend/market_data.db).

CÁCH CHẠY:
    cd backend
    source venv/bin/activate
    python -m scripts.sync_market_data

    # Chỉ test nhanh với 20 mã đầu tiên:
    python -m scripts.sync_market_data --limit 20

    # Chỉ đồng bộ 1 sàn:
    python -m scripts.sync_market_data --exchange HOSE

NÊN CHẠY ĐỊNH KỲ (1 LẦN/NGÀY) qua cron, vì:
- Quét toàn bộ ~1.600 mã, mỗi mã vài request -> mất khá lâu (ước tính
  vài chục phút đến 1-2 tiếng tùy tốc độ mạng & rate limit của nguồn
  dữ liệu). KHÔNG chạy trong lúc phục vụ request của user.
- Chỉ số tài chính (P/E, ROE...) không đổi nhiều lần trong ngày, nên
  cập nhật 1 lần/ngày là đủ cho mục đích sàng lọc/khuyến nghị.

VÍ DỤ CRONTAB (chạy 1h sáng mỗi ngày):
    0 1 * * * cd /path/to/backend && venv/bin/python -m scripts.sync_market_data >> sync.log 2>&1

LƯU Ý: Mình chưa test được script này với dữ liệu thật (môi trường sandbox
không có internet ra ngoài tới nguồn dữ liệu vnstock). Hãy chạy thử với
--limit 20 trước để kiểm tra hoạt động đúng, rồi mới chạy full.
"""

import argparse
import logging
import sys
import time

from app import market_cache
from app.services import vnstock_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("sync_market_data")

# Nghỉ giữa các request để tránh bị chặn IP do gọi quá nhanh
SLEEP_BETWEEN_SYMBOLS = 0.5  # giây


def build_sector_map() -> dict[str, str]:
    """Map symbol -> tên ngành, từ Listing().symbols_by_industries()."""
    try:
        rows = vnstock_data.get_symbols_by_industries()
    except Exception as e:
        logger.error("Không lấy được danh sách ngành: %s", e)
        return {}

    sector_map = {}
    for row in rows:
        symbol = row.get("symbol") or row.get("ticker")
        sector = None
        for k, v in row.items():
            lk = str(k).lower()
            if "industry" in lk or "icb" in lk or "sector" in lk:
                sector = v
                break
        if symbol and sector:
            sector_map[symbol] = sector
    return sector_map


def sync(limit: int | None = None, exchange_filter: str | None = None):
    market_cache.init_db()

    logger.info("Đang lấy danh sách toàn bộ mã...")
    symbols_data = vnstock_data.get_all_symbols()
    if not symbols_data:
        logger.error("Không lấy được danh sách mã nào. Dừng lại.")
        sys.exit(1)

    logger.info("Đang lấy bản đồ ngành (sector)...")
    sector_map = build_sector_map()

    # Chuẩn hóa: tìm đúng tên cột symbol/exchange trong kết quả trả về
    sample = symbols_data[0]
    symbol_key = next((k for k in sample if "symbol" in k.lower() or k.lower() == "ticker"), None)
    exchange_key = next((k for k in sample if "exchange" in k.lower()), None)

    if not symbol_key:
        logger.error("Không tìm thấy cột symbol trong dữ liệu Listing trả về: %s", list(sample.keys()))
        sys.exit(1)

    rows = symbols_data
    if exchange_filter and exchange_key:
        rows = [r for r in rows if str(r.get(exchange_key, "")).upper() == exchange_filter.upper()]

    if limit:
        rows = rows[:limit]

    total = len(rows)
    logger.info("Bắt đầu đồng bộ %d mã...", total)

    ok, failed = 0, 0
    for i, row in enumerate(rows, start=1):
        symbol = row.get(symbol_key)
        if not symbol:
            continue
        exchange = row.get(exchange_key) if exchange_key else None

        try:
            snapshot = vnstock_data.get_financial_snapshot(symbol)
            price = vnstock_data.get_latest_price(symbol)
            overview = vnstock_data.get_company_overview(symbol)

            market_cache.upsert_stock_metrics(
                {
                    "symbol": symbol,
                    "name": overview.get("company_name") or overview.get("companyName") or row.get("organ_name"),
                    "sector": sector_map.get(symbol),
                    "exchange": exchange,
                    "pe": snapshot.get("pe"),
                    "pb": snapshot.get("pb"),
                    "eps": snapshot.get("eps"),
                    "roe": snapshot.get("roe"),
                    "roa": snapshot.get("roa"),
                    "market_cap": vnstock_data._safe_float(overview.get("market_cap")),
                    "dividend_yield": snapshot.get("dividend_yield"),
                    "last_price": price,
                }
            )
            ok += 1
        except Exception as e:
            logger.warning("Lỗi đồng bộ mã %s: %s", symbol, e)
            failed += 1

        if i % 20 == 0 or i == total:
            logger.info("Tiến độ: %d/%d (thành công: %d, lỗi: %d)", i, total, ok, failed)

        time.sleep(SLEEP_BETWEEN_SYMBOLS)

    logger.info("Hoàn tất. Thành công: %d, lỗi: %d, tổng: %d", ok, failed, total)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Đồng bộ chỉ số tài chính toàn thị trường vào cache")
    parser.add_argument("--limit", type=int, default=None, help="Chỉ đồng bộ N mã đầu tiên (dùng để test)")
    parser.add_argument("--exchange", type=str, default=None, help="Chỉ đồng bộ 1 sàn: HOSE | HNX | UPCOM")
    args = parser.parse_args()

    sync(limit=args.limit, exchange_filter=args.exchange)
