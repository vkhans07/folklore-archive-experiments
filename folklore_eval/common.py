import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "outputs"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(data):
    if not isinstance(data, bytes):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def safe_name(doc_id):
    return Path(doc_id).stem


def manifest():
    docs = read_json(ROOT / "config/manifest.json")["documents"]
    ids = [d["doc_id"] for d in docs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate doc_id in manifest")
    paths = [str((ROOT / d["pdf"]).resolve()) for d in docs]
    if len(paths) != len(set(paths)):
        raise ValueError("One PDF mapped to multiple document IDs")
    return docs


def evaluation_directory(output, phase, target, prompt_version=None):
    base = output / "evaluation"
    if target == "archive":
        base = base / "archive"
    base = base / phase
    if prompt_version in ("regions_v3", "archive_v3"):
        base = base / prompt_version
    return base


def run_directory(output, phase, target, prompt_version=None):
    if target == "archive":
        return output / "runs" / "archive" / phase
    if prompt_version == "regions_v3":
        return output / "runs" / "regions_v3" / phase
    return output / "runs" / phase
