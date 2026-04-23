import json
from pathlib import Path
from typing import Any, Dict

ARTIFACT_DIR = Path("artifacts")

def ensure_dirs():
    ARTIFACT_DIR.mkdir(exist_ok=True)

def save_json(run_id: str, name: str, data: Dict[str, Any]) -> str:
    ensure_dirs()
    path = ARTIFACT_DIR / f"{run_id}_{name}.json"
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return str(path)

def load_json(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
