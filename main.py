"""
Personal Finance Tracker - FastAPI Backend
Main application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db.connection import connect_to_mongo, close_mongo_connection
from app.routes import auth
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()


app = FastAPI(
    title="Personal Finance Tracker API",
    description="Backend API for managing personal finances",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Include routers
app.include_router(auth.router)

# Import and include all module routers
from app.routes import (
    bank_accounts,
    credit_cards,
    emis,
    borrows,
    cashflows,
    financial_engine,
    dashboard,
    snapshots
)

app.include_router(bank_accounts.router)
app.include_router(credit_cards.router)
app.include_router(emis.router)
app.include_router(borrows.router)
app.include_router(cashflows.router)
app.include_router(financial_engine.router)
app.include_router(dashboard.router)
app.include_router(snapshots.router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Personal Finance Tracker API"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint"""
    return {"status": "healthy", "database": "connected"}


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.svg")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/svg+xml")
    return {"message": "Favicon not found"}


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for Render) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False  # Disable reload in production
    )
