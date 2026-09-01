import pytest
from mongomock_motor import AsyncMongoMockClient
from app.services.session_repository import MongoSessionRepository

@pytest.fixture
def mock_repo():
    # Use mongomock to simulate motor's async client
    client = AsyncMongoMockClient()
    db = client["test_db"]
    collection = db["test_sessions"]
    
    repo = MongoSessionRepository(uri="mongodb://localhost:27017", db_name="test_db", collection_name="test_sessions")
    repo.client = client
    repo.db = db
    repo.collection = collection
    return repo

@pytest.mark.asyncio
async def test_add_and_get_message(mock_repo):
    session_id = "test_session_1"
    
    # Verify initial history is empty
    history = await mock_repo.get_history(session_id)
    assert history == []
    
    # Add messages
    await mock_repo.add_message(session_id, "user", "Hello")
    await mock_repo.add_message(session_id, "assistant", "Hi there!")
    
    # Retrieve history
    history = await mock_repo.get_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"

@pytest.mark.asyncio
async def test_get_history_limit(mock_repo):
    session_id = "test_session_2"
    
    for i in range(15):
        await mock_repo.add_message(session_id, "user", f"Message {i}")
        
    # Get history with limit 10
    history = await mock_repo.get_history(session_id, limit=10)
    assert len(history) == 10
    # The last message should be "Message 14"
    assert history[-1]["content"] == "Message 14"
    # The first in the limited list should be "Message 5"
    assert history[0]["content"] == "Message 5"
