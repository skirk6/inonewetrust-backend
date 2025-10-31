# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 20:55:02 2025

@author: G756
"""

import os
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Optional

app = FastAPI(title="In One We Trust API")

# --- CORS: only allow your site (add preview if you use it) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://inonewetrust.com",
        "https://www.inonewetrust.com",
        # add Vercel preview domains if needed, e.g.:
        # "https://inonewetrust-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY")  # set in Render

async def require_api_key(x_api_key: Optional[str] = Header(None)):
    # Allow /health without a key so you can probe uptime
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "server_time": datetime.now(timezone.utc).isoformat(),
        "version": "0.0.1",
    }

# Example: protect everything else with API key
from pydantic import BaseModel
from typing import List

class Signal(BaseModel):
    symbol: str
    action: str
    score: float
    reasons: List[str]

class LuckyResponse(BaseModel):
    picks: List[Signal]
    note: str

def compute_signal(symbol: str) -> Signal:
    s = symbol.upper().strip()
    score = (len(s) % 2) * 0.5 + 1.0
    action = "BUY" if len(s) % 2 == 0 else "HOLD"
    reasons = ["Placeholder engine", f"len={len(s)} score={score:.2f}"]
    return Signal(symbol=s, action=action, score=round(score,2), reasons=reasons)

@app.get("/search", dependencies=[Depends(require_api_key)])
def search(q: str):
    norm = q.strip().upper()
    t = "ticker" if norm.isalpha() and 1 <= len(norm) <= 5 else "company"
    return {"query": q, "normalized": norm if t=="ticker" else q.title(), "type": t, "suggestions": [norm] if t=="ticker" else []}

@app.get("/signal/{symbol}", response_model=Signal, dependencies=[Depends(require_api_key)])
def get_signal(symbol: str):
    return compute_signal(symbol)

@app.get("/lucky", response_model=LuckyResponse, dependencies=[Depends(require_api_key)])
def lucky():
    universe = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","AVGO","JPM","UNH","XOM"]
    picks = [compute_signal(s) for s in universe[:5]]
    return LuckyResponse(picks=picks, note="Demo picks.")
