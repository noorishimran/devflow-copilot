import json
import sys
from pathlib import Path

from app.services.requirement_service import generate_specification


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT / "evaluation" / "scenarios.json"

PROMPT_VERSION = sys.argv[1] if len(sys.argv) > 1 else "v2"

if PROMPT_VERSION not in {"v1", "v2"}:
    raise ValueError("Prompt version must be v1 or v2.")

RESULTS_PATH = ROOT / "evaluation" / f"results_{PROMPT_VERSION}.json"
REPORT_PATH = ROOT / "evaluation" / f"evaluation_report_{PROMPT_VERSION}.md"


def normalize(text: str) -> str:
    return " ".join(str(text).lower().split())


def feature_text(specification) -> str:
    parts = []
    for feature in specification.features:
        parts.append(feature.name)
        parts.append(feature.description)
    return normalize(" ".join(parts))


def calculate_feature_coverage(expected_features, specification):
    if not expected_features:
        return 100

    generated_text = feature_text(specification)
    matched = 0

    for expected in expected_features:
        words = [word for word in normalize(expected).split() if len(word) > 2]
        if words and all(word in generated_text for word in words):
            matched += 1

    return round((matched / len(expected_features)) * 100)


def check_forbidden_content(scenario, specification):
    forbidden = scenario.get("must_not_include", [])
    if not forbidden:
        return [], 100

    output_text = normalize(
        json.dumps(specification.model_dump(), ensure_ascii=False)
    )

    violations = []
    for item in forbidden:
        if normalize(item) in output_text:
            violations.append(item)

    return violations, 0 if violations else 100


def calculate_uncertainty_score(scenario, specification):
    required_min = scenario.get("expected_open_questions_min", 0)
    actual = len(specification.open_questions)

    if required_min == 0:
        return 100
    if actual >= required_min:
        return 100
    if actual > 0:
        return 50
    return 0


def evaluate_scenario(scenario):
    specification = generate_specification(
        scenario["input"],
        prompt_version=PROMPT_VERSION,
    )

    coverage = calculate_feature_coverage(
        scenario.get("expected_features", []),
        specification,
    )

    uncertainty = calculate_uncertainty_score(
        scenario,
        specification,
    )

    forbidden_violations, fidelity = check_forbidden_content(
        scenario,
        specification,
    )

    overall_score = round(
        coverage * 0.50
        + uncertainty * 0.25
        + fidelity * 0.25
    )

    if fidelity == 0:
        status = "fail"
    elif overall_score >= 85:
        status = "pass"
    elif overall_score >= 60:
        status = "partial"
    else:
        status = "fail"

    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "category": scenario["category"],
        "status": status,
        "overall_score": overall_score,
        "feature_coverage": coverage,
        "uncertainty_handling": uncertainty,
        "evidence_fidelity": fidelity,
        "open_questions_returned": len(specification.open_questions),
        "forbidden_violations": forbidden_violations,
        "output": specification.model_dump(),
    }


def save_results(results):
    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_report(results):
    total = len(results)
    passed = sum(1 for item in results if item["status"] == "pass")
    partial = sum(1 for item in results if item["status"] == "partial")
    failed = sum(1 for item in results if item["status"] == "fail")

    average_score = round(
        sum(item["overall_score"] for item in results) / total,
        2,
    ) if total else 0

    lines = [
        f"# DevFlow Copilot — Evaluation Report {PROMPT_VERSION}",
        "",
        f"- Prompt version: {PROMPT_VERSION}",
        f"- Scenarios executed: {total}",
        f"- Passed: {passed}",
        f"- Partial: {partial}",
        f"- Failed: {failed}",
        f"- Average score: {average_score}/100",
        "",
        "## Scenario Results",
        "",
        "| ID | Category | Status | Score | Coverage | Uncertainty | Fidelity |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for item in results:
        lines.append(
            f"| {item['id']} | {item['category']} | {item['status'].upper()} | "
            f"{item['overall_score']} | {item['feature_coverage']} | "
            f"{item['uncertainty_handling']} | {item['evidence_fidelity']} |"
        )

    failed_items = [item for item in results if item["status"] != "pass"]

    lines.extend(["", "## Failures / Partial Results", ""])

    if failed_items:
        for item in failed_items:
            lines.extend(
                [
                    f"### {item['id']} — {item['title']}",
                    "",
                    f"- Status: {item['status'].upper()}",
                    f"- Score: {item['overall_score']}/100",
                    f"- Feature coverage: {item['feature_coverage']}/100",
                    f"- Uncertainty handling: {item['uncertainty_handling']}/100",
                    f"- Evidence fidelity: {item['evidence_fidelity']}/100",
                    f"- Forbidden violations: {item['forbidden_violations'] or 'None'}",
                    "",
                ]
            )
    else:
        lines.append("All executed scenarios passed.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    scenarios = json.loads(
        SCENARIOS_PATH.read_text(encoding="utf-8")
    )

    results = []

    print(
        f"Running {len(scenarios)} scenarios with prompt {PROMPT_VERSION}..."
    )
    print()

    for index, scenario in enumerate(scenarios, start=1):
        print(
            f"[{index}/{len(scenarios)}] {scenario['id']} - {scenario['title']}"
        )

        try:
            result = evaluate_scenario(scenario)
        except Exception as exc:
            result = {
                "id": scenario["id"],
                "title": scenario["title"],
                "category": scenario["category"],
                "status": "fail",
                "overall_score": 0,
                "feature_coverage": 0,
                "uncertainty_handling": 0,
                "evidence_fidelity": 0,
                "open_questions_returned": 0,
                "forbidden_violations": [],
                "error": str(exc),
                "output": None,
            }

        results.append(result)
        save_results(results)

        print(
            f"    Status: {result['status'].upper()} | "
            f"Score: {result['overall_score']}/100"
        )

    write_report(results)

    print()
    print("Evaluation complete.")
    print(f"Prompt:  {PROMPT_VERSION}")
    print(f"Results: {RESULTS_PATH}")
    print(f"Report:  {REPORT_PATH}")


if __name__ == "__main__":
    main()
