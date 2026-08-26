from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import audit, auth, consents, doctor, documents, patients, processing, records

Base.metadata.create_all(bind=engine)
Path(settings.storage_path).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="MediVault API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", str(uuid4())),
            }
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


app.include_router(auth.router, prefix="/v1")
app.include_router(patients.router, prefix="/v1")
app.include_router(documents.router, prefix="/v1")
app.include_router(records.router, prefix="/v1")
app.include_router(consents.router, prefix="/v1")
app.include_router(audit.router, prefix="/v1")
app.include_router(processing.router, prefix="/v1")
app.include_router(doctor.router, prefix="/v1")
