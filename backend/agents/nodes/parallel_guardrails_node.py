import time
import logging
import traceback
import asyncio
from backend.agents.state import ChatState
from backend.agents.guardrails.guardrails import Guardrails

guardrails = Guardrails()
logger = logging.getLogger(__name__)

async def parallel_guardrails_output(state: ChatState) -> ChatState:
    """
    Node để xử lý guardrails output validation song song với LLM generation.
    Node này sẽ được chạy parallel với generate_node.
    """
    start_time = time.time()
    
    # Kiểm tra nếu input đã bị chặn bởi guardrails
    if state.get("error") == "input_validation_failed":
        logger.info(f"[ParallelGuardrails] Skipping output validation due to input guardrails error")
        state["processing_time"]["parallel_output_validation"] = time.time() - start_time
        return state
    
    # Lấy answer từ state (có thể là chunk hoặc full answer)
    answer = state.get("answer", "")
    answer_chunks = state.get("answer_chunks", [])
    
    # Nếu chưa có answer, đợi generation hoàn thành
    if not answer and not answer_chunks:
        logger.info(f"[ParallelGuardrails] No answer available yet, waiting for generation")
        state["processing_time"]["parallel_output_validation"] = time.time() - start_time
        return state
    
    # Nếu có chunks, validate từng chunk
    if answer_chunks:
        validated_chunks = []
        for i, chunk in enumerate(answer_chunks):
            chunk_safety = guardrails.validate_output(chunk)
            if not chunk_safety["is_safe"]:
                logger.warning(f"[ParallelGuardrails] Chunk {i+1} validation failed: {chunk_safety['block_reason']}")
                # Thay thế chunk bị chặn bằng fallback message
                validated_chunks.append(guardrails.get_fallback_message(chunk_safety["block_reason"]))
            else:
                validated_chunks.append(chunk)
        
        # Cập nhật state với chunks đã validate
        state["answer_chunks"] = validated_chunks
        state["answer"] = "".join(validated_chunks)
        state["guardrails_output_validated"] = True
        
    # Nếu chỉ có answer (không có chunks)
    elif answer:
        output_safety = guardrails.validate_output(answer)
        if not output_safety["is_safe"]:
            logger.warning(f"[ParallelGuardrails] Output validation failed: {output_safety['block_reason']}")
            fallback_msg = guardrails.get_fallback_message(output_safety["block_reason"])
            state["answer"] = fallback_msg
            state["error"] = "output_validation_failed"
        else:
            logger.info(f"[ParallelGuardrails] Output validation passed")
            state["guardrails_output_validated"] = True
    
    # Đánh dấu rằng parallel guardrails đã hoàn thành
    state["parallel_guardrails_completed"] = True
    
    duration = time.time() - start_time
    state["processing_time"]["parallel_output_validation"] = duration
    logger.info(f"[ParallelGuardrails] Parallel output validation: {duration:.4f}s")
    return state
