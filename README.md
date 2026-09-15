# MoinSystems AI — DevFlow Copilot

DevFlow Copilot is a local-first Generative AI tool designed for software-house workflows.

The goal of the project is to convert unstructured client requirements, meeting notes, and later UI screenshots into structured software-development artifacts such as:

- Project requirements
- Features
- User stories
- Assumptions
- Open questions
- Acceptance criteria
- Implementation plans
- Test cases
- Developer prompts
- Client updates
- Release notes

The project is being developed as a 5-day GenAI internship task.

The final goal is to build a usable internal software-house MVP rather than a general-purpose chatbot.

---

# Project Timeline

## Day 1 — GenAI Requirement Generator

Build the foundation of the system:

- Accept unstructured client requirements
- Use a local LLM
- Generate structured software requirements
- Return structured JSON
- Validate model output with Pydantic
- Build a basic Streamlit UI
- Test hallucination behavior
- Document failures and limitations

## Day 2 — Multimodal Inputs

Planned:

- Screenshot understanding
- UI image analysis
- Meeting notes
- Additional multimodal inputs

## Day 3 — Engineering Artifacts

Planned:

- Acceptance criteria
- Implementation plans
- QA test cases
- Developer prompts
- Engineering-ready artifacts

## Day 4 — Reliability and Evaluation

Planned:

- Hallucination testing
- Prompt evaluation
- Output scoring
- Evidence fidelity checks
- Reliability improvements
- Regression tests

## Day 5 — Internal MVP

Planned:

- Integrate the complete workflow
- Improve UX
- Connect all artifact generators
- Final internal DevFlow Copilot MVP

---

# Day 1 Status

Day 1 core implementation is working.

Current pipeline:

```text
Client Requirement
        ↓
Streamlit UI
        ↓
Requirement Service
        ↓
Versioned Prompt
        ↓
Ollama
        ↓
Qwen3 1.7B
        ↓
Structured JSON
        ↓
JSON Parsing
        ↓
Pydantic Schema Validation
        ↓
Validated Specification
        ↓
Streamlit Result Dashboard