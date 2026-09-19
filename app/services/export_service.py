import json

from app.schemas.specification import ProjectSpecification
from app.schemas.engineering import EngineeringArtifacts
from app.schemas.evaluation import ReliabilityReport
from app.schemas.review import ArtifactReview


def build_export_payload(
    specification: ProjectSpecification,
    engineering_artifacts: EngineeringArtifacts,
    reliability_report: ReliabilityReport,
    review: ArtifactReview,
) -> dict:
    """
    Build one complete exportable project package.
    """

    return {
        "specification": specification.model_dump(),
        "engineering_artifacts": engineering_artifacts.model_dump(),
        "reliability_report": reliability_report.model_dump(),
        "human_review": review.model_dump(),
    }


def export_as_json(
    specification: ProjectSpecification,
    engineering_artifacts: EngineeringArtifacts,
    reliability_report: ReliabilityReport,
    review: ArtifactReview,
) -> str:
    payload = build_export_payload(
        specification,
        engineering_artifacts,
        reliability_report,
        review,
    )

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )


def export_as_markdown(
    specification: ProjectSpecification,
    engineering_artifacts: EngineeringArtifacts,
    reliability_report: ReliabilityReport,
    review: ArtifactReview,
) -> str:

    lines = [
        "# DevFlow Copilot — Engineering Package",
        "",
        "## Project Summary",
        "",
        specification.project_summary,
        "",
        "## Features",
        "",
    ]

    for feature in specification.features:
        lines.extend(
            [
                f"### {feature.name}",
                "",
                f"- Priority: {feature.priority}",
                f"- Description: {feature.description}",
                "",
            ]
        )

    lines.extend(
        [
            "## Acceptance Criteria",
            "",
        ]
    )

    for criterion in engineering_artifacts.acceptance_criteria:
        lines.extend(
            [
                f"### {criterion.id} — {criterion.feature}",
                "",
                f"- Given: {criterion.given}",
                f"- When: {criterion.when}",
                f"- Then: {criterion.then}",
                "",
            ]
        )

    lines.extend(
        [
            "## Implementation Plan",
            "",
        ]
    )

    for step in engineering_artifacts.implementation_plan:
        lines.extend(
            [
                f"### Step {step.step_number}: {step.title}",
                "",
                step.description,
                "",
            ]
        )

    lines.extend(
        [
            "## QA Test Cases",
            "",
        ]
    )

    for test_case in engineering_artifacts.qa_test_cases:
        lines.extend(
            [
                f"### {test_case.test_id} — {test_case.title}",
                "",
                f"- Type: {test_case.test_type}",
                "- Steps:",
            ]
        )

        for step in test_case.steps:
            lines.append(f"  - {step}")

        lines.extend(
            [
                f"- Expected Result: {test_case.expected_result}",
                "",
            ]
        )

    lines.extend(
        [
            "## Reliability Evaluation",
            "",
            f"- Overall Score: {reliability_report.overall_score}/100",
            f"- Overall Status: {reliability_report.overall_status}",
            f"- Human Review Required: {reliability_report.human_review_required}",
            "",
        ]
    )

    for metric in reliability_report.metrics:
        lines.extend(
            [
                f"### {metric.name}",
                "",
                f"- Score: {metric.score}/100",
                f"- Status: {metric.status}",
                "",
            ]
        )

    lines.extend(
        [
            "## Human Review",
            "",
            f"- Status: {review.status}",
            f"- Reviewer Notes: {review.reviewer_notes or 'None'}",
            "",
        ]
    )

    if review.action_history:
        lines.append("### Review History")
        lines.append("")

        for item in review.action_history:
            lines.append(f"- {item}")

        lines.append("")

    lines.extend(
        [
            "## Open Questions",
            "",
        ]
    )

    open_questions = list(
        dict.fromkeys(
            specification.open_questions
            + engineering_artifacts.open_questions
        )
    )

    if open_questions:
        for question in open_questions:
            lines.append(f"- {question}")
    else:
        lines.append("- None")

    return "\n".join(lines)