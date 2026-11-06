# Reset Button: execution and review

**Start-time correction, November 6:** The public page's countdown targets **12:00 UTC**, calculated by `eventStartMs` as the date at UTC midnight plus 12 hours. The earlier midnight-based cutoffs were assistant errors. All current work must be disclosed as preexisting validation/preparation. The prior report is not a finished judged entry, even though its experiments, numerical findings and checks are complete. A substantive extension during the event is needed. Do not describe an identical rerun as a new discovery. Source evidence and preserved report versions are recorded in `sources/reset-study-classification-20261106.json`. This correction supersedes earlier completion and eligibility notes below.

**November 6 completion update:** The main study finished at 03:56 UTC. Recorded requests: 4,258; completed outputs: 4,257; incomplete campaign outputs: one. Both verifiers match executor labels on all 2,097 distinct judged inputs each. The eight-check scripted comparison detects 96/96 incidents with persistent-ID escalating reputation, 27/96 with restarted IDs, and 96/96 with trusted-root history. Fixed trusted-root quotas match the attack repair, so there is no demonstrated new-defence advantage. Evidence and PDF audits pass; the report has four main pages plus references and appendices. No submission has been made. Later status entries supersede earlier pending-work notes below.

This project is a solo entry prepared for Inioluwa Atanda. All November 5 design, code and development results are preexisting. They are not the judged weekend contribution. No submission, public repository, message to organizers, automatic wake-up or future model run has been created.

## Current scope

The workers are scripted actions in a closed synthetic lab. Language models author batches of reports and judge actual recorded sample use. The experiment assigns restarts externally. Do not describe this as an autonomous swarm discovering the attack.

The typed policy could be enforced directly by code, with no LLM oversight calls. The study concerns allocation of a simulated reporting budget. A strong deployment claim would need a richer semantic task and controls for existing rate limits and recovery mechanisms.

## What exists

- `src/reset_button.py`: executor, independent policy labels, matched replay, escalating reputation and the trusted-root adaptation.
- `sources/norm-enforcement/`: pinned public baseline code and MIT license. Our simulation is an adaptation, not an exact reproduction.
- `tests/test_reset_button.py`: scientific invariants and a differential check of the published mathematical update.
- `sources/reset-study-plan-20261105.json`: original frozen development/main plan.
- `sources/reset-study-plan-20261105-v2.json`: explicit amendment after output truncation and rate limits. Original records and source snapshots remain available.
- `results/reset-development-20261105/`: original run, including failed requests.
- `results/reset-development-v2-20261105/`: follow-up and exact successful-request reuse; imported records name their original file.
- `report/reset-button-development-report.docx` and `.pdf`: development report populated from the official template. It is not a submission.

## Reproduce without spending credits

```sh
python3 -m unittest discover -s tests -v
.venv/bin/python scripts/analyze_reset_study.py
.venv/bin/python scripts/build_reset_report.py
```

Analysis reads saved requests, responses, execution labels and replay outcomes. It makes no API calls. DOCX generation preserves the official template's page setup, heading styles and title/abstract structure. PDF conversion uses LibreOffice; inspect the rendered PDF, not just extracted text.

## Main experiment during the sprint

The user supplied a November 6 date and **Europe/Berlin** workspace timezone. The main run uses Friday 00:00 in that timezone (November 5, 23:00 UTC) for date-based accounting and retains actual UTC timestamps. The earlier keynote and midnight-UTC delays were self-imposed, not organizer requirements. The official dates are November 6–8, and talks are optional. Original plans and the development report retain historical wording; `sources/reset-study-plan-20261106-v4.json` records the correction before any held-out run. This is not an assertion of an organizer-specified universal start time.

```sh
.venv/bin/python scripts/launch_reset_sprint.py
```

The launcher checks development competence and availability, runs tests, executes the frozen main configuration on 32 new task seeds, analyzes paired seed-level effects, and generates a report draft. It asks privately for an API key through a hidden terminal prompt, never through a file or source-controlled environment variable. No plugin is required. Keys are held only in process memory.

The finite main allowance is at most 6,000 distinct requests and 40 projected credits; this is a conservative request guard, not a provider-enforced billing cap. Actual usage is recorded. Calls run serially with a three-second minimum start interval, no automatic retries, and stop on rate limits or server errors. A large main run may take several hours. A stopped run requires inspecting the recorded failure before a documented follow-up; do not silently replace failure with success.

The development allowance is separate and much smaller. Do not present cached verdict replays as new paid calls, independent trajectories or independent model trials. For uncertainty estimates, the task seed is the experimental unit. The two-model and multiple-budget comparisons must be reported transparently rather than selecting only the most dramatic cell.

## Final scientific review

1. Verify the reports remain identical across paired identity conditions and that attacker allowance never increases with copies.
2. Check actual execution labels, every invalid output and the call/token ledger.
3. Distinguish competent-verifier failures from missing API responses and output truncation.
4. Include the perfect-verifier and unlimited-budget diagnostics, honest-reporter control and direct-code-enforcement limitation.
5. Inspect the included existing-style root/identity quota controls (1, 2 and 4 checks), added after development inspection and before the main study. If they match the proposal, narrow the claim to the evaluated failure/boundary. An independent audit/recovery channel remains a useful extension, not a completed experiment.
6. Check sensitivity to arrival order, number of distinct reported targets and the price of a new identity. A fixed first-in-first-served budget is not a universal deployment model.
7. Report the identity-invariance of trusted-root history as an implementation property. It is not a discovery of Sybil resistance or an empirical generalization result.

## Final submission

The deadline is Monday November 9, 11:59 UTC (Sunday November 8, 23:59 AoE). Target completion at least one day earlier. Use the current official template, 4–8 main pages, 150–250 abstract words, actual author/affiliation information, references and the required Limitations and Dual-Use / Ethical Considerations appendix. Keep the AI-use disclosure accurate. Verify all numerical claims from saved evidence and inspect every PDF page. Identify precisely what was new during the sprint.

The current draft uses an affiliation placeholder because none was supplied. The entrant needs to confirm that line before submission. No independent human review or organizer approval has been claimed.

The chat has no available automatic continuation or notification tool for this task. This runbook and launcher prepare the work; they do not schedule the assistant to return at the kickoff or submit a report later.
