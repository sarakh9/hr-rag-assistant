from dataclasses import dataclass
from enum import Enum
from textwrap import dedent

from pydantic import BaseModel, conint

@dataclass
class GenAIMetric:
    prompt: str

class MetricScore(BaseModel):
    score: conint(ge=1, le=5)
    reason: str

ANSWER_CORRECTNESS = GenAIMetric(
    prompt=dedent(
        """
        Evaluate the correctness of the following AI-generated answer in the context of company HR policy.

        Question:
        "{question}"

        Answer:
        "{answer}"

        Expected Answer (ground truth):
        "{ground_truth}"

        Is the answer correct compared to the expected answer and the company's documentation?
        Return a score between 1 and 5, where 1 is the lowest score and 5 is the highest.
        Also return the reason for the score in plain text.
        """
    )
)

FAITHFULNESS = GenAIMetric(
    prompt=dedent(
        """
        You are evaluating whether an AI-generated HR answer is factually supported by the provided context.

        Context (retrieved passages):
        {context}

        Answer:
        "{answer}"

        Question:
        "{question}"

        Is the answer factually supported by the context above (i.e., grounded in the retrieved documents)?
        Return a score between 1 and 5 and a short reason.
        """
    )
)

CONTEXT_RELEVANCE = GenAIMetric(
    prompt=dedent(
        """
        Evaluate how relevant the provided context passages are to answering the user's question.

        Question:
        "{question}"

        Context (retrieved passages):
        {context}

        How relevant are these passages for answering the question?
        Return a score between 1 and 5 and a short reason.
        """
    )
)

HELPFULNESS = GenAIMetric(
    prompt=dedent(
        """
        Evaluate how helpful the following answer is for the user's question (HR domain).

        Question:
        "{question}"

        Answer:
        "{answer}"

        Is the answer useful and actionable for the employee? Return a score 1-5 and a short reason.
        """
    )
)

class Metric(Enum):
    ANSWER_CORRECTNESS = "answer_correctness"
    FAITHFULNESS = "faithfulness"
    CONTEXT_RELEVANCE = "context_relevance"
    HELPFULNESS = "helpfulness"
    # URL_HIT_RATE = "url_hit_rate"