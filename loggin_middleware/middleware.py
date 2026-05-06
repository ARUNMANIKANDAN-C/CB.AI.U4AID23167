import time
from fastapi import HTTPException, Request, status

PROTECTED_POST_PATHS = {"/notify_group", "/sort_by_priority"}
API_KEY = "api-key"


async def request_logger(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    response.headers["X-Execution-Time"] = f"{duration:.3f}s"
    print(f"{request.method} {request.url.path} completed in {duration:.3f}s")
    return response


async def api_key_protection(request: Request, call_next):
    if request.method == "POST" and request.url.path in PROTECTED_POST_PATHS:
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid API key",
            )
    return await call_next(request)


def add_custom_middleware(app):
    app.middleware("http")(request_logger)
    app.middleware("http")(api_key_protection)
