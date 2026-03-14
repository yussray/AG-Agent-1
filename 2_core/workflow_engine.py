# ============================================================
# workflow_engine.py — Antigravity Multi-Agent System
# Orchestrates sequential multi-step tasks
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Any

logger = logging.getLogger("antigravity.workflow")


# ----------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------

@dataclass
class WorkflowStep:
    """
    A single step in a workflow.

    Attributes:
        name: Human-readable step name
        fn: Callable(context: dict, **params) -> Any
        params: Extra keyword arguments forwarded to fn
        retries: How many times to retry on failure
    """
    name: str
    fn: Callable
    params: dict = field(default_factory=dict)
    retries: int = 1


@dataclass
class WorkflowResult:
    """
    Result from running a workflow.

    Attributes:
        success: True if all required steps completed
        context: Shared dict with step outputs
        errors: List of (step_name, error_message)
    """
    success: bool
    context: dict
    errors: list = field(default_factory=list)


# ----------------------------------------------------------------
# Pre-built step functions
# ----------------------------------------------------------------

def step_ollama_generate(context: dict, prompt_key: str = "input") -> str:
    """
    Generate a response from Ollama using context[prompt_key].
    Puts result in context under the calling step's name.
    """
    from ollama_connector import ollama
    from config import REASONING_MODEL

    prompt = context.get(prompt_key, context.get("input", ""))
    model = context.get("model", REASONING_MODEL)
    result = ollama.generate(model=model, prompt=prompt)
    return result


def step_anythingllm_query(context: dict, query_key: str = "input") -> str:
    """
    Query the AnythingLLM knowledge base using context[query_key].
    """
    from anythingllm_connector import anythingllm

    query = context.get(query_key, context.get("input", ""))
    if not query:
        return "No query provided."
    return anythingllm.smart_query(query)


def step_save_to_file(context: dict, result_key: str, filename: str) -> str:
    """
    Save context[result_key] to OUTPUT_DIR/filename.
    Returns saved file path.
    """
    from config import OUTPUT_DIR

    content = context.get(result_key, "")
    if not content:
        return f"[skip] No content to save for key: {result_key}"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(str(content))

    logger.info(f"Saved: {path}")
    return path


# ----------------------------------------------------------------
# Workflow Engine
# ----------------------------------------------------------------

class WorkflowEngine:
    """
    Runs named workflows as sequences of WorkflowSteps.

    - Each step receives the shared context dict
    - Step output is stored in context[step.name]
    - Steps may read outputs from previous steps via context
    - Retry logic wraps each step independently
    """

    def __init__(self):
        self._registry: dict[str, list] = {}

    # ----------------------------------------------------------------
    # Registry
    # ----------------------------------------------------------------

    def register(self, name: str, steps: list[WorkflowStep]) -> None:
        """Register a named workflow."""
        self._registry[name] = steps
        logger.debug(f"Registered workflow: {name} ({len(steps)} steps)")

    def list_workflows(self) -> list[str]:
        """Return all registered workflow names."""
        return list(self._registry.keys())

    # ----------------------------------------------------------------
    # Execution
    # ----------------------------------------------------------------

    def run(
        self,
        name: str,
        steps: list[WorkflowStep] = None,
        initial_context: dict = None
    ) -> WorkflowResult:
        """
        Execute a workflow by name, or run ad-hoc steps.

        Args:
            name: Workflow name (for logging)
            steps: If provided, run these steps instead of registry lookup
            initial_context: Optional seed data for the context

        Returns:
            WorkflowResult with success flag, context, and errors
        """
        if steps is None:
            steps = self._registry.get(name, [])

        if not steps:
            logger.warning(f"No steps found for workflow: {name}")
            return WorkflowResult(success=False, context={}, errors=[(name, "No steps registered")])

        context: dict = initial_context or {}
        errors: list = []

        logger.info(f"[Workflow] Starting: {name} ({len(steps)} steps)")

        for step in steps:
            success = False
            last_error = None

            for attempt in range(step.retries):
                try:
                    logger.info(f"[Workflow] Step: {step.name} (attempt {attempt + 1}/{step.retries})")
                    t0 = time.time()

                    result = step.fn(context, **step.params)

                    elapsed = round(time.time() - t0, 2)
                    logger.info(f"[Workflow] Step '{step.name}' ✅ ({elapsed}s)")

                    # Store step output
                    step_key = step.name.lower().replace(" ", "_")
                    context[step_key] = result

                    success = True
                    break

                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"[Workflow] Step '{step.name}' failed (attempt {attempt + 1}): {e}")
                    if attempt < step.retries - 1:
                        time.sleep(1)

            if not success:
                logger.error(f"[Workflow] Step '{step.name}' permanently failed: {last_error}")
                errors.append((step.name, last_error))

        overall_success = len(errors) == 0
        logger.info(f"[Workflow] Finished: {name} | success={overall_success} | errors={len(errors)}")

        return WorkflowResult(success=overall_success, context=context, errors=errors)


# ----------------------------------------------------------------
# Singleton instance
# ----------------------------------------------------------------

engine = WorkflowEngine()
