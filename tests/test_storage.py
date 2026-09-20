from app.storage.sqlite_store import (
    create_project,
    save_input,
    create_generation_run,
    save_artifact,
    update_artifact_review,
    get_project_history,
)


def test_project_persistence_flow():
    project = create_project(
        name="Persistence Test Project",
        description="Testing local project history.",
        tech_stack=["Python", "Streamlit"],
    )

    assert project["name"] == "Persistence Test Project"
    assert project["description"] == "Testing local project history."
    assert "Python" in project["tech_stack"]

    saved_input = save_input(
        project_id=project["project_id"],
        input_type="text",
        source_text="Build a simple task manager.",
    )

    assert saved_input["project_id"] == project["project_id"]
    assert saved_input["input_type"] == "text"

    run = create_generation_run(
        project_id=project["project_id"],
        model_name="qwen3:1.7b",
        prompt_version="v2",
        status="completed",
    )

    assert run["project_id"] == project["project_id"]
    assert run["model_name"] == "qwen3:1.7b"

    artifact = save_artifact(
        run_id=run["run_id"],
        artifact_type="specification",
        content={
            "project_summary": "Simple task manager."
        },
        review_status="draft",
    )

    assert artifact["review_status"] == "draft"

    updated = update_artifact_review(
        artifact_id=artifact["artifact_id"],
        review_status="approved",
        reviewer_note="Approved in persistence test.",
    )

    assert updated["review_status"] == "approved"

    history = get_project_history(
        project["project_id"]
    )

    assert history["project"]["project_id"] == project["project_id"]
    assert len(history["inputs"]) >= 1
    assert len(history["generation_runs"]) >= 1
    assert len(history["artifacts"]) >= 1
    assert history["artifacts"][0]["review_status"] == "approved"