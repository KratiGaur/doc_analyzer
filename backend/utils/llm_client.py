import os
import re
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

MODEL_NAME = "gemini-3.6-flash"

_CODE_FENCE_RE = re.compile(r"^```(?:json|markdown|text)?\s*|\s*```$", re.IGNORECASE | re.DOTALL)


def _get_api_key() -> str:
    env_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if env_key:
        return env_key

    try:
        import streamlit as st
    except Exception:
        return ""

    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            secret_value = st.secrets.get(key_name, "")
        except Exception:
            secret_value = ""

        if secret_value:
            return str(secret_value).strip()

    try:
        general_section = st.secrets.get("general", {})
        if isinstance(general_section, dict):
            for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                secret_value = general_section.get(key_name, "")
                if secret_value:
                    return str(secret_value).strip()
    except Exception:
        pass

    return ""


def _configure_genai() -> str:
    api_key = _get_api_key()
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        try:
            genai.configure(api_key=api_key)
        except Exception:
            pass
    return api_key


def _clean_response(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = _CODE_FENCE_RE.sub("", cleaned).strip()
    return cleaned


def ask_gemini(prompt: str) -> str:
    api_key = _configure_genai()
    if not api_key:
        return (
            "LLM Error: No Gemini API key found. Set GEMINI_API_KEY in Streamlit Cloud "
            "Secrets or as an environment variable, then restart the app."
        )

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        cleaned = _clean_response(text)
        return cleaned or "No response was returned by the model."
    except Exception as exc:
        return f"LLM Error: {exc}"
