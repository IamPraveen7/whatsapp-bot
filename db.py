import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from typing import Optional

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "phishing_bot"

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,  # TEMP workaround
            maxPoolSize=20,
            serverSelectionTimeoutMS=10000,
        )
        try:
            await client.admin.command("ping")
        except Exception as e:
            client = None
            raise ConnectionError(f"MongoDB connection failed: {e}")
        db = client[DB_NAME]

async def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        await connect_db()
    return db
