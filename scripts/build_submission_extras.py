"""Build submission slides and a project image from recorded study results."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from textwrap import dedent

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/submission-extras'
NAVY, TEAL, AMBER, INK, MUTED, PAPER = '#17373A', '#237D70', '#AD6D18', '#203538', '#53676B', '#F5F7F4'
REPO = 'https://github.com/Eunini/reset-button-swarm-alignment-2026'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = json.loads((ROOT / 'results/sprint-report-load-20261106/analysis.json').read_text())
    s = json.loads((ROOT / 'results/sprint-report-load-20261106/summary.json').read_text())
    policies = ['root_rep', 'quota:4', 'quota:8', 'identity_rep']
    names = ['Root reputation', 'Root quota 4', 'Root quota 8', 'Process reputation']
    def value(policy, mistake):
        return next(r['detected'] for r in a['primary'] if r['policy'] == policy and r['initial_mistake'] == mistake)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.labelcolor': INK, 'text.color': INK})
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    x = np.arange(len(policies))
    for delta, mistake, color, label in [(-.18, 0, TEAL, 'No initial honest mistake'), (.18, 1, AMBER, 'One initial honest mistake')]:
        bars = ax.bar(x + delta, [value(p, mistake) for p in policies], width=.34, color=color, label=label)
        for b in bars:
            y = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, y + .12, f'{y:.2f}'.rstrip('0').rstrip('.') + '/8', ha='center', fontsize=12)
    ax.set_xticks(x, names); ax.set_ylim(0, 9.7); ax.set_yticks(range(0, 9, 2))
    ax.set_ylabel('Mean genuine incidents detected')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, 1.13), ncol=2, frameon=False)
    ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
    fig.tight_layout(pad=1.8)
    chart = OUT / 'primary-comparison.png'
    fig.savefig(chart, dpi=160); plt.close(fig)

    font_dir = Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('Body', str(font_dir / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('BodyBold', str(font_dir / 'DejaVuSans-Bold.ttf')))
    W, H = 960, 540
    pdf = OUT / 'reset-button-slides.pdf'
    c = canvas.Canvas(str(pdf), pagesize=(W, H))
    c.setTitle('Reset Button — research walkthrough')
    c.setAuthor('Inioluwa Atanda')
    n = [0]
    def text(body, x, y, width=840, size=20, color=INK, bold=False):
        st = ParagraphStyle('p', fontName='BodyBold' if bold else 'Body', fontSize=size, leading=size*1.34, textColor=HexColor(color))
        p = Paragraph(body, st); _, h = p.wrap(width, 480)
        if y-h < 38:
            raise ValueError('Slide content exceeds the safe area')
        p.drawOn(c, x, y-h)
        return y-h
    def start(kicker, title, subtitle=''):
        n[0] += 1
        c.setFillColor(HexColor(PAPER)); c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(HexColor(TEAL)); c.rect(0, 0, 14, H, fill=1, stroke=0)
        text(kicker.upper(), 48, 503, size=11, color=TEAL, bold=True)
        text(title, 48, 469, size=29, color=NAVY, bold=True)
        if subtitle: text(subtitle, 48, 416, size=13, color=MUTED)
        c.setFont('Body', 9); c.setFillColor(HexColor(MUTED))
        c.drawString(48, 18, 'Inioluwa Atanda | Swarm Alignment Hackathon 2026')
        c.drawRightString(915, 18, f'{n[0]} / 6')
    def bullet(body, y, size=20):
        c.setFillColor(HexColor(TEAL)); c.circle(56, y-11, 3, fill=1, stroke=0)
        return text(body, 74, y, 820, size=size) - 24
    def end(): c.showPage()

    start('Research question', 'Reset Button', 'Reporting Limits, Honest Bursts and Inherited Distrust')
    text('Can a control reject false complaints<br/>without silencing real warnings?', 48, 359, size=32, bold=True)
    y = bullet('Strict reporting limits can also limit useful warnings.', 238)
    y = bullet('A truthful child can inherit a parent’s low reputation.', y)
    text('Controlled synthetic evaluation. No new-defence or autonomous-swarm claim.', 48, 96, size=13, color=MUTED)
    end()

    start('Study design', 'The same workloads, replayed across controls', 'Frozen after the event opened; new extension executed November 6, 19:48–20:47 UTC.')
    text(f"{s['task_seeds']} task seeds      1,024 streams      {s['oracle_replays']:,} paired replays", 48, 354, size=25, bold=True)
    y = bullet('Vary honest warning load, an initial mistake, attacker roots and arrival order.', 291, 19)
    y = bullet('Compare process/root reputation, checking every report and root quotas 1/2/4/8.', y, 19)
    y = bullet('Hold the attack allowance at 24 reports; use global check budgets of 8 or 16.', y, 19)
    text('The sweep uses scripted workers and exact executor labels. Replay count is not a count of independent model experiments.', 48, 103, size=14, color=MUTED)
    end()

    start('Primary result', 'Protection depends on honest mistakes', 'Eight genuine warnings, sixteen checks, one attacker root, mixed arrivals and reset aliases; 32 paired seeds.')
    c.drawImage(str(chart), 48, 141, width=864, height=250, preserveAspectRatio=True, anchor='c', mask='auto')
    text('Root reputation falls from 8/8 to 0/8 after the initial mistake.<br/>Quota four detects 4/8 and 3/8: bounded checking also caps useful warnings.', 48, 109, size=17)
    end()

    start('Why it happens', 'A warning needs a path back to being checked')
    y = bullet('A fixed quota bounds false-report demand, but a busy honest root hits the same cap.', 366, 23)
    y = bullet('A mistaken complaint lowers root reputation below the single-report checking threshold.', y, 23)
    y = bullet('Distinct truthful reports then receive no checks, so they cannot restore reputation.', y, 23)
    text('These are structural results under the specified policies. Changing feedback rules, thresholds or capacity can change them.', 48, 110, size=15, color=MUTED)
    end()

    start('Model evidence and limits', 'Separate successful controls from failed calibration')
    y = bullet('128/128 verifier-control judgments matched executor labels across two models and 16 shared seeds.', 365, 21)
    y = bullet('The interactive reporter protocol produced 59/96 incomplete outputs. It supports no policy or model ranking.', y, 21)
    y = bullet('A higher-budget request timed out. Streaming then stopped after 23 requests: 22 complete, one incomplete.', y, 21)
    text('The main sweep is exact-checker and scripted. No emergent collusion, real-world prevalence or frontier-model transfer is established.', 48, 93, size=14, color=MUTED)
    end()

    start('Takeaway and reproducibility', 'Test useful reporting as well as malicious demand')
    y = bullet('Evaluate honest bursts and recovery after mistakes alongside resistance to false-report floods.', 366, 23)
    y = bullet('Source, frozen plans, raw evidence, failures and full replay data accompany the report.', y, 20)
    y = bullet('All earlier preparation is disclosed as preexisting; existing mechanisms and third-party code are credited.', y, 20)
    text(REPO, 48, 143, size=14, color=TEAL)
    text('AI assistance was used for design, code, analysis and writing. Inioluwa Atanda is the sole human entrant. No independent human review is claimed.', 48, 99, size=12, color=MUTED)
    end(); c.save()

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=PAPER)
    fig.text(.055, .89, 'RESET BUTTON', fontsize=48, weight='bold', color=NAVY)
    fig.text(.058, .81, 'When filtering false reports silences real warnings', fontsize=23, color=MUTED)
    fig.text(.058, .69, 'Root reputation in the prespecified synthetic condition', fontsize=17, color=INK)
    for x0, number, label, color in [(.07, value('root_rep', 0), 'No initial honest mistake', TEAL), (.54, value('root_rep', 1), 'One initial honest mistake', AMBER)]:
        fig.text(x0, .40, f'{number:.0f}/8', fontsize=112, weight='bold', color=color)
        fig.text(x0+.005, .30, label, fontsize=22, color=INK)
    fig.text(.058, .16, '8 genuine incidents · 16-check budget · 32 paired task seeds', fontsize=18, color=INK)
    fig.text(.058, .105, 'Scripted workers and an exact checker; no autonomous-swarm or new-defence claim.', fontsize=15, color=MUTED)
    fig.text(.058, .045, 'Inioluwa Atanda  |  Swarm Alignment Hackathon 2026', fontsize=14, color=MUTED)
    project_image = OUT / 'reset-button-project-image.png'
    fig.savefig(project_image, dpi=100, facecolor=PAPER); plt.close(fig)

    script = dedent('''\
        RESET BUTTON — WALKTHROUGH SCRIPT
        Target duration: 3–5 minutes. This is a script, not an existing recording.
        Only record claims you have read and understood. Show the real source, data and report.

        SLIDE 1 — THE QUESTION (about 25 seconds)
        This project asks a simple question. If AI workers can report problems with each other, how do we stop false complaints without blocking real warnings? Reset Button studies reporting limits and reputation. It also asks what happens when a truthful child worker inherits a parent's bad reputation.

        SLIDE 2 — WHAT WAS TESTED (about 40 seconds)
        The new sprint extension uses 32 task seeds to construct 1,024 report streams. It varies how many genuine warnings arrive, whether an honest parent made one mistake, how many attacker roots exist and the report order. Every attacker group has the same total allowance of 24 reports. The same streams are replayed across seven controls, two checking budgets and two alias conditions. That gives 28,672 paired replays. These are scripted mechanism tests, not that many independent AI experiments.

        SLIDE 3 — THE MAIN RESULT (about 40 seconds)
        In the primary condition, there are eight genuine incidents and a budget of sixteen checks. With no initial honest mistake, root reputation finds all eight. With one initial mistake, it finds none. A root quota of four finds four and three respectively. A quota of eight finds eight and seven. No policy is shown to be best in every setting. The chart reports the same prespecified condition and 32 paired seeds for each policy.

        SLIDE 4 — WHAT THAT MEANS (about 30 seconds)
        A fixed quota limits malicious demand, but it also limits a busy honest reporter. Reputation avoids that fixed cap until a mistake reduces trust below the threshold for checking a single report. Later correct reports about different targets are then ignored. Without being checked, those reports cannot earn the feedback that would restore trust. This result depends on the particular threshold and feedback rule.

        SLIDE 5 — WHAT WORKED AND WHAT DID NOT (about 40 seconds)
        Separate controls tested two hosted models on paired safe and unsafe records with neutral worker names. All 128 judgments matched executor labels, but they share only sixteen seeds. The optional interactive reporter test did not work reliably. Fifty-nine of ninety-six outputs were incomplete. A higher-budget request timed out, and a streaming follow-up stopped after twenty-three requests, including one incomplete output. Those tests do not support a defence or model ranking. The main study remains a scripted, exact-checker evaluation.

        SLIDE 6 — WHAT OTHERS CAN USE (about 35 seconds)
        The contribution is a reproducible test of honest reporting load and inherited distrust. The code, frozen plans, raw evidence and failed attempts are retained. The public reputation rule and its code are credited, and all work before the event opening is disclosed as preparation. AI assistance was used for design, implementation, analysis and writing. Inioluwa Atanda is the sole human entrant; no independent human review is claimed. The main lesson is to measure useful warnings and recovery after mistakes, as well as false-report demand.

        OPTIONAL LIVE VIEW
        Open src/report_load.py and results/sprint-report-load-20261106/analysis.json.
        Show: python3 -m unittest discover -s tests -v
        This command performs implementation checks without paid model calls.
        Do not present the 41 software checks as 41 research experiments.
    ''')
    (OUT / 'reset-button-walkthrough-script.txt').write_text(script)
    import pymupdf
    doc = pymupdf.open(pdf)
    assert len(doc) == 6
    for i, page in enumerate(doc):
        page.get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(str(OUT / f'slide-{i+1}.png'))
    paths = [pdf, chart, project_image, OUT / 'reset-button-walkthrough-script.txt']
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'slide_pages': len(doc),
                'primary_values_loaded_from_recorded_analysis': True,
                'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                'presentation_recording_exists': False, 'human_review_claimed': False}
    (OUT / 'extras-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
