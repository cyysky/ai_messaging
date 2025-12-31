import os
import sys
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from sqlalchemy.orm import Session

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.config import get_db, engine
from db.models import Base
from auth.router import router as auth_router

load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Message API",
    description="Authentication and user management API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example endpoint with database dependency
@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"status": "database connection working"}

if __name__ == "__main__":
    host = os.getenv("AI_MESSAGE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_MESSAGE_PORT", 8000))
    domain = os.getenv("AI_MESSAGE_DOMAIN", "localhost")
    cert_file = os.getenv("AI_MESSAGE_SSL_CERT", "ssl/cert.pem")
    key_file = os.getenv("AI_MESSAGE_SSL_KEY", "ssl/key.pem")
    
    print(f"Starting server for domain: {domain}")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file
    )