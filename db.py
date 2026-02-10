from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import MONGO_URI
from typing import Optional

DB_NAME = "phishing_bot"

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=20,
            serverSelectionTimeoutMS=10000,
        )
        try:
            # Ping to verify connection
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
