from smolagents import tool
from typing import List
from conf import conf
from src.rag_chroma import RagChroma

rag_client = RagChroma(conf["collection_name"])


@tool
def filter_documents(
    relevant_text: str,
    category: str,
    category_value: str,
    key_word: str,
    n_results: int = 5,
) -> List[str]:
    """
    Performs metadata filtering to filter the most relevant documents from a vectorstore. E.g if
    filtering for the best japanese food, then this could be a list of possible values
    relevant_text: japanese food
    category: cuisine
    category_value: japanese
    key_word: japanese food

    Args:
        relevant_text (str): relevant text to filter the vectorstore. Uses semantic similarity matching.
        n_results (int): number of top relevant results to filter for. Defaults to 5.
        category (str): category filter which is a single category from a list of categories: [price, taste, worth-it, location, cuisine].
        category_value (str): value of the category to filter for
        key_word (str): key word to look out for in the document

    Returns:
        List[str]: list of most relevant documents
    """
    documents = rag_client.text_collection.query(
        query_texts=[relevant_text],
        n_results=n_results,
        where={category: category_value},
        where_document={"$contains": key_word},
    )
    return documents
