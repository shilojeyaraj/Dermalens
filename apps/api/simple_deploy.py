"""
Minimal FastAPI application for deployment
"""

import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Dermalens API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Dermalens API is running!", "status": "healthy"}


@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is running"}


@app.get("/api/status")
async def status():
    return {
        "service": "Dermalens API",
        "version": "1.0.0",
        "status": "operational",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
