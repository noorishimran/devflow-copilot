import json
from pathlib import Path

from json_repair import repair_json
from pydantic import ValidationError

from app.models.ollama_client import generate_with_ollama
from app.schemas.specification import ProjectSpecification


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPT_PATH = (
    PROJECT_ROOT
    / "prompts"
    / "requirement_prompt_v2.txt"
)


def load_prompt_template() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(
        encoding="utf-8"
    )


def clean_model_response(response: str) -> str:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # Remove accidental text before JSON.
    first_brace = cleaned.find("{")

    if first_brace > 0:
        cleaned = cleaned[first_brace:]

    return cleaned.strip()


def parse_model_json(response: str) -> dict:
    cleaned = clean_model_response(response)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        try:
            repaired = repair_json(cleaned)
            return json.loads(repaired)

        except Exception as exc:
            raise RuntimeError(
                "The AI model returned invalid JSON."
            ) from exc


def generate_specification(
    client_requirement: str
) -> ProjectSpecification:

    client_requirement = client_requirement.strip()

    if not client_requirement:
        raise ValueError(
            "Client requirement cannot be empty."
        )

    # Load versioned requirement prompt.
    prompt_template = load_prompt_template()

    # Insert actual client requirement.
    prompt = prompt_template.replace(
        "{{CLIENT_REQUIREMENT}}",
        client_requirement
    )

    # Generate locally using Ollama.
    raw_response = generate_with_ollama(prompt)

    # Parse JSON with repair fallback.
    parsed_json = parse_model_json(
        raw_response
    )

    # Validate model output.
    try:
        validated_specification = (
            ProjectSpecification.model_validate(
                parsed_json
            )
        )

    except ValidationError as exc:
        raise RuntimeError(
            "AI output failed schema validation:\n"
            f"{exc}"
        ) from exc

    return validated_specification