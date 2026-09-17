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

## Day 2 — Multimodal Requirement Analysis

Completed:

- Screenshot and UI image analysis
- Image-only requirement generation
- Combined text + image analysis
- Qwen3-VL 2B Instruct integration through Ollama
- Observed UI component extraction
- Visible state detection
- Evidence vs assumption separation
- Open-question handling
- Normalized multimodal requirement context
- Pydantic validation
- Local JSON repair for malformed vision-model output
- Manual multimodal evaluation and hallucination testing

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


---

# Day 2 — Multimodal Requirement Analysis

Day 2 extends DevFlow Copilot from text-only requirement generation to multimodal requirement analysis.

The application now supports three input modes:

- Text only
- Image only
- Text + Image

## Day 2 Architecture

```text
Client Text / UI Screenshot
          |
          v
      Streamlit UI
          |
     +----+----+
     |         |
     v         v
Qwen3 1.7B   Qwen3-VL 2B Instruct
Text Model    Vision Model
     |         |
     +----+----+
          |
          v
Normalized Requirement Context
          |
          v
Requirement Generation Service
          |
          v
JSON + Pydantic Validation
          |
          v
Structured Software Specification



---

# Day 3 — Engineering Artifacts

## Status

Day 3 implementation is complete.

The validated software specification can now be converted into engineering-ready artifacts using a local Qwen model.

Generated artifacts include:

- Acceptance Criteria
- Implementation Plan
- QA Test Cases
- Developer Implementation Prompt
- Assumptions
- Open Questions

## Day 3 Pipeline

```text
Validated Project Specification
        |
        v
Engineering Artifact Service
        |
        v
Versioned Engineering Prompt
        |
        v
Qwen3 1.7B via Ollama
        |
        v
Structured JSON
        |
        v
Pydantic Schema Validation
        |
        v
Evidence-Fidelity Safety Guard
        |
        +---- Safe Output ----> Engineering Artifacts
        |
        +---- Unsafe Output
                |
                v
        Automatic Correction Retry
                |
                v
        Evidence-Fidelity Check
                |
                +---- Safe Output
                |
                +---- Still Unsafe
                        |
                        v
                Deterministic Safe Fallback
                        |
                        v
                Human-Reviewable Output