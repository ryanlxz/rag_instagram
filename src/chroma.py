from conf import conf

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader


class ChromaDb:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=conf["chromadb_path"])
        # self.client = chromadb.PersistentClient(
        #     path=conf[r"C:\Users\ryanl\Desktop\rag_instagram\data\chromadb"]
        # )
        self.embedding_function = OpenCLIPEmbeddingFunction()
        image_loader = ImageLoader()
        self.collection = self.client.get_or_create_collection(
            name="eatinara",
            embedding_function=self.embedding_function,
            data_loader=image_loader,
        )
        # try:
        #     self.collection = self.client.get_collection(
        #         name="test", embedding_function=emb_fn
        #     )
        # except:
        #     collection = self.client.create_collection(
        #         name="my_collection", embedding_function=emb_fn
        #     )

    def add(self, documents: list, metadatas: list, ids: list):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)


if __name__ == "__main__":
    chroma = ChromaDb()
