# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Local imports from project structure
from api import module as api_module
from core import config
from core.security import get_current_user
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, UserPublic
from dependencies import get_db

# Create the FastAPI app
app = FastAPI()

# Setup database tables
Base.metadata.create_all(bind=engine)

# Middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router from api module
app.include_router(api_module.router)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database.
    """
    # Add user creation logic here
    pass

@app.get("/users/", response_model=List[UserPublic])
def read_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user)):
    """
    Retrieve users from the database.
    """
    # Add user retrieval logic here
    pass

# Main entry point for running the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)