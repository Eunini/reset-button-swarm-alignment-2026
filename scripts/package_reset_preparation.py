"""Create a sanitized reproducibility package, excluding all credentials/state."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DEST = Path("/home/kamicode/aps/alma/deliverables/swarm-alignment-2026")


def main():
    files = set()
    def add(pattern):
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ["README.md", ".gitignore", "requirements-reset.txt", "src/*.py", "tests/*.py", "scripts/*.py", "docs/*.md",
                    "sources/reset-*.json", "sources/reset-snapshots/**/*.py", "sources/official-template.docx",
                    "sources/official-template.pdf", "sources/official-template.txt",
                    "sources/norm-enforcement/LICENSE", "sources/norm-enforcement/README.md",
                    "sources/norm-enforcement/pyproject.toml", "sources/norm-enforcement/norm_enforcement/**/*.py",
                    "sources/norm-enforcement/configs/*.yaml", "submission/*.md",
                    "results/reset-development-20261105/**/*.json", "results/reset-development-20261105/*.csv",
                    "results/reset-development-v2-20261105/**/*.json", "results/reset-development-v2-20261105/*.csv",
                    "results/reset-development-v2-20261105/figures/*",
                    "report/reset-button-development-report.docx", "report/reset-button-development-report.pdf",
                    "report/reset-report-*.json"]:
        add(pattern)
    # Require a token boundary: random provider IDs can contain an internal 'sk-'.
    forbidden = re.compile(rb"(?<![A-Za-z0-9_-])(?:pt_live_[a-fA-F0-9]{30,}|sk-[A-Za-z0-9_-]{24,})")
    hashes = {}
    for p in sorted(files):
        rel = str(p.relative_to(ROOT))
        if any(x in p.parts for x in (".private", ".venv", ".git", "__pycache__")):
            raise ValueError("forbidden path in package")
        data = p.read_bytes()
        if forbidden.search(data):
            raise ValueError("credential pattern detected; stopped before packaging")
        hashes[rel] = hashlib.sha256(data).hexdigest()
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "stage": "preexisting November 5 preparation",
                "submission_ready": False, "new_weekend_work": "none yet", "files": hashes,
                "credential_scan": "no live credential patterns in allowlisted files",
                "excluded": ["private identity/state", "all credentials", "virtual environment", "git metadata", "bytecode"],
                "baseline_commit": "0568d47da7dc6ab75cc3fa4041bb228f074d91c1"}
    mpath = ROOT / "sources/preexisting-reset-manifest-20261105.json"
    if mpath.exists():
        old = json.loads(mpath.read_text())
        if old["files"] != manifest["files"]:
            raise ValueError("preexisting package changed; preserve the manifest and create a new version")
    else:
        mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    files.add(mpath)
    DEST.mkdir(parents=True, exist_ok=True)
    zip_path = DEST / "reset-button-preparation-package.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for p in sorted(files):
            archive.write(p, str(p.relative_to(ROOT)))
    for name in ["reset-button-development-report.pdf", "reset-button-development-report.docx"]:
        shutil.copy2(ROOT / "report" / name, DEST / name)
    print(json.dumps({"zip": str(zip_path), "files": len(files), "bytes": zip_path.stat().st_size,
                      "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(), "credential_patterns_found": 0,
                      "submitted": False}, indent=2))


if __name__ == "__main__":
    main()
