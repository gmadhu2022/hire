from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import (auth, admin, enterprise, institute, jobseeker, public,
                      chat, health, uploads, notifications, ai)
from .migrate import sync_schema

# Create tables on startup (for production use Alembic migrations instead).
try:
    Base.metadata.create_all(bind=engine)
    sync_schema()   # add any columns missing from an existing database
except Exception as exc:                                  # pragma: no cover
    raise RuntimeError(
        "\n\nCould not connect to the database.\n\n"
        f"  {type(exc).__name__}: {str(exc).splitlines()[0][:200]}\n\n"
        "Run this for a plain-English diagnosis and the exact fix:\n"
        "    python check_db.py\n"
    ) from None   # add any columns missing from an existing database

app = FastAPI(title=f"{settings.APP_NAME} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(enterprise.router)
app.include_router(institute.router)
app.include_router(jobseeker.router)
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(uploads.router)
app.include_router(ai.router)

# Serve uploaded images (swap for Supabase Storage in production)
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.include_router(uploads.router)
app.include_router(ai.router)
app.include_router(notifications.router)

# Serve uploaded logos/photos at /uploads/<file>
_uploads = Path(__file__).resolve().parent.parent / "uploads"
_uploads.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_uploads)), name="uploads")


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "ok", "docs": "/docs"}
