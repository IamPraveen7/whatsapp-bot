from fastapi import Request, HTTPException
from twilio.request_validator import RequestValidator
from config import TWILIO_AUTH_TOKEN

validator = RequestValidator(TWILIO_AUTH_TOKEN)

async def validate_twilio_request(request: Request):
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing Twilio signature")

    # Full URL as seen by FastAPI (includes path + query params)
    url = str(request.url)

    form = dict(await request.form())

    if not validator.validate(url, form, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
