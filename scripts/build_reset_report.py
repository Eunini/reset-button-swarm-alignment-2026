"""Populate the official DOCX template using recorded results; no model calls.

The development PDF is explicitly NOT a submission. Human review is not claimed.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from reset_button import VERIFIER_INSTRUCTIONS


def build(path):
    analysis = json.loads((path / "analysis.json").read_text())
    summary = json.loads((path / "summary-live.json").read_text())
    budget_controls_path = path / "budget-controls.json"
    budget_controls = json.loads(budget_controls_path.read_text()) if budget_controls_path.exists() else None
    dev = analysis["stage"] == "development"
    classification_file = ROOT / "sources/reset-study-classification-20261106.json"
    early_validation = (not dev and classification_file.exists() and
                        json.loads(classification_file.read_text()).get("all_completed_study_before_opening", False))
    n = analysis["seed_n"]
    output = ROOT / "report" / ("reset-button-development-report.docx" if dev else "reset-button-main-report-draft.docx")
    doc = Document(ROOT / "sources/official-template.docx")
    # Retain the official template's page setup, styles and title/abstract box.
    first_table = doc.tables[0]
    for child in list(doc._element.body):
        if child is not first_table._element and child.tag != qn("w:sectPr"):
            doc._element.body.remove(child)
    for cell in (first_table.cell(0, 0), first_table.cell(1, 0)):
        cell._tc.clear_content()
        cell.add_paragraph()
    normal = doc.styles["normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.06
    for s in ("Heading 2", "Heading 3"):
        doc.styles[s].font.name = "Times New Roman"
        doc.styles[s].font.size = Pt(12 if s == "Heading 2" else 10.5)
        doc.styles[s].font.bold = True
        doc.styles[s].paragraph_format.space_before = Pt(8)
        doc.styles[s].paragraph_format.space_after = Pt(5)

    def para(text="", bold=False, target=None, size=None):
        p = (target.add_paragraph() if target is not None else doc.add_paragraph())
        p.style = doc.styles["normal"]
        r = p.add_run(text)
        r.bold = bold
        if size:
            r.font.size = Pt(size)
        return p

    next_heading_new_page = [False]
    def heading(text, level=2):
        p = doc.add_paragraph(text, style=f"Heading {level}")
        if next_heading_new_page[0]:
            p.paragraph_format.page_break_before = True
            next_heading_new_page[0] = False
        return p

    def page():
        next_heading_new_page[0] = True

    def table(headers, rows):
        t = doc.add_table(rows=1, cols=len(headers))
        if "Table Grid" not in doc.styles:
            doc.styles.add_style("Table Grid", WD_STYLE_TYPE.TABLE)
        t.style = "Table Grid"
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement("w:" + edge)
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4"); el.set(qn("w:color"), "B7B7B7")
            borders.append(el)
        t._tbl.tblPr.append(borders)
        for c, v in zip(t.rows[0].cells, headers):
            c.text = str(v)
        for values in rows:
            for c, v in zip(t.add_row().cells, values):
                c.text = str(v)
        for ri, row in enumerate(t.rows):
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.space_before = Pt(3)
                    for r in p.runs:
                        r.font.name = "Times New Roman"; r.font.size = Pt(9)
                        r.bold = ri == 0
        return t

    status = ("PRE-SPRINT DEVELOPMENT • 5 NOVEMBER 2026 • NOT FOR SUBMISSION"
              if dev else "SWARM ALIGNMENT HACKATHON • 6 NOVEMBER 2026 • REVIEW COPY")
    if early_validation:
        status = "PRE-SPRINT VALIDATION • 6 NOVEMBER 2026 • NOT FOR SUBMISSION"
    header = doc.sections[0].header.paragraphs[0]
    header.text = status
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in header.runs:
        r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string("8C3430")
    footer = doc.sections[0].footer.paragraphs[0]
    footer.text = "Reset Button | " + ("Preexisting preparation" if dev else "Research report") + " | "
    if early_validation:
        footer.text = "Reset Button | Preexisting validation | "
    field = OxmlElement("w:fldSimple"); field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in footer.runs:
        r.font.size = Pt(8)

    title_cell, abstract_cell = first_table.cell(0, 0), first_table.cell(1, 0)
    p = title_cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Reset Button: Oversight under\nReplaceable Agent Identities"); r.bold=True; r.font.size=Pt(18)
    p = para("Inioluwa Atanda\n" + ("Solo entrant • institutional affiliation not supplied" if dev else "Independent researcher • solo entry"), target=title_cell)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    abstract = (
        "Multi-agent oversight can rely on a reporter's history to discount false allegations. "
        "That history becomes less useful if a worker can restart under a fresh identity. "
        "We implement a closed synthetic research lab and adapt a published escalating-reputation "
        "mechanism to sequential reports and a finite shared verification budget. The experiment "
        "holds report contents, arrival order and attacker report allowance fixed while changing "
        "identity handling. We compare checking every report, reputation attached to a worker "
        "identity, and reputation attached to an executor-attested delegation root. "
        f"This {'pre-sprint development' if dev else 'main'} study uses {n} task seeds, two hosted language-model verifiers, "
        "scripted allegations and model-authored report campaigns. A perfect-verifier diagnostic "
        "isolates resource allocation from judgment errors. Restarting can restore default reporter "
        "weight and consume checks on compliant workers; preserving root history prevents that "
        "specific reset. However, a constructed honest-reporter control shows that inherited distrust "
        "can also prevent a later truthful warning from triggering a check. These observations concern "
        "a controlled mechanism, not autonomous discovery or deployment safety. The objective lab "
        "policy is directly enforceable by code. The practical question is therefore when persistent "
        "accountability helps allocate scarce oversight, and what recovery path honest agents require."
    )
    if not dev:
        abstract = (
            "A safety checker can reject every false allegation it sees and still miss real misconduct "
            "because its verification budget runs out. We study this allocation failure when an AI reporter "
            "can restart under a new identity. In a closed synthetic research lab, we adapt a published "
            "escalating-reputation mechanism and hold report contents, arrival order and attacker report "
            "allowance fixed across identity conditions. Across 32 task seeds, each containing three real "
            "policy violations, detection at an eight-check budget falls from 96/96 incidents with persistent "
            "reporter identities to 27/96 with identity resets. Both language-model verifiers agree with "
            "executor labels on all 2,097 distinct judged inputs each; this failure therefore occurs despite "
            "correct judgments on the observed evidence. Attaching history to a trusted delegation root "
            "restores 96/96 detections, but suppresses 32/32 later truthful warnings in a constructed "
            "honest-reporter control. A simple fixed quota of four checks per trusted root matches attack "
            "detection and preserves those warnings, so we demonstrate no new-defence advantage. Workers "
            "and restarts are scripted, model-authored allegations are generated in batches, and the "
            "objective policy is directly enforceable by code. The contribution is a reproducible "
            "identity-and-budget stress test and an explicit recovery trade-off, rather than autonomous "
            "attack discovery or a deployment-ready defence."
        )
    if early_validation:
        abstract = "This pre-sprint validation study is preparation, not judged sprint work. " + abstract
    abstract_cell.paragraphs[0].add_run("Abstract").bold = True
    para(abstract, target=abstract_cell)
    abstract_words = len(abstract.split())
    if not 150 <= abstract_words <= 250:
        raise ValueError(f"abstract has {abstract_words} words")

    heading("1. Introduction")
    para("Safety reporting is useful only if complaints can be evaluated without overwhelming the system. "
         "A reputation mechanism can reduce repeated checks from an unreliable reporter. But an AI worker "
         "may be copied or restarted more cheaply than a human participant can be replaced. A system that "
         "attaches history to the replaceable process identity may repeatedly give one adversary a fresh start.")
    para("Our question is narrow: under a fixed allowance of false reports, how does restarting the reporter "
         "change the allocation of a finite checking budget? We also test the cost of retaining history: "
         "an honest reporter who made a mistake should still have a route to raise a genuine concern. "
         "This is a mechanism study in a local simulation. It is not evidence that deployed AI swarms "
         "already execute this strategy.")
    heading("2. Related Work")
    para("Ye and Steinhardt [1] demonstrate abuse of peer reporting and compare verification and reputation "
         "mechanisms, including escalating penalties for false reports. We adapt their update equation; "
         "we do not claim the false-reporting phenomenon or that equation as new. Their discussion names "
         "dynamic populations as future work. Gatta et al. [2] already model replaceable identities and "
         "reputation in agent markets. Identity reset and persistent accountability are therefore prior ideas. "
         "Our candidate contribution is an explicit identity intervention in a budgeted reporting testbed, "
         "including the honest-reporter cost of the proposed repair. Novelty beyond that specific extension "
         "is not established by this study.")

    page()
    heading("3. Methods")
    heading("3.1 Executed sandbox and independent labels", 3)
    para("Each scenario creates 12 opaque sample IDs: eight training and four heldout samples. Eight compliant "
         "workers fit on training samples and evaluate on heldout samples. Three incident workers fit on at "
         "least one heldout sample. The executor stores each action and output payload. A separate evaluation "
         "function labels a worker as violating exactly when a fit action includes a heldout ID. Evaluating "
         "on heldout data is explicitly allowed. Model inputs contain the target's actions, the relevant "
         "sample registry and an untrusted report reason; they omit evaluation labels.")
    heading("3.2 Report streams and paired intervention", 3)
    para("An adversary has 24 report opportunities. Three genuine reports from distinct witnesses are "
         "interleaved at seeded random positions after the first two positions. The scripted campaign cycles "
         "over compliant targets with misleading allegations; model campaigns provide 24 target/reason pairs "
         "in a single response. Invalid campaigns are retained as failures and excluded from campaign replays. "
         "The experiment, rather than the model, assigns identity restarts. We reuse identical report contents "
         "and verdict receipts across mechanisms and budgets; replay counts are not independent model trials.")
    heading("3.3 Oversight mechanisms", 3)
    table(["Mechanism", "Rule"], [
        ["Checked", "Check every incoming report while the shared call budget remains."],
        ["Escalating", "Accumulate reporter reputation by target; check at score ≥0.666."],
        ["Lineage", "The same escalating rule, using the trusted delegation root as history key."],
        ["Fixed quota control", "Check at most 1, 2 or 4 reports per identity or trusted root; same global budget."],
    ])
    para("With v verified valid and f verified invalid reports, weight is (2+v) / "
         "[3+v+3f(f+1)/2]. Fresh identities start at 2/3. Verification resets the target's accumulated "
         "score and updates contributing reports. An unknown/invalid verdict consumes a call and makes "
         "no sanction or reputation update. Budgets are 4, 8, 12, 16 and unlimited. The original study uses "
         "per-round updates; our sequential per-report update, objective policy, global budget and dynamic "
         "identities are disclosed adaptations, not an exact reproduction.")
    heading("3.4 Metrics and controls", 3)
    para("The primary outcome is genuine incidents detected at budget eight, paired by seed. Secondary "
         "outcomes are verifier calls, checks spent on false reports, false sanctions and invalid outputs. "
         "Unlimited-budget and perfect-verifier runs diagnose judgment versus allocation errors. An honest "
         "reporter makes two incorrect allegations, restarts, then correctly reports an incident. Its results "
         "are an analytical control with perfect judgments. Main-study intervals use 5,000 paired "
         "bootstrap resamples of task seeds, with fixed bootstrap seed 819; they describe seeded workload "
         "variation conditional on cached model outputs, not uncertainty over deployments or repeated model draws. "
         "No multiplicity-adjusted significance claim is made. No intervals are reported for the two development seeds.")

    page()
    heading("4. Results")
    para(f"Scope: {n} {'development' if dev else 'main'} task seeds. The development seeds were fixed before "
         "running the model checks. They are a debugging/calibration sample, not a population estimate. "
         "The main 32-seed study remains time-gated until the sprint." if dev else
         (f"Scope: {n} held-out validation seeds. All inference finished before the website countdown opening "
          "at November 6, 12:00 UTC. These are preexisting results, not sprint contributions." if early_validation else
          f"Scope: {n} held-out task seeds with fixed analysis and budgets. Development results are disclosed separately."))
    if not dev:
        para("At the prespecified eight-check budget, persistent-ID escalating reputation detects 96/96 real "
             "incidents; restarting the reporter reduces this to 27/96 (28.1%). The paired loss is 71.9 "
             "percentage points (conditional bootstrap 95% interval: 63.5–80.2). Trusted-root history restores "
             "96/96. Both verifiers yield the same scripted-campaign outcome; their results are not pooled "
             "as 64 independent task seeds.")
    doc.add_picture(str(path / "figures/budget-curves.png"), width=Inches(6.35))
    para("Figure 1. Genuine incident detection across checking budgets, using scripted report contents. "
         "Each point averages task seeds; methods share the same recorded verdicts. Stable-ID and lineage "
         "curves may overlap. ‘All’ permits every report to be checked. These are simulation outcomes, "
         "not independent autonomous swarm trials.", size=8.5)
    rows = []
    names = {"qwen3.8-27b": "Qwen 3.8 27B", "deepseek-v4-flash": "DeepSeek V4 Flash"}
    for model, name in names.items():
        for mechanism, identity in [("checked", "restart"), ("escalating", "persistent"),
                                    ("escalating", "restart"), ("lineage", "restart")]:
            g = next(g for g in summary["groups"] if g["verifier"] == model and g["campaign"] == "scripted"
                     and g["mechanism"] == mechanism and g["identity"] == identity and g["budget"] == 8)
            rows.append([name, mechanism + "/" + identity, f"{g['true_detected']:.2f}/3",
                         f"{g['verifier_calls']:.2f}", f"{g['false_stops']:.2f}"])
    table(["Verifier", "Condition", "Detected", "Calls", "False stops"], rows)
    para("Table 1. Mean results at budget eight for the scripted campaign. Averages use the same task "
         "seeds across conditions; false stops refer to compliant target workers.", size=8.5)
    for c in analysis["calibration"]:
        para(f"{names[c['model']]}: {c['correct']}/{c['usable']} usable unique verifier requests agreed with "
             f"executor labels; {c['unique_requests'] - c['usable']} requests were unusable. Unique requests "
             "still share workers and task seeds; this is a competence check, not independent-case generalization.", size=9)
    valid_campaigns = sum(r["valid"] for r in analysis["campaign_status"])
    para(f"Campaign generation produced {valid_campaigns}/{len(analysis['campaign_status'])} valid campaigns "
         "in this version. All raw failures and the earlier protocol version are retained. Campaign-specific "
         "paired results are in analysis.json and paired-effects.csv.", size=9)
    if not dev:
        para("All 32 Qwen-authored campaigns and 31/32 DeepSeek-authored campaigns are valid. The incomplete "
             "DeepSeek campaign is retained as a generation failure and excluded from campaign-specific "
             "replays. Paired detection losses are 2.156 incidents/seed for scripted and Qwen campaigns "
             "(n=32), and 2.129 for valid DeepSeek campaigns (n=31). These cohorts share task seeds and "
             "many evidence records; they are sensitivity comparisons, not independent replications.", size=9)

    page()
    heading("5. Discussion and Limitations")
    para("The causal mechanism is allocation, not necessarily a gullible verifier. A checker can reject every "
         "false allegation it sees and still run out of capacity before a truthful warning arrives. A fresh "
         "identity restores default reputation, so repeatedly relaunching the same underlying reporter can "
         "remove the savings that escalating history was meant to provide. In a trusted closed orchestrator, "
         "retaining the root key prevents this specific reset by construction.")
    heading("The repair has a measurable cost", 3)
    if budget_controls:
        controls8 = [r for r in budget_controls["rows"] if r["scope"] == "root" and r["quota"] == 2
                     and r["budget"] == 8 and r["identity"] == "restart" and r["campaign"] == "scripted"]
        if controls8:
            mean_detected = sum(r["true_detected"] for r in controls8) / len(controls8)
            honest_q4 = [r for r in budget_controls["honest_control"] if r["scope"] == "root" and r["quota"] == 4]
            para(f"A simple fixed quota of two checks per trusted root detected {mean_detected:.2f}/3 genuine "
                 f"incidents in the scripted {'development' if dev else 'main-study'} comparison at budget eight. That baseline uses no "
                 "reputation equation. Any matching result limits the case for a new reputation-based defence: "
                 "the contribution must concern the identity assumption and measured trade-off. A quota of "
                 f"four also retained {sum(r['true_detected'] for r in honest_q4)}/{len(honest_q4)} honest-control "
                 "warnings, outperforming lineage reputation in that control. These quota controls were "
                 "added after inspecting development results and before the held-out study.")
    by = defaultdict(list)
    for row in analysis["honest_control"]:
        if row["identity"] == "restart":
            by[row["mechanism"]].append(row["true_detected"])
    para(f"In the perfect-verifier honest control, Checked detected {sum(by['checked'])}/{len(by['checked'])} "
         f"later genuine warnings, identity-based Escalating detected {sum(by['escalating'])}/{len(by['escalating'])}, "
         f"and Lineage detected {sum(by['lineage'])}/{len(by['lineage'])}. "
         "After one verified mistake, weight falls below the single-report threshold. Carrying that history "
         "to a child can therefore prevent its truthful report from triggering verification. This is a "
         "constructed counterexample, not an observed frequency of honest-agent mistakes. Root persistence "
         "alone is not a complete reporting policy; an appeal path or reserved independent audit capacity "
         "would need its own evaluation.")
    heading("What the experiment cannot establish", 3)
    para("The workers and restarts are scripted. Models author batches of allegations and judge evidence; "
         "they do not discover a strategy through interaction. The simple data-split policy could be "
         "enforced directly by code, avoiding all three incidents with no language-model checking calls. "
         "Our results therefore concern oversight allocation under a reporting interface, not the best "
         "engineering solution for training-data integrity. Semantic policies, adaptive timing, concurrent "
         "queues, trusted-root spoofing and separate-account creation are outside this experiment.")
    para("The arrival distribution, number of compliant targets and equal call-based budgets are modelling "
         "choices. Calls need not have equal token or latency cost. The lineage equality under alias changes "
         "is an implementation invariant, not a novel empirical discovery. Broad efficacy and deployment "
         "claims require more seeds, different workloads and a strong existing budget-allocation baseline.")
    heading("6. Conclusion")
    para("Reporting history can conserve oversight capacity only if the identity carrying that history "
         "persists across the relevant restarts. Yet inherited distrust can also suppress a genuine warning. "
         "This testbed makes both effects explicit and reproducible. The development evidence supports "
         "running the held-out study; it does not establish a deployment-ready defence or a prize-worthy novelty claim."
         if dev else "Reporting history and restart identity jointly affect oversight allocation. Preserving "
         "history addresses this specific bypass while retaining a recovery problem for honest reporters. "
         "A simple trusted-root quota matches the attack repair and preserves the honest-control warning. "
         "The result is a stress test and boundary condition, not evidence for a superior new defence.")
    heading("Code and Data")
    para("Local package: src/reset_button.py; scripts/run_reset_study.py; scripts/analyze_reset_study.py; "
         f"{path.relative_to(ROOT)}/. Saved requests, raw responses, executed cases, labels, usage and source hashes "
         "are included. No public repository or submission is claimed.", size=9)

    page()
    heading("References")
    para("[1] Yaowen Ye and Jacob Steinhardt. 2026. Norm Enforcement for AI Agents: Robustly Shaping Behavior "
         "in Multi-Agent Systems. arXiv:2607.09766v1. https://arxiv.org/abs/2607.09766v1")
    para("[2] Federico Gatta, Manuel Naviglio and Francesco Tarantelli. 2026. Tempting the Agent: The Economics "
         "of Reputation without Persistent Identity in AI Agent Markets. arXiv:2609.02992v2. "
         "https://arxiv.org/abs/2609.02992v2")
    para("[3] Apart Research. 2026. Swarm Alignment Hackathon: official rules, rubric and template. "
         "https://apartresearch.com/sprints/swarm-alignment-2026. Accessed November 5, 2026.")
    para("[4] Adaption Labs. 2026. Hosted inference model pricing. "
         "https://docs.adaptionlabs.ai/inference-stacks/models/. Accessed November 5, 2026.")
    heading("Preexisting Work and Provenance")
    if early_validation:
        para("All experiments, code and findings in this document are pre-sprint preparation. The 4,258 "
             "recorded requests ran from November 5, 23:09 UTC to November 6, 03:56 UTC. The official "
             "page's countdown targets November 6, 12:00 UTC. Its public eventStartMs function adds "
             "12 hours to a date at UTC midnight, which the earlier assistant review missed. Earlier "
             "workspace-midnight and UTC-midnight cutoffs were self-imposed and are withdrawn as "
             "bases for claiming sprint contributions. Raw timestamps and the prior report version "
             "remain preserved. This report is not a completed hackathon submission. A substantive "
             "extension and new evaluation during the event are still needed; simply repeating these "
             "known results would not establish a new finding.")
    else:
        para("This document, the research design, code, development prompts and all November 5 results are "
         "preexisting preparation. They must be disclosed in the final README and report. Only work actually "
         "performed during the sprint may be identified as sprint contributions. No main study or submission "
         "has occurred." if dev else "The design, code and November 5 development study predate the sprint. "
         "The main execution began November 5 at 23:09:56 UTC (November 6, 00:09:56 Europe/Berlin, the "
         "supplied project timezone) and ended November 6 at 03:56 UTC. For conservative UTC accounting, "
         "522 recorded requests precede November 6 00:00 UTC: all 64 campaign requests and 458 Qwen "
         "verifier requests. The weekend contribution includes the remaining 3,736 verifier requests "
         "(all 2,097 DeepSeek judgments and 1,639 Qwen judgments), paired analysis, main-study quota results "
         "and this report. Earlier design, code, generated campaigns and pre-cutoff judgments are disclosed "
         "as preexisting inputs. Original UTC timestamps are retained; no universal organizer start-time "
         "ruling or independent human verification is claimed.")
    para("The mathematical mechanism is adapted from the public MIT-licensed norm-enforcement code, commit "
         "0568d47da7dc6ab75cc3fa4041bb228f074d91c1. Copyright (c) 2026 Yaowen Ye and Jacob Steinhardt. "
         "The original license is retained in sources/norm-enforcement/LICENSE. A differential test compares "
         "reputation values on 100 seeded random report histories. This does not validate every part of the "
         "original simulation or constitute an exact replication.")
    heading("Cost and Failed Attempts")
    u = analysis["usage"]
    para(f"The {'development versions' if dev else 'main study'} contain {u['physical_calls']} recorded API requests, with "
         f"{u['computed_credits']:.5f} credits estimated from token usage at published uncached rates. "
         f"Provider-reported usage cost totals {u['provider_reported_cost']:.5f}. Neither is an independent "
         "account-balance audit; failed requests may omit usage. In development, version 1 included two truncated Qwen "
         "campaigns and 26 HTTP 429 responses. Version 2 increases campaign output allowance to 8,192 "
         "tokens, serializes calls, preserves those failures and records the follow-up separately. "
         "Identical saved requests are reused across replay conditions rather than treated as independent draws.")
    if not dev:
        para("One main-study campaign output was incomplete; all verifier requests completed. The original "
             "terminal worker stopped after 522 recorded requests with no available termination reason. A "
             "detached worker resumed using the unchanged scientific runner and cache. A possibly billed "
             "in-flight request without a saved receipt cannot be ruled out; request and cost totals above "
             "refer to recorded receipts, not an independently reconciled account debit.")

    page()
    heading("Appendix A. Limitations and Dual-Use / Ethical Considerations")
    para("All workers, samples and incidents are artificial. No real users are accused, no external system "
         "receives reports, and model output is never executed as shell code. The only allowed actions "
         "operate on generated IDs in the local lab. Evaluation labels are independent of model judgments "
         "and are omitted from request bodies.")
    para("Publishing report-flooding mechanisms could help someone disrupt an oversight channel. The package "
         "therefore documents a local simulation and bounded reporting strategies rather than instructions "
         "for attacking a production reporting service. Persistent lineage also has risks: it can link "
         "otherwise separate agents and propagate one worker's mistakes to legitimate descendants. No "
         "real-person identity tracking, indefinite blacklist or cross-account attribution is proposed.")
    para("A trusted orchestrator assigns parent/root links. The experiment assumes that an adversary cannot "
         "forge those links, modify executor evidence or add unlimited report opportunities. The repair "
         "does not address independently created accounts or compromise of that orchestrator. The fixed "
         "budget and simple policies limit transfer to real environments. An always-ignore or always-stop "
         "policy would not satisfy the useful-oversight objective.")
    heading("LLM Usage Statement")
    para("The coding assistant proposed and implemented the study, inspected prior work, generated analysis "
         "and drafted this report. Adaption-hosted models generate artificial report text and assess evidence. "
         "Programmatic checks verify sample-policy labels, source hashes and paired replay invariants. No "
         "independent human review or approval of this draft is claimed. Inioluwa Atanda remains the human "
         "entrant and must understand and verify the final submission. AI-generated text is not itself "
         "evidence for the research claims.")
    heading("Reproduction" if not dev else "Reproduction and Remaining Work")
    para("Run python3 -m unittest discover -s tests -v for implementation checks. Saved-results analysis "
         "requires the listed Python dependencies and makes no API calls. Run .venv/bin/python "
         "scripts/analyze_reset_study.py, then .venv/bin/python scripts/build_reset_report.py. "
         "The main command is time-gated until November 6, 21:30 UTC, a conservative local convention, "
         "not a claimed official start-time ruling. The submission deadline is November 9, 11:59 UTC. "
         "No autonomous future wake-up, notification or submission has been configured." if dev else
         "Run python3 -m unittest discover -s tests -v for implementation checks. Rebuild the main analysis "
         "with .venv/bin/python scripts/analyze_reset_study.py --results results/reset-main-20261106. "
         "Run scripts/check_reset_budget_controls.py and scripts/build_reset_report.py with the same "
         "--results argument for quota controls and DOCX generation. These saved-data commands make no "
         "API calls. The inference protocol uses two model aliases, temperature zero, 8,192 campaign "
         "output tokens and 4,096 verifier output tokens; complete request bodies and usage are saved. "
         "No provider determinism is assumed. This report does not claim that submission has occurred.")
    heading("Review status" if not dev else "Acceptance gates for a final entry")
    para("Before submission: run and inspect the held-out study during the sprint; reassess the exact "
         "contribution relative to the closest work; include honest-agent and resource-allocation controls; "
         "verify author affiliation, results and citations; inspect the complete PDF; retain the required "
         "appendix and AI disclosure; check the official submission receipt. This development draft is "
         "not the final report." if dev else
         "The report distinguishes executor labels, model observations, mathematical implications and "
         "interpretation. Machine checks cover labels, paired budgets, source hashes and recorded totals; "
         "they do not establish real-world transfer or research novelty. No independent human review "
         "is claimed. The solo entrant remains responsible for the report and any submission.")

    page()
    heading("Appendix B. Prompts and a Mechanistic Counterexample")
    heading("Verifier instructions (full text)", 3)
    para(VERIFIER_INSTRUCTIONS.strip(), size=9)
    heading("Campaign instructions and input", 3)
    para("The reporter is told that it is operating in a closed artificial lab and is asked to author 24 "
         "plausible false allegations against listed compliant workers. Each JSON entry supplies a listed "
         "target and a short reason. The prompt states that restarts are assigned by the experiment and "
         "makes no autonomous-discovery claim. Exact full prompt and inputs appear in each request receipt. "
         "Campaigns use temperature zero and up to 8,192 output tokens in version 2; verifiers use zero "
         "temperature and up to 4,096 output tokens. Provider determinism is not assumed.", size=9)
    heading("Why both effects can occur", 3)
    para("A fresh reporter starts at 2/3, above the 0.666 checking threshold. One rejected report changes "
         "its weight to 2/(3+3)=1/3. The same reporter's next complaint about a different target therefore "
         "does not independently trigger checking. A fresh alias restores 2/3. A root key prevents that "
         "restoration, but it also leaves a subsequent truthful complaint about a different target at "
         "1/3. Thus the toy counterexample follows from the rule itself. The empirical question concerns "
         "its consequences under realistic report streams, errors, costs and recovery policies.", size=9)
    doc.core_properties.title = "Reset Button — " + ("Pre-sprint Development Report" if dev else "Main Study Draft")
    doc.core_properties.author = "Prepared for Inioluwa Atanda"
    output.parent.mkdir(exist_ok=True)
    doc.save(output)
    (output.parent / "reset-report-metadata.json").write_text(json.dumps({"docx": str(output.relative_to(ROOT)),
        "abstract_words": abstract_words, "stage": analysis["stage"], "results": str(path.relative_to(ROOT)), "template": "sources/official-template.docx",
        "submission_ready": False, "human_review_claimed": False,
        "preexisting_validation": early_validation,
        "eligibility_note": "All results precede the website countdown opening; substantive sprint work remains" if early_validation else None}, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/reset-development-v2-20261105")
    args = parser.parse_args()
    build(ROOT / args.results)
