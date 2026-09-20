import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "devflow.db"


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def get_connection():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                tech_stack TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS input_documents (
                input_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                input_type TEXT NOT NULL,
                source_text TEXT,
                file_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id)
                    REFERENCES projects(project_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS generation_runs (
                run_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id)
                    REFERENCES projects(project_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                content_json TEXT NOT NULL,
                review_status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id)
                    REFERENCES generation_runs(run_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS review_feedback (
                feedback_id TEXT PRIMARY KEY,
                artifact_id TEXT NOT NULL,
                reviewer_note TEXT NOT NULL DEFAULT '',
                label TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(artifact_id)
                    REFERENCES artifacts(artifact_id)
                    ON DELETE CASCADE
            );
            """
        )


def create_project(
    name: str,
    description: str = "",
    tech_stack: list[str] | None = None,
) -> dict:

    project_id = str(
        uuid.uuid4()
    )

    created_at = utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO projects (
                project_id,
                name,
                description,
                tech_stack,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_id,
                name,
                description,
                json.dumps(
                    tech_stack or []
                ),
                created_at,
            ),
        )

    return get_project(
        project_id
    )


def get_project(
    project_id: str,
) -> dict | None:

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM projects
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()

    if row is None:
        return None

    result = dict(row)

    result["tech_stack"] = json.loads(
        result["tech_stack"] or "[]"
    )

    return result


def list_projects() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM projects
            ORDER BY created_at DESC
            """
        ).fetchall()

    projects = []

    for row in rows:
        item = dict(row)

        item["tech_stack"] = json.loads(
            item["tech_stack"] or "[]"
        )

        projects.append(item)

    return projects


def save_input(
    project_id: str,
    input_type: str,
    source_text: str = "",
    file_path: str = "",
) -> dict:

    input_id = str(
        uuid.uuid4()
    )

    created_at = utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO input_documents (
                input_id,
                project_id,
                input_type,
                source_text,
                file_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                input_id,
                project_id,
                input_type,
                source_text,
                file_path,
                created_at,
            ),
        )

    return {
        "input_id": input_id,
        "project_id": project_id,
        "input_type": input_type,
        "source_text": source_text,
        "file_path": file_path,
        "created_at": created_at,
    }


def create_generation_run(
    project_id: str,
    model_name: str,
    prompt_version: str,
    status: str = "completed",
) -> dict:

    run_id = str(
        uuid.uuid4()
    )

    created_at = utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO generation_runs (
                run_id,
                project_id,
                model_name,
                prompt_version,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                project_id,
                model_name,
                prompt_version,
                status,
                created_at,
            ),
        )

    return {
        "run_id": run_id,
        "project_id": project_id,
        "model_name": model_name,
        "prompt_version": prompt_version,
        "status": status,
        "created_at": created_at,
    }


def save_artifact(
    run_id: str,
    artifact_type: str,
    content: dict,
    review_status: str = "draft",
) -> dict:

    artifact_id = str(
        uuid.uuid4()
    )

    created_at = utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO artifacts (
                artifact_id,
                run_id,
                artifact_type,
                content_json,
                review_status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                artifact_id,
                run_id,
                artifact_type,
                json.dumps(
                    content,
                    ensure_ascii=False,
                ),
                review_status,
                created_at,
            ),
        )

    return {
        "artifact_id": artifact_id,
        "run_id": run_id,
        "artifact_type": artifact_type,
        "content": content,
        "review_status": review_status,
        "created_at": created_at,
    }


def update_artifact_review(
    artifact_id: str,
    review_status: str,
    reviewer_note: str = "",
) -> dict:

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT *
            FROM artifacts
            WHERE artifact_id = ?
            """,
            (artifact_id,),
        ).fetchone()

        if existing is None:
            raise ValueError(
                "Artifact not found."
            )

        connection.execute(
            """
            UPDATE artifacts
            SET review_status = ?
            WHERE artifact_id = ?
            """,
            (
                review_status,
                artifact_id,
            ),
        )

        feedback_id = str(
            uuid.uuid4()
        )

        connection.execute(
            """
            INSERT INTO review_feedback (
                feedback_id,
                artifact_id,
                reviewer_note,
                label,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                feedback_id,
                artifact_id,
                reviewer_note,
                review_status,
                utc_now(),
            ),
        )

        row = connection.execute(
            """
            SELECT *
            FROM artifacts
            WHERE artifact_id = ?
            """,
            (artifact_id,),
        ).fetchone()

    result = dict(row)

    result["content"] = json.loads(
        result.pop("content_json")
    )

    return result

def get_project_history(
    project_id: str,
) -> dict:

    project = get_project(
        project_id
    )

    if project is None:
        raise ValueError(
            "Project not found."
        )

    with get_connection() as connection:
        inputs = [
            dict(row)
            for row in connection.execute(
                """
                SELECT *
                FROM input_documents
                WHERE project_id = ?
                ORDER BY created_at ASC
                """,
                (project_id,),
            ).fetchall()
        ]

        runs = [
            dict(row)
            for row in connection.execute(
                """
                SELECT *
                FROM generation_runs
                WHERE project_id = ?
                ORDER BY created_at ASC
                """,
                (project_id,),
            ).fetchall()
        ]

        artifacts = [
            dict(row)
            for row in connection.execute(
                """
                SELECT a.*
                FROM artifacts a
                JOIN generation_runs r
                    ON a.run_id = r.run_id
                WHERE r.project_id = ?
                ORDER BY a.created_at ASC
                """,
                (project_id,),
            ).fetchall()
        ]

        review_feedback = [
            dict(row)
            for row in connection.execute(
                """
                SELECT rf.*
                FROM review_feedback rf
                JOIN artifacts a
                    ON rf.artifact_id = a.artifact_id
                JOIN generation_runs r
                    ON a.run_id = r.run_id
                WHERE r.project_id = ?
                ORDER BY rf.created_at ASC
                """,
                (project_id,),
            ).fetchall()
        ]

    for artifact in artifacts:
        artifact["content"] = json.loads(
            artifact.pop(
                "content_json"
            )
        )

    return {
        "project": project,
        "inputs": inputs,
        "generation_runs": runs,
        "artifacts": artifacts,
        "review_feedback": review_feedback,
    }


init_db()