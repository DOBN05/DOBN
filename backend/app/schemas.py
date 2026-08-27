from typing import Literal, Optional

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    total_score: int = Field(..., description="Tổng điểm risk-question từ form")
    risk_type: Literal["Conservative", "Balanced", "Aggressive"]
    horizon: Literal["Short-term", "Medium-term", "Long-term"]


class RecommendedStock(BaseModel):
    code: str
    name: Optional[str] = None
    sector: Optional[str] = None
    logo: Optional[str] = None
    match_score: int
    reason: str
    key_metrics: dict


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedStock]


class StockDetailResponse(BaseModel):
    code: str
    overview: dict
    price_history: list[dict]
    latest_metrics: dict


class StockListItem(BaseModel):
    code: str
    name: Optional[str] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None
    last_price: Optional[float] = None


class ReportResponse(BaseModel):
    symbol: str
    company_overview: str
    financial_health: str
    valuation_commentary: str
    risks: str
    outlook_note: str
    key_metrics: dict
    raw_data: dict
    ai_generated: bool
