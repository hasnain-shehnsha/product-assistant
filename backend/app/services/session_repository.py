import motor.motor_asyncio
import certifi
from typing import List, Dict, Any
from app.models.interfaces import ChatMemory
from app.core.config import settings

class MongoSessionRepository(ChatMemory):
    def __init__(self, uri: str, db_name: str, collection_name: str = "sessions"):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            uri, 
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True
        )
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        message = {"role": role, "content": content}
        await self.collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": message}},
            upsert=True
        )
        
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        doc = await self.collection.find_one({"session_id": session_id})
        if not doc or "messages" not in doc:
            return []
        
        # Return the last 'limit' messages
        messages = doc["messages"]
        return messages[-limit:]

    async def get_all_sessions(self) -> List[Dict[str, str]]:
        cursor = self.collection.find({}, {"session_id": 1, "messages": {"$slice": 5}, "_id": 0})
        sessions = await cursor.to_list(length=100)
        result = []
        for doc in sessions:
            if "session_id" in doc:
                title = "New Chat"
                for msg in doc.get("messages", []):
                    if msg.get("role") == "user":
                        title = msg.get("content", "New Chat")
                        break
                result.append({"id": doc["session_id"], "title": title})
        return result

    async def delete_session(self, session_id: str) -> bool:
        result = await self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0

# Dependency to get repository
def get_session_repository() -> MongoSessionRepository:
    return MongoSessionRepository(settings.MONGODB_URI, settings.MONGODB_DB_NAME)
