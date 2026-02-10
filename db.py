import os
import certifi
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

# ---------------- CONFIG ----------------
MONGO_URI = os.getenv("MONGO_URI")  # Must be set as a Render secret
DB_NAME = os.getenv("DB_NAME", "phishing_bot")  # fallback

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set!")

# ---------------- GLOBALS ----------------
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None
db_lock = asyncio.Lock()  # prevents race conditions on high traffic

# ---------------- CONNECT ----------------
async def connect_db(retries: int = 3, delay: float = 5.0):
    """
    Initialize MongoDB client with TLS. Retries if connection fails.
    """
    global client, db

    async with db_lock:
        if client is not None:
            return  # already connected

        for attempt in range(1, retries + 1):
            try:
                client = AsyncIOMotorClient(
                    MONGO_URI,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    ssl_cert_reqs=False  # ⚠️ skips certificate verification
                )
                # Test connection
                await client.admin.command("ping")
                db = client[DB_NAME]
                print(f"MongoDB connected successfully to '{DB_NAME}'")
                return
            except Exception as e:
                print(f"[Attempt {attempt}/{retries}] MongoDB connection failed: {e}")
                client = None
                db = None
                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    raise ConnectionError(f"MongoDB connection failed after {retries} attempts: {e}")

# ---------------- CLOSE ----------------
async def close_db():
    global client, db
    async with db_lock:
        if client:
            client.close()
            client = None
            db = None
            print("MongoDB connection closed")

# ---------------- FASTAPI DEPENDENCY ----------------
async def get_db() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency for accessing the database.
    Lazily connects if not already connected.
    """
    global db
    if db is None:
        await connect_db()
    return db
