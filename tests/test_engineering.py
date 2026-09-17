import pytest

from app.schemas.engineering import EngineeringArtifacts
from app.schemas.specification import ProjectSpecification
from app.services.engineering_service import (
    EvidenceFidelityError,
    build_safe_fallback,
    find_unsupported_behaviors,
    validate_evidence_fidelity,
)


def make_specification() -> ProjectSpecification:
    return ProjectSpecification.model_validate(
        {
            "project_summary": (
                "A simple login page where users can enter "
                "their email and password and press a Login button."
            ),
            "features": [
                {
                    "name": "Login Functionality",
                    "description": (
                        "Users can enter their email and password "
                        "and press a Login button."
                    ),
                    "priority": "high",
                }
            ],
            "user_stories": [
                {
                    "role": "User",
                    "goal": "To log in to their account",
                    "benefit": "To access their account",
                }
            ],
            "assumptions": [],
            "open_questions": [],
        }
    )


def make_safe_artifacts() -> EngineeringArtifacts:
    return EngineeringArtifacts.model_validate(
        {
            "acceptance_criteria": [
                {
                    "id": "AC-001",
                    "feature": "Login Functionality",
                    "given": "User is on the login page",
                    "when": "User enters email and password",
                    "then": "A Login button is available",
                }
            ],
            "implementation_plan": [
                {
                    "step_number": 1,
                    "title": "Implement Login UI",
                    "description": (
                        "Create email and password inputs "
                        "and a Login button"
                    ),
                    "files_or_components": [],
                    "dependencies": [],
                }
            ],
            "qa_test_cases": [
                {
                    "test_id": "TC-001",
                    "title": "Login button availability",
                    "test_type": "ui",
                    "preconditions": [],
                    "steps": [
                        "Open the login page"
                    ],
                    "expected_result": (
                        "A Login button is available"
                    ),
                }
            ],
            "developer_prompt": {
                "objective": "Implement the confirmed login UI",
                "implementation_instructions": [
                    (
                        "Create email and password inputs "
                        "and a Login button"
                    )
                ],
                "constraints": [
                    (
                        "Do not add unsupported functionality"
                    )
                ],
                "unknowns": [
                    (
                        "What should happen after the user "
                        "clicks the Login button?"
                    )
                ],
            },
            "assumptions": [],
            "open_questions": [
                (
                    "What should happen after the user "
                    "clicks the Login button?"
                )
            ],
        }
    )


def test_safe_engineering_artifacts_pass_fidelity_check():
    specification = make_specification()
    artifacts = make_safe_artifacts()

    validate_evidence_fidelity(
        specification,
        artifacts,
    )


def test_unsupported_redirect_is_detected():
    violations = find_unsupported_behaviors(
        "User is redirected to their account",
        "User can press a Login button",
    )

    assert "redirect behavior" in violations


def test_unsupported_behavior_raises_error():
    specification = make_specification()

    unsafe_artifacts = make_safe_artifacts()

    unsafe_artifacts.qa_test_cases[0].expected_result = (
        "User is redirected to their account"
    )

    with pytest.raises(EvidenceFidelityError):
        validate_evidence_fidelity(
            specification,
            unsafe_artifacts,
        )


def test_safe_fallback_removes_unsafe_test_case():
    specification = make_specification()

    unsafe_artifacts = make_safe_artifacts()

    unsafe_artifacts.qa_test_cases[0].expected_result = (
        "User is redirected to their account"
    )

    safe_artifacts = build_safe_fallback(
        specification,
        unsafe_artifacts,
    )

    assert len(safe_artifacts.qa_test_cases) == 0

    assert len(
        safe_artifacts.open_questions
    ) >= 1