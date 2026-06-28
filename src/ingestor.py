# this script ingests markdown files and their corresponding JSON metadata files into a ChromaDB collection. 
# It uses the Google GenAI API to generate embeddings for the content of the markdown files.
# this is the oop version of the ingestor.py script. 
# It uses classes and methods to encapsulate the functionality of the script.
import json
import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from tqdm import tqdm
from chromadb.utils import embedding_functions

load_dotenv("config/.env")

class Ingestor:
    def __init__(
        self,
        source_dir: Path, 
        embedding_model: str,
        collection_name: str) -> None:
        self.source_dir = source_dir
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        if not os.getenv("GEMINI_API_KEY"):
            raise OSError("Environment variable 'GEMINI_API_KEY' is not set")
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_func = embedding_functions.GoogleGeminiEmbeddingFunction(
            model_name = embedding_model,
            task_type = "RETRIEVAL_DOCUMENT",
            dimension = 768
        )
        self.collection = self.chroma_client.get_or_create_collection(name = self.collection_name,
            embedding_function = self.embedding_func)

    def _insert_knowledge(self, content: str, metadata: dict, indexed_count: int) -> None:
        self.collection.add(
            ids=[str(indexed_count)],
            documents=[content],
            metadatas=[metadata]
        )

    def run_ingestor(self) -> None:
        md_files = list(self.source_dir.rglob("**/*.md"))
        indexed_count = 0
        for md_file in tqdm(md_files):
            json_file = md_file.with_suffix(".json")
            if not json_file.exists():
                continue
            content = md_file.read_text()
            metadata = json.loads(json_file.read_text())
            self._insert_knowledge(content, metadata, indexed_count)
            indexed_count += 1


if __name__ == "__main__":
    source_dir: Path = Path("data/chunked")
    embedding_model = "gemini-embedding-2"
    collection_name = "hr-policies-kb-collection"
    ingestor = Ingestor(source_dir, embedding_model, collection_name)
    ingestor.run_ingestor()

