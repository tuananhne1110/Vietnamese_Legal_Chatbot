import logging
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and logging requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Log error details
            process_time = time.time() - start_time
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)} - {process_time:.3f}s",
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e) if logger.isEnabledFor(logging.DEBUG) else "An error occurred",
                    "path": str(request.url.path),
                    "method": request.method
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request details."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request start
        logger.debug(f"Request started: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log request completion
        logger.debug(f"Request completed: {request.method} {request.url.path} - {response.status_code}")
        
        return response
