import os
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from google import genai
from dotenv import load_dotenv

load_dotenv("config/.env")

@dataclass
class HRSearchResult:
    text: str
    metadata: dict


class KBEmbeddingError(Exception):
    pass


class KBSearchError(Exception):
    pass


class ChromaDBKnowledgeBase:
    def __init__(
        self,
        collection_name: str,
        embedding_model: str = "gemini-embedding-2",
        search_limit: int = 10,
        chroma_db_path: str = "./chroma_db",
    ):
        self.collection_name = collection_name
        self.search_limit = search_limit
        
        self.kb = chromadb.PersistentClient(path = chroma_db_path)
        
        self.collection = self.kb.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedding_model = embedding_model
        if os.getenv("GEMINI_API_KEY") is None:
            raise OSError("GEMINI_API_KEY env var is not set")
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def _embed_content(self, content: str) -> list[float]:
        try:
            result = self.gemini_client.models.embed_content(
                model=self.embedding_model,
                contents=content,
                config={
                    "output_dimensionality": 768
                }
            )
            return result.embeddings[0].values
        except Exception as e:
            raise KBEmbeddingError(f"Failed to embed content: {e}") from e

    def search(self, query: str) -> list[HRSearchResult]:
        """Vector-based search (ChromaDB doesn't support native BM25/hybrid search)"""
        embedding = self._embed_content(query)
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=self.search_limit,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            raise KBSearchError(f"Failed to search knowledge base: {e}") from e

        try:
            return [
                HRSearchResult(
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i]
                )
                for i in range(len(results["documents"][0]))
            ]
        except Exception as e:
            raise KBSearchError(f"Error while parsing search results: {e}") from e