import logging
import time
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Depends, Request
from assistant.assistant import HRAssistant
from assistant.assistant_config import  load_assistant_config
from assistant.knowledgebase import ChromaDBKnowledgeBase
from .schema import ChatInput, ChatOutput

logger = logging.getLogger(__name__)

router = APIRouter()

config = load_assistant_config("config/assistant.yaml")

ASSISTANT = HRAssistant(
        answer_generation_prompt=config.answer_generation_prompt,
        retrieval_query_prompt=config.retrieval_query_prompt,
        top_p=config.top_p,
        knowledge_base=ChromaDBKnowledgeBase(
            collection_name=config.knowledge_base.collection_name,
            embedding_model=config.knowledge_base.embedding_model,
            search_limit=config.knowledge_base.search_limit,
        ),
        answer_generation_model=config.answer_generation_model,
        retrieval_query_model=config.retrieval_query_model,
    )


def get_request_id(request: Request):
    return request.state.request_id


@router.post("/chat", response_model=ChatOutput)
def chat(chat_input: ChatInput, request_id: str = Depends(get_request_id)):
    try:
        logger.info(f"Chat request received {request_id}")
        logger.debug(f"Chat request: {chat_input}")
        start_time = time.time()

        assistant_response, _ = ASSISTANT.chat(chat_input.conversation)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Chat request processed {request_id} in {duration:.2f} seconds")
        logger.debug(f"Chat response: {assistant_response}")

        return ChatOutput(assistant_response=assistant_response)
    except Exception as e:
        logger.error(f"Error processing chat {request_id}: {e}")
        raise