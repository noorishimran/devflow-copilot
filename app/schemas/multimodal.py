from typing import Literal

from pydantic import BaseModel, Field


class UIComponent(BaseModel):
    component_type: str = Field(..., min_length=1)
    label: str = ""
    visible_text: str = ""
    state: str = ""
    evidence: str = Field(..., min_length=1)


class ImageEvidence(BaseModel):
    observed_components: list[UIComponent] = Field(default_factory=list)

    visible_states: list[str] = Field(default_factory=list)

    possible_interactions: list[str] = Field(default_factory=list)

    observed_facts: list[str] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)

    open_questions: list[str] = Field(default_factory=list)


class NormalizedRequirementContext(BaseModel):
    source_mode: Literal[
        "text_only",
        "image_only",
        "combined",
    ]

    client_text: str = ""

    image_evidence: ImageEvidence | None = None

    observed_evidence: list[str] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)

    open_questions: list[str] = Field(default_factory=list)