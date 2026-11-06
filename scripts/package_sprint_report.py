"""Package the during-sprint evidence and report, excluding credentials and identity state."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('/home/kamicode/aps/alma/deliverables/swarm-alignment-2026')


def main():
    checks = json.loads((ROOT / 'report/report-load-checks.json').read_text())
    if not checks['passed'] or checks['visual_review_pending']:
        raise RuntimeError('Final report review is incomplete')
    pdf = ROOT / 'report/reset-button-sprint-report.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != checks['sha256']:
        raise RuntimeError('PDF changed since review')
    files = set()
    for pattern in (
        'README.md', 'LICENSE', 'requirements-reset.txt', 'requirements-extras.txt', '.gitignore', 'src/*.py', 'tests/*.py', 'scripts/*.py',
        'submission/status-20261106.json',
        'docs/*.md', 'docs/history/*.md',
        'sources/sprint-*.json', 'sources/reset-study-classification-20261106.json',
        'sources/reset-study-plan-*.json', 'sources/reset-quota-controls-plan-20261105.json',
        'sources/reset-snapshots/**/*', 'sources/norm-enforcement/**/*',
        'sources/official-template.*', 'sources/event-timing-js/*.js', 'sources/event-page-timing-20261106.html',
        'results/sprint-report-load-20261106/**/*', 'results/sprint-interactive-v2-20261106/**/*',
        'results/sprint-interactive-v3-20261106/**/*',
        'report/reset-button-sprint-report.*', 'report/report-load-metadata.json',
        'report/report-load-checks.json',
        'report/submission-extras/*.pdf', 'report/submission-extras/reset-button-project-image.png',
        'report/submission-extras/*.txt', 'report/submission-extras/*.json',
    ):
        files.update(p for p in ROOT.glob(pattern) if p.is_file() and not any(x in p.parts for x in ('.git', '__pycache__', '.private', '.venv')))
    manifest_path = ROOT / 'sources/sprint-report-load-package-manifest-20261106.json'
    files.discard(manifest_path)
    forbidden = re.compile(rb'(?<![A-Za-z0-9_-])(?:pt_live_[a-fA-F0-9]{30,}|sk-[A-Za-z0-9_-]{24,})')
    hashes = {}
    for path in sorted(files):
        data = path.read_bytes()
        if forbidden.search(data):
            raise RuntimeError('Credential pattern detected; package not written')
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    manifest = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'during-sprint report-load extension; earlier code and studies are disclosed as preexisting',
        'files': hashes, 'report_sha256': checks['sha256'], 'credential_patterns_found': 0,
        'baseline_commit': '0568d47da7dc6ab75cc3fa4041bb228f074d91c1',
        'scope': 'New extension data, all failed supplemental attempts, source and provenance. Earlier preparation data is preserved separately.',
        'excluded': ['credentials', 'private submission/identity state', 'browser profiles', 'virtual environment', 'git metadata', 'bytecode']
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    files.add(manifest_path)
    DEST.mkdir(parents=True, exist_ok=True)
    package = DEST / 'reset-button-sprint-research-package.zip'
    with ZipFile(package, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, str(path.relative_to(ROOT)))
    for suffix in ('pdf', 'docx'):
        shutil.copy2(ROOT / f'report/reset-button-sprint-report.{suffix}', DEST / f'reset-button-sprint-report.{suffix}')
    result = {'package': str(package), 'files': len(files), 'bytes': package.stat().st_size,
              'sha256': hashlib.sha256(package.read_bytes()).hexdigest(), 'pdf_sha256': checks['sha256'],
              'credential_patterns_found': 0}
    (DEST / 'sprint-package-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
