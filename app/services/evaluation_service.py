import re

from app.schemas.engineering import EngineeringArtifacts
from app.schemas.evaluation import (
    EvaluationMetric,
    ReliabilityReport,
)
from app.schemas.specification import ProjectSpecification
from app.services.engineering_service import (
    EvidenceFidelityError,
    validate_evidence_fidelity,
)


STOP_WORDS = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "from",
    "into",
    "when",
    "where",
    "what",
    "should",
    "user",
    "users",
    "must",
    "have",
    "will",
    "can",
    "for",
    "are",
    "was",
    "were",
    "then",
    "each",
    "only",
    "using",
}


def normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.lower().strip(),
    )


def extract_keywords(text: str) -> set[str]:
    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if len(word) >= 4
        and word not in STOP_WORDS
    }


def engineering_text(
    artifacts: EngineeringArtifacts
) -> str:
    parts = []

    for criterion in artifacts.acceptance_criteria:
        parts.extend(
            [
                criterion.feature,
                criterion.given,
                criterion.when,
                criterion.then,
            ]
        )

    for step in artifacts.implementation_plan:
        parts.extend(
            [
                step.title,
                step.description,
                *step.files_or_components,
                *step.dependencies,
            ]
        )

    for test_case in artifacts.qa_test_cases:
        parts.extend(
            [
                test_case.title,
                *test_case.preconditions,
                *test_case.steps,
                test_case.expected_result,
            ]
        )

    parts.append(
        artifacts.developer_prompt.objective
    )

    parts.extend(
        artifacts.developer_prompt.implementation_instructions
    )

    return normalize_text(
        " ".join(parts)
    )


def evaluate_schema_validity() -> EvaluationMetric:
    return EvaluationMetric(
        name="schema_validity",
        score=100,
        status="pass",
        findings=[
            (
                "Project specification and engineering artifacts "
                "were successfully validated by Pydantic schemas."
            )
        ],
    )


def evaluate_evidence_fidelity(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts,
) -> EvaluationMetric:

    try:
        validate_evidence_fidelity(
            specification,
            artifacts,
        )

        return EvaluationMetric(
            name="evidence_fidelity",
            score=100,
            status="pass",
            findings=[
                (
                    "No unsupported high-risk engineering behavior "
                    "was detected by the evidence-fidelity guard."
                )
            ],
        )

    except EvidenceFidelityError as exc:
        return EvaluationMetric(
            name="evidence_fidelity",
            score=0,
            status="fail",
            findings=[
                str(exc)
            ],
        )


def evaluate_requirement_coverage(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts,
) -> EvaluationMetric:

    artifact_text = engineering_text(
        artifacts
    )

    if not specification.features:
        return EvaluationMetric(
            name="requirement_coverage",
            score=100,
            status="pass",
            findings=[
                "No specification features were supplied."
            ],
        )

    feature_scores = []
    missing_features = []

    for feature in specification.features:
        feature_text = (
            feature.name
            + " "
            + feature.description
        )

        keywords = extract_keywords(
            feature_text
        )

        if not keywords:
            feature_scores.append(100)
            continue

        matched = sum(
            1
            for keyword in keywords
            if keyword in artifact_text
        )

        score = round(
            (matched / len(keywords)) * 100
        )

        feature_scores.append(
            score
        )

        if score < 60:
            missing_features.append(
                feature.name
            )

    average_score = round(
        sum(feature_scores)
        / len(feature_scores)
    )

    if average_score >= 80:
        status = "pass"

    elif average_score >= 50:
        status = "partial"

    else:
        status = "fail"

    findings = [
        (
            f"Average deterministic feature coverage: "
            f"{average_score}%."
        )
    ]

    if missing_features:
        findings.append(
            "Low-coverage features: "
            + ", ".join(missing_features)
        )

    return EvaluationMetric(
        name="requirement_coverage",
        score=average_score,
        status=status,
        findings=findings,
    )


