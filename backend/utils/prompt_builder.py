def _summary_profile(summary_length: int) -> tuple[str, str, list[str]]:
    profiles = {
        1: ("ultra concise", "about 90-140 words", ["Matter", "Key Findings", "Recommendations"]),
        2: ("concise", "about 150-220 words", ["Matter", "Key Findings", "Diagnoses Mentioned", "Recommendations"]),
        3: ("balanced", "about 250-350 words", ["Matter", "Key Findings", "Diagnoses Mentioned", "Medications", "Laboratory Findings", "Recommendations"]),
        4: ("detailed", "about 400-550 words", ["Matter", "Key Findings", "Diagnoses Mentioned", "Medications", "Laboratory Findings", "Document Findings", "Abnormal Findings", "Recommendations"]),
        5: ("very detailed", "about 550-750 words", ["Matter", "Key Findings", "Diagnoses Mentioned", "Medications", "Laboratory Findings", "Document Findings", "Abnormal Findings", "Recommendations"]),
    }
    return profiles.get(max(1, min(5, summary_length)), profiles[3])


def build_medical_prompt(
    report_text: str,
    summary_style: str = "Clinical",
    summary_length: int = 3,
    merge_multiple_files: bool = True,
    extract_medical_entities: bool = True,
    highlight_abnormal_findings: bool = True,
) -> str:
    profile_name, target_words, sections = _summary_profile(summary_length)

    merge_instruction = (
        "Merge all uploaded document files into one unified clinical response."
        if merge_multiple_files
        else "Summarize each uploaded file separately, then provide one overall clinical takeaway."
    )

    entity_instruction = (
        "Include key medical entities in a compact way when they are explicitly present."
        if extract_medical_entities
        else "Do not add a separate medical-entities emphasis; keep the response more narrative."
    )

    abnormal_instruction = (
        "Clearly surface abnormal or critical findings without alarmist language."
        if highlight_abnormal_findings
        else "If abnormalities are present, mention them neutrally without special emphasis."
    )

    section_rules = "\n".join(f"- {section}" for section in sections)

    prompt = f"""
You are a premium medical AI assistant. Write a clean, human-readable clinical summary for the uploaded medical documents.

Style: {summary_style}
Length profile: {profile_name}.
Target length: {target_words}.

Output rules:
- Do NOT return JSON.
- Do NOT use code blocks.
- Do NOT repeat the raw report.
- Do NOT invent facts, diagnoses, or values.
- Keep the tone calm, professional, and assistant-like.
- Make the response feel like a helpful chatbot answer.
- Use concise headings and bullets where useful.
- If a section is unavailable, write "Not mentioned."
- Keep the response aligned to the selected length profile.

Required sections:
{section_rules}

Section guidance:
- Matter: write the opening paragraph first.
- Key Findings: list only the most important findings.
- Diagnoses Mentioned: include only diagnoses explicitly present.
- Medications: include only medications explicitly present.
- Laboratory Findings: include only relevant lab values or states.
- Document Findings: include notable observations from the uploaded documents.
- Abnormal Findings: include only clear abnormalities, if any.
- Recommendations: keep this brief and document-grounded.

Behavior notes:
- {merge_instruction}
- {entity_instruction}
- {abnormal_instruction}
- If multiple files disagree, mention the discrepancy briefly.
- If the documents are sparse, keep the response concise.
- If the selected length is short, compress the sections and avoid extra commentary.
- If the selected length is high, expand the Matter section and provide fuller bullet detail.

Medical content to summarize:

{report_text}
"""
    return prompt.strip()
