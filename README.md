# Reset Button

**Reporting Limits, Honest Bursts and Inherited Distrust**  
Inioluwa Atanda · Solo entry · Swarm Alignment Hackathon 2026

Can a reporting control reject false complaints without silencing real warnings? This project tests fixed reporting limits and reputation when agents can restart with new names, when one honest root has many useful warnings, and when a truthful child inherits its parent's mistake.

[Research report](report/reset-button-sprint-report.pdf) · [Slides](report/submission-extras/reset-button-slides.pdf) · [Project image](report/submission-extras/reset-button-project-image.png) · [Frozen plan](sources/sprint-report-load-plan-20261106.json)

## Findings

In the prespecified condition with eight genuine incidents, sixteen available checks, one attacker root and mixed arrivals:

| Control | No initial honest mistake | One initial honest mistake |
|---|---:|---:|
| Root reputation | 8/8 detected | 0/8 detected |
| Root quota 4 | 4/8 | 3/8 |
| Root quota 8 | 8/8 | 7/8 |
| Process reputation | 3.84/8 | 3.53/8 |

Each cell averages 32 paired task seeds under reset aliases. Fixed quotas limit malicious checking demand, but they also cap useful warnings. Root reputation avoids that cap until a mistake lowers trust enough to prevent future distinct reports from being checked. Those reports then cannot earn feedback to restore trust.

The full sweep has 1,024 constructed streams and 28,672 paired replays. It uses scripted workers and exact executor labels. It does not measure autonomous swarm behaviour or establish that one control works best everywhere.

## Model controls and unsuccessful tests

Two hosted models each matched all 64 executor labels in paired verifier controls. These 128 judgments share sixteen seeds and are not independent scenarios. Worker names and allegation text are matched across safe/unsafe worlds to reduce shortcuts.

The optional interactive reporter protocol failed calibration: 59 of 96 outputs were incomplete. A higher-budget nonstreaming request then timed out, and streaming stopped after 23 requests (22 complete, one incomplete). All failed attempts are retained. They support no policy or model ranking.

## Run the saved-data analysis

Python 3.10+ is sufficient for the implementation checks. Analysis and document generation require the packages in `requirements-reset.txt`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-reset.txt
python3 -m unittest discover -s tests -v
.venv/bin/python scripts/analyze_report_load.py
```

These commands make no paid model calls. All 41 implementation checks passed. `results/sprint-report-load-20261106/evidence-audit.json` records separate label, raw-response and full-replay checks. Software tests are not independent research experiments.

To rebuild the report, download the original template from the official Guidelines link, then generate the document. LibreOffice is used for PDF conversion:

```sh
.venv/bin/python scripts/fetch_official_template.py
.venv/bin/python scripts/build_report_load_report.py
libreoffice --headless --convert-to pdf --outdir report report/reset-button-sprint-report.docx
.venv/bin/python scripts/check_report_load_report.py
```

Slides and the project image can be regenerated with `scripts/build_submission_extras.py` after installing `requirements-extras.txt`. The walkthrough text is a recording script; it is not an existing presentation recording.

## What was done during the sprint

The event website countdown opened November 6, 2026 at 12:00 UTC. The new report-load extension was frozen at 19:48 UTC and executed from 19:48 to 20:47 UTC. Its contribution is the workload/mistake/principal-count/arrival-order sweep, neutral-name verifier controls and the disclosed unsuccessful interactive supplement.

All earlier code, design and results, including the 4,258-request identity-reset study, are **preexisting preparation**. Earlier timing interpretations were corrected; none of that study is claimed as new sprint work. Prior plans, source snapshots and the correction record are preserved. The new extension reuses the existing executor, transport and reputation implementation. It does not claim that persistent identity, reputation or quotas are new inventions.

## Authorship and AI use

Inioluwa Atanda is the sole human author and entrant. AI assistance was used for study design, implementation, literature review, analysis and report drafting. Adaption-hosted models supplied the recorded verifier judgments and prompted reporter outputs. Programmatic checks and assistant review were performed; no independent human review is claimed. The entrant remains responsible for understanding and verifying the submission.

## Prior research and licence

The reputation baseline adapts [Ye and Steinhardt, Norm Enforcement for AI Agents](https://arxiv.org/abs/2607.09766v1) and its [MIT-licensed code](https://github.com/helloelwin/norm-enforcement), pinned at commit `0568d47da7dc6ab75cc3fa4041bb228f074d91c1`. Its copyright and licence notice are retained in `sources/norm-enforcement/LICENSE`. The adaptation is not an exact reproduction. Replaceable identity and reputation are also studied by [Gatta, Naviglio and Tarantelli](https://arxiv.org/abs/2609.02992v2).

Project code is provided under the MIT licence; third-party material retains its original rights and notices. The report details the threat model, limitations, AI use and ethical considerations. No credentials or private registration fields are included.
