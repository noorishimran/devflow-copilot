from fastapi.testclient import TestClient

from app.api.main import app
from app.storage import sqlite_store


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "devflow-copilot"
    assert data["runtime"] == "local-first"


def test_docs_available():
    response = client.get("/docs")

    assert response.status_code == 200


def test_project_api_persistence_flow(
    monkeypatch,
    tmp_path,
):
    test_db = tmp_path / "test_devflow.db"

    monkeypatch.setattr(
        sqlite_store,
        "DB_PATH",
        test_db,
    )

    sqlite_store.init_db()

    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "API Test Project",
            "description": "Testing project API.",
            "tech_stack": [
                "Python",
                "FastAPI",
            ],
        },
    )

    assert create_response.status_code == 200

    project = create_response.json()

    assert project["name"] == "API Test Project"
    assert "Python" in project["tech_stack"]

    project_id = project["project_id"]

    get_response = client.get(
        f"/api/v1/projects/{project_id}"
    )

    assert get_response.status_code == 200
    assert (
        get_response.json()["project_id"]
        == project_id
    )

    list_response = client.get(
        "/api/v1/projects"
    )

    assert list_response.status_code == 200

    project_ids = [
        item["project_id"]
        for item in list_response.json()
    ]

    assert project_id in project_ids

    history_response = client.get(
        f"/api/v1/projects/{project_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert (
        history["project"]["project_id"]
        == project_id
    )
    assert history["inputs"] == []
    assert history["generation_runs"] == []
    assert history["artifacts"] == []


def test_missing_project_returns_404(
    monkeypatch,
    tmp_path,
):
    test_db = tmp_path / "missing_project.db"

    monkeypatch.setattr(
        sqlite_store,
        "DB_PATH",
        test_db,
    )

    sqlite_store.init_db()

    response = client.get(
        "/api/v1/projects/not-a-real-project"
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Project not found."
    )


def test_project_generation_is_saved_to_history(
    monkeypatch,
    tmp_path,
):
    from app.api import main as api_main
    from app.schemas.specification import (
        ProjectSpecification,
    )

    test_db = tmp_path / "traceability.db"

    monkeypatch.setattr(
        sqlite_store,
        "DB_PATH",
        test_db,
    )

    sqlite_store.init_db()

    fake_specification = (
        ProjectSpecification.model_validate(
            {
                "project_summary": (
                    "A simple task manager."
                ),
                "features": [
                    {
                        "name": "Add Task",
                        "description": (
                            "Users can add tasks."
                        ),
                        "priority": "high",
                    }
                ],
                "user_stories": [
                    {
                        "role": "User",
                        "goal": "Add a task",
                        "benefit": "Track work",
                    }
                ],
                "assumptions": [],
                "open_questions": [],
            }
        )
    )

    def fake_generate_specification(
        requirement,
        prompt_version="v2",
    ):
        return fake_specification

    monkeypatch.setattr(
        api_main,
        "generate_specification",
        fake_generate_specification,
    )

    project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Traceability Project",
            "description": (
                "Tests generation history."
            ),
            "tech_stack": ["Python"],
        },
    )

    assert project_response.status_code == 200

    project_id = (
        project_response.json()["project_id"]
    )

    generation_response = client.post(
        (
            f"/api/v1/projects/{project_id}"
            "/specifications/generate"
        ),
        json={
            "requirement": (
                "Build a task manager."
            ),
            "prompt_version": "v2",
        },
    )

    assert generation_response.status_code == 200

    generated = generation_response.json()

    assert (
        generated["project_id"]
        == project_id
    )

    assert (
        generated["generation_run"]
        ["prompt_version"]
        == "v2"
    )

    assert (
        generated["artifact"]
        ["review_status"]
        == "draft"
    )

    history_response = client.get(
        f"/api/v1/projects/{project_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history["inputs"]) == 1
    assert len(history["generation_runs"]) == 1
    assert len(history["artifacts"]) == 1

    assert (
        history["inputs"][0]["source_text"]
        == "Build a task manager."
    )

    assert (
        history["generation_runs"][0]
        ["prompt_version"]
        == "v2"
    )

    assert (
        history["artifacts"][0]
        ["artifact_type"]
        == "specification"
    )

    assert (
        history["artifacts"][0]
        ["review_status"]
        == "draft"
    )


def test_artifact_review_endpoint_updates_status(
    monkeypatch,
    tmp_path,
):
    test_db = tmp_path / "review_api.db"

    monkeypatch.setattr(
        sqlite_store,
        "DB_PATH",
        test_db,
    )

    sqlite_store.init_db()

    project = sqlite_store.create_project(
        name="Review API Project",
        description="Testing artifact review.",
        tech_stack=["Python"],
    )

    generation_run = (
        sqlite_store.create_generation_run(
            project_id=project["project_id"],
            model_name="qwen3:1.7b",
            prompt_version="v2",
            status="completed",
        )
    )

    artifact = sqlite_store.save_artifact(
        run_id=generation_run["run_id"],
        artifact_type="specification",
        content={
            "project_summary": "Test project."
        },
        review_status="draft",
    )

    response = client.post(
        (
            f"/api/v1/artifacts/"
            f"{artifact['artifact_id']}/review"
        ),
        json={
            "status": "approved",
            "reviewer_note": (
                "Reviewed and approved."
            ),
        },
    )

    assert response.status_code == 200

    reviewed = response.json()

    assert (
        reviewed["artifact_id"]
        == artifact["artifact_id"]
    )

    assert (
        reviewed["review_status"]
        == "approved"
    )

    history = sqlite_store.get_project_history(
        project["project_id"]
    )

    assert (
        history["artifacts"][0]
        ["review_status"]
        == "approved"
    )

    assert len(history["review_feedback"]) == 1

    assert (
        history["review_feedback"][0]
        ["artifact_id"]
        == artifact["artifact_id"]
    )

    assert (
        history["review_feedback"][0]
        ["label"]
        == "approved"
    )

    assert (
        history["review_feedback"][0]
        ["reviewer_note"]
        == "Reviewed and approved."
    )
