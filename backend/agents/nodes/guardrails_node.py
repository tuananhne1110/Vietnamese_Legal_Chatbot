import time
import logging
from backend.agents.state import ChatState
from backend.agents.guardrails.guardrails import Guardrails

guardrails = Guardrails()
logger = logging.getLogger(__name__)

async def guardrails_input(state: ChatState) -> ChatState:
    """
    Node để validate input trước khi xử lý.
    """
    start_time = time.time()
    
    question = state["question"]
    messages = state.get("messages", [])
    
    logger.info(f"[GuardrailsInput] Validating input: {question[:50]}...")
    
    try:
        # Validate input
        validation_result = guardrails.validate_input(question, messages)
        
        if not validation_result["is_safe"]:
            logger.warning(f"[GuardrailsInput] Input validation failed: {validation_result['block_reason']}")
            state["error"] = "input_validation_failed"
            state["answer"] = validation_result["block_reason"]
        else:
            logger.info(f"[GuardrailsInput] Input validation passed")
        
    except Exception as e:
        logger.error(f"[GuardrailsInput] Error during input validation: {e}")
        state["error"] = "input_validation_exception"
        state["answer"] = "Xin lỗi, có lỗi xảy ra trong quá trình kiểm tra đầu vào."
    
    duration = time.time() - start_time
    state["processing_time"]["input_validation"] = duration
    logger.info(f"[GuardrailsInput] Input validation: {duration:.4f}s")
    
    return state
