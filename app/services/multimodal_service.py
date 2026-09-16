import json
from pathlib import Path

from json_repair import repair_json
from pydantic import ValidationError

from app.models.ollama_vision_client import analyze_image_with_ollama
from app.schemas.multimodal import ImageEvidence, NormalizedRequirementContext
from app.services.requirement_service import generate_specification


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PROMPT_PATH = PROJECT_ROOT / "prompts" / "image_analysis_prompt_v1.txt"


def load_image_prompt() -> str:
    if not IMAGE_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Image prompt not found: {IMAGE_PROMPT_PATH}")
    return IMAGE_PROMPT_PATH.read_text(encoding="utf-8")


def clean_json_response(response_text: str) -> str:
    if not response_text:
        raise RuntimeError("Vision model returned an empty response.")

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()
    first_brace = cleaned.find("{")

    if first_brace == -1:
        raise RuntimeError("Vision model did not return a JSON object.")

    return cleaned[first_brace:]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []

    for item in items:
        clean_item = str(item).strip()
        if not clean_item:
            continue

        key = clean_item.casefold()

        if key not in seen:
            seen.add(key)
            result.append(clean_item)

    return result


def _normalize_vision_payload(parsed: object) -> dict:
    if not isinstance(parsed, dict):
        raise RuntimeError("Vision model JSON root must be an object.")

    list_fields = [
        "observed_components",
        "visible_states",
        "possible_interactions",
        "observed_facts",
        "assumptions",
        "open_questions",
    ]

    for field in list_fields:
        if not isinstance(parsed.get(field), list):
            parsed[field] = []

    valid_components = []

    for component in parsed["observed_components"]:
        if not isinstance(component, dict):
            continue

        component_type = str(component.get("component_type", "")).strip()
        evidence = str(component.get("evidence", "")).strip()

        if not component_type or not evidence:
            continue

        valid_components.append(
            {
                "component_type": component_type,
                "label": str(component.get("label", "")).strip(),
                "visible_text": str(component.get("visible_text", "")).strip(),
                "state": str(component.get("state", "")).strip(),
                "evidence": evidence,
            }
        )

    # Remove duplicate UI components and enforce a maximum of 6.
    unique_components = []
    seen_components = set()

    for component in valid_components:
        key = (
            component["component_type"].casefold(),
            component["evidence"].casefold(),
        )

        if key not in seen_components:
            seen_components.add(key)
            unique_components.append(component)

    parsed["observed_components"] = unique_components[:6]

    for field in [
        "visible_states",
        "possible_interactions",
        "observed_facts",
        "assumptions",
        "open_questions",
    ]:
        parsed[field] = _dedupe(
            [str(item) for item in parsed[field] if item is not None]
        )

    return parsed


def parse_vision_json(raw_response: str) -> dict:
    cleaned = clean_json_response(raw_response)

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError:
        try:
            repaired_text = repair_json(cleaned)
            parsed = json.loads(repaired_text)

        except Exception as exc:
            raise RuntimeError(
                "Vision model returned malformed JSON and the local JSON repair step could not recover it."
            ) from exc

    return _normalize_vision_payload(parsed)


def analyze_screenshot(image_bytes: bytes) -> ImageEvidence:
    if not image_bytes:
        raise ValueError("Please provide an image.")

    prompt = load_image_prompt()

    raw_response = analyze_image_with_ollama(
        prompt=prompt,
        image_bytes=image_bytes,
    )

    parsed = parse_vision_json(raw_response)

    try:
        return ImageEvidence.model_validate(parsed)

    except ValidationError as exc:
        raise RuntimeError(
            "Vision model output failed schema validation:\n"
            f"{exc}"
        ) from exc


def build_normalized_context(
    client_text: str = "",
    image_evidence: ImageEvidence | None = None,
) -> NormalizedRequirementContext:
    clean_text = client_text.strip()
    has_text = bool(clean_text)
    has_image = image_evidence is not None

    if not has_text and not has_image:
        raise ValueError("Provide client text, an image, or both.")

    if has_text and has_image:
        source_mode = "combined"
    elif has_image:
        source_mode = "image_only"
    else:
        source_mode = "text_only"

    observed_evidence = []
    assumptions = []
    open_questions = []

    if image_evidence:
        observed_evidence.extend(image_evidence.observed_facts)
        observed_evidence.extend(image_evidence.visible_states)

        for component in image_evidence.observed_components:
            observed_evidence.append(component.evidence)

        assumptions.extend(image_evidence.assumptions)
        open_questions.extend(image_evidence.open_questions)

    return NormalizedRequirementContext(
        source_mode=source_mode,
        client_text=clean_text,
        image_evidence=image_evidence,
        observed_evidence=_dedupe(observed_evidence),
        assumptions=_dedupe(assumptions),
        open_questions=_dedupe(open_questions),
    )


def normalized_context_to_text(
    context: NormalizedRequirementContext,
) -> str:
    sections = [f"SOURCE MODE: {context.source_mode}"]

    if context.client_text:
        sections.append("CLIENT-PROVIDED TEXT:\n" + context.client_text)

    if context.image_evidence:
        if context.observed_evidence:
            observed = "\n".join(
                f"- {item}" for item in context.observed_evidence
            )
            sections.append(
                "OBSERVED SCREENSHOT EVIDENCE:\n" + observed
            )

        if context.image_evidence.possible_interactions:
            interactions = "\n".join(
                f"- {item}"
                for item in _dedupe(
                    context.image_evidence.possible_interactions
                )
            )

            sections.append(
                "POSSIBLE SCREENSHOT INTERACTIONS (UNCONFIRMED):\n"
                + interactions
            )

    if context.assumptions:
        assumption_text = "\n".join(
            f"- {item}" for item in context.assumptions
        )

        sections.append(
            "ASSUMPTIONS / INFERENCES "
            "(DO NOT TREAT AS CONFIRMED FACTS):\n"
            + assumption_text
        )

    if context.open_questions:
        question_text = "\n".join(
            f"- {item}" for item in context.open_questions
        )

        sections.append("OPEN QUESTIONS:\n" + question_text)

    sections.append(
        "IMPORTANT: Use only client-provided text and directly observed "
        "screenshot evidence as factual requirement evidence. "
        "Do not convert assumptions or possible interactions into confirmed client facts."
    )

    return "\n\n".join(sections)


def generate_multimodal_specification(
    client_text: str = "",
    image_bytes: bytes | None = None,
):
    image_evidence = None

    if image_bytes:
        image_evidence = analyze_screenshot(image_bytes)

    context = build_normalized_context(
        client_text=client_text,
        image_evidence=image_evidence,
    )

    normalized_text = normalized_context_to_text(context)
    specification = generate_specification(normalized_text)

    return specification, image_evidence, context
