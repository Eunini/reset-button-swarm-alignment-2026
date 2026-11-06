"""Download the public report template linked by the event guidelines."""
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/export?format=docx'


def main():
    target = ROOT / 'sources/official-template.docx'
    if target.exists():
        print('The official template is already present; keeping the existing file.')
        return
    with urlopen(URL, timeout=30) as response:
        data = response.read(10 * 1024 * 1024)
    with ZipFile(BytesIO(data)) as doc:
        if 'word/document.xml' not in doc.namelist():
            raise ValueError('The response is not a Word document')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print('Saved sources/official-template.docx from the official event template.')


if __name__ == '__main__':
    main()
