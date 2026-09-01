from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from app.models.interfaces import Retriever, ChatMemory
from app.core.prompts import CHAT_PROMPT_TEMPLATE
from app.core.config import settings

class ProductAssistantAgent:
    def __init__(self, retriever: Retriever, memory: ChatMemory):
        self.retriever = retriever
        self.memory = memory
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="qwen/qwen3.8-27b", 
            temperature=0.2
        )
        self.chain = CHAT_PROMPT_TEMPLATE | self.llm
        
    def _format_history(self, history: List[Dict[str, str]]) -> List[Any]:
        formatted = []
        for msg in history:
            if msg["role"] == "user":
                formatted.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted.append(AIMessage(content=msg["content"]))
        return formatted
        
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []
        for doc in documents:
            meta = doc.get("metadata", {})
            text = meta.get("text", "")
            if text:
                context_parts.append(f"- {text}")
        return "\n\n".join(context_parts)

    async def chat(self, session_id: str, user_input: str) -> str:
        # 1. Retrieve context
        docs = await self.retriever.retrieve(user_input, top_k=3)
        context_str = self._format_context(docs)
        
        # 2. Get history
        history_dicts = await self.memory.get_history(session_id)
        history_objs = self._format_history(history_dicts)
        
        # 3. Generate response
        response = self.chain.invoke({
            "context": context_str,
            "history": history_objs,
            "input": user_input
        })
        
        answer = response.content
        
        # 4. Save to memory
        await self.memory.add_message(session_id, "user", user_input)
        await self.memory.add_message(session_id, "assistant", answer)
        
        return answer

    async def stream_chat(self, session_id: str, user_input: str):
        # 1. Retrieve context
        docs = await self.retriever.retrieve(user_input, top_k=3)
        context = self._format_context(docs)
        
        # 2. Get chat history
        history = await self.memory.get_history(session_id)
        formatted_history = self._format_history(history)
        
        # 3. Save user message
        await self.memory.add_message(session_id, "user", user_input)
        
        # 4. Stream response
        full_response = ""
        async for chunk in self.chain.astream({
            "context": context,
            "history": formatted_history,
            "input": user_input
        }):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
                
        # 5. Save bot response to memory
        await self.memory.add_message(session_id, "bot", full_response)
