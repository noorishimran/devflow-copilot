# DevFlow Copilot — Failure Analysis and Known Limitations

## Evaluation Scope

The DevFlow Copilot requirement-generation pipeline was evaluated using 30 scenarios.

The evaluation set included:

- CRUD applications
- E-commerce requirements
- Booking systems
- CRM requirements
- SaaS dashboards
- Mobile applications
- API integrations
- Authentication requirements
- Ambiguous requirements
- Missing information
- Contradictory requirements
- Noisy client input
- Prompt-injection attempts
- Unsupported technology requests
- Unsupported deadline, budget, and infrastructure assumptions

Two prompt versions were evaluated using the same scenario set.

## Prompt v1 Results

- Scenarios executed: 30
- Passed: 11
- Partial: 12
- Failed: 7
- Average score: 77.53/100

## Prompt v2 Results

- Scenarios executed: 30
- Passed: 10
- Partial: 12
- Failed: 8
- Average score: 76.10/100

## Prompt Comparison

Measured difference:

- Prompt v2 average minus Prompt v1 average: -1.43 points
- Improved scenarios in v2: 1
- Regressed scenarios in v2: 2
- Unchanged scenarios: 27

The evaluation does not assume that the newer prompt is automatically better.

### Improved in v2

- EV-015 — Weather API Integration

### Regressed in v2

- EV-020 — Missing User Roles
- EV-025 — Noisy Client Requirement

## Observed Failure Categories

### 1. Missing Requirement Extraction

Some scenarios received low feature-coverage scores because the generated specification did not preserve every explicitly requested capability.

Examples include requirements involving:

- user roles
- authentication
- API behavior
- noisy or conversational client messages

This can reduce downstream requirement coverage.

### 2. Weak Uncertainty Handling

Several scenarios expected the system to surface missing information as open questions.

In some cases the model produced no open question even when implementation details were incomplete.

Examples include:

- undefined payment provider
- undefined API provider
- missing cancellation rules
- undefined dashboard metrics
- unspecified user roles

This is one of the most visible weaknesses in the current requirement-generation stage.

### 3. Prompt-Injection Resistance

The evaluation included explicit prompt-injection and untrusted-input scenarios.

The current model did not consistently achieve the required evidence-fidelity behavior on all adversarial cases.

Relevant scenarios include:

- EV-027 — Prompt Injection Attempt
- EV-028 — Untrusted Instruction Inside Requirement

These cases demonstrate that prompt rules alone should not be treated as a complete security boundary.

### 4. Unsupported Information

The system was tested for invention of information that was not present in the source requirement.

Relevant scenarios include:

- EV-029 — Unsupported Technology Should Not Be Invented
- EV-030 — Unsupported Deadline, Budget and Infrastructure

These scenarios remain important failure cases because the product must avoid presenting unsupported implementation choices as confirmed client requirements.

### 5. Noisy Input Sensitivity

EV-025 showed that performance can change when a requirement contains informal wording, uncertain statements, and conversational filler.

Prompt v2 regressed on this scenario compared with prompt v1.

The system therefore remains sensitive to phrasing even when the underlying client intent is similar.

### 6. Small Local Model Limitations

The current text model is Qwen3 1.7B running locally through Ollama.

The local-first approach provides:

- no paid API dependency
- local execution
- greater control over data flow
- predictable software cost

However, the smaller model can be less consistent when handling:

- ambiguous requirements
- long mixed requirements
- subtle contradictions
- adversarial instructions
- incomplete requirements
- complex inference about missing information

## Structure and Validation

Generated specifications are validated with Pydantic schemas.

Schema validation reduces invalid structured output, but schema validity does not guarantee that:

- every requirement was captured
- every feature is correct
- every open question was identified
- the model remained fully grounded in evidence

For this reason schema validation is combined with deterministic evaluation and mandatory human review.

## Human Review Requirement

AI-generated artifacts must remain reviewable drafts.

The system includes human review states:

- Draft
- Approved
- Needs Edit
- Rejected

Final JSON and Markdown export remains locked until a human reviewer explicitly approves the current artifact set.

This control is necessary because evaluation demonstrates that model output can still contain omissions or weak interpretations.

## Current Known Limitations

1. Requirement extraction can miss explicitly stated features.
2. Open-question generation is inconsistent.
3. Prompt-injection resistance is not perfect.
4. Unsupported technical assumptions may still appear.
5. Small local models are sensitive to wording and prompt structure.
6. Similar requirements may produce different outputs between runs.
7. The evaluation uses heuristic string-based feature matching.
8. Feature-coverage scoring does not fully measure semantic equivalence.
9. Current evaluation scenarios are representative but not exhaustive.
10. Human review is still required before software implementation.

## Recommended Future Improvements

- Improve deterministic requirement-evidence tracing.
- Add stronger prompt-injection filtering before model execution.
- Add semantic feature-matching to the evaluator.
- Expand the evaluation dataset beyond 30 scenarios.
- Add repeated-run consistency testing.
- Add explicit contradiction detection.
- Improve automatic missing-information detection.
- Evaluate larger local models when hardware permits.
- Continue prompt iteration based on measured evaluation results.
- Maintain mandatory human approval for generated engineering artifacts.

## Conclusion

The evaluation demonstrates that DevFlow Copilot is operational but not infallible.

The system successfully combines:

- local GenAI generation
- schema validation
- deterministic reliability checks
- evaluation scenarios
- prompt-version comparison
- human review
- controlled export

The measured results and documented failures are retained rather than hidden so future prompt and validation improvements can be evaluated objectively.