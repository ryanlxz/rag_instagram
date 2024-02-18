from rag_chroma import RagChroma
from extract_metadata import sort_insta_posts, extract_metadata
import yaml

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)

if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    # posts_dict = sort_insta_posts(f"./data/{credentials['USERNAME']}")
    # (
    #     text_documents_list,
    #     text_metadata_list,
    #     text_id_list,
    #     image_documents_list,
    #     image_metadata_list,
    #     image_id_list,
    # ) = extract_metadata(posts_dict=posts_dict)
    # print("completed metadata extraction")
    # rag_client.add(
    #     text_documents_list=text_documents_list,
    #     text_metadata_list=text_metadata_list,
    #     text_id_list=text_id_list,
    #     image_documents_list=image_documents_list,
    #     image_metadata_list=image_metadata_list,
    #     image_id_list=image_id_list,
    # )
    # print("added documents to chromadb")

    print(rag_client.query_index("what is the best japanese food?"))
    # rag_client.get_documents()
