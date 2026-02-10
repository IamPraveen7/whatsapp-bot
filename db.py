import os
import certifi
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# === Config ===
MONGO_URI = os.getenv("MONGO_URI")  # Set this in Render secrets
DB_NAME = "phishing_bot"

# === Globals ===
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

# === Connect to MongoDB ===
async def connect_db():
    global client, db
    if client is None:
        try:
            client = AsyncIOMotorClient(
                MONGO_URI,
                tls=True,                   # Enable TLS/SSL
                tlsCAFile=certifi.where(),  # Use certifi CA bundle
                maxPoolSize=20,
                serverSelectionTimeoutMS=10000,
            )
            # Verify connection
            await client.admin.command("ping")
        except Exception as e:
            client = None
            raise ConnectionError(f"MongoDB connection failed: {e}")
        db = client[DB_NAME]

# === Close connection ===
async def close_db():
    global client, db
    if client:
        client.close()
        client = None
        db = None

# === FastAPI Dependency ===
async def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        await connect_db()
    return db
