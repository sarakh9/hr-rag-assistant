from typing import Literal

import yaml
from pydantic import BaseModel


class KnowledgeBaseConfig(BaseModel):
    search_limit: int
    embedding_model: str
    collection_name: str


class AssistantConfig(BaseModel):
    answer_generation_prompt: str
    retrieval_query_prompt: str
    top_p: float
    answer_generation_model: Literal[
        "gemini-2.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3-flash-preview"
    ]
    retrieval_query_model: Literal[
        "gemini-2.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3-flash-preview"
    ]
    knowledge_base: KnowledgeBaseConfig


def load_assistant_config(config_path: str) -> AssistantConfig:
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return AssistantConfig(**config)