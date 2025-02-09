from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from conf import conf
from src.rag_chroma import RagChroma
from fastapi.middleware.cors import CORSMiddleware

from src.instagram_scraper import GetInstagramProfile
from src.utils import (
    monitor_file_count,
    count_text_files,
    filter_pending_posts_for_update,
)
from logs.logging import logger
from src.extract_metadata import sort_insta_posts, extract_metadata
import asyncio
import yaml

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)
USERNAME = credentials["USERNAME"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiate the instagram scraper
    app.state.instagram_scraper = GetInstagramProfile()
    # Start the rag client
    app.state.rag_client = RagChroma(conf["collection_name"])
    # Start updating posts
    monitor_task = asyncio.create_task(monitor_file_count())
    update_task = asyncio.create_task(update_posts())
    try:
        await monitor_task
    finally:
        update_task.cancel()
        monitor_task.cancel()
        logger.info("update_posts task cancelled")
    # asyncio.create_task(extract_metadata_and_update_vector_db())
    await extract_metadata_and_update_vector_db()
    yield
    # update_task.cancel()
    # logger.info("update_posts task cancelled")
    # update_vector_db_task = asyncio.create_task(update_vector_db())


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query")
async def query_index(query: str):
    try:
        response = app.state.rag_client.query_index(query)
        logger.info(f"response: {response}")
        return StreamingResponse(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_posts():
    await app.state.instagram_scraper.update_downloaded_posts()


# async def update_vector_db():
#     await extract_metadata_and_update_vector_db()


async def extract_metadata_and_update_vector_db():
    id_list = app.state.rag_client.text_collection.get(ids=None)["ids"]
    latest_id = sorted(id_list)[-1]
    num_text_docs = len(id_list)
    num_files = count_text_files(folder_path=f"data/{USERNAME}")
    posts_dict, multi_part_review_counter = sort_insta_posts(f"data/{USERNAME}")
    num_posts = num_files - multi_part_review_counter
    # check number of docs in text vectordb and number of posts. Does not check image vectordb as images db will be updated together with text db.
    if num_text_docs < num_posts:
        logger.info(
            f"Number of text docs in vectordb: {num_text_docs} is less than Number of posts: {num_files}. Proceeding to update vectordb."
        )
        # get pending posts to update
        update_posts_dict = filter_pending_posts_for_update(
            sorted_posts_dict=posts_dict, latest_vectordb_id=latest_id
        )
        logger.info(f"Preparing to update {len(update_posts_dict)} posts")
        (
            text_documents_list,
            text_metadata_list,
            text_id_list,
            image_documents_list,
            image_metadata_list,
            image_id_list,
            uri_list,
        ) = extract_metadata(posts_dict=update_posts_dict)
        logger.info("completed metadata extraction")
        app.state.rag_client.add(
            text_documents_list=text_documents_list,
            text_metadata_list=text_metadata_list,
            text_id_list=text_id_list,
            image_documents_list=image_documents_list,
            image_metadata_list=image_metadata_list,
            image_id_list=image_id_list,
            uri_list=uri_list,
        )
        logger.info("completed vector db update")
    elif num_text_docs == num_posts:
        logger.info(
            f"Number of text docs in vectordb: {num_text_docs} = Number of posts: {num_posts}"
        )
    else:
        logger.debug(
            f"Please check as number of text docs in vectordb: {num_text_docs} is not the same as number of posts: {num_posts}"
        )


if __name__ == "__main__":
    uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)
