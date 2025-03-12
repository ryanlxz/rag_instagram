from smolagents import tool, Tool
from typing import List
from conf import conf
from src.rag_chroma import RagChroma

rag_client = RagChroma(conf["collection_name"])


# @tool
# def filter_documents(
#     relevant_text: str,
#     category: str,
#     category_value: str,
#     key_word: str,
#     n_results: int = 5,
# ) -> List[str]:
#     """
#     Performs metadata filtering to filter the most relevant documents from a vectorstore. E.g if
#     filtering for the best japanese food, then this could be a list of possible values
#     relevant_text: japanese food
#     category: cuisine
#     category_value: japanese
#     key_word: japanese food
#     The relevant_text is essentially a text for similarity matching to get the relevant documents.

#     Args:
#         relevant_text (str): relevant text to filter the vectorstore. Uses semantic similarity matching.
#         n_results (int): number of top relevant results to filter for. Defaults to 5.
#         category (str): category filter which is a single category from a list of categories: [price, taste, worth-it, location, cuisine].
#         category_value (str): value of the category to filter for
#         key_word (str): key word to look out for in the document

#     Returns:
#         List[str]: list of most relevant documents
#     """
#     documents = rag_client.text_collection.query(
#         query_texts=[relevant_text],
#         n_results=n_results,
#         where={category: category_value},
#         where_document={"$contains": key_word},
#     )
#     return documents


class FilterVectorStoreTool(Tool):
    name = "filter_vector_store"
    description = """
    This tool filters a vector store and retrieves the most relevant documents based on a query.
    It performs semantic similarity matching and applies metadata filters.
    """

    inputs = {
        "relevant_text": {
            "type": "string",
            "description": "Relevant text for semantic similarity matching to retrieve relevant documents.",
        },
        "category": {
            "type": "string",
            "description": "Category filter to apply. Must be one of: ['price', 'taste', 'worth-it', 'location', 'cuisine'].",
        },
        "category_value": {
            "type": "string",
            "description": "The value for the selected category filter.",
        },
        "key_word": {
            "type": "string",
            "description": "A keyword to look for within the document content.",
        },
        "n_results": {
            "type": "integer",
            "description": "Number of top relevant documents to retrieve. Defaults to 5.",
            "nullable": True,
        },
    }

    output_type = "string"

    def forward(
        self,
        relevant_text: str,
        category: str,
        category_value: str,
        key_word: str,
        n_results: int = 5,
    ):
        documents = rag_client.text_collection.query(
            query_texts=[relevant_text],
            n_results=n_results,
            where={category: category_value},
            where_document={"$contains": key_word},
        )
        return documents
