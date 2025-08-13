import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from backend.configs.settings import get_settings
from backend.middleware.error_handler import ErrorHandlerMiddleware, RequestLoggingMiddleware
from backend.routers import health
from backend.routers.ct01 import router as ct01_router
from backend.routers.langgraph_chat import router as langgraph_chat_router
from backend.routers.voice_to_text import router as voice_to_text_router

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # Reduce noisy modules
    logging.getLogger("backend.agents.context_manager").setLevel(logging.WARNING)
    logging.getLogger("backend.prompt.prompt_manager").setLevel(logging.WARNING)
    logging.getLogger("backend.prompt.prompt_templates").setLevel(logging.WARNING)
    logging.getLogger("backend.services.qdrant_service").setLevel(logging.WARNING)
    logging.getLogger("backend.services.reranker_service").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()

    
    # Lazy load heavy resources during startup
    logger.info("Application startup: Initializing resources...")
    from backend.configs.settings import get_qdrant_client, get_supabase_client, get_embedding_model, get_voice_model
    from backend.services.reranker_service import get_reranker
    from backend.embeddings import get_embedding  # This will trigger eager loading
    
    # Preload clients/models to ensure they are available for dependency injection
    get_qdrant_client()
    get_supabase_client()
    get_embedding_model()
    get_voice_model()  # Preload voice model if configured
    get_reranker()  # Preload BGE reranker
    
    # Test embedding to ensure it's working
    try:
        get_embedding("test")
        logger.info("Embedding model validated successfully")
    except Exception as e:
        logger.error(f"Embedding model validation failed: {e}")
    
    logger.info("Resources initialized. Application ready.")
    yield
    # Shutdown
    logger.info("Application shutdown: Cleaning up resources...")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    # Add middleware
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Routers
    app.include_router(langgraph_chat_router)
    app.include_router(health.router)
    app.include_router(ct01_router)
    app.include_router(voice_to_text_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
