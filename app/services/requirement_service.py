import json
from pathlib import Path

from json_repair import repair_json
from pydantic import ValidationError

from app.models.ollama_client import generate_with_ollama
from app.schemas.specification import ProjectSpecification


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PROMPT_VERSION = "v2"

PROMPT_PATHS = {
    "v1": (
        PROJECT_ROOT
        / "prompts"
        / "requirement_prompt_v1.txt"
    ),
    "v2": (
        PROJECT_ROOT
        / "prompts"
        / "requirement_prompt_v2.txt"
    ),
}


def load_prompt_template(
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> str:

    if prompt_version not in PROMPT_PATHS:
        raise ValueError(
            f"Unsupported prompt version: {prompt_version}. "
            f"Available versions: {', '.join(PROMPT_PATHS)}"
        )

    prompt_path = PROMPT_PATHS[prompt_version]

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}"
        )

    return prompt_path.read_text(
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
    client_requirement: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> ProjectSpecification:

    client_requirement = client_requirement.strip()

    if not client_requirement:
        raise ValueError(
            "Client requirement cannot be empty."
        )

    prompt_template = load_prompt_template(
        prompt_version
    )

    prompt = prompt_template.replace(
        "{{CLIENT_REQUIREMENT}}",
        client_requirement
    )

    raw_response = generate_with_ollama(
        prompt
    )

    parsed_json = parse_model_json(
        raw_response
    )

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