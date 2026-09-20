from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.models.ollama_client import MODEL_NAME

from app.schemas.specification import ProjectSpecification
from app.schemas.engineering import EngineeringArtifacts
from app.schemas.evaluation import ReliabilityReport

from app.services.requirement_service import generate_specification
from app.services.engineering_service import generate_engineering_artifacts
from app.services.evaluation_service import evaluate_reliability

from app.storage.sqlite_store import (
    create_project,
    get_project,
    list_projects,
    get_project_history,
    save_input,
    create_generation_run,
    save_artifact,
    update_artifact_review,
)


app = FastAPI(
    title="MoinSystems AI — DevFlow Copilot API",
    version="1.0.0",
    description=(
        "Local-first FastAPI service boundary for "
        "DevFlow Copilot."
    ),
)


class RequirementGenerationRequest(BaseModel):
    requirement: str = Field(
        ...,
        min_length=1,
    )
    prompt_version: Literal["v1", "v2"] = "v2"


class ReliabilityRequest(BaseModel):
    specification: ProjectSpecification
    engineering_artifacts: EngineeringArtifacts


class ProjectCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
    )
    description: str = ""

    tech_stack: list[str] = Field(
        default_factory=list
    )


class ArtifactReviewRequest(BaseModel):
    status: Literal[
        "approved",
        "needs_edit",
        "rejected",
    ]
    reviewer_note: str = ""


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "devflow-copilot",
        "runtime": "local-first",
    }


# ---------------------------------------------------------
# Project endpoints
# ---------------------------------------------------------


@app.post("/api/v1/projects")
def create_project_endpoint(
    request: ProjectCreateRequest,
):
    return create_project(
        name=request.name,
        description=request.description,
        tech_stack=request.tech_stack,
    )


@app.get("/api/v1/projects")
def list_projects_endpoint():
    return list_projects()


@app.get("/api/v1/projects/{project_id}")
def get_project_endpoint(
    project_id: str,
):
    project = get_project(
        project_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return project


@app.get(
    "/api/v1/projects/{project_id}/history"
)
def get_project_history_endpoint(
    project_id: str,
):
    try:
        return get_project_history(
            project_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        ) from exc


# ---------------------------------------------------------
# Project-linked generation endpoint
# ---------------------------------------------------------


@app.post(
    "/api/v1/projects/"
    "{project_id}/specifications/generate"
)
def generate_project_specification_endpoint(
    project_id: str,
    request: RequirementGenerationRequest,
):
    project = get_project(
        project_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    # Preserve the raw source requirement before generation.
    saved_input = save_input(
        project_id=project_id,
        input_type="text",
        source_text=request.requirement,
    )

    # Generate the validated specification.
    specification = generate_specification(
        request.requirement,
        prompt_version=request.prompt_version,
    )

    # Record the model + prompt version used.
    generation_run = create_generation_run(
        project_id=project_id,
        model_name=MODEL_NAME,
        prompt_version=request.prompt_version,
        status="completed",
    )

    # Store generated output as a draft artifact.
    artifact = save_artifact(
        run_id=generation_run["run_id"],
        artifact_type="specification",
        content=specification.model_dump(),
        review_status="draft",
    )

    return {
        "project_id": project_id,
        "input": saved_input,
        "generation_run": generation_run,
        "artifact": artifact,
        "specification": (
            specification.model_dump()
        ),
    }


# ---------------------------------------------------------
# Artifact review endpoint
# ---------------------------------------------------------


@app.post(
    "/api/v1/artifacts/{artifact_id}/review"
)
def review_artifact_endpoint(
    artifact_id: str,
    request: ArtifactReviewRequest,
):
    try:
        return update_artifact_review(
            artifact_id=artifact_id,
            review_status=request.status,
            reviewer_note=request.reviewer_note,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Artifact not found.",
        ) from exc


# ---------------------------------------------------------
# Existing standalone generation endpoints
# ---------------------------------------------------------


@app.post(
    "/api/v1/specifications/generate",
    response_model=ProjectSpecification,
)
def generate_specification_endpoint(
    request: RequirementGenerationRequest,
):
    return generate_specification(
        request.requirement,
        prompt_version=request.prompt_version,
    )


@app.post(
    "/api/v1/engineering/generate",
    response_model=EngineeringArtifacts,
)
def generate_engineering_endpoint(
    specification: ProjectSpecification,
):
    return generate_engineering_artifacts(
        specification
    )


@app.post(
    "/api/v1/reliability/evaluate",
    response_model=ReliabilityReport,
)
def evaluate_reliability_endpoint(
    request: ReliabilityRequest,
):
    return evaluate_reliability(
        request.specification,
        request.engineering_artifacts,
    )
