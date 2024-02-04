import chromadb


class ChromaDb:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path="/path/to/save/to")
        self.collection = self.client.get_or_create_collection(
            name="test", embedding_function=emb_fn
        )
        # try:
        #     self.collection = self.client.get_collection(
        #         name="test", embedding_function=emb_fn
        #     )
        # except:
        #     collection = self.client.create_collection(
        #         name="my_collection", embedding_function=emb_fn
        #     )
