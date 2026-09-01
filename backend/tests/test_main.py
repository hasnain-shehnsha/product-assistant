from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the RAG Chatbot API"}

from unittest.mock import MagicMock
from app.api.chat import get_agent

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint():
    # Mock the agent using dependency injection
    mock_agent = MagicMock()
    
    # We must return a coroutine result or use AsyncMock for async methods
    # But for chat(), it is async, so we mock it properly
    async def mock_chat(session_id, message):
        return "This is a mocked response."
        
    mock_agent.chat = mock_chat
    
    app.dependency_overrides[get_agent] = lambda: mock_agent
    
    response = client.post(
        "/api/chat",
        json={"session_id": "test_session_123", "message": "I need a laptop"}
    )
    
    assert response.status_code == 200
    assert response.json()["response"] == "This is a mocked response."
    
    # Reset override
    app.dependency_overrides.clear()

def test_websocket_chat_endpoint():
    mock_agent = MagicMock()
    
    async def mock_stream(session, msg):
        yield "Streamed "
        yield "chunk."
    
    mock_agent.stream_chat = mock_stream
    app.dependency_overrides[get_agent] = lambda: mock_agent
    
    with client.websocket_connect("/api/chat/stream") as websocket:
        websocket.send_json({"session_id": "ws_123", "message": "hello"})
        
        data = websocket.receive_json()
        assert data == {"chunk": "Streamed "}
        
        data2 = websocket.receive_json()
        assert data2 == {"chunk": "chunk."}
        
        data3 = websocket.receive_json()
        assert data3 == {"done": True}
        
    app.dependency_overrides.clear()
