from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from conf import conf
from src.rag_chroma import RagChroma
from fastapi.middleware.cors import CORSMiddleware

from src.instagram_scraper import GetInstagramProfile
from src.utils import monitor_file_count
from logs.logging import logger
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiate the instagram scraper
    app.state.instagram_scraper = GetInstagramProfile()
    # Start the rag client
    app.state.rag_client = RagChroma(conf["collection_name"])
    # Start updating posts
    monitor_task = asyncio.create_task(monitor_file_count())
    update_task = asyncio.create_task(update_posts())
    await monitor_task
    update_task.cancel()
    logger.info("update_posts task cancelled")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
