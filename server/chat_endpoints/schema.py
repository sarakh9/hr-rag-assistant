import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pydantic import BaseModel
from assistant.assistant import ConversationTurn


class ChatInput(BaseModel):
    conversation: list[ConversationTurn]


class ChatOutput(BaseModel):
    assistant_response: ConversationTurn