from app.services.requirement_service import generate_specification
from app.services.engineering_service import generate_engineering_artifacts
from app.services.evaluation_service import evaluate_reliability


client_requirement = """
Build a simple task list.

Users can enter a task title and press an Add Task button.

If the task title is empty, display:
"Task title is required."

If the task title contains text, add that task to the visible task list.

Each visible task must have a Delete button.

When Delete is pressed for a task, remove that task from the visible list.

Do not assume any database, API, authentication, cloud storage,
framework, notification system, user accounts, or external integration.
"""


print("\nGenerating specification...\n")

specification = generate_specification(
    client_requirement
)

print("SPECIFICATION GENERATED")


print("\nGenerating engineering artifacts...\n")

artifacts = generate_engineering_artifacts(
    specification
)

print("ENGINEERING ARTIFACTS GENERATED")


print("\nRunning Day 4 reliability evaluation...\n")

report = evaluate_reliability(
    specification,
    artifacts,
)

print(
    report.model_dump_json(
        indent=2
    )
)