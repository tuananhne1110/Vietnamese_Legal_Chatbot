from dataclasses import dataclass
import json
import re
import logging
from typing import Any, Dict, List, Tuple
from enum import Enum
import boto3

import yaml
from backend.configs.settings import settings
from backend.agents.prompt.prompt_templates import prompt_templates

logger = logging.getLogger(__name__)

# =========================== CONFIG ============================
class IntentType(Enum):
    """Các loại intent của câu hỏi"""
    LAW = "law"           # Tra cứu luật pháp
    FORM = "form"         # Hướng dẫn điền biểu mẫu
    TERM = "term"         # Tra cứu thuật ngữ, định nghĩa
    PROCEDURE = "procedure"  # Thủ tục hành chính
    TEMPLATE = "template"     # Biểu mẫu gốc (template)
    GENERAL = "general"   # câu hỏi chung

COLLECTION_MAP = {
    "procedure": "thủ tục hành chính về lĩnh vực cư trú",
    "law": "văn bản pháp lý về lĩnh vực cư trú",
    "form": "hướng dẫn điền giấy tờ/biểu mẫu về lĩnh vực cư trú",
    "term": "thuật ngữ/định nghĩa về lĩnh vực cư trú",
    "template": "biểu mẫu gốc được dùng làm nền để trích xuất dữ liệu tự động hoặc điền thông tin trong lĩnh vực cư trú",
    "general": "các tình huống giao tiếp thông thường hoặc câu hỏi không liên quan đến cư trú" 
}

COLLECTION_DESCRIPTIONS = {
    IntentType.PROCEDURE: "Thủ tục hành chính cư trú",
    IntentType.LAW: "Văn bản pháp lý cư trú",
    IntentType.FORM: "Hướng dẫn điền biểu mẫu",
    IntentType.TERM: "Thuật ngữ pháp lý",
    IntentType.TEMPLATE: "Biểu mẫu hành chính",
    IntentType.GENERAL: "Câu hỏi chung"
}

MAPPING_IntentType = {
    "procedure": IntentType.PROCEDURE,
    "law": IntentType.LAW,
    "form": IntentType.FORM,
    "term": IntentType.TERM,
    "template": IntentType.TEMPLATE,
    "general": IntentType.GENERAL,

}

# Router system prompt sẽ được lấy từ prompt_templates


intent_cfg = settings.intent_config
KEYWORDS = intent_cfg.get("keywords", {})


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "toolSpec": {
                "name": self.name,
                "description": self.description,
                "inputSchema": {"json": self.input_schema}
            }
        }

TOOL_CONFIGS: List[ToolSpec] = [
    ToolSpec(
        name=collection.value,
        description=COLLECTION_DESCRIPTIONS[collection],
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"Truy vấn tìm kiếm liên quan đến {COLLECTION_MAP[collection.value]}."
                }
            },
            "required": ["query"]
        }
    )
    for collection in IntentType
]


