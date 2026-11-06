# Swarm Alignment 2026 — research preparation

**CORRECTION, November 6, approximately 05:52 UTC:** The website countdown targets **12:00 UTC November 6** (13:00 Nigeria/Berlin). All work completed so far is classified as **pre-sprint validation/preexisting preparation**, not a finished judged entry. The earlier midnight-based eligibility claim is withdrawn. The data and findings remain real and unchanged, but a substantive extension during the sprint is still needed. See `sources/reset-study-classification-20261106.json`. This correction supersedes the earlier status below. No submission was made.

**November 6 status: main experiment and reviewed research report complete; not submitted.** The main study has 32 task seeds and 4,258 recorded requests (one incomplete campaign). The independent evidence audit passes. At eight checks, persistent reporter IDs detect 96/96 incidents, identity resets 27/96, and trusted-root history 96/96. A simple root quota also works and preserves the honest-control warning; no new-defence advantage is claimed. See `report/reset-button-main-report-draft.pdf`, `results/reset-main-20261106/evidence-audit.json` and `report/reset-main-report-checks.json`. The report conservatively distinguishes the 522 pre-midnight-UTC requests from 3,736 later verifier requests and marks earlier code/design as preexisting inputs.

Solo participant: Inioluwa Atanda. Proposed anchor: Track 4, Multi-Agent Oversight and Control.

**Recommended focus, November 5:** [Reset Button](docs/focus-identity-reset-20261105.md), a stress test of reputation-based oversight when AI workers can restart with new identities. Development experiments have run; the main sprint study has not. The earlier **Blind Spots** work below is retained as preexisting calibration, not evidence for the new hypothesis.

## Reset Button preparation

See [the execution runbook](docs/reset-runbook.md). The closed sandbox, saved development inference, matched replay, honest-reporter control and quota baselines are preexisting November 5 work. The main held-out study is time-gated until the sprint; no entry has been submitted and no automatic continuation is configured.

```sh
python3 -m unittest discover -s tests -v
.venv/bin/python scripts/analyze_reset_study.py
.venv/bin/python scripts/check_reset_budget_controls.py
.venv/bin/python scripts/build_reset_report.py
```

These commands verify and analyze saved records without API calls. During the sprint, `.venv/bin/python scripts/launch_reset_sprint.py` checks readiness and launches the bounded main study. It requests a key privately in the terminal and uses the direct API, with no plugin. The development report uses the official template and is clearly marked **not for submission**.

## Earlier Blind Spots calibration (preexisting)

**Status: pre-sprint preparation, not a completed hackathon entry. A small live model pilot is complete; no main sprint study, training job or submission has occurred.** The title and design remain provisional until the related-work review and pilot justify them.

The proposed question is whether partial multi-agent traces cause false assurances of safety, and how completeness checks and independently recorded execution evidence affect both safety and useful completion.

## Preexisting work — required disclosure

Everything created on November 5, 2026, including this design, the generator, rule-based baselines, tests, and smoke-check outputs, is **preexisting**. It must be identified as such in the final README and report. Only work actually performed during the sprint may be presented as sprint contributions. `scripts/freeze_preexisting.py` records file hashes. `docs/work-log.md` records the boundary. The final report must separately explain changes made during the sprint, including whether experiments were preregistered before seeing their results.

The current generator constructs synthetic paired cases. Its deterministic checks test implementation and illustrate information constraints. They are **not observations of LLM behaviour, evidence of emergent collusion, or validation of a deployed defence**.

## Run the free preparation checks

Python 3.10+; the experiment scaffolding uses the standard library only.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/run_checks.py --stage preexisting-smoke
python3 scripts/freeze_preexisting.py
```

Free construction-check outputs go to `results/preexisting-smoke/`. Those checks make no external model calls. The separate `scripts/run_model_pilot.py` performs a bounded, billable Adaption inference pilot only when given an API key. It does not start training. All pilot outputs are marked preexisting.

## Review and continue

- `docs/research-plan.md`: hypothesis, controls, limitations, analysis and decision gates.
- `docs/related-work.md`: checked primary sources and limits on novelty claims.
- `docs/operations.md`: deadlines, credit activation, talk links, execution sequence.
- `docs/work-log.md`: completed work and open dependencies.
- `sources/official-template.docx`: original official template; keep unchanged.
- `report/outline.md`: report content plan; not submission-ready.
- `submission/checklist.md`: final requirements and receipt verification.

Personal registration details are kept only in `.private/participant.json`, excluded from source control. There is no connection to the Alma or Camie Upwork accounts.

## Live preparation pilot — November 5 update

The matched-budget exploratory pilot covers three model aliases, 36 unique model inputs, and 54 graded views. The views include reused observations across counterfactual worlds and are not independent trials. See `results/preexisting-model-pilot-20261105-v3/analysis.json` and `report/pre-sprint-brief.pdf`. Integration checks and a token-budget follow-up brought the total physical API call count across pilot versions to 51. The uncached published-rate estimate from recorded usage is approximately 0.0163 credits; no account debit has been independently checked.

The first preparation snapshots and manifest are preserved. Later changes are recorded in additional dated manifests. The pilot tests synthetic quota reasoning and evidence sufficiency; it does not run autonomous workers, show emergent collusion, establish model-family rankings, or constitute the main sprint results. `docs/main-study-candidate.md` sets out the needed extension.

To reproduce the saved analysis without API calls:

```sh
python3 scripts/analyze_pilot.py
python3 -m unittest discover -s tests -v
```
