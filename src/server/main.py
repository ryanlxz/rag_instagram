from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from conf import conf
from src.rag_chroma import RagChroma
from fastapi.middleware.cors import CORSMiddleware
from src.instagram_scraper import GetInstagramProfile
from logs.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiate the instagram scraper
    app.state.instagram_scraper = GetInstagramProfile()
    # Start the rag client
    app.state.rag_client = RagChroma(conf["collection_name"])
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/update_posts")
async def update_posts():
    await app.state.instagram_scraper.update_downloaded_posts()


@app.post("/query")
async def query_index(query: str):
    try:
        response = app.state.rag_client.query_index(query)
        logger.info(f"response: {response}")
        return StreamingResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)
