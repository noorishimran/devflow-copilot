import json
from pathlib import Path

from json_repair import repair_json
from pydantic import ValidationError

from app.models.ollama_client import generate_with_ollama
from app.schemas.engineering import (
    EngineeringArtifacts,
    DeveloperPrompt,
)
from app.schemas.specification import ProjectSpecification


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROMPT_PATH = (
    PROJECT_ROOT
    / "prompts"
    / "engineering_artifacts_prompt_v1.txt"
)


class EvidenceFidelityError(RuntimeError):
    """Raised when generated artifacts contain unsupported behavior."""

    def __init__(
        self,
        message: str,
        violations: list[str] | None = None
    ):
        super().__init__(message)
        self.violations = violations or []


RISKY_PHRASES = {
    "valid credentials": "valid credential behavior",
    "invalid credentials": "invalid credential behavior",
    "successful login": "successful authentication behavior",
    "login succeeds": "successful authentication behavior",
    "login fails": "authentication failure behavior",
    "authentication": "authentication behavior",
    "authenticate": "authentication behavior",
    "server": "server behavior",
    "api": "API behavior",
    "database": "database behavior",
    "session": "session behavior",
    "redirect": "redirect behavior",
    "directed to": "navigation outcome",
    "navigate to account": "navigation outcome",
    "access their account": "account-access outcome",
    "allows access": "account-access outcome",
    "allow access": "account-access outcome",
    "error message": "error-message behavior",
    "submitted": "form-submission behavior",
    "submits": "form-submission behavior",
    "submit the form": "form-submission behavior",
    "sent to": "data-transfer behavior",
    "stored in": "data-storage behavior",
}


def load_engineering_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Engineering prompt not found: {PROMPT_PATH}"
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

    first_brace = cleaned.find("{")

    if first_brace > 0:
        cleaned = cleaned[first_brace:]

    return cleaned.strip()


def parse_engineering_json(
    response: str
) -> dict:
    cleaned = clean_model_response(response)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        try:
            repaired = repair_json(cleaned)

            return json.loads(repaired)

        except Exception as exc:
            raise RuntimeError(
                "The AI model returned invalid engineering JSON."
            ) from exc


def validate_engineering_schema(
    parsed_json: dict
) -> EngineeringArtifacts:
    try:
        return EngineeringArtifacts.model_validate(
            parsed_json
        )

    except ValidationError as exc:
        raise RuntimeError(
            "Engineering artifacts failed schema validation:\n"
            f"{exc}"
        ) from exc


def get_supported_text(
    specification: ProjectSpecification
) -> str:
    supported_parts = [
        specification.project_summary,
    ]

    for feature in specification.features:
        supported_parts.append(
            feature.name
        )
        supported_parts.append(
            feature.description
        )

    supported_parts.extend(
        specification.assumptions
    )

    supported_parts.extend(
        specification.open_questions
    )

    return " ".join(
        supported_parts
    ).lower()


def find_unsupported_behaviors(
    text: str,
    supported_text: str
) -> list[str]:
    text = text.lower()

    violations = []

    for phrase, description in RISKY_PHRASES.items():
        if (
            phrase in text
            and phrase not in supported_text
        ):
            violations.append(
                description
            )

    return sorted(
        set(violations)
    )


def validate_evidence_fidelity(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts
) -> None:
    supported_text = get_supported_text(
        specification
    )

    confirmed_parts = []

    for criterion in artifacts.acceptance_criteria:
        confirmed_parts.extend(
            [
                criterion.feature,
                criterion.given,
                criterion.when,
                criterion.then,
            ]
        )

    for step in artifacts.implementation_plan:
        confirmed_parts.extend(
            [
                step.title,
                step.description,
                *step.files_or_components,
                *step.dependencies,
            ]
        )

    for test_case in artifacts.qa_test_cases:
        confirmed_parts.extend(
            [
                test_case.title,
                *test_case.preconditions,
                *test_case.steps,
                test_case.expected_result,
            ]
        )

    confirmed_parts.append(
        artifacts.developer_prompt.objective
    )

    confirmed_parts.extend(
        artifacts.developer_prompt.implementation_instructions
    )

    confirmed_text = " ".join(
        confirmed_parts
    )

    violations = find_unsupported_behaviors(
        confirmed_text,
        supported_text
    )

    if violations:
        raise EvidenceFidelityError(
            "Engineering output introduced unsupported behavior: "
            + ", ".join(violations),
            violations=violations
        )


def item_is_safe(
    text: str,
    supported_text: str
) -> bool:
    violations = find_unsupported_behaviors(
        text,
        supported_text
    )

    return len(violations) == 0


