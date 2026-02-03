"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import get_settings
from app.db.database import init_database
from app.api.routes import excel, documents, answer, review, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    settings = get_settings()

    # Create required directories
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.documents_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_database()

    yield

    # Shutdown
    pass


app = FastAPI(
    title="Security Check Assistant",
    description="API for Security Check Sheet automatic answer generation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(excel.router, prefix="/api/excel", tags=["excel"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(answer.router, prefix="/api/answer", tags=["answer"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(report.router, prefix="/api", tags=["report"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Security Check Assistant API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
