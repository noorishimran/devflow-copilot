import json

from app.schemas.specification import ProjectSpecification
from app.schemas.engineering import EngineeringArtifacts
from app.schemas.evaluation import ReliabilityReport
from app.schemas.review import ArtifactReview, ReviewStatus

from app.services.export_service import (
    build_export_payload,
    export_as_json,
    export_as_markdown,
)


def make_specification():
    return ProjectSpecification.model_validate(
        {
            "project_summary": "Build a simple task list application.",
            "features": [
                {
                    "name": "Task Addition",
                    "description": "Users can add a task to the visible task list.",
                    "priority": "high",
                }
            ],
            "user_stories": [
                {
                    "role": "User",
                    "goal": "Add a task",
                    "benefit": "Keep track of work",
                }
            ],
            "assumptions": [],
            "open_questions": [
                "Should completed tasks remain visible?"
            ],
        }
    )


def make_engineering_artifacts():
    return EngineeringArtifacts.model_validate(
        {
            "acceptance_criteria": [
                {
                    "id": "AC-001",
                    "feature": "Task Addition",
                    "given": "The user has entered a task title",
                    "when": "The user presses Add Task",
                    "then": "The task is added to the visible task list",
                }
            ],
            "implementation_plan": [
                {
                    "step_number": 1,
                    "title": "Implement Task Addition",
                    "description": "Create the task input and Add Task behavior.",
                    "files_or_components": [],
                    "dependencies": [],
                }
            ],
            "qa_test_cases": [
                {
                    "test_id": "TC-001",
                    "title": "Add Task",
                    "test_type": "functional",
                    "preconditions": [],
                    "steps": [
                        "Enter a task title",
                        "Press Add Task",
                    ],
                    "expected_result": "The task appears in the visible task list",
                }
            ],
            "developer_prompt": {
                "objective": "Implement the confirmed task addition requirement.",
                "implementation_instructions": [
                    "Create a task input and Add Task action."
                ],
                "constraints": [
                    "Do not add unsupported functionality."
                ],
                "unknowns": [],
            },
            "assumptions": [],
            "open_questions": [
                "Should completed tasks remain visible?"
            ],
        }
    )


def make_reliability_report():
    return ReliabilityReport.model_validate(
        {
            "overall_score": 95,
            "overall_status": "pass",
            "metrics": [
                {
                    "name": "schema_validity",
                    "score": 100,
                    "status": "pass",
                    "findings": [
                        "Schema validation passed."
                    ],
                },
                {
                    "name": "evidence_fidelity",
                    "score": 100,
                    "status": "pass",
                    "findings": [
                        "No unsupported behavior detected."
                    ],
                },
            ],
            "detected_issues": [],
            "regression_flags": [],
            "human_review_required": True,
        }
    )


def make_review():
    return ArtifactReview(
        status=ReviewStatus.APPROVED,
        reviewer_notes="Reviewed and approved.",
        action_history=[
            "Review approved."
        ],
    )


def test_build_export_payload_contains_all_sections():
    payload = build_export_payload(
        make_specification(),
        make_engineering_artifacts(),
        make_reliability_report(),
        make_review(),
    )

    assert "specification" in payload
    assert "engineering_artifacts" in payload
    assert "reliability_report" in payload
    assert "human_review" in payload


def test_export_as_json_is_valid_json():
    result = export_as_json(
        make_specification(),
        make_engineering_artifacts(),
        make_reliability_report(),
        make_review(),
    )

    parsed = json.loads(result)

    assert parsed["specification"]["project_summary"] == (
        "Build a simple task list application."
    )
    assert parsed["reliability_report"]["overall_score"] == 95
    assert parsed["human_review"]["status"] == "approved"


def test_export_as_markdown_contains_project_sections():
    result = export_as_markdown(
        make_specification(),
        make_engineering_artifacts(),
        make_reliability_report(),
        make_review(),
    )

    assert "# DevFlow Copilot — Engineering Package" in result
    assert "## Project Summary" in result
    assert "## Features" in result
    assert "## Acceptance Criteria" in result
    assert "## Implementation Plan" in result
    assert "## QA Test Cases" in result
    assert "## Reliability Evaluation" in result
    assert "## Human Review" in result
    assert "## Open Questions" in result


def test_markdown_open_questions_are_deduplicated():
    result = export_as_markdown(
        make_specification(),
        make_engineering_artifacts(),
        make_reliability_report(),
        make_review(),
    )

    question = "Should completed tasks remain visible?"

    assert result.count(question) == 1