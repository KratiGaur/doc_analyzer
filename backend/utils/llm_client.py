import os
import re
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

MODEL_NAME = "gemini-3.6-flash"

_CODE_FENCE_RE = re.compile(r"^```(?:json|markdown|text)?\s*|\s*```$", re.IGNORECASE | re.DOTALL)


def _normalize_key(key: str) -> str:
    return str(key).strip().lower().replace("-", "_")


def _find_matching_value(mapping, candidate_names: tuple[str, ...]) -> str:
    if not mapping:
        return ""

    if isinstance(mapping, dict):
        for key_name in candidate_names:
            value = mapping.get(key_name, "")
            if value:
                return str(value).strip()

        for key, value in mapping.items():
            normalized_key = _normalize_key(key)
            if normalized_key in candidate_names and value:
                return str(value).strip()

    return ""


def _get_api_key() -> str:
    candidate_names = ("gemini_api_key", "google_api_key")

    for env_name, env_value in os.environ.items():
        if _normalize_key(env_name) in candidate_names and env_value:
            return str(env_value).strip()

    try:
        import streamlit as st
    except Exception:
        return ""

    try:
        top_level_value = _find_matching_value(st.secrets, candidate_names)
        if top_level_value:
            return top_level_value
    except Exception:
        pass

    try:
        general_section = st.secrets.get("general", {})
        if isinstance(general_section, dict):
            general_value = _find_matching_value(general_section, candidate_names)
            if general_value:
                return general_value
    except Exception:
        pass

    return ""


def _configure_genai() -> str:
    api_key = _get_api_key()
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
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
