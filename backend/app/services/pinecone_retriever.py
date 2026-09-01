from typing import List, Dict, Any
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from app.models.interfaces import Retriever

class PineconeRetriever(Retriever):
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # Generate embedding for the query
        query_vector = self.embeddings.embed_query(query)
        
        # Search Pinecone
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in response.get("matches", []):
            results.append({
                "id": match["id"],
                "score": match["score"],
                "metadata": match.get("metadata", {})
            })
            
        return results
