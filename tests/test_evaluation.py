from app.schemas.engineering import EngineeringArtifacts
from app.schemas.specification import ProjectSpecification
from app.services.evaluation_service import (
    evaluate_evidence_fidelity,
    evaluate_open_question_quality,
    evaluate_reliability,
    evaluate_requirement_coverage,
)


def make_specification() -> ProjectSpecification:
    return ProjectSpecification.model_validate(
        {
            "project_summary": (
                "Build a product search page where users can enter "
                "a product name and press Search to display matching products."
            ),
            "features": [
                {
                    "name": "Product Search",
                    "description": (
                        "Users can enter a product name into a search field "
                        "and press a Search button to display matching products."
                    ),
                    "priority": "high",
                }
            ],
            "user_stories": [
                {
                    "role": "User",
                    "goal": "Search for products",
                    "benefit": "View matching products",
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
                    "feature": "Product Search",
                    "given": (
                        "User is on the product search page "
                        "with a search field"
                    ),
                    "when": (
                        "User enters a product name and "
                        "presses the Search button"
                    ),
                    "then": (
                        "Products matching the entered "
                        "product name are displayed"
                    ),
                }
            ],
            "implementation_plan": [
                {
                    "step_number": 1,
                    "title": "Implement Product Search",
                    "description": (
                        "Create a product search field and Search button "
                        "that display products matching the entered name"
                    ),
                    "files_or_components": [],
                    "dependencies": [],
                }
            ],
            "qa_test_cases": [
                {
                    "test_id": "TC-001",
                    "title": "Product Search",
                    "test_type": "functional",
                    "preconditions": [],
                    "steps": [
                        "Enter a product name into the search field",
                        "Press the Search button",
                    ],
                    "expected_result": (
                        "Matching products are displayed"
                    ),
                }
            ],
            "developer_prompt": {
                "objective": (
                    "Implement the confirmed Product Search behavior"
                ),
                "implementation_instructions": [
                    (
                        "Allow users to enter a product name "
                        "and press Search to display matching products"
                    )
                ],
                "constraints": [
                    "Do not add unsupported functionality"
                ],
                "unknowns": [],
            },
            "assumptions": [],
            "open_questions": [],
        }
    )


def test_safe_output_gets_high_reliability_score():
    specification = make_specification()
    artifacts = make_safe_artifacts()

    report = evaluate_reliability(
        specification,
        artifacts,
    )

    assert report.overall_score >= 80
    assert report.overall_status == "pass"
    assert report.human_review_required is True


def test_unsupported_redirect_fails_evidence_fidelity():
    specification = make_specification()
    artifacts = make_safe_artifacts()

    artifacts.acceptance_criteria[0].then = (
        "User is redirected to a dashboard"
    )

    metric = evaluate_evidence_fidelity(
        specification,
        artifacts,
    )

    assert metric.score == 0
    assert metric.status == "fail"


def test_generic_duplicate_questions_are_penalized():
    artifacts = make_safe_artifacts()

    artifacts.open_questions = [
        (
            "What should happen after any user action "
            "whose outcome is not explicitly defined?"
        ),
        (
            "What should happen after any user action "
            "whose outcome is not explicitly defined?"
        ),
    ]

    metric = evaluate_open_question_quality(
        artifacts
    )

    assert metric.score < 80
    assert metric.status != "pass"


def test_missing_feature_reduces_requirement_coverage():
    specification = make_specification()

    data = specification.model_dump()

    data["features"].append(
        {
            "name": "Export Reports",
            "description": (
                "Users can export a report of search results."
            ),
            "priority": "medium",
        }
    )

    specification = ProjectSpecification.model_validate(
        data
    )

    artifacts = make_safe_artifacts()

    metric = evaluate_requirement_coverage(
        specification,
        artifacts,
    )

    assert metric.score < 100
    assert metric.status in {
        "partial",
        "fail",
    }