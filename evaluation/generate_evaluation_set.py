import concurrent.futures
import json
import logging
import logging.config
import os
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv
from google.genai import Client
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

logger = logging.getLogger(__name__)


def init_config():
    with open("config/logging.yaml") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logger.info("Logging configured")
    if not load_dotenv("config/.env"):
        raise ValueError("No secrets found in config/.env")
    else:
        logger.info("Secrets loaded from config/.env")


class GeminiQAGenerator:
    class QaPair(BaseModel):
        question: str
        ground_truth: str

    
    VALID_LLM_MODELS = [
        "gemini-2.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3-flash-preview"
    ]

    def __init__(self, model_name: str, qa_prompt: str | None = None):
        if model_name not in self.VALID_LLM_MODELS:
            raise ValueError(f"Model {model_name} is not a valid LLM model.")
        self.model_name = model_name
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY env var is not set")
        self.gemini_client = Client(api_key=api_key)
        if qa_prompt is not None:
            self.qa_prompt = qa_prompt
        else:
            self.qa_prompt = "Generate a question and answer pair that is about and can be answered with the following knowledge: {knowledge_content}."

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=30, max=60),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def generate_qa_pair(self, knowledge_content: str) -> QaPair:
        reponse = self.gemini_client.models.generate_content(
            model=self.model_name,
            contents=self.qa_prompt.format(knowledge_content=knowledge_content),
            config={
                "response_mime_type": "application/json",
                "response_schema": GeminiQAGenerator.QaPair,
            },
        )
        qa_pair: GeminiQAGenerator.QaPair = reponse.parsed
        return qa_pair


@dataclass
class QAPair:
    question: str
    ground_truth: str


@dataclass
class EvaluationSet:
    metadata: dict
    qa_pairs: list[QAPair]


def generate_qa_pair(doc: Path, model_name: str) -> QAPair:

    with open(doc) as f:
        print(f"DOC: {doc}")
        knowledge_content = f.read()

    gemini_qa_generator = GeminiQAGenerator(model_name=model_name)
    qa_pair = gemini_qa_generator.generate_qa_pair(knowledge_content)

    return QAPair(
        question=qa_pair.question,
        ground_truth=qa_pair.ground_truth,
    )


def generate_evaluation_set(
    num_questions: int = 10,
    model_name: str = "gemini-3.1-flash-lite",
    knowledge_dir: Path = Path("data/raw"),
    output_dir: Path = Path("evaluation_set"),
    threads: int = 2,
):
    docs = list(knowledge_dir.glob("**/*.md"))
    selected_docs = random.sample(docs, num_questions)
    qa_pairs = [generate_qa_pair(doc=doc, model_name=model_name) for doc in selected_docs]

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    evaluation_set = EvaluationSet(
        metadata={
            "model": model_name,
            "num_questions": len(qa_pairs),
            "timestamp": timestamp,
        },
        qa_pairs=qa_pairs,
    )
    # save the evaluation set
    with open(output_dir / f"evaluation_set_{timestamp}.json", "w") as f:
        json.dump(asdict(evaluation_set), f, indent=4, ensure_ascii=False)
    logger.info(
        f"Evaluation set saved to {output_dir / f'evaluation_set_{timestamp}.json'}"
    )


if __name__ == "__main__":
    init_config()
    generate_evaluation_set(
        num_questions=10,
        model_name="gemini-3.1-flash-lite",
        knowledge_dir=Path("data/chunked/hr-policies-handbook"),
        output_dir=Path("evaluation_set"),
        threads=2,
    )