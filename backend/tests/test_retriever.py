import pytest
from unittest.mock import MagicMock, patch
from app.services.pinecone_retriever import PineconeRetriever

@pytest.fixture
def mock_pinecone():
    with patch("app.services.pinecone_retriever.Pinecone") as MockPinecone:
        mock_pc_instance = MockPinecone.return_value
        mock_index = MagicMock()
        mock_pc_instance.Index.return_value = mock_index
        yield mock_index

@pytest.mark.asyncio
async def test_retriever(mock_pinecone):
    # Setup mock return value for Pinecone search
    mock_pinecone.query.return_value = {
        "matches": [
            {
                "id": "prod_1",
                "score": 0.95,
                "metadata": {"text": "Premium Laptop for $1200"}
            },
            {
                "id": "prod_2",
                "score": 0.85,
                "metadata": {"text": "Budget Laptop for $500"}
            }
        ]
    }
    
    # We mock embeddings inside retriever for this test
    with patch("app.services.pinecone_retriever.HuggingFaceEmbeddings") as MockEmbeddings:
        mock_embeddings_instance = MockEmbeddings.return_value
        mock_embeddings_instance.embed_query.return_value = [0.1] * 384
        
        retriever = PineconeRetriever(api_key="fake", index_name="test")
        results = await retriever.retrieve("laptop", top_k=2)
        
        assert len(results) == 2
        assert results[0]["metadata"]["text"] == "Premium Laptop for $1200"
        assert "Budget Laptop" in results[1]["metadata"]["text"]
        
        # Ensure pinecone query was called
        mock_pinecone.query.assert_called_once()
