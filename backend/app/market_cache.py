"""
Cache SQLite cho chỉ số tài chính của TOÀN BỘ thị trường (HOSE/HNX/UPCOM).

Vì `vnstock` chỉ hỗ trợ lấy chỉ số tài chính từng mã một (không có API bulk
đáng tin cậy cho ~1.600+ mã cùng lúc), việc gọi live cho toàn thị trường mỗi
khi user nộp form là không khả thi (mất nhiều phút, dễ bị chặn IP).

Giải pháp: một script chạy nền (`scripts/sync_market_data.py`) quét toàn bộ
thị trường 1 lần/ngày (qua cron), lưu kết quả vào SQLite. Request của user
chỉ đọc từ cache này (nhanh, không cần internet ra ngoài).

DB file mặc định: backend/market_data.db (tạo tự động lần đầu chạy).
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "market_data.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS stock_metrics (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    exchange TEXT,
    pe REAL,
    pb REAL,
    eps REAL,
    roe REAL,
    roa REAL,
    market_cap REAL,
    dividend_yield REAL,
    last_price REAL,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_stock_sector ON stock_metrics(sector);
CREATE INDEX IF NOT EXISTS idx_stock_exchange ON stock_metrics(exchange);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_stock_metrics(row: dict):
    """Ghi/cập nhật 1 dòng chỉ số cho 1 mã. Được gọi bởi sync script."""
    row = {**row, "updated_at": datetime.now(timezone.utc).isoformat()}
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO stock_metrics
                (symbol, name, sector, exchange, pe, pb, eps, roe, roa,
                 market_cap, dividend_yield, last_price, updated_at)
            VALUES
                (:symbol, :name, :sector, :exchange, :pe, :pb, :eps, :roe, :roa,
                 :market_cap, :dividend_yield, :last_price, :updated_at)
            ON CONFLICT(symbol) DO UPDATE SET
                name=excluded.name, sector=excluded.sector, exchange=excluded.exchange,
                pe=excluded.pe, pb=excluded.pb, eps=excluded.eps, roe=excluded.roe,
                roa=excluded.roa, market_cap=excluded.market_cap,
                dividend_yield=excluded.dividend_yield, last_price=excluded.last_price,
                updated_at=excluded.updated_at
            """,
            row,
        )


def count_cached() -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) AS c FROM stock_metrics")
        return cur.fetchone()["c"]


def last_synced_at() -> Optional[str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT MAX(updated_at) AS t FROM stock_metrics")
        row = cur.fetchone()
        return row["t"] if row else None


def query_universe(
    max_pe: Optional[float] = None,
    min_market_cap: Optional[float] = None,
    sectors: Optional[list[str]] = None,
    min_dividend_yield: Optional[float] = None,
    exchanges: Optional[list[str]] = None,
    limit: int = 60,
) -> list[dict]:
    """Lọc rule-based trực tiếp trong SQL trên dữ liệu đã cache."""
    clauses = []
    params: dict = {}

    if max_pe is not None:
        clauses.append("(pe IS NULL OR pe <= :max_pe)")
        params["max_pe"] = max_pe
    if min_market_cap is not None:
        clauses.append("(market_cap IS NULL OR market_cap >= :min_market_cap)")
        params["min_market_cap"] = min_market_cap
    if min_dividend_yield is not None:
        clauses.append("(dividend_yield IS NOT NULL AND dividend_yield >= :min_div)")
        params["min_div"] = min_dividend_yield
    if sectors:
        placeholders = ",".join(f":sector{i}" for i in range(len(sectors)))
        clauses.append(f"sector IN ({placeholders})")
        for i, s in enumerate(sectors):
            params[f"sector{i}"] = s
    if exchanges:
        placeholders = ",".join(f":exch{i}" for i in range(len(exchanges)))
        clauses.append(f"exchange IN ({placeholders})")
        for i, e in enumerate(exchanges):
            params[f"exch{i}"] = e

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM stock_metrics {where} ORDER BY market_cap DESC LIMIT :limit"
    params["limit"] = limit

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_all_cached(search: Optional[str] = None, exchange: Optional[str] = None, limit: int = 2000) -> list[dict]:
    clauses = []
    params: dict = {"limit": limit}
    if search:
        clauses.append("(symbol LIKE :q OR name LIKE :q)")
        params["q"] = f"%{search.upper()}%"
    if exchange and exchange.upper() != "ALL":
        clauses.append("exchange = :exchange")
        params["exchange"] = exchange.upper()
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM stock_metrics {where} ORDER BY symbol ASC LIMIT :limit"
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_one(symbol: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM stock_metrics WHERE symbol = :s", {"s": symbol.upper()}
        ).fetchone()
        return dict(row) if row else None
