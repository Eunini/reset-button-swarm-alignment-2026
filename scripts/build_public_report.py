"""Create a public research-note edition while preserving the official report."""
from pathlib import Path
from docx import Document

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'report/reset-button-sprint-report.docx'
    target = ROOT / 'report/reset-button-research-note.docx'
    doc = Document(source)
    doc.core_properties.title = 'Reset Button: Reporting Limits, Honest Bursts and Inherited Distrust'
    doc.core_properties.author = 'Inioluwa Atanda'
    doc.core_properties.subject = 'Research note on reporting controls and inherited trust'
    for section in doc.sections:
        for p in section.header.paragraphs:
            if p.text:
                p.text = 'RESET BUTTON | RESEARCH NOTE'
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.text = run.text.replace('Independent researcher • solo entry', 'Independent researcher')
    for p in list(doc.paragraphs):
        if p.text.startswith('[3] Apart Research.'):
            p._element.getparent().remove(p._element)
            continue
        for run in p.runs:
            run.text = (run.text
                        .replace('Prior Work and Sprint Contributions', 'Prior Work and Study Contributions')
                        .replace('During the sprint, the project added', 'For the present study, the project added')
                        .replace('These new experiments and their analysis form this submission.', 'These new experiments and their analysis form the present study.')
                        .replace('[4] Adaption Labs.', '[3] Adaption Labs.'))
    doc.save(target)
    print(target)


if __name__ == '__main__':
    main()
