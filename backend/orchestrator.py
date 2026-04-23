import uuid
import json
from crewai import Crew
from backend.schemas import RawSupplierDataset, FinalSuppliers
from backend.storage import save_json

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

        final_json.setdefault(
            "ranking_method",
            {
                "weights": {
                    "capability_fit": 0.35,
                    "certifications": 0.20,
                    "capacity": 0.20,
                    "lead_time": 0.15,
                    "evidence_quality": 0.10
                }
            }
        )

        suppliers = final_json.get("suppliers", [])
        for idx, s in enumerate(suppliers, start=1):
            if not s.get("supplier_id"):
                s["supplier_id"] = f"sup_{idx:03d}"

            if "fit_score" not in s:
                if isinstance(s.get("score"), (int, float)):
                    val = float(s["score"])
                    s["fit_score"] = val / 100.0 if val > 1 else val
                else:
                    rank = s.get("rank", idx)
                    s["fit_score"] = max(0.0, 1.0 - (rank - 1) * 0.05)

            s.setdefault("strengths", [])
            s.setdefault("gaps", [])
            s.setdefault("risk_flags", [])
            s.setdefault("recommended_next_questions", [])
            s.setdefault("evidence_count", s.get("evidence_count", 0))

    def run(self, query: dict):
        run_id = f"RUN-{uuid.uuid4().hex[:8]}"
        state = "RUN_CREATED"

        # 1) Research
        state = "RESEARCH_IN_PROGRESS"
        crew1 = Crew(agents=[self.researcher], tasks=[self.research_task], verbose=False)
        raw_out = crew1.kickoff(inputs={"query": query, "run_id": run_id})

        # Validation gate (schema)
        state = "RESEARCH_VALIDATION"
        raw_json = json.loads(str(raw_out))
        raw_json["run_id"] = run_id  # enforce

        # Fix: ensure query is a dict, not a plain string
        if isinstance(raw_json.get("query"), str):
            raw_json["query"] = {"text": raw_json["query"]}
        # Fix: if query key is missing entirely, inject it
        if "query" not in raw_json:
            raw_json["query"] = {"text": str(query)}

        # Normalize research_notes to dict if LLM returns string
        rn = raw_json.get("research_notes")
        if isinstance(rn, str):
            raw_json["research_notes"] = {"summary": rn}
        elif rn is None:
            raw_json["research_notes"] = {}

        self._normalize_locations(raw_json)
        raw = RawSupplierDataset.model_validate(raw_json)

        # Hard rule: every supplier must have evidence
        for s in raw.suppliers:
            if len(s.evidence) < 1:
                raise ValueError(f"Supplier '{s.supplier_name}' missing evidence")

        raw_path = save_json(run_id, "raw_supplier_dataset", raw.model_dump(mode="json"))

        # 2) Writing
        state = "WRITING_IN_PROGRESS"
        crew2 = Crew(agents=[self.writer], tasks=[self.write_task], verbose=False)
        writer_out = crew2.kickoff(inputs={"raw_supplier_dataset": raw.model_dump(mode="json"), "run_id": run_id})

        # Parse writer output (two-part)
        text = str(writer_out)
        if "===FINAL_JSON===" not in text or "===REPORT_MD===" not in text:
            raise ValueError("Writer output missing required delimiters ===FINAL_JSON=== / ===REPORT_MD===")

        final_part = text.split("===FINAL_JSON===")[1].split("===REPORT_MD===")[0].strip()
        report_md = text.split("===REPORT_MD===")[1].strip()


        state = "FINAL_VALIDATION"
        final_json = json.loads(final_part)
        final_json["run_id"] = run_id  # enforce

        self._normalize_final(final_json, run_id)

        final = FinalSuppliers.model_validate(final_json)

        final_path = save_json(run_id, "final_suppliers", final.model_dump(mode="json"))
        # Save report as a text file (optional)
        with open(f"artifacts/{run_id}_report.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        state = "COMPLETED"
        return {
            "run_id": run_id,
            "state": state,
            "raw_dataset_path": raw_path,
            "final_suppliers_path": final_path,
            "report_path": f"artifacts/{run_id}_report.md"
        }
    
    @staticmethod
    def _normalize_locations(raw_json: dict) -> None:
        suppliers = raw_json.get("suppliers", [])
        for s in suppliers:
            locs = s.get("locations", [])
            fixed = []
            for loc in locs:
                if isinstance(loc, str):
                    fixed.append(loc)
                elif isinstance(loc, dict):
                    city = loc.get("city")
                    state = loc.get("state")
                    country = loc.get("country")
                    parts = [p for p in [city, state, country] if p]
                    fixed.append(", ".join(parts) if parts else str(loc))
                else:
                    fixed.append(str(loc))
            s["locations"] = fixed


