from enum import Enum

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_EDIT = "needs_edit"


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    REGENERATE = "regenerate"


class ArtifactReview(BaseModel):
    status: ReviewStatus = ReviewStatus.DRAFT
    reviewer_notes: str = ""
    action_history: list[str] = Field(default_factory=list)


class ReviewResult(BaseModel):
    previous_status: ReviewStatus
    current_status: ReviewStatus
    action: ReviewAction
    message: str
    reviewer_notes: str = ""