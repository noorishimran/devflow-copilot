import json
from pathlib import Path

from pydantic import ValidationError

from app.models.ollama_client import generate_with_ollama
from app.schemas.specification import ProjectSpecification


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = PROJECT_ROOT / "prompts" / "requirement_prompt_v2.txt"


def load_prompt_template() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def clean_model_response(response: str) -> str:
    cleaned = response.strip()

    # Sometimes models still return markdown code fences.
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()


def generate_specification(
    client_requirement: str
) -> ProjectSpecification:

    client_requirement = client_requirement.strip()

    if not client_requirement:
        raise ValueError(
            "Client requirement cannot be empty."
        )

    # Load versioned prompt
    prompt_template = load_prompt_template()

    # Insert actual client requirement
    prompt = prompt_template.replace(
        "{{CLIENT_REQUIREMENT}}",
        client_requirement
    )

    # Send prompt to local Qwen model
    raw_response = generate_with_ollama(prompt)

    # Clean possible markdown around JSON
    cleaned_response = clean_model_response(raw_response)

    # Parse model output as JSON
    try:
        parsed_json = json.loads(cleaned_response)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The AI model returned invalid JSON."
        ) from exc

    # Validate JSON against our schema
    try:
        validated_specification = (
            ProjectSpecification.model_validate(parsed_json)
        )

    except ValidationError as exc:
        raise RuntimeError(
            f"AI output failed schema validation:\n{exc}"
        ) from exc

    return validated_specification