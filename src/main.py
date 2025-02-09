from .rag_chroma import RagChroma
from .extract_metadata import sort_insta_posts, extract_metadata
import yaml
from logs.logging import logger
from src.instagram_scraper import GetInstagramProfile
import os
import json

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)
USERNAME = credentials["USERNAME"]

if __name__ == "__main__":
    cls = GetInstagramProfile()
    cls.download_and_update_posts(USERNAME)
    rag_client = RagChroma(USERNAME)
    posts_dict, multi_part_review_counter = sort_insta_posts(f"data/{USERNAME}")
    (
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        uri_list,
    ) = extract_metadata(posts_dict=posts_dict)
    logger.info("completed metadata extraction")
    rag_client.add(
        text_documents_list=text_documents_list,
        text_metadata_list=text_metadata_list,
        text_id_list=text_id_list,
        image_documents_list=image_documents_list,
        image_metadata_list=image_metadata_list,
        image_id_list=image_id_list,
        uri_list=uri_list,
    )
    results = rag_client.image_collection.query(
        query_texts=["pizza"],
        n_results=5,
        include=["distances", "uris"],
    )
    print(len(rag_client.image_collection.get(ids=None)["ids"]))
    print(results)
    # print("added documents to chromadb")
    # print(rag_client.query_index("what is the best japanese food?"))
    # rag_client.get_documents()
