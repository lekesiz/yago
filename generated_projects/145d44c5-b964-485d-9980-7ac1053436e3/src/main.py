# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base_class import Base  # Import all models
from app.models import *  # Ensure all models are imported before initializing DB

# Create all tables in the database.
# Comment this out if you're using Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Middleware configurations
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Include the router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Main entry point for Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)