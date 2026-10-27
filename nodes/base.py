"""Shared helpers for all workflow nodes."""

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Callable, Type, TypeVar

from pydantic import BaseModel

from exceptions import AnalysisError, ConfigurationError
from state import AnalyzerState
from utils.llm import get_llm

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def run_structured(
    schema: Type[T], system_prompt: str, user_prompt: str, retries: int = 2
) -> T:
    """Call the LLM and return a validated Pydantic object, retrying on transient failures."""
    structured_llm = get_llm().with_structured_output(schema)
    messages = [("system", system_prompt), ("human", user_prompt)]

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            result = structured_llm.invoke(messages)
            if result is None:
                raise ValueError("The model returned an empty response.")
            if isinstance(result, dict):
                result = schema.model_validate(result)
            return result
        except ConfigurationError:
            raise
        except Exception as exc:  # network, rate limit, parsing...
            last_error = exc
            logger.warning("LLM call failed (attempt %d/%d): %s", attempt + 1, retries + 1, exc)
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))

    raise AnalysisError(f"The model could not produce a valid answer: {last_error}") from last_error


def safe_node(label: str) -> Callable:
    """Decorator: turn any exception inside a node into `state['error']` so the graph stops cleanly."""

    def decorator(fn: Callable[[AnalyzerState], dict]) -> Callable[[AnalyzerState], dict]:
        @wraps(fn)
        def wrapper(state: AnalyzerState) -> dict:
            try:
                return fn(state)
            except Exception as exc:
                logger.exception("Node '%s' failed", label)
                return {"error": f"{label} failed: {exc}"}

        return wrapper

    return decorator
