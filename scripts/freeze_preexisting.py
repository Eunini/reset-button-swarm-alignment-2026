"""Record preparation hashes without backdating or altering original files."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "sources/preexisting-manifest.json"
EXCLUDE = {".private", ".git", ".venv", "__pycache__", ".pytest_cache"}

if DEST.exists():
    raise SystemExit("Manifest already exists. Preserve it; use a new dated delta manifest for later edits.")

paths = sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(x in EXCLUDE for x in p.parts)
               and p != DEST and p.suffix != ".pyc")
value = {"created_utc": datetime.now(timezone.utc).isoformat(),
         "classification": "preexisting preparation, not sprint contributions",
         "note": "Local hashes record content; not an independent timestamp attestation.",
         "files": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
DEST.write_text(json.dumps(value, indent=2) + "\n")
print(f"Recorded {len(paths)} preparation files in {DEST}")
