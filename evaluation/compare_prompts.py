import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evaluation"

V1_PATH = EVAL_DIR / "results_v1.json"
V2_PATH = EVAL_DIR / "results_v2.json"
REPORT_PATH = EVAL_DIR / "prompt_comparison_report.md"

STATUS_RANK = {"fail": 0, "partial": 1, "pass": 2}


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected a list in {path}")
    return data


def summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for item in results if item.get("status") == "pass")
    partial = sum(1 for item in results if item.get("status") == "partial")
    failed = sum(1 for item in results if item.get("status") == "fail")
    average = round(
        sum(item.get("overall_score", 0) for item in results) / total,
        2,
    ) if total else 0
    return {
        "total": total,
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "average": average,
    }


def compare_results(v1_results: list[dict], v2_results: list[dict]):
    v1_by_id = {item["id"]: item for item in v1_results}
    v2_by_id = {item["id"]: item for item in v2_results}
    common_ids = sorted(set(v1_by_id) & set(v2_by_id))

    rows = []
    improved = []
    regressed = []
    unchanged = []

    for scenario_id in common_ids:
        v1 = v1_by_id[scenario_id]
        v2 = v2_by_id[scenario_id]

        v1_score = v1.get("overall_score", 0)
        v2_score = v2.get("overall_score", 0)
        v1_status = v1.get("status", "fail")
        v2_status = v2.get("status", "fail")
        delta = v2_score - v1_score

        if STATUS_RANK.get(v2_status, 0) > STATUS_RANK.get(v1_status, 0) or delta > 0:
            change = "improved"
            improved.append(scenario_id)
        elif STATUS_RANK.get(v2_status, 0) < STATUS_RANK.get(v1_status, 0) or delta < 0:
            change = "regressed"
            regressed.append(scenario_id)
        else:
            change = "unchanged"
            unchanged.append(scenario_id)

        rows.append(
            {
                "id": scenario_id,
                "title": v2.get("title", v1.get("title", "")),
                "v1_status": v1_status,
                "v1_score": v1_score,
                "v2_status": v2_status,
                "v2_score": v2_score,
                "delta": delta,
                "change": change,
            }
        )

    return rows, improved, regressed, unchanged


def write_report():
    v1_results = load_results(V1_PATH)
    v2_results = load_results(V2_PATH)

    v1_summary = summarize(v1_results)
    v2_summary = summarize(v2_results)

    rows, improved, regressed, unchanged = compare_results(
        v1_results,
        v2_results,
    )

    average_delta = round(
        v2_summary["average"] - v1_summary["average"],
        2,
    )

    lines = [
        "# DevFlow Copilot — Prompt v1 vs v2 Comparison",
        "",
        "## Summary",
        "",
        "| Metric | Prompt v1 | Prompt v2 | Difference (v2 - v1) |",
        "|---|---:|---:|---:|",
        f"| Scenarios | {v1_summary['total']} | {v2_summary['total']} | {v2_summary['total'] - v1_summary['total']} |",
        f"| Passed | {v1_summary['passed']} | {v2_summary['passed']} | {v2_summary['passed'] - v1_summary['passed']} |",
        f"| Partial | {v1_summary['partial']} | {v2_summary['partial']} | {v2_summary['partial'] - v1_summary['partial']} |",
        f"| Failed | {v1_summary['failed']} | {v2_summary['failed']} | {v2_summary['failed'] - v1_summary['failed']} |",
        f"| Average score | {v1_summary['average']} | {v2_summary['average']} | {average_delta:+.2f} |",
        "",
        "## Scenario-Level Comparison",
        "",
        "| ID | Scenario | v1 Status | v1 Score | v2 Status | v2 Score | Delta | Change |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['id']} | {row['title']} | "
            f"{row['v1_status'].upper()} | {row['v1_score']} | "
            f"{row['v2_status'].upper()} | {row['v2_score']} | "
            f"{row['delta']:+} | {row['change']} |"
        )

    lines.extend([
        "",
        "## Change Counts",
        "",
        f"- Improved in v2: {len(improved)}",
        f"- Regressed in v2: {len(regressed)}",
        f"- Unchanged: {len(unchanged)}",
        "",
        "## Improved Scenarios in v2",
        "",
    ])

    if improved:
        lines.extend(f"- {item}" for item in improved)
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Regressed Scenarios in v2",
        "",
    ])

    if regressed:
        lines.extend(f"- {item}" for item in regressed)
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Evaluation Notes",
        "",
        "- This comparison reports measured results only. A newer prompt version is not assumed to be better.",
        "- Prompt quality should be judged across coverage, uncertainty handling, evidence fidelity, and failure behavior.",
        "- Partial and failed scenarios should be reviewed before making further prompt changes.",
    ])

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print("Prompt comparison complete.")
    print(f"v1 average: {v1_summary['average']}/100")
    print(f"v2 average: {v2_summary['average']}/100")
    print(f"v2 - v1: {average_delta:+.2f}")
    print(f"Improved in v2: {len(improved)}")
    print(f"Regressed in v2: {len(regressed)}")
    print(f"Unchanged: {len(unchanged)}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    write_report()
