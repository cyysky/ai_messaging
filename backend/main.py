import os
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
from sqlalchemy.orm import Session

from backend.db.config import get_db, engine
from backend.db.models import Base

load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

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