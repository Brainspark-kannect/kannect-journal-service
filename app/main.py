# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, journal, habits, goals, dashboard
from app.core.exceptions import add_exception_handlers
from app.db.base import Base
from app.db.session import engine
from app.core.logging import setup_logging
import logging
import traceback

# Setup logging
logger = setup_logging()

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    logger.debug(f"Stack trace: {traceback.format_exc()}")

app = FastAPI(
    title="Journal API",
    description="API for journaling, habit tracking, goal planning, and sentiment analysis",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
add_exception_handlers(app)

# Include API routers
app.include_router(auth.router)
app.include_router(journal.router)
app.include_router(habits.router)
app.include_router(goals.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Journal API"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Journal API")
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Journal API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
