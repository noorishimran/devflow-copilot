import pytest
from pydantic import ValidationError

from app.schemas.specification import (
    Feature,
    UserStory,
    ProjectSpecification,
)


def test_valid_project_specification():

    specification = ProjectSpecification(
        project_summary="Simple task management application.",
        features=[
            Feature(
                name="Create Task",
                description="Users can create tasks.",
                priority="high",
            )
        ],
        user_stories=[
            UserStory(
                role="user",
                goal="create a task",
                benefit="I can keep track of my work",
            )
        ],
        assumptions=[],
        open_questions=[],
    )

    assert specification.project_summary
    assert len(specification.features) == 1
    assert specification.features[0].priority == "high"


def test_invalid_priority_rejected():

    with pytest.raises(ValidationError):

        Feature(
            name="Create Task",
            description="Users can create tasks.",
            priority="urgent",
        )