import os
import re
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"

_CODE_FENCE_RE = re.compile(r"^```(?:json|markdown|text)?\s*|\s*```$", re.IGNORECASE | re.DOTALL)


def _clean_response(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = _CODE_FENCE_RE.sub("", cleaned).strip()
    return cleaned


def ask_gemini(prompt: str) -> str:
    if not api_key:
        return f"LLM Error: No GEMINI_API_KEY found. Set GEMINI_API_KEY in {ROOT_DIR / '.env'} or your environment."

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        cleaned = _clean_response(text)
        return cleaned or "No response was returned by the model."
    except Exception as exc:
        return f"LLM Error: {exc}"
