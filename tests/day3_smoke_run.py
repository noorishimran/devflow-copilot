from app.services.requirement_service import generate_specification
from app.services.engineering_service import generate_engineering_artifacts


client_requirement = """
Build a simple login page where users can enter their email and password
and press a Login button. If required information is missing, do not invent it.
"""


print("\nGenerating validated specification...\n")

specification = generate_specification(
    client_requirement
)

print("SPECIFICATION GENERATED")
print(
    specification.model_dump_json(
        indent=2
    )
)


print("\nGenerating Day 3 engineering artifacts...\n")

artifacts = generate_engineering_artifacts(
    specification
)

print("ENGINEERING ARTIFACTS GENERATED")
print(
    artifacts.model_dump_json(
        indent=2
    )
)