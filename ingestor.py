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
    api_key=os.getenv("GEMINI_API_KEY")
)

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="hr-policies_collection")

def embed_content(content: str) -> list[float]:
    result = gemini_client.models.embed_content(
        model=embedding_model,
        contents=content,
    )
    return result.embeddings[0].values

def insert_knowledge(content: str, metadata: dict):
    embedding = embed_content(content)
    # Insert the content, embedding, and metadata into the knowledge base
    # This is a placeholder for the actual insertion logic, which will depend on your knowledge base implementation
    print(f"Inserting content with metadata: {metadata}")

def run_ingestor(input_path: Path) -> None:
    for md_file in tqdm(list(input_path.glob("**/*.md"))):
        json_file = md_file.with_suffix(".json")
        if not json_file.exists():
            print(f"Metadata file {json_file} does not exist for {md_file}. Skipping.")
            continue
        
        content = md_file.read_text()
        metadata = json.loads(json_file.read_text())
        insert_knowledge(content, metadata)