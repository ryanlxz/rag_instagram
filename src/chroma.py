from conf import conf

import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader


class ChromaDb:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path="/path/to/save/to")
        self.embedding_function = OpenCLIPEmbeddingFunction()
        image_loader = ImageLoader()
        self.collection = self.client.get_or_create_collection(
            name="test",
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


print(conf["chromadb_path"])