def build_safe_fallback(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts
) -> EngineeringArtifacts:
    """
    Deterministically remove generated artifact items that contain
    unsupported behavior.

    The fallback does not ask the model to guess again.
    """

    supported_text = get_supported_text(
        specification
    )

    safe_acceptance_criteria = []

    for criterion in artifacts.acceptance_criteria:
        criterion_text = " ".join(
            [
                criterion.feature,
                criterion.given,
                criterion.when,
                criterion.then,
            ]
        )

        if item_is_safe(
            criterion_text,
            supported_text
        ):
            safe_acceptance_criteria.append(
                criterion
            )

    safe_implementation_plan = []

    for step in artifacts.implementation_plan:
        step_text = " ".join(
            [
                step.title,
                step.description,
                *step.files_or_components,
                *step.dependencies,
            ]
        )

        if item_is_safe(
            step_text,
            supported_text
        ):
            safe_implementation_plan.append(
                step
            )

    safe_qa_test_cases = []

    for test_case in artifacts.qa_test_cases:
        test_text = " ".join(
            [
                test_case.title,
                *test_case.preconditions,
                *test_case.steps,
                test_case.expected_result,
            ]
        )

        if item_is_safe(
            test_text,
            supported_text
        ):
            safe_qa_test_cases.append(
                test_case
            )

    safe_instructions = []

    for instruction in (
        artifacts.developer_prompt
        .implementation_instructions
    ):
        if item_is_safe(
            instruction,
            supported_text
        ):
            safe_instructions.append(
                instruction
            )

    if not safe_instructions:
        safe_instructions = [
            (
                "Implement only the functionality explicitly "
                "described in the validated specification."
            )
        ]

    unknowns = list(
        artifacts.developer_prompt.unknowns
    )

    open_questions = list(
        artifacts.open_questions
    )

    generic_question = (
        "What should happen after any user action whose "
        "outcome is not explicitly defined in the specification?"
    )

    if generic_question not in open_questions:
        open_questions.append(
            generic_question
        )

    if generic_question not in unknowns:
        unknowns.append(
            generic_question
        )

    developer_prompt = DeveloperPrompt(
        objective=(
            "Implement only the confirmed requirements described "
            "in the validated specification."
        ),
        implementation_instructions=safe_instructions,
        constraints=[
            (
                "Do not add functionality not explicitly supported "
                "by the validated specification."
            ),
            (
                "Do not invent APIs, databases, authentication "
                "behavior, redirects, servers, or hidden workflows."
            ),
        ],
        unknowns=unknowns,
    )

    return EngineeringArtifacts(
        acceptance_criteria=safe_acceptance_criteria,
        implementation_plan=safe_implementation_plan,
        qa_test_cases=safe_qa_test_cases,
        developer_prompt=developer_prompt,
        assumptions=list(
            artifacts.assumptions
        ),
        open_questions=open_questions,
    )


def generate_once(
    prompt: str
) -> EngineeringArtifacts:
    raw_response = generate_with_ollama(
        prompt,
        num_predict=1400
    )

    parsed_json = parse_engineering_json(
        raw_response
    )

    return validate_engineering_schema(
        parsed_json
    )


def generate_engineering_artifacts(
    specification: ProjectSpecification
) -> EngineeringArtifacts:

    if specification is None:
        raise ValueError(
            "Validated specification is required."
        )

    prompt_template = load_engineering_prompt()

    specification_json = (
        specification.model_dump_json(
            indent=2
        )
    )

    base_prompt = (
        prompt_template
        + "\n\nVALIDATED SPECIFICATION:\n"
        + specification_json
    )

    # Attempt 1
    artifacts = generate_once(
        base_prompt
    )

    try:
        validate_evidence_fidelity(
            specification,
            artifacts
        )

        return artifacts

    except EvidenceFidelityError as first_error:

        correction_prompt = (
            base_prompt
            + "\n\nCORRECTION REQUIRED:\n"
            + "The previous output was rejected by the "
              "evidence-fidelity safety guard.\n"
            + "Detected unsupported behavior:\n"
            + ", ".join(
                first_error.violations
            )
            + "\n\n"
            + "Generate the COMPLETE JSON again.\n"
            + "Remove all unsupported behavior.\n"
            + "Do not replace it with another assumption.\n"
            + "Move genuinely missing behavior to "
              "open_questions and developer_prompt.unknowns.\n"
            + "Return ONLY valid JSON."
        )

        # Attempt 2
        corrected_artifacts = generate_once(
            correction_prompt
        )

        try:
            validate_evidence_fidelity(
                specification,
                corrected_artifacts
            )

            return corrected_artifacts

        except EvidenceFidelityError:
            # Final deterministic safety fallback.
            safe_artifacts = build_safe_fallback(
                specification,
                corrected_artifacts
            )

            # Safety-check the fallback too.
            validate_evidence_fidelity(
                specification,
                safe_artifacts
            )

            return safe_artifacts