import time
import logging
from backend.agents.state import ChatState
from backend.agents.guardrails.guardrails import Guardrails

guardrails = Guardrails()
logger = logging.getLogger(__name__)

async def validate_output(state: ChatState) -> ChatState:
    """
    Node để validate output sau khi generate.
    Sequential processing thay vì parallel.
    """
    start_time = time.time()
    
    # Kiểm tra nếu input đã bị chặn bởi guardrails
    if state.get("error") == "input_validation_failed":
        logger.info(f"[ValidateOutput] Skipping output validation due to input guardrails error")
        state["processing_time"]["output_validation"] = time.time() - start_time
        return state
    
    answer = state.get("answer", "")
    
    if not answer:
        logger.info(f"[ValidateOutput] No answer to validate")
        state["processing_time"]["output_validation"] = time.time() - start_time
        return state
    
    try:
        # Validate output
        validation_result = guardrails.validate_output(answer)
        
        if not validation_result["is_safe"]:
            logger.warning(f"[ValidateOutput] Output validation failed: {validation_result['block_reason']}")
            fallback_msg = guardrails.get_fallback_message(validation_result["block_reason"])
            state["answer"] = fallback_msg
            state["error"] = "output_validation_failed"
        else:
            logger.info(f"[ValidateOutput] Output validation passed")
        
    except Exception as e:
        logger.error(f"[ValidateOutput] Error during output validation: {e}")
        state["error"] = "output_validation_exception"
        state["answer"] = "Xin lỗi, có lỗi xảy ra trong quá trình kiểm tra đầu ra."
    
    duration = time.time() - start_time
    state["processing_time"]["output_validation"] = duration
    logger.info(f"[ValidateOutput] Output validation: {duration:.4f}s")
    
    return state
