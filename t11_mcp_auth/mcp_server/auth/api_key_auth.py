from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

API_KEY: str = "dev-secret-key"


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that validates the X-API-Key header on every
    incoming request before it reaches the MCP server.
    """

    async def dispatch(self, request: Request, call_next):
        #TODO:
        # 1. Read the `X-API-Key` header from `request.headers`
        # 2. If it doesn't match `API_KEY` — return a 401 `JSONResponse` with an error message
        # 3. Otherwise pass the request to the next handler and return its response
        raise NotImplementedError()