def evaluate_open_question_quality(
    artifacts: EngineeringArtifacts,
) -> EvaluationMetric:

    questions = [
        normalize_text(question)
        for question in artifacts.open_questions
    ]

    if not questions:
        return EvaluationMetric(
            name="open_question_quality",
            score=100,
            status="pass",
            findings=[
                "No open questions were generated."
            ],
        )

    unique_questions = set(
        questions
    )

    duplicate_count = (
        len(questions)
        - len(unique_questions)
    )

    generic_phrases = [
        (
            "what should happen after any user action "
            "whose outcome is not explicitly defined"
        ),
        "what should happen after this action",
    ]

    generic_count = 0

    for question in questions:
        if any(
            phrase in question
            for phrase in generic_phrases
        ):
            generic_count += 1

    penalty = (
        duplicate_count * 25
        + generic_count * 20
    )

    score = max(
        0,
        100 - penalty
    )

    if score >= 80:
        status = "pass"

    elif score >= 50:
        status = "partial"

    else:
        status = "fail"

    findings = []

    if duplicate_count:
        findings.append(
            f"{duplicate_count} duplicate open question(s) detected."
        )

    if generic_count:
        findings.append(
            f"{generic_count} overly generic open question(s) detected."
        )

    if not findings:
        findings.append(
            "Open questions are unique and sufficiently specific."
        )

    return EvaluationMetric(
        name="open_question_quality",
        score=score,
        status=status,
        findings=findings,
    )


def evaluate_traceability(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts,
) -> EvaluationMetric:

    artifact_text = engineering_text(
        artifacts
    )

    if not specification.features:
        return EvaluationMetric(
            name="traceability",
            score=100,
            status="pass",
            findings=[
                "No specification features required traceability."
            ],
        )

    traced = 0
    untraced = []

    for feature in specification.features:
        feature_name = normalize_text(
            feature.name
        )

        if feature_name in artifact_text:
            traced += 1

        else:
            untraced.append(
                feature.name
            )

    score = round(
        (
            traced
            / len(specification.features)
        )
        * 100
    )

    if score >= 80:
        status = "pass"

    elif score >= 50:
        status = "partial"

    else:
        status = "fail"

    findings = [
        (
            f"{traced} of "
            f"{len(specification.features)} "
            "features were directly traceable by feature name."
        )
    ]

    if untraced:
        findings.append(
            "Untraced features: "
            + ", ".join(untraced)
        )

    return EvaluationMetric(
        name="traceability",
        score=score,
        status=status,
        findings=findings,
    )


def evaluate_reliability(
    specification: ProjectSpecification,
    artifacts: EngineeringArtifacts,
) -> ReliabilityReport:

    if specification is None:
        raise ValueError(
            "Specification is required."
        )

    if artifacts is None:
        raise ValueError(
            "Engineering artifacts are required."
        )

    metrics = [
        evaluate_schema_validity(),
        evaluate_evidence_fidelity(
            specification,
            artifacts,
        ),
        evaluate_requirement_coverage(
            specification,
            artifacts,
        ),
        evaluate_open_question_quality(
            artifacts,
        ),
        evaluate_traceability(
            specification,
            artifacts,
        ),
    ]

    overall_score = round(
        sum(
            metric.score
            for metric in metrics
        )
        / len(metrics)
    )

    if overall_score >= 80:
        overall_status = "pass"

    elif overall_score >= 50:
        overall_status = "partial"

    else:
        overall_status = "fail"

    detected_issues = []
    regression_flags = []

    for metric in metrics:
        if metric.status != "pass":
            detected_issues.extend(
                metric.findings
            )

        if metric.status == "fail":
            regression_flags.append(
                metric.name
            )

    return ReliabilityReport(
        overall_score=overall_score,
        overall_status=overall_status,
        metrics=metrics,
        detected_issues=detected_issues,
        regression_flags=regression_flags,
        human_review_required=True,
    )