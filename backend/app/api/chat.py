from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.core.agent import ProductAssistantAgent
from app.services.pinecone_retriever import PineconeRetriever
from app.services.session_repository import MongoSessionRepository
from app.core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

import asyncio

_agent_instance = None
_agent_lock = asyncio.Lock()

async def get_agent():
    global _agent_instance
    
    async with _agent_lock:
        if _agent_instance is not None:
            return _agent_instance
            
        try:
            retriever = PineconeRetriever(
                api_key=settings.PINECONE_API_KEY, 
                index_name=settings.PINECONE_INDEX_NAME
            )
            memory = MongoSessionRepository(
                uri=settings.MONGODB_URI, 
                db_name=settings.MONGODB_DB_NAME
            )
            _agent_instance = ProductAssistantAgent(retriever=retriever, memory=memory)
            return _agent_instance
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, agent: ProductAssistantAgent = Depends(get_agent)):
    try:
        response_text = await agent.chat(request.session_id, request.message)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions")
async def get_sessions(agent: ProductAssistantAgent = Depends(get_agent)):
    try:
        sessions = await agent.memory.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}")
async def get_session_history(session_id: str, agent: ProductAssistantAgent = Depends(get_agent)):
    try:
        history = await agent.memory.get_history(session_id, limit=50)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str, agent: ProductAssistantAgent = Depends(get_agent)):
    try:
        success = await agent.memory.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/chat/stream")
async def chat_stream(websocket: WebSocket, agent: ProductAssistantAgent = Depends(get_agent)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            session_id = data.get("session_id")
            message = data.get("message")
            
            if not session_id or not message:
                await websocket.send_json({"error": "Missing session_id or message"})
                continue
                
            async for chunk in agent.stream_chat(session_id, message):
                await websocket.send_json({"chunk": chunk})
                
            await websocket.send_json({"done": True})
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
