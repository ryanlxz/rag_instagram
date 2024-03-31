import os
from typing import List
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import matplotlib.pyplot as plt
from chromadb.utils.data_loaders import ImageLoader

# from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    get_response_synthesizer,
    ServiceContext,
)
from llama_index.core.extractors import TitleExtractor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import ImageNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.indices import MultiModalVectorStoreIndex
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from conf import conf

os.environ["CURL_CA_BUNDLE"] = ""


class RagChroma:
    def __init__(self, collection: str) -> None:
        image_loader = ImageLoader()
        # image_embedding_model = embedding_functions.HuggingFaceEmbeddingFunction(
        #     api_key="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",
        #     model_name="openai/clip-vit-base-patch32",
        # )
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
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = embed_model
        # Settings.embed_model = embedding_functions.HuggingFaceEmbeddingFunction(
        #     model_name="BAAI/bge-small-en-v1.5",
        #     api_key="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",
        # )

    def add(
        self,
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        image_embedding_list,
        uri_list,
    ):
        self.text_collection.upsert(
            documents=text_documents_list,
            metadatas=text_metadata_list,
            ids=text_id_list,
        )
        self.image_collection.upsert(
            images=image_documents_list,  # A list of numpy arrays representing images
            # metadatas=image_metadata_list,
            # embeddings=image_embedding_list,
            ids=image_id_list,
            uris=uri_list,
        )
        print(self.image_collection.count())
        print(self.image_collection.get())
        print(
            self.image_collection.query(
                query_texts=["food"],
                n_results=1,
                include=["documents", "distances", "data", "uris"],
            )
        )
        print("completed adding of documents")
        self.save_or_load_index(save_index=False)

    def save_or_load_index(self, save_index: bool, documents=None):
        text_vector_store = ChromaVectorStore(chroma_collection=self.text_collection)
        image_vector_store = ChromaVectorStore(chroma_collection=self.image_collection)
        storage_context = StorageContext.from_defaults(
            vector_store=text_vector_store, image_store=image_vector_store
        )
        service_context = ServiceContext.from_defaults(
            chunk_size=1024,
            llm=Ollama(model="mistral", request_timeout=60.0),
            embed_model="local",
        )
        print("initialized storage_context")
        if save_index:
            # title_extractor = TitleExtractor(nodes=5)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
            )
        else:
            # documents = SimpleDirectoryReader("data/eatinara_data").load_data()
            # index = MultiModalVectorStoreIndex.from_documents(
            #     documents,
            #     storage_context=storage_context,
            # )

            index = MultiModalVectorStoreIndex.from_vector_store(
                vector_store=text_vector_store,
                image_vector_store=image_vector_store,
                service_context=service_context,
            )
            print("loaded index")
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
        index = self.save_or_load_index(save_index=False)
        # retriever = VectorIndexRetriever(
        #     index=index,
        #     similarity_top_k=3,
        #     # image_similarity_top_k=5
        # )

        retriever = index.as_retriever(similarity_top_k=2, image_similarity_top_k=1)
        retrieval_results = retriever.retrieve(query)
        # retrieved_image = []
        # for res_node in retrieval_results:
        #     if isinstance(res_node.node, ImageNode):
        #         retrieved_image.append(res_node.node.metadata["file_path"])
        #     else:
        #         display_source_node(res_node, source_length=200)

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

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)

    def delete_collection(self, collection: str):
        self.client.delete_collection(collection)
        print(self.client.list_collections())


if __name__ == "__main__":
    rag_client = RagChroma("eatinara")
    # rag_client.delete_collection("eatinara")