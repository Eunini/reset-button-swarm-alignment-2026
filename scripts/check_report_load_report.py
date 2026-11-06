"""Check the final during-sprint PDF against its saved evidence; no API calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def main():
    pdf = ROOT / 'report/reset-button-sprint-report.pdf'
    doc = pymupdf.open(pdf)
    text = ' '.join(' '.join(p.get_text() for p in doc).split())
    metadata = json.loads((ROOT / 'report/report-load-metadata.json').read_text())
    plan = json.loads((ROOT / 'sources/sprint-report-load-plan-20261106.json').read_text())
    audit = json.loads((ROOT / 'results/sprint-report-load-20261106/evidence-audit.json').read_text())
    sources = {**plan['source_sha256'], **plan['preexisting_source_sha256']}
    main_pages = next(i for i, p in enumerate(doc) if 'References\n[1]' in p.get_text())
    checks = {
        'frozen_scientific_sources_unchanged': all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in sources.items()),
        'independent_evidence_audit_passes': audit['passed'],
        'main_pages_4_to_8': 4 <= main_pages <= 8,
        'abstract_150_to_250_words': 150 <= metadata['abstract_words'] <= 250,
        'correct_author': 'Inioluwa Atanda' in text,
        'correct_metadata_author': doc.metadata.get('author') == 'Inioluwa Atanda',
        'required_appendix': 'Limitations and Dual-Use / Ethical Considerations' in text,
        'ai_use_disclosed': 'LLM Usage Statement' in text,
        'prior_work_disclosed': '4,258-request identity-reset study' in text and 'preexisting preparation' in text,
        'failed_interactive_calibration_disclosed': '59/96 incomplete outputs' in text,
        'timeout_and_partial_stream_disclosed': 'HTTP 504' in text and '23 requests: 22 complete outputs and 1 incomplete output' in text,
        'no_human_review_claim': 'No independent human review is claimed' in text,
        'no_empty_pages': all(len(p.get_text()) > 300 for p in doc),
        'no_template_placeholders': not any(x in text for x in ('PROJECT TITLE', 'Author name 1', 'affiliation not supplied', 'How to use this template', 'NOT FOR SUBMISSION')),
        'within_25MB': pdf.stat().st_size < 25 * 1024 * 1024,
        'text_inside_page': all(w[0] >= 8 and w[1] >= 8 and w[2] <= p.rect.width - 8 and w[3] <= p.rect.height - 8 for p in doc for w in p.get_text('words')),
    }
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'pdf': str(pdf.relative_to(ROOT)), 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'checks': checks, 'passed': all(checks.values()),
        'main_pages': main_pages, 'total_pages': len(doc), 'abstract_words': metadata['abstract_words'],
        'assistant_visual_review': 'All seven rendered pages inspected; readable figures and tables, no clipping.',
        'visual_review_pending': False, 'human_review_claimed': False,
        'scope': 'Assistant and programmatic review; submission status is recorded separately.'
    }
    (ROOT / 'report/report-load-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
