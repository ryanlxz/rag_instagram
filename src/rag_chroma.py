import os
from typing import List, Union
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import matplotlib.pyplot as plt
from chromadb.utils.data_loaders import ImageLoader
from logs.logging import logger

# from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
    ServiceContext,
)
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from conf import conf


class RagChroma:
    def __init__(self, collection: str) -> None:
        image_loader = ImageLoader()
        image_embedding_model = OpenCLIPEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=conf["chromadb_path"])
        self.text_collection = self.client.get_or_create_collection(
            name=f"{collection}_text",
        )
        self.image_collection = self.client.get_or_create_collection(
            name=f"{collection}_image",
            embedding_function=image_embedding_model,
            data_loader=image_loader,
        )
        Settings.llm = Ollama(model="mistral", request_timeout=60.0)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def add(
        self,
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        uri_list,
    ):
        """adds text and image documents into a chromadb text and image collection respectively. Note that collections must have ids for each document and their related info
        like metadata.

        Args:
            text_documents_list (_type_): _description_
            text_metadata_list (_type_): _description_
            text_id_list (_type_): _description_
            image_documents_list (_type_): _description_
            image_metadata_list (_type_): _description_
            image_id_list (_type_): _description_
            uri_list (_type_): _description_
        """
        self.text_collection.upsert(
            documents=text_documents_list,
            metadatas=text_metadata_list,
            ids=text_id_list,
        )
        self.image_collection.upsert(
            ids=image_id_list,
            images=image_documents_list,  # A list of numpy arrays representing images
            metadatas=image_metadata_list,
            uris=uri_list,
        )
        logger.info("completed adding of documents")
        self._load_index()

    def _load_index(self):
        text_vector_store = ChromaVectorStore(chroma_collection=self.text_collection)
        storage_context = StorageContext.from_defaults(vector_store=text_vector_store)
        service_context = ServiceContext.from_defaults(
            chunk_size=1024,
            llm=Ollama(model="mistral", request_timeout=60.0),
            embed_model="local",
        )
        index = VectorStoreIndex.from_vector_store(
            vector_store=text_vector_store,
            storage_context=storage_context,
            service_context=service_context,
        )
        logger.info("loaded index")
        return index

    def get_documents(self, collection: str, ids: List[str] = None):
        if collection == "image":
            document_collection = self.image_collection.get(ids=ids)
        elif collection == "text":
            document_collection = self.text_collection.get(ids=ids)
        else:
            logger.debug(
                f"Invalid collection {collection}. Accepts either 'image' or 'text'."
            )
        print(document_collection)
        return document_collection

    def plot_images(self, image_path:str):
        images_shown = 0
        plt.figure(figsize=(16, 9))
        for img_path in image_paths:
            if os.path.isfile(img_path):
                image = Image.open(img_path)

                plt.subplot(2, 3, images_shown + 1)
                plt.imshow(image)
                plt.xticks([])
                plt.yticks([])

                images_shown += 1
                if images_shown >= 9:
                    break

    def query_index(self, query: str):
        index = self._load_index()
        vector_store_info = VectorStoreInfo(
            content_info="food review",
            metadata_info=[
                MetadataInfo(
                    name="cuisine",
                    type="str",
                    description=(
                        "Cuisine of the food, one of [Sports, Entertainment,"
                        " Business, Music]"
                    ),
                ),
                MetadataInfo(
                    name="country",
                    type="str",
                    description=(
                        "Country of the celebrity, one of [United States, Barbados,"
                        " Portugal]"
                    ),
                ),
            ],
        )
        retriever = VectorIndexAutoRetriever(index, vector_store_info=vector_store_info)

        retrieval_results = retriever.retrieve(query)

        # response_synthesizer = get_response_synthesizer(
        #     response_mode="tree_summarize", streaming=True
        # )
        # query_engine = RetrieverQueryEngine(
        #     retriever=retriever, response_synthesizer=response_synthesizer
        # )
        # response = query_engine.query(query)

        # def generate():
        #     for text in response.response_gen:
        #         print(text)
        #         yield text

        # return generate()
        return retrieval_results

    def query_image_collection(self, query_text: str):
        """queries the image collection with query_text. After a user inputs a prompt, extract the key words from the prompt and pass them as the query_text.

        Args:
            query_text (str): _description_

        Returns:
            _type_: _description_
        """
        results = self.image_collection.query(
            query_texts=[query_text],
            n_results=5,
            include=["distances", "uris"],
        )
        return results

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def delete_collection(self, collection: str):
        self.client.delete_collection(collection)
        print(self.client.list_collections())


if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    # print(rag_client.query_image_collection(query_text="corn"))
    rag_client.get_documents(collection="text", ids=["2020-05-29_10-30-00_text"])
    # rag_client.delete_collection("eatinara")
