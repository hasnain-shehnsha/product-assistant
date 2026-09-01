import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.agent import ProductAssistantAgent

@pytest.fixture
def mock_agent_deps():
    mock_retriever = AsyncMock()
    mock_retriever.retrieve.return_value = [{"metadata": {"text": "Test Product for $10"}}]
    
    mock_memory = AsyncMock()
    mock_memory.get_history.return_value = []
    
    return mock_retriever, mock_memory

@pytest.mark.asyncio
async def test_agent_generation(mock_agent_deps):
    mock_retriever, mock_memory = mock_agent_deps
    
    with patch("app.core.agent.ChatGroq"):
        agent = ProductAssistantAgent(retriever=mock_retriever, memory=mock_memory)
        
        mock_response = MagicMock()
        mock_response.content = "Here is the Test Product for $10."
        agent.chain = MagicMock()
        agent.chain.invoke.return_value = mock_response
        
        response = await agent.chat("session_1", "What products do you have?")
        
        assert "Test Product" in response
        assert "$10" in response
        
        # Verify dependencies were called
        mock_retriever.retrieve.assert_called_once_with("What products do you have?", top_k=3)
        mock_memory.get_history.assert_called_once_with("session_1")
        mock_memory.add_message.assert_called() # Should add both user and AI messages
