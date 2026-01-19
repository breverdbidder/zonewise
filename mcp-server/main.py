"""
ZoneWise MCP Server - Minimal Version
"""

from fastapi import FastAPI
import os

app = FastAPI(title="ZoneWise MCP Server", version="1.0.0")

@app.get("/")
def root():
    return {"status": "ok", "name": "ZoneWise MCP Server"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
