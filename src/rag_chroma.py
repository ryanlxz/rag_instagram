from email.mime import image
import os
from typing import List, Union
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import matplotlib.pyplot as plt
from chromadb.utils.data_loaders import ImageLoader
from logs.logging import logger
import time

# from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
    PromptTemplate,
)
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from conf import conf
from .utils import parse_response, filter_relevant_images
from .prompt import PromptLoader


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
        Settings.llm = Ollama(model=conf["llm"], request_timeout=500.0)
        # Settings.llm = ollama
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
        self.load_system_prompt()

    def load_system_prompt(self):
        prompts = PromptLoader()
        system_prompt = prompts.system_prompt
        prompt_template = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            f"{system_prompt}"
            "Query: {query_str}\n"
            "Answer: "
        )
        self.system_prompt = PromptTemplate(prompt_template)

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
        index = VectorStoreIndex.from_vector_store(
            vector_store=text_vector_store,
            storage_context=storage_context,
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

    def plot_images(self, image_path: str):
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
                    description=("Cuisine of the food"),
                ),
                MetadataInfo(
                    name="taste",
                    type="str",
                    description=(
                        "Taste of the food which is a measure of how delicious the food is. It is a rating between 0 and 11 where 7 is the average. The highest rating is 11."
                    ),
                ),
                MetadataInfo(
                    name="price",
                    type="str",
                    description=("Average price of the meal."),
                ),
                MetadataInfo(
                    name="worth_it",
                    type="str",
                    description=(
                        """The overall value of the meal which takes into account both the price and taste of the meal. It is a rating between 0 and 10 where 0 is the lowest, 7 is 
                        the average, and 10 is the highest.  
                        """
                    ),
                ),
                MetadataInfo(
                    name="location",
                    type="str",
                    description=(
                        "Location of the food. Usually it is the name of the shop or restaurant."
                    ),
                ),
            ],
        )
        # time how long querying index takes with local llm
        start_time = time.time()
        retriever = VectorIndexAutoRetriever(index, vector_store_info=vector_store_info)

        retry = 0
        self.retrieval_results = []
        while retry < 3:
            try:
                self.retrieval_results = retriever.retrieve(query)
                if self.retrieval_results:
                    break
                else:
                    retry += 1
                    logger.info("retrying retrieve documents from vector store")
            except Exception as e:
                logger.debug(f"Error retrieving results {e}")
                retry += 1
                logger.info("retrying retrieve documents from vector store")
        if not self.retrieval_results:
            logger.error(f"Unable to retrieve any results given the query: {query}")
        # get the top k results
        # retrieval_results = retrieval_results[:3]

        response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT, text_qa_template=self.system_prompt
        )
        response = response_synthesizer.synthesize(
            query,
            nodes=self.retrieval_results,
            # streaming=True
        )
        response = parse_response(str(response))

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

        # def generate():
        #     capture = False
        #     for text in response.response_gen:
        #         if capture:
        #             print(text)
        #             yield text
        #         elif "</think>" in text:
        #             capture = True  # Start streaming from the next chunk
        #             text_after_tag = text.split("</think>", 1)[
        #                 -1
        #             ]  # Get text after </think>
        #             if text_after_tag.strip():  # Avoid yielding empty text
        #                 print(text_after_tag)
        #                 yield text_after_tag

        # return generate()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Execution time:", elapsed_time, "seconds")
        return response

    def get_relevant_images(self, query_text: str):
        results = self.image_collection.query(
            query_texts=[query_text],
            n_results=5,
            include=["distances", "uris"],
        )

    def query_image_collection(self, query_text: str, image_ids: List[str]):
        """queries the image collection with query_text. After a user inputs a prompt, extract the key words from the prompt and pass them as the query_text.

        Args:
            query_text (str): relevant text for querying the image collection
            image_ids (List[str]): list of image ids to filter

        Returns:
            _type_: _description_
        """
        results = self.image_collection.query(
            query_texts=query_text,
            where={"$or": [{"id": doc_id} for doc_id in image_ids]},
            # where={"id": "2020-05-30_08-03-20"},
            n_results=5,
            include=["distances", "uris"],
        )
        return results

    def query_workflow(self, query: str):
        response = self.query_index(query=query)
        ids = [node.node.id_ for node in self.retrieval_results]
        image_list = self.query_image_collection(query_text=response, image_ids=ids)
        relevant_images = filter_relevant_images(
            image_uri=image_list["uris"][0], distances=image_list["distances"][0]
        )
        # [('data/eatinara/2020-06-05_12-57-23_UTC.jpg', 1.408056052458937), ('data/eatinara/2020-06-02_12-33-58_UTC_1.jpg', 1.4813308509936796), ('data/eatinara/2020-06-02_12-33-58_UTC_2.jpg', 1.4862864724349267)]

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def delete_collection(self, collection: str):
        self.client.delete_collection(collection)
        print(self.client.list_collections())


if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    print(rag_client.image_collection.count())
    # print(
    #     rag_client.image_collection.get(
    #         ids=["2020-05-30_08-03-20_1", "2020-06-06_10-24-09_1"]
    #     )
    # )
    # print(rag_client.text_collection.get(include=["documents", "metadatas"]))
    # print(
    #     rag_client.text_collection.query(
    #         query_texts=["Japanese food"],
    #         n_results=5,
    #         where={"cuisine": "Japanese"},
    #         where_document={"$contains": "japanese"},
    #     )
    # )
    rag_client.query_workflow("what would you recommend for food?")
    # retrieval_results = rag_client.query_index(
    #     query="what would you recommend for food under 30?"
    # )
    # print(retrieval_results)

    # print(rag_client.query_index(query="what are the best foods in takashimaya?"))
    # image_list = rag_client.query_image_collection(query_text="salad and corn")
    # print(
    #     filter_relevant_images(
    #         image_uri=image_list["uris"][0], distances=image_list["distances"][0]
    #     )
    # )
    # rag_client.get_documents(collection="text", ids=["2020-05-29_10-30-00_text"])
    # rag_client.delete_collection("eatinara")
