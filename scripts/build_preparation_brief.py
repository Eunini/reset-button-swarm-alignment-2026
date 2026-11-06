"""Build an explicitly preparatory PDF and figure from saved pilot evidence."""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               Image, PageBreak, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/preexisting-model-pilot-20261105-v3"
REPORT = ROOT / "report"


def main():
    data = json.loads((RESULTS / "analysis.json").read_text())
    strict = {r["model"]: r for r in data["summary"] if r["parser"] == "strict"}
    normalized = {r["model"]: r for r in data["summary"] if r["parser"] != "strict"}
    models = ["deepseek-v4-flash", "qwen3.8-27b", "gemma-4-26b-a4b-it"]
    names = ["DeepSeek V4 Flash", "Qwen 3.8 27B", "Gemma 4 26B A4B"]
    fig, ax = plt.subplots(figsize=(8.3, 2.5), dpi=180)
    left = [0] * len(models)
    for field, label, color in [("policy_consistent_n", "Supported decision", "#27735C"),
                                ("wrong_valid_n", "Wrong valid decision", "#D3903C"),
                                ("invalid_n", "Output-format error", "#B1BAC3")]:
        vals = [strict[m][field] for m in models]
        ax.barh(names, vals, left=left, label=label, color=color, height=.58)
        for i, n in enumerate(vals):
            if n:
                ax.text(left[i] + n / 2, i, str(n), va="center", ha="center",
                        color="white" if field == "policy_consistent_n" else "#19252c", fontsize=10)
        left = [a + b for a, b in zip(left, vals)]
    ax.invert_yaxis()
    ax.set_xlim(0, 18)
    ax.set_xticks([0, 3, 6, 9, 12, 15, 18])
    ax.set_xlabel("Graded views in the matched-budget pilot (not independent trials)", fontsize=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.3), ncol=3, frameon=False, fontsize=9)
    fig.tight_layout()
    figure = REPORT / "pilot-decisions.png"
    fig.savefig(figure, bbox_inches="tight")
    fig.savefig(REPORT / "pilot-decisions.svg", bbox_inches="tight")
    plt.close(fig)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BriefTitle", fontName="Helvetica-Bold", fontSize=23,
                              leading=27, spaceAfter=10, textColor=colors.HexColor("#173B30")))
    styles.add(ParagraphStyle(name="BriefBody", fontName="Helvetica", fontSize=9.5,
                              leading=13.3, spaceAfter=8))
    styles.add(ParagraphStyle(name="BriefNote", fontSize=8, leading=10.5,
                              textColor=colors.HexColor("#53616D"), spaceAfter=7))
    styles.add(ParagraphStyle(name="BriefHeading", fontName="Helvetica-Bold", fontSize=12,
                              leading=15, spaceBefore=8, spaceAfter=5))
    story = []
    def para(text, kind="BriefBody"):
        story.append(Paragraph(text, styles[kind]))
    def heading(text):
        para(text, "BriefHeading")
    para("PRE-SPRINT PREPARATION | 5 NOVEMBER 2026 | NOT A SUBMISSION", "BriefNote")
    para("Blind Spots", "BriefTitle")
    para("Swarm oversight under missing evidence", "Heading2")
    para("Prepared for Inioluwa Atanda · Solo entry · Proposed Track 4", "BriefNote")
    para("<b>The question:</b> Can an oversight model tell the difference between a safe execution and a record that merely lacks visible evidence of harm? Can better evidence improve that decision while allowing compliant work to proceed?")
    heading("What has been done")
    para("A synthetic, reproducible calibration harness is built and tested. A live Adaption pilot evaluates three models on quota compliance across multiple workers. The matched-budget version uses 12 distinct inputs per model, with up to 4,096 output tokens each. Reusing identical observations across compliant and violating counterfactual worlds yields 18 graded views per model. Those views are <b>not 18 independent trials</b>.")
    story.append(Image(str(figure), width=6.55 * inch, height=1.98 * inch))
    para("Figure 1. Strict JSON outcomes from the saved matched-budget pilot. Cases are two deliberately constructed near-quota pairs and two additional controls. No confidence intervals or population claims are warranted by this small calibration set.", "BriefNote")
    heading("What the pilot actually shows")
    para("DeepSeek V4 Flash and Qwen 3.8 27B produced supported decisions on all 18 graded views in this pilot, including appropriate uncertainty and benign incomplete-log controls. Gemma 4 26B A4B produced 3 supported decisions, 4 wrong valid decisions, and 11 output-format errors. Two valid SAFE decisions occurred in views whose underlying execution violated policy. Formatting failures are reported separately from incorrect safety decisions.")
    para("Accepting a single surrounding JSON fence is an explicitly exploratory sensitivity check. It leaves Gemma at 3 supported decisions, changes wrong-valid decisions to 9 and invalid outputs to 6, and exposes additional unsupported SAFE verdicts. Conflicting or multiple answers are never repaired by another model.")
    cost = data["all_pilot_versions"]["uncached_credit_estimate"]
    para(f"<b>Compute used:</b> 51 physical inference calls across the integration and calibration versions; approximately {cost:.4f} credits calculated from recorded tokens at published uncached rates. Some responses were reused in the matched-budget analysis. The account debit has not been independently checked. No training job was launched.", "BriefNote")

    story.append(PageBreak())
    para("FROM CALIBRATION TO A REVIEWABLE STUDY", "BriefNote")
    heading("What this does not establish")
    para("These are synthetic records, not autonomous swarm trajectories. The pilot does not demonstrate emergent collusion, real-world containment, robust model-family rankings, or a generally effective defence. Exact arithmetic quotas should be enforced by code when possible. A hash alone does not make a trace complete or prove that an action occurred. The trusted verifier is an explicit assumption of the experiment.")
    heading("The sprint contribution to build")
    para("Extend the calibration tool into an actual local multi-worker execution workflow with separate worker contexts and an executor-owned record. Add a substantive research-evaluation integrity task: data preparation, training and reporting workers can make changes that jointly leak original evaluation examples into training. Derive labels independently from actual executed example IDs. Keep all records fabricated and actions restricted to a typed API.")
    para("Replay identical executed workflows under full visibility, random loss, targeted evidence loss and altered agent-side records. Compare per-worker review, a strong joint monitor, a trusted completeness envelope, exact checks, always-abstain, and paid-by-access recovery from independently retained records. Report safety, benign-work completion, unsupported certainty, false accusations, invalid outputs, latency and cost.")
    heading("Literature and novelty boundary")
    para("Distributed attacks and per-agent monitoring weaknesses are established in Makins et al. (2026). Trace manipulation and independent interception are established in Qin et al. (2026). Arslan (2026) studies the influence of agent reports on external attribution. The proposed contribution is a measured evidence-sufficiency and safety–utility comparison in actual worker workflows. Its novelty remains to be checked against adjacent benchmarks; it is not a new invention of external logging.")
    heading("Rules and provenance")
    para("<b>All work in this brief was prepared on November 5, before the sprint.</b> Code, prompts, preliminary results and this document must be disclosed as preexisting in the final README and report. The original preparation manifest, later source versions and failed pilot calls are preserved. Only new work actually done during the sprint may be claimed as sprint contributions.")
    para("The final submission remains pending: a 4–8 page report using the official template, verified author information, a 150–250 word abstract, references, and the required Limitations and Dual-Use / Ethical Considerations appendix. Submission cutoff: November 9, 2026, 11:59 UTC. This brief is not that report, and no submission has been sent.")
    heading("Reproduce and inspect")
    para("The project contains saved request bodies, raw responses, token usage, source hashes, independent labels, and separate strict/fence-normalized analyses. Run <font name='Courier'>python3 scripts/analyze_pilot.py</font> to regenerate the saved analysis without any API calls. Run <font name='Courier'>python3 -m unittest discover -s tests -v</font> to check the invariants.")
    heading("Sources")
    for label, url in [
        ("Official sprint rules and template", "https://apartresearch.com/sprints/swarm-alignment-2026"),
        ("Makins et al., Multi-Agent AI Control (2026)", "https://arxiv.org/abs/2607.07368v2"),
        ("Qin et al., LLM Agents Can Easily Tamper With Their Own Traces (2026)", "https://arxiv.org/abs/2609.30266v1"),
        ("Arslan, Audit Without Verification (2026)", "https://arxiv.org/abs/2609.07680v1"),
        ("Adaption hosted inference rates", "https://docs.adaptionlabs.ai/inference-stacks/models/")]:
        para(f'<link href="{url}" color="#175A42">{label}</link>', "BriefNote")
    para("AI assistance: The assistant prepared the code, literature triage, exploratory analysis and this brief. No independent human review is claimed. The human entrant must review the eventual submission and remains responsible for its accuracy.", "BriefNote")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#53616D"))
        canvas.drawString(42, 28, "Preexisting preparation · not the hackathon submission")
        canvas.drawRightString(570, 28, str(doc.page))
        canvas.restoreState()
    doc = SimpleDocTemplate(str(REPORT / "pre-sprint-brief.pdf"), pagesize=(612, 792),
                            rightMargin=42, leftMargin=42, topMargin=36, bottomMargin=43,
                            title="Blind Spots — Pre-sprint Preparation Brief", author="Prepared for Inioluwa Atanda")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(REPORT / "pre-sprint-brief.pdf")


if __name__ == "__main__":
    main()
