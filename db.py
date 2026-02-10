import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

MONGO_URI = os.getenv("MONGO_URI")  # e.g. mongodb+srv://user:pass@cluster0.abc.mongodb.net/phishing_bot
DB_NAME = "phishing_bot"

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_db():
    global client, db
    if client is None:
        try:
            client = AsyncIOMotorClient(
                MONGO_URI,
                tls=True,                     # enable TLS
                tlsCAFile=certifi.where(),    # use certifi bundle
                maxPoolSize=20,
                serverSelectionTimeoutMS=10000
            )
            # verify connection
            await client.admin.command("ping")
        except Exception as e:
            client = None
            raise ConnectionError(f"MongoDB connection failed: {e}")
        db = client[DB_NAME]

async def close_db():
    global client, db
    if client:
        client.close()
        client = None
        db = None

# FastAPI dependency
async def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        await connect_db()
    return db
