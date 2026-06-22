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

load_dotenv("config/.env")

if not os.getenv("GEMINI_API_KEY"):
    raise OSError("Environment variable 'GEMINI_API_KEY' is not set")

class Ingestor:
    def __init__(self, source_dir: Path, embedding_model: str):
        self.source_dir = source_dir
        self.embedding_model = embedding_model
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(name="hr-policies-collection")

    def embed_content(self, content: str) -> list[float]:
        result = self.gemini_client.models.embed_content(
            model=self.embedding_model,
            contents=content,
        )
        return result.embeddings[0].values

    def insert_knowledge(self, content: str, metadata: dict) -> None:
        embedding = self.embed_content(content)
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[metadata["chunk_id"]],
            embeddings=[embedding]
        )

    def run_ingestor(self) -> None:
        md_files = list(self.source_dir.rglob("**/*.md"))
        for md_file in tqdm(md_files):
            json_file = md_file.with_suffix(".json")
            if not json_file.exists():
                print(f"Metadata file {json_file} does not exist for {md_file}. Skipping.")
                continue
            content = md_file.read_text()
            metadata = json.loads(json_file.read_text())
            self.insert_knowledge(content, metadata)
