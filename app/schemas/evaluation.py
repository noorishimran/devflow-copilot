from typing import Literal

from pydantic import BaseModel, Field


class EvaluationMetric(BaseModel):
    name: Literal[
        "schema_validity",
        "evidence_fidelity",
        "requirement_coverage",
        "open_question_quality",
        "traceability",
    ]

    score: int = Field(
        ...,
        ge=0,
        le=100,
    )

    status: Literal[
        "pass",
        "partial",
        "fail",
    ]

    findings: list[str] = Field(
        default_factory=list
    )


class ReliabilityReport(BaseModel):
    overall_score: int = Field(
        ...,
        ge=0,
        le=100,
    )

    overall_status: Literal[
        "pass",
        "partial",
        "fail",
    ]

    metrics: list[EvaluationMetric] = Field(
        default_factory=list
    )

    detected_issues: list[str] = Field(
        default_factory=list
    )

    regression_flags: list[str] = Field(
        default_factory=list
    )

    human_review_required: bool = True