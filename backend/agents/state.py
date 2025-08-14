from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from backend.agents.utils.intent_detector import IntentType

class ChatState(TypedDict):
    """State cho LangGraph chat system"""
    messages: Annotated[List[BaseMessage], "add_messages"]  # Use Annotated for multiple updates
    question: str
    session_id: str
    intent: Optional[IntentType]
    all_intents: List[tuple]  
    context_docs: List[Document]
    rewritten_query: Optional[str]
    sources: List[Dict[str, Any]]
    answer: Annotated[Optional[str], "answer"]  
    error: Annotated[Optional[str], "error"]  
    metadata: Dict[str, Any]
    processing_time: Annotated[Dict[str, float], "processing_time"]  
    prompt: Optional[str]  # Add prompt for streaming
    answer_chunks: Annotated[Optional[List[str]], "answer_chunks"]  
