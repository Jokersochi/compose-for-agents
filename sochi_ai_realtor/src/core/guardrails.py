from typing import Type, Any
import typing
from pydantic import BaseModel, ValidationError
from src.core.logger import log

class GuardrailException(Exception):
    def __init__(self, message: str, errors: list):
        super().__init__(message)
        self.errors = errors

def validate_llm_output(model_class: Type[BaseModel], llm_output: dict | str) -> BaseModel:
    """
    Validates the output of an LLM against a Pydantic model.
    This acts as a 'guardrail' to prevent hallucinations or malformed JSON from breaking the system.
    If the LLM outputs invalid data, it raises an exception which should trigger a retry.
    """
    try:
        if isinstance(llm_output, str):
            # Try parsing JSON string to model
            validated_data = model_class.model_validate_json(llm_output)
        else:
            # Parse dict directly
            validated_data = model_class.model_validate(llm_output)

        log.info(
            "llm_output_validated",
            model=model_class.__name__,
            status="success"
        )
        return validated_data

    except ValidationError as e:
        log.error(
            "llm_output_validation_failed",
            model=model_class.__name__,
            errors=e.errors(),
            raw_output=str(llm_output)
        )
        raise GuardrailException(f"LLM output failed validation against {model_class.__name__}", e.errors())

def execute_with_guardrails(action_name: str, agent_name: str, func: typing.Callable, model_class: Type[BaseModel], *args, **kwargs) -> Any:
    """
    Executes a function (usually a call to an LLM) and applies guardrails to its output.
    Logs the action for audit purposes.
    """
    log.info("agent_action_started", agent_name=agent_name, action=action_name)
    try:
        raw_output = func(*args, **kwargs)
        validated_output = validate_llm_output(model_class, raw_output)

        # In a real scenario, here we would also save the action to `DBAgentActionLog`
        # via an async background task or synchronous db call depending on context.

        log.info("agent_action_completed", agent_name=agent_name, action=action_name, status="success")
        return validated_output
    except Exception as e:
        log.error("agent_action_failed", agent_name=agent_name, action=action_name, error=str(e))
        raise
