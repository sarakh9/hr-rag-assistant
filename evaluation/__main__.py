import logging
from pathlib import Path

from answer_generator import AnswerGenerator
from evaluator import Evaluator
from metrics import Metric

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    answer_generator = AnswerGenerator(
        assistant_config_path=Path("config/assistant.yaml")
    )
    answered_evaluation_set = answer_generator.complete_evaluation_set(
        evaluation_set_path=Path(
            "evaluation_set/evaluation_set_2026_06_28_17_02_15.json"
        )
    )
    evaluator = Evaluator(
        model="gemini-3.1-flash-lite",
        save_dir=Path("results"),
    )
    evaluator.evaluate(
        answered_evaluation_set=answered_evaluation_set,
        metrics=[
            Metric.FAITHFULNESS,
            Metric.CONTEXT_RELEVANCE,
            Metric.HELPFULNESS,
        ],
    )
    logger.info("Evaluation set completed successfully.")