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

source_dir: Path = Path("data/chunked")
embedding_model: str = "models/text-embedding-001"

gemini_client = genai.Client(
    api_key = os.getenv("GEMINI_API_KEY")
)

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="hr-policies-collection")

def embed_content(embedding_model: str, content: str) -> list[float]:
    result = gemini_client.models.embed_content(
        model=embedding_model,
        contents=content,
    )
    return result.embeddings[0].values

def insert_knowledge(collection: chromadb.Collection, embedding_model: str, content: str, metadata: dict) -> None:
    embedding = embed_content(embedding_model, content)
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[metadata["chunk_id"]],
        embeddings=[embedding]
    )

def run_ingestor(collection: chromadb.Collection, embedding_model: str, input_path: Path) -> None:
    md_files = list(input_path.rglob("**/*.md"))
    for md_file in tqdm(md_files):
        json_file = md_file.with_suffix(".json")
        if not json_file.exists():
            print(f"Metadata file {json_file} does not exist for {md_file}. Skipping.")
            continue
        content = md_file.read_text()
        metadata = json.loads(json_file.read_text())
        insert_knowledge(collection, embedding_model, content, metadata)

if __name__ == "__main__":
    run_ingestor(collection, embedding_model, source_dir)