# from rag_chroma import RagChroma
from rag_chroma_2 import RagChroma
from extract_metadata import sort_insta_posts, extract_metadata
import yaml
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ["CURL_CA_BUNDLE"] = ""

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)

if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    folder_name = "eatinara_data"
    posts_dict = sort_insta_posts(f"./data/{folder_name}")
    # posts_dict = sort_insta_posts(f"./data/{credentials['USERNAME']}")
    (
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        image_embedding_list,
        uri_list,
    ) = extract_metadata(posts_dict=posts_dict)
    print("completed metadata extraction")
    rag_client.add(
        text_documents_list=text_documents_list,
        text_metadata_list=text_metadata_list,
        text_id_list=text_id_list,
        image_documents_list=image_documents_list,
        image_metadata_list=image_metadata_list,
        image_id_list=image_id_list,
        image_embedding_list=image_embedding_list,
        uri_list=uri_list,
    )
    # print("added documents to chromadb")
    # print(rag_client.query_index("what is the best japanese food?"))
    # rag_client.get_documents()
