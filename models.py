from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class NLPSignal(BaseModel):
    intent: str
    confidence: int
    signals: List[str]

class ScanResult(BaseModel):
    url: str
    domain: str
    risk_score: int
    verdict: str
    heuristic_score: int
    virustotal_score: int
    gsb_score: int
    nlp: Optional[NLPSignal]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "http://bit.ly/xyz",
                "domain": "bit.ly",
                "risk_score": 92,
                "verdict": "CRITICAL RISK",
                "heuristic_score": 20,
                "virustotal_score": 40,
                "gsb_score": 40,
                "nlp": {
                    "intent": "phishing",
                    "confidence": 88,
                    "signals": ["urgent language", "account suspension threat"]
                },
                "created_at": "2026-02-10T10:15:22Z"
            }
        }
    }
