﻿import time
import logging
import traceback
from backend.agents.state import ChatState
from backend.agents.guardrails.guardrails import Guardrails

guardrails = Guardrails()
logger = logging.getLogger(__name__)

async def validate_output(state: ChatState) -> ChatState:
    start_time = time.time()
    
    # Kiểm tra nếu input đã bị chặn bởi guardrails
    if state.get("error") == "input_validation_failed":
        logger.info(f"[Validate] Skipping output validation due to input guardrails error")
        state["processing_time"]["output_validation"] = time.time() - start_time
        return state
    
    # Kiểm tra nếu parallel guardrails đã validate output
    if state.get("guardrails_output_validated") and state.get("parallel_guardrails_completed"):
        logger.info(f"[Validate] Skipping output validation - parallel guardrails already validated")
        state["processing_time"]["output_validation"] = time.time() - start_time
        return state
    
    answer = state["answer"] or ""
    output_safety = guardrails.validate_output(answer)
    try:
        if not output_safety["is_safe"]:
            fallback_msg = guardrails.get_fallback_message(output_safety["block_reason"])
            state["answer"] = fallback_msg
            state["error"] = "output_validation_failed"
            logger.warning(f"[LangGraph] Output validation failed: {output_safety['block_reason']}")
        else:
            logger.info(f"[LangGraph] Output validation passed")
    except Exception as e:
        logger.error(f"[LangGraph] Exception in output validation: {e}")
        tb = traceback.format_exc()
        state["error"] = "output_validation_exception"
    duration = time.time() - start_time
    state["processing_time"]["output_validation"] = duration
    logger.info(f"[LangGraph] Output validation: {duration:.4f}s")
    return state 