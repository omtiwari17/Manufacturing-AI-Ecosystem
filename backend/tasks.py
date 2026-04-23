from crewai import Task

def research_task(agent):
    return Task(
        description=(
            "Input manufacturing sourcing query: {query}\n\n"
            "Return ONLY a JSON object with keys:\n"
            "artifact_version, run_id, query, suppliers, research_notes.\n\n"
            "Each supplier must include:\n"
            "supplier_name, locations[], capabilities[], materials[], certifications[], contact{}, evidence[].\n"
            "Evidence must include: url, notes.\n"
            "No markdown. No explanations. JSON only."
        ),
        expected_output="Valid RawSupplierDataset JSON only.",
        agent=agent
    )

def write_task(writer):
    return Task(
        description=(
            "You are given a supplier research dataset: {raw_supplier_dataset}\n\n"
            "Do the following:\n"
            "1) Normalize supplier fields.\n"
            "2) Score and rank suppliers for the query.\n\n"
            "Return output in EXACT format:\n"
            "===FINAL_JSON===\n"
            "{\n"
            '  "artifact_version": "1.0",\n'
            '  "run_id": "{run_id}",\n'
            '  "ranking_method": {"weights": {"capability_fit": 0.35, "certifications": 0.20, "capacity": 0.20, "lead_time": 0.15, "evidence_quality": 0.10}},\n'
            '  "suppliers": [\n'
            "    {\n"
            '      "supplier_id": "sup_001",\n'
            '      "supplier_name": "...",\n'
            '      "fit_score": 0.0,\n'
            '      "rank": 1,\n'
            '      "strengths": [],\n'
            '      "gaps": [],\n'
            '      "risk_flags": [],\n'
            '      "recommended_next_questions": [],\n'
            '      "evidence_count": 0\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "===REPORT_MD===\n"
            "<markdown report>\n"
            "No extra text."
        ),
        expected_output="Final JSON and markdown report in the exact delimiter format.",
        agent=writer,
    )
