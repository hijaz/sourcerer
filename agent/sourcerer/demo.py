"""
Sourcerer FastAPI Entrypoint

This file launches the FastAPI app and exposes the LangGraph agent using CopilotKit. 
All imports now use the new sourcerer package structure.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from sourcerer.langgraph.agent import graph
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

initial_state = {
    "messages": [],
    "model": "openai",
    "logs": [],
    "accounts": [],
    "transactions": [],
    "categories": [],
    "budgets": [],
}

sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="sourcerer_agent",
            description="Sourcerer agent.",
            graph=graph,
        ),
    ],
)
import logging
logging.basicConfig(level=logging.INFO, force=True)
print("Registering CopilotKit endpoint...")
logging.info("[demo.py] Registering CopilotKit endpoint with agents: %s", [agent.name for agent in sdk.agents])

# Monkey-patch the endpoint to add logging
from fastapi import Request
from copilotkit.integrations.fastapi import add_fastapi_endpoint as orig_add_fastapi_endpoint

def add_fastapi_endpoint_with_logging(app, sdk, path):
    @app.middleware("http")
    async def log_request(request: Request, call_next):
        body = await request.body()
        logging.info(f"[demo.py] Incoming request to {request.url.path} with body: {body}")
        response = await call_next(request)
        return response
    orig_add_fastapi_endpoint(app, sdk, path)

add_fastapi_endpoint_with_logging(app, sdk, "/copilotkit")

@app.get("/health")
def health():
    return {"status": "ok"}

def main():
    uvicorn.run("sourcerer.demo:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
