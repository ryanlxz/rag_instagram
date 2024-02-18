import os
from typing import List

import chromadb
import matplotlib.pyplot as plt
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.extractors import TitleExtractor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import ImageNode
from llama_index.vector_stores.chroma import ChromaVectorStore

from conf import conf


class RagChroma:
    def __init__(self, collection: str) -> None:
        image_loader = ImageLoader()
        self.client = chromadb.PersistentClient(path=conf["chromadb_path"])
        self.collection = self.client.get_or_create_collection(
            name=collection,
            data_loader=image_loader,
            embedding_function=OpenCLIPEmbeddingFunction(),
        )
        Settings.embed_model = OpenCLIPEmbeddingFunction()
        Settings.llm = Ollama(model="mistral", request_timeout=60.0)

    def add(
        self,
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
    ):
        self.collection.add(
            documents=text_documents_list,
            metadatas=text_metadata_list,
            ids=text_id_list,
        )
        self.collection.add(
            images=image_documents_list,  # A list of numpy arrays representing images
            metadatas=image_metadata_list,
            ids=image_id_list,
        )
        self.save_or_load_index(save_index=False)

    def save_or_load_index(self, save_index: bool, documents=None):
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        if save_index:
            # title_extractor = TitleExtractor(nodes=5)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
            )
        else:
            index = VectorStoreIndex.from_vector_store(
                vector_store, storage_context=storage_context
            )
        return index

    def get_documents(self):
        document_collection = self.collection.get()
        print(document_collection)
        return document_collection

    def plot_images(self):
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
        print(self.collection.count())
        index = self.save_or_load_index(save_index=False)
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=3,
            # image_similarity_top_k=5
        )
        retrieval_results = retriever.retrieve(query)
        retrieved_image = []
        for res_node in retrieval_results:
            if isinstance(res_node.node, ImageNode):
                retrieved_image.append(res_node.node.metadata["file_path"])
            else:
                display_source_node(res_node, source_length=200)

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
        return None

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def delete_collection(self, collection: str):
        self.client.delete_collection(collection)
        print(self.client.list_collections())


if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    rag_client.delete_collection("eatinara")
