# app/config.py

import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "dev").lower()

if ENV in ("dev", "local"):
    load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


TWILIO_AUTH_TOKEN = required_env("TWILIO_AUTH_TOKEN")
OPENAI_API_KEY = required_env("OPENAI_API_KEY")
MONGO_URI = required_env("MONGO_URI")

VT_API_KEY = os.getenv("VT_API_KEY")
GSB_API_KEY = os.getenv("GSB_API_KEY")

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))

__all__ = [
    "TWILIO_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "VT_API_KEY",
    "GSB_API_KEY",
    "MONGO_URI",
    "REQUEST_TIMEOUT",
]