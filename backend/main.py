import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import market_cache
from app.config import settings
from app.schemas import (
    RecommendRequest,
    RecommendResponse,
    ReportResponse,
    StockDetailResponse,
    StockListItem,
)
from app.services import recommend as recommend_service
from app.services import report as report_service
from app.services import vnstock_data

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="DOBN Capital API",
    description="Backend bổ sung dữ liệu sống toàn thị trường + AI recommendation/report cho website DOBN Capital",
    version="0.2.0",
)

origins = ["*"] if settings.FRONTEND_ORIGIN == "*" else [settings.FRONTEND_ORIGIN]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    market_cache.init_db()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "cached_symbols": market_cache.count_cached(),
        "last_synced_at": market_cache.last_synced_at(),
    }


@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    try:
        recs = recommend_service.get_recommendations(
            req.total_score, req.risk_type, req.horizon
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi khi tạo khuyến nghị: {e}")

    if not recs:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã phù hợp.")

    return RecommendResponse(recommendations=recs)


@app.get("/api/stocks", response_model=list[StockListItem])
def list_stocks(search: str = "", exchange: str = "ALL", limit: int = 500):
    """Danh sách mã cho trang stocks.html - đọc từ cache (nhanh). Nếu cache
    rỗng, trả về rỗng - frontend sẽ tự fallback về pool 39 mã tĩnh."""
    rows = market_cache.get_all_cached(search=search or None, exchange=exchange, limit=limit)
    return [
        StockListItem(
            code=r["symbol"],
            name=r.get("name"),
            sector=r.get("sector"),
            exchange=r.get("exchange"),
            last_price=r.get("last_price"),
        )
        for r in rows
    ]


@app.get("/api/stock/{code}", response_model=StockDetailResponse)
def stock_detail(code: str):
    code = code.upper()
    try:
        overview = vnstock_data.get_company_overview(code)
        price_history = vnstock_data.get_price_history(code)
        latest_metrics = vnstock_data.get_financial_snapshot(code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Không lấy được dữ liệu cho {code}: {e}")

    if not overview and not price_history:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mã {code}")

    return StockDetailResponse(
        code=code,
        overview=overview,
        price_history=price_history,
        latest_metrics=latest_metrics,
    )


@app.get("/api/report/{code}", response_model=ReportResponse)
def stock_report(code: str):
    """Sinh báo cáo phân tích AI cho 1 mã bất kỳ trên thị trường (thay thế
    file PDF tĩnh). Gọi vnstock SỐNG cho đúng mã này (nhanh vì chỉ 1 mã)."""
    try:
        report = report_service.generate_report(code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi không xác định: {e}")

    return ReportResponse(**report)
