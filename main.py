import asyncio
import logging

from fastapi import FastAPI, Request, Depends, Response
from twilio.twiml.messaging_response import MessagingResponse

from security import validate_twilio_request
from services.url_utils import extract_url
from services.heuristics import heuristic_score
from services.reputation import virustotal_score, gsb_score
from services.nlp import analyze_text
from services.scoring import final_score, classify

from db import get_db
import json
from models import ScanResult, NLPSignal
from services.url_utils import extract_domain

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    _: None = Depends(validate_twilio_request),
    db=Depends(get_db)
):
    form = await request.form()
    body = form.get("Body", "")
    resp = MessagingResponse()

    url = extract_url(body)
    if not url:
        resp.message("❌ No valid link detected.")
        return Response(content=str(resp), media_type="application/xml")

    h = heuristic_score(url)

    # run VT + GSB in parallel
    try:
        vt, gsb = await asyncio.gather(
            virustotal_score(url),
            gsb_score(url)
        )
    except Exception as e:
        logging.error(f"Reputation API failed: {e}")
        vt = gsb = 0

    # NLP
    try:
        raw_nlp = await analyze_text(body)
        nlp_obj = NLPSignal(**raw_nlp)
        nlp_score = min(20, int(nlp_obj.confidence * 0.2)) if nlp_obj.intent in ("phishing","scam") else 0
    except Exception as e:
        logging.error(f"NLP failed: {e}")
        nlp_obj = None
        nlp_score = 0

    score = final_score(h, vt, gsb, nlp_score)
    verdict = classify(score)

    scan = ScanResult(
        url=url,
        domain=extract_domain(url),
        risk_score=score,
        verdict=verdict,
        heuristic_score=h,
        virustotal_score=vt,
        gsb_score=gsb,
        nlp=nlp_obj,
    )

    if db is None:
        raise RuntimeError("Database is not initialized!")
    
    await db.scans.insert_one(scan.dict())
    resp.message(
        f"🚨 {verdict}\n\n"
        f"Risk Score: {score}/100\n\n"
        "Advice:\n"
        "❌ Do not open\n"
        "❌ Do not enter credentials"
    )

    return Response(content=str(resp), media_type="application/xml")
