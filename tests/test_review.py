from app.schemas.review import (
    ArtifactReview,
    ReviewAction,
    ReviewStatus,
)
from app.services.review_service import apply_review_action


def test_approve_review():
    review = ArtifactReview()

    updated_review, result = apply_review_action(
        review,
        ReviewAction.APPROVE,
        "Reviewed and approved.",
    )

    assert updated_review.status == ReviewStatus.APPROVED
    assert result.current_status == ReviewStatus.APPROVED
    assert updated_review.reviewer_notes == "Reviewed and approved."
    assert len(updated_review.action_history) == 1


def test_reject_review():
    review = ArtifactReview()

    updated_review, result = apply_review_action(
        review,
        ReviewAction.REJECT,
        "Requirements need correction.",
    )

    assert updated_review.status == ReviewStatus.REJECTED
    assert result.current_status == ReviewStatus.REJECTED
    assert "reject" in updated_review.action_history[0]


def test_mark_review_for_edit():
    review = ArtifactReview()

    updated_review, result = apply_review_action(
        review,
        ReviewAction.EDIT,
        "Update the QA cases.",
    )

    assert updated_review.status == ReviewStatus.NEEDS_EDIT
    assert result.current_status == ReviewStatus.NEEDS_EDIT


def test_regenerate_returns_to_draft():
    review = ArtifactReview(
        status=ReviewStatus.REJECTED,
        action_history=[
            "reject: draft -> rejected"
        ],
    )

    updated_review, result = apply_review_action(
        review,
        ReviewAction.REGENERATE,
        "Generate a cleaner version.",
    )

    assert updated_review.status == ReviewStatus.DRAFT
    assert result.previous_status == ReviewStatus.REJECTED
    assert result.current_status == ReviewStatus.DRAFT
    assert len(updated_review.action_history) == 2