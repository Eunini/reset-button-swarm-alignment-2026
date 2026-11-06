"""Check PDF structure and recorded quantitative claims; no model calls."""
import json
from pathlib import Path
import re
import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def main():
    pdf = ROOT / "report/reset-button-development-report.pdf"
    doc = pymupdf.open(pdf)
    text = "\n".join(p.get_text() for p in doc)
    text = " ".join(text.split())
    a = json.loads((ROOT / "results/reset-development-v2-20261105/analysis.json").read_text())
    metadata = json.loads((ROOT / "report/reset-report-metadata.json").read_text())
    reference_page = next(i for i, p in enumerate(doc) if "References\n[1]" in p.get_text())
    checks = {"main_pages_4_to_8": 4 <= reference_page <= 8,
              "abstract_150_to_250_words": 150 <= metadata["abstract_words"] <= 250,
              "correct_author": "Inioluwa Atanda" in text,
              "required_appendix": "Limitations and Dual-Use / Ethical Considerations" in text,
              "llm_usage_statement": "LLM Usage Statement" in text,
              "preexisting_disclosure": "preexisting preparation" in text,
              "marked_not_for_submission_every_page": all("NOT FOR SUBMISSION" in p.get_text() for p in doc),
              "template_placeholders_removed": not any(x in text for x in ["PROJECT TITLE", "Author name 1", "[Reference 1]", "How to use this template"]),
              "actual_cost_present": f"{a['usage']['computed_credits']:.5f}" in text,
              "actual_physical_calls_present": str(a['usage']['physical_calls']) + " physical API calls" in text,
              "current_results_version": metadata["results"] == "results/reset-development-v2-20261105",
              "small_sample_limit": "two development seeds" in text,
              "quota_control_reported": "A quota of four" in text or "quota of four" in text,
              "no_sprint_claim": "No main study or submission" in text}
    bounds_ok = True
    for page in doc:
        for word in page.get_text("words"):
            x0, y0, x1, y1 = word[:4]
            if x0 < 10 or y0 < 10 or x1 > page.rect.width - 10 or y1 > page.rect.height - 10:
                bounds_ok = False
    checks["text_within_page_bounds"] = bounds_ok
    result = {"pdf": str(pdf.relative_to(ROOT)), "total_pages": len(doc), "main_pages": reference_page,
              "checks": checks, "passed": all(checks.values()),
              "scope": "Structural/numerical checks do not replace scientific or visual review."}
    (ROOT / "report/reset-report-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
