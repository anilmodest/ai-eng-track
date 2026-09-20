from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.api import documents, extract
from app.api.schemas import ErrorOut
from app.db.session import get_engine


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_engine()  # create tables on first start
    yield


app = FastAPI(title="ai-eng-track", version="0.1.0", lifespan=_lifespan)
app.include_router(documents.router)
app.include_router(extract.router)


@app.exception_handler(HTTPException)
async def _http_error(_: Request, exc: HTTPException) -> JSONResponse:
    code = {404: "not_found", 415: "unsupported_type"}.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorOut(error=code, detail=str(exc.detail)).model_dump(),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
