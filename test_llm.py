from backend.utils.llm_client import ask_gemini
from backend.utils.prompt_builder import build_medical_prompt

sample_report = """
Patient Name: XYZ
Hemoglobin: 9.5 g/dL
WBC Count: 7200
Blood Sugar: 210 mg/dL
"""

prompt = build_medical_prompt(sample_report)

response = ask_gemini(prompt)

print(response)
