from dataclasses import dataclass
from typing import Optional
import boto3
from instructor import from_bedrock, Mode, Instructor

import yaml
from .configs import LoggerConfig, Models, Database, \
    SystemSettings, EmbeddingModelConfig, QdrantConfig, \
        RerankerModelConfig, LLMModelConfig, VoiceToTextConfig


# from utils import CONFIG
# from configs import LoggerConfig, Models, Database, SystemSettings, EmbeddingModelConfig, QdrantConfig, RerankerModelConfig, LLMModelConfig

@dataclass
class RetrievalSettings:
    qdrant_config: Optional[QdrantConfig]
    embedding_config: Optional[EmbeddingModelConfig]
    reranker_config: Optional[RerankerModelConfig]


# Global variables for lazy loading
_qdrant_client = None
_supabase_client = None
_embedding_model = None
_voice_model = None


class Settings:
    def __init__(self, config_path: str = None):
        if config_path is None:
            import os
            # Sử dụng đường dẫn tuyệt đối
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "configs.yaml")
        self.config_path = config_path
        self._config = self._load_yaml_config()
        
        self.models = Models.from_dict(self._config['models'])

        self.system_settings = SystemSettings(
                logger=LoggerConfig(**self._config['system_settings']['logger'])
            )
        self.logger = self.system_settings.setup_logger()
        self.database = Database.from_dict(self._config['database'])

        self.llm_model_settings = self.models.aws_bedrock.llm_model_configs

        self.guardrails_settings = self.models.aws_bedrock.guardrails

        self.retrieval_settings = RetrievalSettings(
            qdrant_config= self._setup_qdrant_config(),
            embedding_config= self.models.hugging_face.embedding_model_configs['qwen'],
            # embedding_config= self.models.aws_bedrock.embedding_model_configs['titan'],
            reranker_config=self.models.hugging_face.reranker_model_configs['bge'],
        )
        
        # Voice config
        self.voice_config = self.models.hugging_face.voice_to_text_config
        
        # Intent config
        self.intent_config = self._config.get('intent', {})
        
        # Cache config
        self.cache_config = self._config.get('cache', {})
        

        
        # LLM config
        self.llm_config = self._config.get('llm', {})
        
        # App configuration
        self.app_name = "Vietnamese Legal Chatbot"
        self.app_version = "1.0.0"
        self.cors_origins = ["*"]
        self.cors_allow_credentials = True
        self.cors_allow_methods = ["*"]
        self.cors_allow_headers = ["*"]
    
    def _load_yaml_config(self) -> dict:
        """Load YAML configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config: {e}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _setup_llm_client(self):
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.models.aws_bedrock.llm_model_configs['llama'].region_name)
        return from_bedrock(
            client=bedrock_runtime,
            model=self.models.aws_bedrock.llm_model_configs['llama'].model_id,
            mode=Mode.BEDROCK_JSON,
        )
    
    def _setup_qdrant_config(self) -> QdrantConfig:
        for db_type in self.database.db_type:
            if db_type.database_name == "qdrant":
                return db_type
        return None


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def get_qdrant_client():
    """Get or create Qdrant client instance"""
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import QdrantClient
            qdrant_config = settings.retrieval_settings.qdrant_config
            if qdrant_config:
                if qdrant_config.qdrant_url:
                    _qdrant_client = QdrantClient(url=qdrant_config.qdrant_url, api_key=qdrant_config.qdrant_api_key)
                else:
                    _qdrant_client = QdrantClient(host=qdrant_config.qdrant_host, port=qdrant_config.qdrant_port)
            else:
                _qdrant_client = QdrantClient(host="localhost", port=6333)
        except ImportError:
            print("Warning: qdrant-client not installed")
            _qdrant_client = None
        except Exception as e:
            print(f"Error creating Qdrant client: {e}")
            _qdrant_client = None
    return _qdrant_client


def get_supabase_client():
    """Get or create Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client, Client
            # You would need to add Supabase configuration to your config file
            # For now, returning None as placeholder
            _supabase_client = None
        except ImportError:
            print("Warning: supabase not installed")
            _supabase_client = None
        except Exception as e:
            print(f"Error creating Supabase client: {e}")
            _supabase_client = None
    return _supabase_client


def get_embedding_model():
    """Get or create embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            embedding_config = settings.retrieval_settings.embedding_config
            if embedding_config:
                _embedding_model = SentenceTransformer(
                    embedding_config.model_name,
                    device=embedding_config.device
                )
            else:
                _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("Warning: sentence-transformers not installed")
            _embedding_model = None
        except Exception as e:
            print(f"Error creating embedding model: {e}")
            _embedding_model = None
    return _embedding_model


def get_voice_model():
    """Get or create voice model instance"""
    global _voice_model
    if _voice_model is None:
        try:
            voice_config = settings.voice_config
            if voice_config:
                # Import and initialize voice model based on config
                # This is a placeholder - you'll need to implement based on your voice model
                _voice_model = None
            else:
                _voice_model = None
        except Exception as e:
            print(f"Error creating voice model: {e}")
            _voice_model = None
    return _voice_model