from app.schemas.review import (
    ArtifactReview,
    ReviewAction,
    ReviewResult,
    ReviewStatus,
)


def apply_review_action(
    review: ArtifactReview,
    action: ReviewAction,
    reviewer_notes: str = "",
) -> tuple[ArtifactReview, ReviewResult]:

    if review is None:
        raise ValueError("Review state is required.")

    previous_status = review.status

    if action == ReviewAction.APPROVE:
        new_status = ReviewStatus.APPROVED
        message = "Engineering artifacts approved for use."

    elif action == ReviewAction.REJECT:
        new_status = ReviewStatus.REJECTED
        message = "Engineering artifacts rejected by reviewer."

    elif action == ReviewAction.EDIT:
        new_status = ReviewStatus.NEEDS_EDIT
        message = "Engineering artifacts marked for editing."

    elif action == ReviewAction.REGENERATE:
        new_status = ReviewStatus.DRAFT
        message = "Engineering artifacts marked for regeneration."

    else:
        raise ValueError(
            f"Unsupported review action: {action}"
        )

    history_entry = (
        f"{action.value}: "
        f"{previous_status.value} -> {new_status.value}"
    )

    updated_history = [
        *review.action_history,
        history_entry,
    ]

    updated_review = ArtifactReview(
        status=new_status,
        reviewer_notes=reviewer_notes.strip(),
        action_history=updated_history,
    )

    result = ReviewResult(
        previous_status=previous_status,
        current_status=new_status,
        action=action,
        message=message,
        reviewer_notes=reviewer_notes.strip(),
    )

    return updated_review, result