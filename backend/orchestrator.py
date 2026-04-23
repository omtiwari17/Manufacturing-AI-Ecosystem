import uuid
import json
import re
import os
from crewai import Crew
from backend.schemas import RawSupplierDataset, FinalSuppliers
from backend.storage import save_json


def _extract_json(text: str) -> dict:
    """Robustly extract a JSON object from LLM output."""
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        pass
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    raise ValueError(f"Could not extract JSON from LLM output. First 500 chars: {text[:500]}")


class Orchestrator:
    def __init__(self, researcher, writer, research_task, write_task):
        self.researcher = researcher
        self.writer = writer
        self.research_task = research_task
        self.write_task = write_task

    @staticmethod
    def _normalize_final(final_json: dict, run_id: str) -> None:
        final_json.setdefault("artifact_version", "1.0")
        final_json["run_id"] = run_id
        final_json.setdefault("ranking_method", {"weights": {"capability_fit": 0.35, "certifications": 0.20, "capacity": 0.20, "lead_time": 0.15, "evidence_quality": 0.10}})
        for idx, s in enumerate(final_json.get("suppliers", []), start=1):
            if not s.get("supplier_id"):
                s["supplier_id"] = f"sup_{idx:03d}"
            if "fit_score" not in s:
                if isinstance(s.get("score"), (int, float)):
                    val = float(s["score"])
                    s["fit_score"] = val / 100.0 if val > 1 else val
                else:
                    s["fit_score"] = max(0.0, 1.0 - (s.get("rank", idx) - 1) * 0.05)
            s.setdefault("strengths", [])
            s.setdefault("gaps", [])
            s.setdefault("risk_flags", [])
            s.setdefault("recommended_next_questions", [])
            s.setdefault("evidence_count", s.get("evidence_count", 0))

    @staticmethod
    def _normalize_locations(raw_json: dict) -> None:
        for s in raw_json.get("suppliers", []):
            fixed = []
            for loc in s.get("locations", []):
                if isinstance(loc, str):
                    fixed.append(loc)
                elif isinstance(loc, dict):
                    parts = [p for p in [loc.get("city"), loc.get("state"), loc.get("country")] if p]
                    fixed.append(", ".join(parts) if parts else str(loc))
                else:
                    fixed.append(str(loc))
            s["locations"] = fixed

    def run(self, query: dict):
        run_id = f"RUN-{uuid.uuid4().hex[:8]}"

        # 1) Research
        crew1 = Crew(agents=[self.researcher], tasks=[self.research_task], verbose=False)
        raw_out = crew1.kickoff(inputs={"query": query, "run_id": run_id})

        raw_json = _extract_json(str(raw_out))
        raw_json["run_id"] = run_id

        if isinstance(raw_json.get("query"), str):
            raw_json["query"] = {"text": raw_json["query"]}
        if "query" not in raw_json:
            raw_json["query"] = {"text": str(query)}

        rn = raw_json.get("research_notes")
        if isinstance(rn, str):
            raw_json["research_notes"] = {"summary": rn}
        elif rn is None:
            raw_json["research_notes"] = {}

        self._normalize_locations(raw_json)
        raw = RawSupplierDataset.model_validate(raw_json)
        raw_path = save_json(run_id, "raw_supplier_dataset", raw.model_dump(mode="json"))

        # 2) Writing
        crew2 = Crew(agents=[self.writer], tasks=[self.write_task], verbose=False)
        writer_out = crew2.kickoff(inputs={"raw_supplier_dataset": raw.model_dump(mode="json"), "run_id": run_id})
        text = str(writer_out)

        if "===FINAL_JSON===" in text and "===REPORT_MD===" in text:
            final_part = text.split("===FINAL_JSON===")[1].split("===REPORT_MD===")[0].strip()
            report_md = text.split("===REPORT_MD===")[1].strip()
            final_json = _extract_json(final_part)
        else:
            try:
                final_json = _extract_json(text)
                report_md = f"# Supplier Research Report\n\nRun ID: {run_id}\n\n{text}"
            except Exception:
                final_json = {
                    "artifact_version": "1.0",
                    "run_id": run_id,
                    "ranking_method": {"weights": {}},
                    "suppliers": [
                        {
                            "supplier_id": f"sup_{i+1:03d}",
                            "supplier_name": s.supplier_name,
                            "fit_score": round(0.8 - i * 0.05, 2),
                            "strengths": list(s.capabilities[:3]),
                            "gaps": [],
                            "risk_flags": [],
                            "recommended_next_questions": [],
                            "evidence_count": len(s.evidence)
                        }
                        for i, s in enumerate(raw.suppliers)
                    ]
                }
                report_md = f"# Supplier Research Report\n\nRun ID: {run_id}\n\n{text}"

        final_json["run_id"] = run_id
        self._normalize_final(final_json, run_id)
        final = FinalSuppliers.model_validate(final_json)
        final_path = save_json(run_id, "final_suppliers", final.model_dump(mode="json"))

        os.makedirs("artifacts", exist_ok=True)
        with open(f"artifacts/{run_id}_report.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        return {
            "run_id": run_id,
            "state": "COMPLETED",
            "raw_dataset_path": raw_path,
            "final_suppliers_path": final_path,
            "report_path": f"artifacts/{run_id}_report.md"
        }