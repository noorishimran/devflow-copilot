from typing import Literal

from pydantic import BaseModel, Field


class AcceptanceCriterion(BaseModel):
    id: str = Field(..., min_length=1)
    feature: str = Field(..., min_length=1)
    given: str = Field(..., min_length=1)
    when: str = Field(..., min_length=1)
    then: str = Field(..., min_length=1)


class ImplementationStep(BaseModel):
    step_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    files_or_components: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class QATestCase(BaseModel):
    test_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    test_type: Literal[
        "functional",
        "validation",
        "negative",
        "integration",
        "ui",
    ]
    preconditions: list[str] = Field(default_factory=list)
    steps: list[str] = Field(..., min_length=1)
    expected_result: str = Field(..., min_length=1)


class DeveloperPrompt(BaseModel):
    objective: str = Field(..., min_length=1)
    implementation_instructions: list[str] = Field(..., min_length=1)
    constraints: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class EngineeringArtifacts(BaseModel):
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    implementation_plan: list[ImplementationStep] = Field(default_factory=list)
    qa_test_cases: list[QATestCase] = Field(default_factory=list)
    developer_prompt: DeveloperPrompt
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)