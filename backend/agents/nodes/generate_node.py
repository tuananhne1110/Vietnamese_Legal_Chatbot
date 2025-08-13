﻿import time
import asyncio
import logging
import traceback
from backend.agents.state import ChatState
from langchain_core.messages import AIMessage

import boto3
import yaml
from backend.agents.utils.intent_detector import IntentType
from backend.configs.settings import settings
from backend.agents.prompt.prompt_templates import prompt_templates

logger = logging.getLogger(__name__)
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

def load_llm_config(yaml_path="config/config.yaml"):
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("llm", {})
    except Exception:
        return {}

llm_cfg = settings.llm_config
prompt_version = llm_cfg.get("prompt_version", "v1")
model_name = llm_cfg.get("default_model_name", "us.meta.llama4-scout-17b-instruct-v1:0")

async def generate_answer(state: ChatState) -> ChatState:
    start_time = time.time()
    
    # Kiểm tra nếu đã có error từ guardrails
    if state.get("error") == "input_validation_failed":
        logger.info(f"[Generate] Skipping generation due to guardrails error")
        state["processing_time"]["answer_generation"] = time.time() - start_time
        return state
    
    question = state["question"]
    docs = state["context_docs"]
    intent = state["intent"]
    history = state.get("messages", [])

    if docs:
        logger.info(f"[Generate] First doc: {docs[0] if docs else 'None'}")
    if not docs:
        logger.warning(f"[LangGraph] No docs found for question: {question}")
        logger.info(f"[LangGraph] Intent detected: {intent}")
        
        # Xử lý câu hỏi chung chung
        if intent == IntentType.GENERAL:
            logger.info(f"[LangGraph] Processing GENERAL intent for question: {question}")
            # Sử dụng LLM để trả lời câu hỏi chung chung
            try:
                from backend.services.llm_service import call_llm_stream
                
                loop = asyncio.get_running_loop()
                answer_chunks = []
                for chunk in await loop.run_in_executor(None, lambda: list(call_llm_stream(question, model_name, max_tokens=500, temperature=0.3))):
                    answer_chunks.append(chunk)
                answer = "".join(answer_chunks)
                state["answer"] = answer
                state["answer_chunks"] = answer_chunks
                
                logger.info(f"[Generate] Logging input/model/metadata: input={question}, model={model_name}")
                
                return state
            except Exception as e:
                logger.error(f"[LangGraph] Error generating general response: {e}")
                # Fallback response cho câu hỏi chung chung
                state["answer"] = "Xin chào! Tôi là trợ lý AI, rất vui được gặp bạn. Bạn có thể hỏi tôi về các vấn đề liên quan đến thủ tục hành chính, luật pháp, biểu mẫu hoặc các câu hỏi khác."
        else:
            # Giữ nguyên response cho các intent khác
            state["answer"] = "Xin lỗi, không tìm thấy thông tin liên quan đến câu hỏi của bạn trong cơ sở dữ liệu pháp luật hiện có. Vui lòng thử câu hỏi khác hoặc liên hệ với cơ quan chức năng có thẩm quyền để được hỗ trợ."
        
        logger.info(f"[Generate] Logging input/model/metadata: input={question}, model={model_name}")

        return state
    loop = asyncio.get_running_loop()
    # Format docs để phù hợp với prompt_templates
    formatted_docs = []
    for doc in docs:
        doc_dict = {
            "content": doc.page_content,
            "page_content": doc.page_content,
            **doc.metadata
        }
        formatted_docs.append(doc_dict)
    
    # Tạo prompt trực tiếp từ prompt_templates
    prompt_template = prompt_templates.get_prompt_by_category()
    formatted_context = prompt_templates.format_context_by_category(formatted_docs)
    prompt = prompt_template.format(
        context=formatted_context,
        question=question
    )
    
    system_prompt = prompt_templates.get_prompt_by_category()
    state["prompt"] = prompt
    logger.info(f"[Generate] Logging input/model/metadata: input={prompt}, model={model_name}")
    token_input = 0
    token_output = 0
    try:
        from backend.services.llm_service import call_llm_stream
        answer_chunks = []
        raw_llm_response = []
        for chunk in await loop.run_in_executor(None, lambda: list(call_llm_stream(prompt, model_name, max_tokens=800, temperature=0.2))):
            answer_chunks.append(chunk)
            raw_llm_response.append(chunk)
        answer = "".join(answer_chunks)
        
        # Post-processing: cắt bớt nếu câu trả lời quá dài
        if len(answer) > 1500:  # Giới hạn 1500 ký tự
            # Tìm vị trí cắt hợp lý (cuối câu)
            cut_position = answer.rfind('.', 0, 1500)
            if cut_position == -1:
                cut_position = answer.rfind('\n', 0, 1500)
            if cut_position == -1:
                cut_position = 1500
            answer = answer[:cut_position + 1].strip()
            logger.info(f"[Generate] Truncated long answer from {len(''.join(answer_chunks))} to {len(answer)} characters")
        
        state["answer"] = answer
        state["answer_chunks"] = answer_chunks 
        # Log usage details
        logger.info(f"[Generate] Logging usage_details={token_input}/{token_output}, cost_details=0")
    except Exception as e:
        logger.error(f"[LangGraph] Error in generate_answer: {e}")
        tb = traceback.format_exc()
        state["error"] = "generation_exception"
        state["answer"] = f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi: {str(e)}"
    duration = time.time() - start_time
    state["processing_time"]["answer_generation"] = duration
    logger.info(f"[LangGraph] Answer generation: {duration:.4f}s")
    return state 