import argparse
import shutil
import json
from tqdm import tqdm
from pathlib import Path
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

def chunk_markdown(text: str) -> list:
    """
    Chunk markdown text using a recursive character text splitter.

    Args:
        text (str): The markdown text to chunk.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 2048.
        chunk_overlap (int, optional): The number of characters to overlap between chunks. Defaults to 0.
        org_path (Path, optional): The path to the original markdown file. Defaults to None.
        save_path (Path, optional): The path to save the chunked text. Defaults to None.

    Returns:
        List[str]: A list of text chunks.
    """
    chunk_size = 2048
    chunk_overlap = 0
    # First, split the markdown text into sections based on headers
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
            strip_headers=False,)
    sections = header_splitter.split_text(text)
    # print(f"First section: {sections[0][:100]}...")  # Print the first 100 characters of the first section

    # Then, use a recursive character text splitter to further split the sections into chunks
    char_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    chunks = char_splitter.split_documents(sections)
    # print(f"First chunk: {chunks[0][:100]}...")  # Print the first 100 characters of the first chunk

    return chunks

# normalizing each chunk
def normalize_chunk(chunk, id: int, source: str) -> (str, json):
    """
    Normalize a chunk of text by adding metadata and formatting to be compatible with the knowledge base.
    ---
    chunk_id: 123
    source: hr-policies-v4.md
    Header 1: HR-Policies Knowledge Base (Refined Framework v4)
    Header 2: 30. Employee Exit & Separation Policy
    ---

    <page_content>
    """
    metadata = {
        "chunk_id": id,
        "source": source,
        "Header 1": chunk.metadata.get("Header 1", ""),
        "Header 2": chunk.metadata.get("Header 2", ""),
    }
    normalized_chunk = f"{chunk.page_content}"
    return normalized_chunk, metadata

def run_chunker(input_path: Path, output_path: Path) -> None:
    """
    Run the chunker on a markdown file and save the chunked text to a new file.

    Args:
        input_path (Path): The path to the input markdown file.
        output_path (Path): The path to save the chunked text.
    """
    md_files = list(input_path.rglob("**/*.md"))
    for md_file in tqdm(md_files, desc="Chunking"):
        md_text = md_file.read_text()
        chunks = chunk_markdown(md_text)
        for i, chunk in enumerate(chunks):
            save_path_md = output_path / md_file.name.replace(".md", "") / f"{i}.md"
            save_path_json = output_path / md_file.name.replace(".md", "") / f"{i}.json"
            save_path_md.parent.mkdir(parents=True, exist_ok=True)
            save_path_json.parent.mkdir(parents=True, exist_ok=True)

            normalized_chunk, metadata = normalize_chunk(chunk, i, md_file.name)
            save_path_md.write_text(normalized_chunk)
            with open(save_path_json, "w") as f:
                json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    run_chunker(Path("data/raw"), Path("data/chunked"))