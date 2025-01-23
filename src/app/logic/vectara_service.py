import json
import uuid
import requests
import pandas as pd
from langdetect import detect
import urllib.parse as urlparse


class VectaraService:
    """
    A service class for interacting with the Vectara API, providing methods for document management and search functionality.

    This class handles document ingestion, querying, and corpus management through Vectara's REST API endpoints.
    It supports both simple and advanced querying capabilities, as well as corpus management operations.

    Attributes:
        api_key (str): The API key used for authenticating with Vectara services.

    Example:
        ```python
        service = VectaraService(api_key="your_api_key")

        # Add a document to a corpus
        service.add_document_to_corpus(
            corpus_key="123",
            title="Sample Document",
            metadata={"author": "John Doe"},
            document_parts=["Content part 1", "Content part 2"]
        )

        # Query the corpus
        results = service.simple_single_corpus_query(
            corpus_key="123",
            query="search term",
            limit=5
        )
        ```

    Dependencies:
        - requests: For making HTTP requests to the Vectara API
        - pandas: For handling query results in DataFrame format
        - langdetect: For automatic language detection of document titles
        - json: For JSON serialization/deserialization
        - uuid: For generating unique document IDs
        - urllib.parse: For URL encoding of query parameters
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def add_document_to_corpus(self, corpus_key, title, metadata, document_parts):
        """
        Adds a document to a specified corpus in Vectara.

        Args:
            corpus_key: The unique identifier of the target corpus.
            title (str): The title of the document.
            metadata (dict): Additional metadata for the document.
            document_parts (list): List of document content parts to be indexed.

        Returns:
            None: Prints the API response text.
        """
        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/documents"

        data = {
            "id": str(uuid.uuid4()),
            "type": "core",
            "metadata": {
                "title": title,
                "lang": detect(title),
            },
            "document_parts": document_parts,
        }

        data["metadata"].update(metadata)

        payload = json.dumps(data)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    def simple_single_corpus_query(self, corpus_key, query, limit=5):
        """
        Performs a simple search query on a single corpus.

        Args:
            corpus_key: The unique identifier of the corpus to search.
            query (str): The search query string.
            limit (int, optional): Maximum number of results to return. Defaults to 5.

        Returns:
            pandas.DataFrame: Search results in a DataFrame format.
        """
        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/query?query={urlparse.quote(query)}&limit={limit}"

        payload = {}
        headers = {"Accept": "application/json", "x-api-key": self.api_key}

        response = requests.request("GET", url, headers=headers, data=payload)
        return pd.DataFrame(json.loads(response.text)["search_results"])

    def advanced_single_corpus_query(self, corpus_key, query, limit=5):
        """
        Performs an advanced search query with reranking capabilities.

        Args:
            corpus_key: The unique identifier of the corpus to search.
            query (str): The search query string.
            limit (int, optional): Maximum number of final results to return. Defaults to 5.

        Returns:
            pandas.DataFrame: Search results in a DataFrame format after reranking.

        Note:
            This method fetches twice the requested limit of initial results before
            applying reranking to get the final limited set.
        """
        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/query"

        payload = json.dumps(
            {
                "query": query,
                "search": {
                    "limit": limit * 2,
                    "reranker": {
                        "type": "customer_reranker",
                        "reranker_name": "Rerank_Multilingual_v1",
                        "limit": limit,
                    },
                },
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return pd.DataFrame(json.loads(response.text)["search_results"])

    def remove_all_documents_and_data_in_a_corpus(self, corpus_key):
        """
        Removes all documents and data from a specified corpus.

        Args:
            corpus_key: The unique identifier of the corpus to reset.

        Returns:
            None: Prints the API response text.

        Warning:
            This is a destructive operation that cannot be undone.
        """

        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/reset"

        payload = {}
        headers = {"x-api-key": self.api_key}

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    def list_rerankers(self):
        """
        Retrieves a list of available rerankers from the Vectara API.

        Returns:
            requests.Response: The API response containing available rerankers.
        """
        url = f"https://api.vectara.io/v2/rerankers"

        payload = {}
        headers = {"Accept": "application/json", "x-api-key": self.api_key}

        response = requests.request("GET", url, headers=headers, data=payload)
        return response
