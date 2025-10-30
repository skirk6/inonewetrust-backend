# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 20:55:02 2025

@author: G756
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="In One We Trust API")

# Allow local frontend during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to In One We Trust API"}

@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import Query
from pydantic import BaseModel

class SearchResult(BaseModel):
    query: str
    normalized: str
    type: str  # "ticker" | "company"
    suggestions: list[str]

@app.get("/search", response_model=SearchResult)
def search(q: str = Query(..., min_length=1, max_length=20)):
    # Very simple placeholder logic for now:
    raw = q.strip()
    norm = raw.upper()
    # If it looks like a ticker (A-Z, 1–5 chars), treat it as one
    if norm.isalpha() and 1 <= len(norm) <= 5:
        return SearchResult(
            query=raw,
            normalized=norm,
            type="ticker",
            suggestions=[norm]  # later this can return best matches
        )
    # Otherwise, assume company name and return an empty suggestion list for now
    return SearchResult(
        query=raw,
        normalized=raw.title(),
        type="company",
        suggestions=[]
    )

from pydantic import BaseModel
from typing import List

# ---------- Models ----------
class Signal(BaseModel):
    symbol: str
    action: str          # BUY | SELL | HOLD
    score: float
    reasons: List[str]

class LuckyResponse(BaseModel):
    picks: List[Signal]
    note: str

# ---------- Helpers (placeholder logic) ----------
def compute_signal(symbol: str) -> Signal:
    s = symbol.upper().strip()
    # Dumb demo logic: even-length tickers = BUY, odd = HOLD; add simple reasons.
    score = (len(s) % 2) * 0.5 + 1.0
    action = "BUY" if len(s) % 2 == 0 else "HOLD"
    reasons = [
        "Placeholder engine: deterministic demo",
        f"Symbol length = {len(s)} → score {score:.2f}"
    ]
    return Signal(symbol=s, action=action, score=round(score, 2), reasons=reasons)

# ---------- Routes ----------
@app.get("/signal/{symbol}", response_model=Signal)
def get_signal(symbol: str):
    return compute_signal(symbol)

@app.get("/lucky", response_model=LuckyResponse)
def lucky():
    # Demo universe; later you’ll use your ranked list with constraints.
    universe = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "AVGO", "JPM", "UNH", "XOM"]
    picks = [compute_signal(s) for s in universe[:5]]
    return LuckyResponse(
        picks=picks,
        note="Demo picks. Not investment advice. Real logic coming soon."
    )
