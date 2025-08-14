from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from backend.agents.state import ChatState
from backend.agents.nodes.intent_node import set_intent
from backend.agents.nodes.rewrite_node import rewrite_query_with_context
from backend.agents.nodes.retrieve_node import retrieve_context
from backend.agents.nodes.generate_node import generate_answer
from backend.agents.nodes.validate_node import validate_output
from backend.agents.nodes.memory_node import update_memory
from backend.agents.nodes.semantic_cache_node import semantic_cache
from backend.agents.nodes.guardrails_node import guardrails_input
# parallel_guardrails_node removed - using sequential processing
from backend.configs import settings
import os
import logging

logger = logging.getLogger(__name__)

class LangChainRAGComponents:
    def __init__(self):
        self.embeddings = None
        self.memory = None
    def create_conversational_chain(self):
        return {"type": "conversational_chain", "description": "LangChain conversational retrieval chain"}
    def create_retrieval_chain(self, intent: str):
        return {"type": "retrieval_chain", "intent": intent, "description": f"LangChain retrieval chain for {intent}"}

def should_continue_after_guardrails(state: ChatState) -> str:
    """Kiểm tra xem có nên tiếp tục sau guardrails hay không."""
    if state.get("error") == "input_validation_failed":
        return "update_memory"  # Chuyển thẳng đến update_memory nếu bị chặn
    return "rewrite"  # Tiếp tục bình thường

def should_continue_to_validate(state: ChatState) -> str:
    """Quyết định có tiếp tục validate hay không."""
    if state.get("error") == "input_validation_failed":
        return "update_memory"
    return "validate"

def create_rag_workflow():
    workflow = StateGraph(ChatState)
    workflow.add_node("set_intent", set_intent)
    workflow.add_node("semantic_cache", semantic_cache)
    workflow.add_node("guardrails_input", guardrails_input)
    workflow.add_node("rewrite", rewrite_query_with_context)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("validate", validate_output)
    workflow.add_node("update_memory", update_memory)
    
    # Edges - Sequential flow with guardrails
    workflow.add_edge(START, "set_intent")
    workflow.add_edge("set_intent", "semantic_cache")
    
    # Conditional edge after guardrails input
    workflow.add_conditional_edges(
        "semantic_cache",
        lambda state: "guardrails_input",  # Always go to guardrails first
        {"guardrails_input": "guardrails_input"}
    )
    
    # Conditional edge after guardrails - continue or skip to memory
    workflow.add_conditional_edges(
        "guardrails_input",
        should_continue_after_guardrails,
        {
            "rewrite": "rewrite",
            "update_memory": "update_memory"
        }
    )
    
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("retrieve", "generate")
    
    # Conditional edge after generate - validate or skip to memory
    workflow.add_conditional_edges(
        "generate",
        should_continue_to_validate,
        {
            "validate": "validate",
            "update_memory": "update_memory"
        }
    )
    
    workflow.add_edge("validate", "update_memory")
    workflow.add_edge("update_memory", END)
    
    # Compile workflow
    app = workflow.compile()
    
    return app

rag_workflow = create_rag_workflow()
langchain_components = LangChainRAGComponents() 