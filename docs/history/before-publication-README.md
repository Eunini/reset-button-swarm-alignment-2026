# Reset Button: Reporting Limits, Honest Bursts and Inherited Distrust

Solo Swarm Alignment Hackathon entry by Inioluwa Atanda. Final during-sprint study and report completed November 6, 2026. Submission status is tracked separately in `submission/status-20261106.json`.

## Current results and scope

The new report is `report/reset-button-sprint-report.pdf`, four main pages plus references and required appendices (seven total). It evaluates 1,024 constructed report streams from 32 task seeds using 28,672 paired exact-checker replays. Those replays are not independent LLM experiments. All 128 paired verifier-control judgments matched actual executor labels. The interactive reporter protocol failed calibration (59/96 incomplete outputs); a subsequent nonstreaming attempt timed out, and a streaming follow-up stopped after 23 requests (22 complete and one incomplete). No model or defence ranking is claimed from these failures.

Under the prespecified eight-warning, sixteen-check condition, root reputation catches 8/8 incidents with no initial honest mistake but 0/8 after one. A root quota of four catches 4/8 and 3/8. Quotas bound false-report demand while capping useful warning bursts; inherited distrust can block a truthful child. These are controlled mechanism results, not evidence of autonomous swarm behaviour, real-world attack prevalence or a new best defence.

## Preexisting work and during-sprint contribution

The official website countdown opens November 6 at 12:00 UTC. ALL earlier work, including the 4,258-request identity-reset study and its findings, is preexisting preparation. Prior assistant claims that part of that study qualified as sprint work were withdrawn. Earlier reports and immutable source snapshots are retained separately; never submit a preparation report as this entry.

The new extension was frozen at 19:48 UTC and executed from 19:48 to 20:47 UTC on November 6. New work includes the legitimate-load/mistake/principal-count/arrival-order comparison, neutrally named counterfactual verifier controls, and the disclosed unsuccessful interactive supplement. `sources/sprint-report-load-plan-20261106.json` records the plan and scientific source hashes. Existing executor, reputation and direct API code are reused and credited. The public norm-enforcement code is pinned at commit 0568d47da7dc6ab75cc3fa4041bb228f074d91c1; its MIT license is retained.

## Reproduce without paid model calls

Install Python dependencies from `requirements-reset.txt`. The final report generator uses the original supplied official DOCX template. LibreOffice can convert the generated DOCX to PDF.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/analyze_report_load.py
python3 scripts/build_report_load_report.py
libreoffice --headless --convert-to pdf --outdir report report/reset-button-sprint-report.docx
python3 scripts/check_report_load_report.py
```

The saved-data analysis makes no API calls. All 41 implementation checks passed. The independent evidence audit recomputed labels, checked raw controls and reproduced all 28,672 replay rows. The coding assistant visually inspected all seven final PDF pages. No independent human review is claimed. Raw receipts, failures, usage and exact plans are included in the sprint research package. Credentials, private registration fields and browser state are excluded.

Earlier preparation data is preserved separately in the earlier research package. Historical instructions and timing mistakes are retained in `docs/history/` and `docs/work-log.md`; this README states the current scope. Optional interactive debugging is closed, and no further live model work is running.

The submission deadline is November 9, 2026 at 11:59 UTC (November 8, 23:59 Anywhere on Earth). There is no guarantee of a prize. Inioluwa Atanda remains responsible for understanding and verifying the entry.
