# Final sprint report and reproduction

The current report is `report/reset-button-sprint-report.pdf`, titled Reset Button: Reporting Limits, Honest Bursts and Inherited Distrust. This is the post-opening report-load extension, not the earlier identity-reset preparation report. The scientific design was frozen after the November 6, 12:00 UTC opening. All prior work, including the 4,258-request study, is disclosed as preexisting.

Read the repository README for findings and limitations. Read `report/report-load-checks.json` for the exact checked PDF hash and `results/sprint-report-load-20261106/evidence-audit.json` for the full replay audit. The saved-data analysis and report generators make no model calls. All 41 implementation checks pass. The assistant inspected all seven rendered pages; no independent human review is claimed.

The optional interactive reporter follow-ups are closed: the original 96-call protocol had 59 incomplete outputs, the next request returned HTTP 504, and the streaming attempt stopped after 23 calls with one incomplete output. These are calibration failures, not successful defence tests. No inference process is still running.

Use `scripts/package_sprint_report.py` to package the reviewed report and all new evidence. The package excludes private submission fields, credentials and browser state. Earlier preparation artifacts remain separate. Follow `submission/status-20261106.json` for actual submission state; do not infer submission from a completed experiment or generated PDF.

Official deadline: Monday November 9 at 11:59 UTC. Any later revision must preserve accurate prior-work disclosure and raw failed attempts.
