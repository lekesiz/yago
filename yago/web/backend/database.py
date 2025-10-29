"""
YAGO v8.0 - Database Configuration
SQLAlchemy setup for PostgreSQL with Connection Pooling
"""

import os
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
# Format: postgresql://user:password@localhost:5432/yago
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./yago.db"  # Fallback to SQLite for development
)

# Create engine with optimized connection pooling
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        # SQLite-specific optimizations
        echo=False,  # Disable SQL logging for performance
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        # Connection pool settings
        poolclass=pool.QueuePool,
        pool_size=20,  # Number of connections to maintain
        max_overflow=30,  # Maximum number of connections that can be created beyond pool_size
        pool_timeout=30,  # Seconds to wait before timing out
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Test connections before using them
        # Performance settings
        echo=False,  # Disable SQL logging in production
        # Query execution settings
        execution_options={
            "isolation_level": "READ COMMITTED"  # Default isolation level
        },
    )

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Don't expire objects after commit for better performance
)

# Create Base class
Base = declarative_base()


# Event listeners for performance optimization
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite performance pragmas"""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        # Performance optimizations for SQLite
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster commits
        cursor.execute("PRAGMA cache_size=10000")  # 10MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool"""
    pass  # Can add monitoring here


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Reset connection state when returned to pool"""
    pass  # Can add cleanup here


def get_db():
    """
    Dependency to get database session
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
