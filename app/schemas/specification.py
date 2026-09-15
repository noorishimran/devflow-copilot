from typing import Literal

from pydantic import BaseModel, Field


class Feature(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: Literal["high", "medium", "low"] = "medium"


class UserStory(BaseModel):
    role: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    benefit: str = Field(..., min_length=1)


class ProjectSpecification(BaseModel):
    project_summary: str = Field(..., min_length=1)
    features: list[Feature]
    user_stories: list[UserStory]
    assumptions: list[str]
    open_questions: list[str]
