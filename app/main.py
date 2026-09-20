import re
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.api import ask, documents, extract, health, search, tasks, traces
from app.api.schemas import ErrorOut
from app.db.session import get_engine
from app.settings import get_settings
from app.trace import ErrorKind, begin_request, end_request, mark_error


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_engine()  # create tables on first start
    yield


app = FastAPI(title="ai-eng-track", version="0.1.0", lifespan=_lifespan)
app.include_router(documents.router)
app.include_router(extract.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(tasks.router)
app.include_router(traces.router)
app.include_router(health.router)
# The hub page (GitHub Pages) calls the live service from the browser: CORS must allow it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id"],
)


@app.middleware("http")
async def _trace_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """One span tree per request; the id comes back as X-Request-Id for GET /traces/{id}."""
    route = re.sub(r"/\d+(?=/|$)", "/{id}", request.url.path)
    rid = begin_request(f"{request.method} {route}")
    try:
        response = await call_next(request)
    except Exception:
        mark_error(ErrorKind.unknown, "unhandled exception")
        with Session(get_engine()) as session:
            end_request(session)
        raise
    with Session(get_engine()) as session:
        end_request(session)
    response.headers["X-Request-Id"] = rid
    return response


@app.exception_handler(HTTPException)
async def _http_error(_: Request, exc: HTTPException) -> JSONResponse:
    code = {404: "not_found", 415: "unsupported_type"}.get(exc.status_code, "http_error")
    kind = {404: ErrorKind.not_found, 415: ErrorKind.unsupported}.get(exc.status_code)
    mark_error(kind or ErrorKind.unknown, str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorOut(error=code, detail=str(exc.detail)).model_dump(),
    )
