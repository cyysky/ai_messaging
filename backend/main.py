import os
from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    host = os.getenv("AI_MESSAGE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_MESSAGE_PORT", 8000))
    domain = os.getenv("AI_MESSAGE_DOMAIN", "localhost")
    cert_file = os.getenv("AI_MESSAGE_SSL_CERT", "ssl/cert.pem")
    key_file = os.getenv("AI_MESSAGE_SSL_KEY", "ssl/key.pem")
    
    print(f"Starting server for domain: {domain}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file
    )