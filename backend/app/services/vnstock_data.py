"""
Lấy dữ liệu SỐNG (giá, chỉ số tài chính) cho đúng 39 mã trong stock_pool.json
(pool đã được nhóm DOBN Capital chọn lọc thủ công, có sẵn logo + PDF báo cáo).

LƯU Ý: vnstock đổi API khá thường xuyên (đã kiểm tra kỹ với vnstock==4.0.6,
dùng module vnstock.api). Nếu lỗi sau khi nâng cấp, dùng
`help(Listing)` / `help(Finance)` / `help(Quote)` / `help(Company)` để xem
lại tên method/tham số mới nhất.
"""

import json
import logging
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional

from vnstock.api.company import Company
from vnstock.api.financial import Finance
from vnstock.api.listing import Listing
from vnstock.api.quote import Quote

from app.config import settings

logger = logging.getLogger(__name__)

SOURCE = settings.VNSTOCK_SOURCE
POOL_PATH = Path(__file__).resolve().parent.parent / "stock_pool.json"


@lru_cache(maxsize=1)
def load_stock_pool() -> list[dict]:
    with open(POOL_PATH, encoding="utf-8") as f:
        return json.load(f)


def _safe_float(val) -> Optional[float]:
    try:
        if val is None:
            return None
        f = float(val)
        if f != f:  # NaN
            return None
        return f
    except (TypeError, ValueError):
        return None


def get_latest_price(symbol: str) -> Optional[float]:
    try:
        quote = Quote(symbol=symbol, source=SOURCE)
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=10)).isoformat()
        df = quote.history(start=start, end=end, interval="1D")
        if df is None or df.empty:
            return None
        close_col = "close" if "close" in df.columns else df.columns[-1]
        return _safe_float(df.iloc[-1][close_col])
    except Exception as e:
        logger.warning("Không lấy được giá cho %s: %s", symbol, e)
        return None


def get_price_history(symbol: str, days: int = 365) -> list[dict]:
    try:
        quote = Quote(symbol=symbol, source=SOURCE)
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=days)).isoformat()
        df = quote.history(start=start, end=end, interval="1D")
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.warning("Không lấy được lịch sử giá cho %s: %s", symbol, e)
        return []


def get_financial_snapshot(symbol: str) -> dict:
    """Lấy các chỉ số tài chính mới nhất (PE, PB, ROE, ROA, EPS...) cho 1 mã."""
    try:
        finance = Finance(source=SOURCE, symbol=symbol, period="year", get_all=True)
        ratio_df = finance.ratio()
        if ratio_df is None or ratio_df.empty:
            return {}
        latest = ratio_df.iloc[0].to_dict()

        def find(*keys):
            for k in latest:
                lk = str(k).lower()
                if any(t in lk for t in keys):
                    return _safe_float(latest[k])
            return None

        return {
            "pe": find("pe", "p/e"),
            "pb": find("pb", "p/b"),
            "eps": find("eps"),
            "roe": find("roe"),
            "roa": find("roa"),
            "dividend_yield": find("dividend", "cotuc"),
        }
    except Exception as e:
        logger.warning("Không lấy được chỉ số tài chính cho %s: %s", symbol, e)
        return {}


def get_company_overview(symbol: str) -> dict:
    try:
        company = Company(source=SOURCE, symbol=symbol)
        df = company.overview()
        if df is None or (hasattr(df, "empty") and df.empty):
            return {}
        return df.iloc[0].to_dict()
    except Exception as e:
        logger.warning("Không lấy được overview cho %s: %s", symbol, e)
        return {}


def get_income_statement(symbol: str, period: str = "year") -> list[dict]:
    try:
        finance = Finance(source=SOURCE, symbol=symbol, period=period, get_all=True)
        df = finance.income_statement()
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.warning("Không lấy được KQKD cho %s: %s", symbol, e)
        return []


def get_balance_sheet(symbol: str, period: str = "year") -> list[dict]:
    try:
        finance = Finance(source=SOURCE, symbol=symbol, period=period, get_all=True)
        df = finance.balance_sheet()
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.warning("Không lấy được bảng CĐKT cho %s: %s", symbol, e)
        return []


# ──────────────────────────────────────────────────────────
# TOÀN BỘ THỊ TRƯỜNG (dùng bởi scripts/sync_market_data.py)
# ──────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_all_symbols() -> list[dict]:
    """Danh sách toàn bộ mã trên HOSE/HNX/UPCOM. Cache trong RAM cho lần
    chạy hiện tại (script sync chỉ chạy 1 lần/ngày nên không cần cache lâu)."""
    listing = Listing(source=SOURCE)
    df = listing.all_symbols()
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


@lru_cache(maxsize=1)
def get_symbols_by_industries() -> list[dict]:
    """Danh sách mã kèm ngành (ICB) để gắn sector khi sync."""
    listing = Listing(source=SOURCE)
    df = listing.symbols_by_industries()
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


def build_live_candidates(symbols: list[str]) -> list[dict]:
    """Ghép thông tin tĩnh trong pool (tên, ngành, logo...) với dữ liệu sống
    (giá, chỉ số tài chính) cho danh sách symbol được chọn."""
    pool_by_code = {p["code"]: p for p in load_stock_pool()}
    result = []
    for sym in symbols:
        base = pool_by_code.get(sym, {"code": sym})
        snapshot = get_financial_snapshot(sym)
        price = get_latest_price(sym)
        result.append({**base, **snapshot, "last_price": price})
    return result
