import ssl
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "phishing_bot"

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def connect_db():
    global client, db
    if client is None:
        # create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2  # enforce TLS 1.2

        client = AsyncIOMotorClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            ssl=ssl_context,  # pass the context
            maxPoolSize=20,
            serverSelectionTimeoutMS=10000,
        )
        try:
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

async def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        await connect_db()
    return db