class TextUtils:
    """Tiện ích xử lý văn bản"""
    
    @staticmethod
    def contains_special_characters(text: str) -> bool:
        """Kiểm tra xem chuỗi có chứa các ký tự đặc biệt (escape, unicode, điều khiển)."""
        pattern = r'(\\[ntr"\'\\])|(\\u[0-9a-fA-F]{4})'
        return bool(re.search(pattern, text))

    @staticmethod
    def decode_tool_output(content: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Giải mã nội dung từ assistant trả về ở dạng text chứa JSON bị escape nhiều lần.
        
        Args:
            content: List chứa dict với key "text" (kiểu string).

        Returns:
            Danh sách dict đã parse từ JSON thực sự.
        """
        try:
            raw_text = content[0]["text"]
            json_str_list = json.loads(raw_text)
            decoded = [json.loads(item) for item in json_str_list]
            return decoded
        except Exception as e:
            print(f"Lỗi khi giải mã nội dung: {e}")
            return []

    @staticmethod
    def decode_text_json(text_value: str) -> List[Dict[str, Any]]:
        """
        Giải mã chuỗi text JSON bị escape nhiều lần.
        
        Args:
            text_value: Chuỗi JSON dạng list chứa các string bị escape nhiều lần.

        Returns:
            List các dict giải mã được.
        """
        try:
            raw_list = json.loads(text_value)
            result = [json.loads(item) for item in raw_list]
            return result
        except Exception as e:
            print(f"Lỗi khi decode text JSON: {e}")
            return []


class IntentDetector:
    def __init__(self, 
                service_name='bedrock-runtime', 
                model_id = "us.meta.llama4-scout-17b-instruct-v1:0", 
                region_name = "us-east-1"):
        self.bedrock_runtime_client = boto3.client(service_name=service_name, region_name = region_name)
        self.model_id = model_id
    
    def _fix_encoding(self, text: str) -> str:
        """Fix encoding issues in text returned from Bedrock"""
        if not text:
            return text
        
        original_text = text
        
        # Step 1: Handle URL encoding (multiple passes)
        try:
            import urllib.parse
            current_text = text
            max_passes = 3
            for pass_num in range(max_passes):
                decoded = urllib.parse.unquote(current_text)
                if decoded == current_text:
                    break
                logger.info(f"[IntentDetector] URL decode pass {pass_num + 1}: '{current_text}' -> '{decoded}'")
                current_text = decoded
            text = current_text
        except Exception as e:
            logger.warning(f"[IntentDetector] Failed URL decoding: {e}")
        
        # Step 2: Handle unicode escape sequences
        try:
            if '\\u' in text or '\\x' in text:
                decoded = text.encode('latin-1').decode('unicode_escape')
                if decoded != text:
                    logger.info(f"[IntentDetector] Fixed unicode escape: '{text}' -> '{decoded}'")
                    text = decoded
        except Exception as e:
            logger.warning(f"[IntentDetector] Failed unicode escape fix: {e}")
        
        # Step 3: Handle mixed encoding issues
        try:
            # Try to fix common Vietnamese character issues
            replacements = {
                'Ä': 'Đ', 'Äƒ': 'ă', 'Ä‚': 'Ă',
                'Ã': 'ã', 'Ã¡': 'á', 'Ã ': 'à',
                'Ã¢': 'â', 'Ã£': 'ã', 'Ã¤': 'ä',
                'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê',
                'Ã­': 'í', 'Ã¬': 'ì', 'Ã®': 'î',
                'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô',
                'Ãº': 'ú', 'Ã¹': 'ù', 'Ã»': 'û',
                'Ã½': 'ý', 'Ã¿': 'ÿ',
                'Ã§': 'ç', 'Ã‡': 'Ç',
                'Ã±': 'ñ', 'Ã': 'Ñ'
            }
            
            for wrong, correct in replacements.items():
                if wrong in text:
                    text = text.replace(wrong, correct)
                    logger.info(f"[IntentDetector] Fixed character: '{wrong}' -> '{correct}'")
        except Exception as e:
            logger.warning(f"[IntentDetector] Failed character replacement: {e}")
        
        # Step 4: Final UTF-8 validation
        try:
            if text != original_text:
                # Ensure proper UTF-8 encoding
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except Exception as e:
            logger.warning(f"[IntentDetector] Failed UTF-8 validation: {e}")
            return original_text
        
        return text
    
    def _is_garbled_text(self, text: str) -> bool:
        """Kiểm tra xem text có bị lỗi encoding không"""
        if not text:
            return True
        
        # Kiểm tra các ký tự lỗi encoding phổ biến
        garbled_patterns = [
            'Ä', 'Ã', 'â', '€', '™', 'š', 'œ', 'ž', 'Ÿ',
            '¡', '¢', '£', '¤', '¥', '¦', '§', '¨', '©',
            'ª', '«', '¬', '®', '¯', '°', '±', '²', '³'
        ]
        
        # Đếm số ký tự lỗi
        garbled_count = sum(1 for char in text if char in garbled_patterns)
        
        # Nếu có quá nhiều ký tự lỗi (>20% text), coi như bị lỗi
        if garbled_count > len(text) * 0.2:
            logger.info(f"[IntentDetector] Text appears garbled: {garbled_count}/{len(text)} garbled chars")
            return True
        
        # Kiểm tra có quá nhiều ký tự đặc biệt không
        special_chars = sum(1 for char in text if ord(char) > 127)
        if special_chars > len(text) * 0.5:
            logger.info(f"[IntentDetector] Text has too many special chars: {special_chars}/{len(text)}")
            return True
        
        return False
    
    def detect_intent(self, query: str, trace_id: str = None) -> List[Tuple[IntentType, str]]:
        logger.info(f"[IntentDetector] Processing query: '{query}'")
        
        messages = [{"role": "user", "content": [{"text": query}]}]
        tool_config = {"tools": [tool.to_dict() for tool in TOOL_CONFIGS]}
        list_intent_type: List[Tuple[IntentType, str]] = []
        
        try:
            logger.info(f"[IntentDetector] Calling Bedrock with model: {self.model_id}")
            # Lấy router system prompt từ prompt_templates
            router_prompt = prompt_templates.get_intent_router_prompt(question=query)
            
            response = self.bedrock_runtime_client.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": router_prompt}],
                toolConfig=tool_config
            )

            output = response["output"]["message"]["content"]
            logger.info(f"[IntentDetector] Raw Bedrock response: {response}")
            logger.info(f"[IntentDetector] Extracted output content: {output}")
            for i, item in enumerate(output):
                logger.info(f"[IntentDetector] Processing output item {i}: {item}")
                
                # Trường hợp toolUse (định tuyến trực tiếp)
                if "toolUse" in item:
                    tool_name = item['toolUse']['name']
                    new_query = item['toolUse']['input'].get('query', query)
                    # Fix encoding issue
                    new_query = self._fix_encoding(new_query)
                    
                    # Fallback: nếu query bị lỗi encoding, sử dụng query gốc
                    if not new_query or len(new_query.strip()) < 3 or self._is_garbled_text(new_query):
                        logger.warning(f"[IntentDetector] Invalid query after encoding fix, using original: '{new_query}' -> '{query}'")
                        new_query = query
                    
                    intent = MAPPING_IntentType.get(tool_name, IntentType.GENERAL)
                    logger.info(f"[IntentDetector] Found toolUse - tool_name: {tool_name}, intent: {intent}, query: '{new_query}'")
                    list_intent_type.append((intent, new_query))
                    continue

                # Trường hợp trả về dưới dạng text (có thể là JSON)
                if "text" in item and isinstance(item["text"], str):
                    logger.info(f"[IntentDetector] Found text response: {item['text']}")
                    try:
                        tool_results = TextUtils.decode_text_json(item["text"])
                        logger.info(f"[IntentDetector] Decoded JSON tool results: {tool_results}")
                        for tool_result in tool_results:
                            new_query = tool_result['parameters'].get('query', query)
                            # Fix encoding issue
                            new_query = self._fix_encoding(new_query)
                            
                            # Fallback: nếu query bị lỗi encoding, sử dụng query gốc
                            if not new_query or len(new_query.strip()) < 3 or self._is_garbled_text(new_query):
                                logger.warning(f"[IntentDetector] Invalid query after encoding fix, using original: '{new_query}' -> '{query}'")
                                new_query = query
                            
                            tool_name = tool_result.get('name')
                            intent = MAPPING_IntentType.get(tool_name, IntentType.GENERAL)
                            logger.info(f"[IntentDetector] From JSON - tool_name: {tool_name}, intent: {intent}, query: '{new_query}'")
                            list_intent_type.append((intent, new_query))
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        logger.warning(f"[IntentDetector] Failed to parse JSON response: {e}")
                        list_intent_type.append((IntentType.GENERAL, query))
                else:
                    logger.info(f"[IntentDetector] Unknown item format, defaulting to GENERAL")
                    list_intent_type.append((IntentType.GENERAL, query))
        except Exception as e:
            logger.error(f"[IntentDetector] Error during intent detection: {e}")
            return [(IntentType.GENERAL, query)]

        logger.info(f"[IntentDetector] Raw detected intents: {list_intent_type}")

        # Nếu có PROCEDURE thì tự động thêm LAW và FORM nếu chưa có
        has_procedure = any(intent == IntentType.PROCEDURE for intent, _ in list_intent_type)
        if has_procedure:
            logger.info(f"[IntentDetector] PROCEDURE intent detected, checking for auto-add LAW and FORM")
            for extra_intent in [IntentType.LAW, IntentType.FORM]:
                if not any(intent == extra_intent for intent, _ in list_intent_type):
                    logger.info(f"[IntentDetector] Auto-adding {extra_intent} intent")
                    list_intent_type.append((extra_intent, query))

        logger.info(f"[IntentDetector] Final result: {list_intent_type}")
        return list_intent_type


    def get_search_collections(self, intents: List[Tuple[IntentType, str]]) -> List[str]:
        logger.info(f"[IntentDetector] Converting intents to collections: {intents}")
        
        list_collections = []
        for intent in intents:
            intent_type = intent[0]
            if intent_type == IntentType.LAW:
                collection = "legal_chunks"
            elif intent_type == IntentType.FORM:
                collection = "form_chunks"
            elif intent_type == IntentType.TERM:
                collection = "legal_chunks"  # Chuyển term search sang legal_chunks
            elif intent_type == IntentType.PROCEDURE:
                collection = "procedure_chunks"
            elif intent_type == IntentType.TEMPLATE:
                collection = "template_chunks"
            else:
                collection = "general_chunks"
            
            logger.info(f"[IntentDetector] Intent {intent_type} → Collection {collection}")
            list_collections.append(collection)
        
        logger.info(f"[IntentDetector] Final collections list: {list_collections}")
        return list_collections


intent_detector = IntentDetector(service_name='bedrock-runtime', model_id = "us.meta.llama4-scout-17b-instruct-v1:0")
