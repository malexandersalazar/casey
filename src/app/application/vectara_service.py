import json
import uuid
import requests
import pandas as pd
from langdetect import detect
import urllib.parse as urlparse


class VectaraService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def add_document_to_corpus(self, corpus_key, title, metadata, document_parts):
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
        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/query?query={urlparse.quote(query)}&limit={limit}"

        payload = {}
        headers = {"Accept": "application/json", "x-api-key": self.api_key}

        response = requests.request("GET", url, headers=headers, data=payload)
        return pd.DataFrame(json.loads(response.text)["search_results"])

    def advanced_single_corpus_query(self, corpus_key, query, limit=5):
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
        url = f"https://api.vectara.io/v2/corpora/{corpus_key}/reset"

        payload = {}
        headers = {"x-api-key": self.api_key}

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    def list_rerankers(self):
        url = f"https://api.vectara.io/v2/rerankers"

        payload = {}
        headers = {"Accept": "application/json", "x-api-key": self.api_key}

        response = requests.request("GET", url, headers=headers, data=payload)
        return response
