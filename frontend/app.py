import os
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from backend.utils.file_parser import extract_text_from_file
from backend.utils.llm_client import ask_gemini
from backend.utils.phi_masker import mask_phi
from backend.utils.prompt_builder import build_medical_prompt


APP_TITLE = "Medical AI Document Summarizer"
SUPPORTED_TYPES = ["pdf", "docx", "txt"]


def local_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --paper: #ffffff;
            --card: #f2eadc;
            --card-2: #faf6ef;
            --border: #dfd3bf;
            --text: #343434;
            --muted: #6c645b;
            --sage: #a8b8a5;
            --gold: #b89c5a;
            --olive: #8a9773;
        }

        .stApp {
            background: linear-gradient(180deg, #faf8f4 0%, #f8f6f2 100%);
            color: var(--text);
            font-family: Inter, Source Sans Pro, Lato, Arial, sans-serif;
        }

        .main .block-container {
            max-width: 1120px;
            padding-top: 1rem;
            padding-bottom: 1.4rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1eadc 0%, #ece3d3 100%);
            border-right: 1px solid rgba(122, 96, 72, 0.12);
        }

        section[data-testid="stSidebar"] * {
            color: #3c352d;
        }

        header[data-testid="stHeader"], div[data-testid="stToolbar"] {
            background: transparent;
        }

        .top-card,
        .paper-card,
        .result-card {
            background: var(--paper);
            border: 1px solid var(--border);
            border-radius: 22px;
            box-shadow: 0 18px 40px rgba(62, 49, 34, 0.06);
        }

        .top-card {
            padding: 1.2rem 1.35rem;
            margin-bottom: 1rem;
        }

        .title-row {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo-mark {
            width: 54px;
            height: 54px;
            border-radius: 18px;
            display: grid;
            place-items: center;
            background: linear-gradient(145deg, #f4ecd9 0%, #e7dcc5 100%);
            border: 1px solid rgba(184, 156, 90, 0.35);
            color: #8f6b34;
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }

        .eyebrow {
            font-size: 0.78rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--gold);
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .page-title {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(1.8rem, 2.6vw, 2.9rem);
            line-height: 1.05;
            color: #2f251d;
        }

        .page-subtitle {
            margin: 0.45rem 0 0;
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .gold-rule {
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--gold), transparent);
            margin: 0.95rem 0 0;
        }

        .section-title {
            margin: 0 0 0.45rem;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #7d6a57;
        }

        .upload-copy {
            margin: 0 0 0.8rem;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: #fffaf2;
            border: 1px solid rgba(184, 156, 90, 0.18);
            border-radius: 16px;
            padding: 1rem;
        }

        div[data-testid="stFileUploaderDropzone"] section {
            padding: 0;
        }

        div[data-testid="stFileUploaderDropzone"] button {
            border-radius: 999px;
            border: 1px solid rgba(184, 156, 90, 0.32);
            background: #f6ebd7;
            color: #6b4f22;
            font-weight: 700;
        }

        .file-list {
            display: grid;
            gap: 0.6rem;
            margin-top: 0.9rem;
        }

        .file-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.85rem;
            padding: 0.75rem 0.85rem;
            border-radius: 14px;
            background: #fcfaf6;
            border: 1px solid #e6dcc9;
        }

        .file-name {
            font-weight: 700;
            color: #342a22;
            word-break: break-word;
        }

        .file-meta {
            color: var(--muted);
            font-size: 0.84rem;
            margin-top: 0.15rem;
        }

        .status-badge {
            padding: 0.3rem 0.62rem;
            border-radius: 999px;
            background: rgba(168, 184, 165, 0.2);
            border: 1px solid rgba(138, 151, 115, 0.22);
            color: #5a6a55;
            font-size: 0.74rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        .sidebar-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .sidebar-chip {
            display: inline-block;
            padding: 0.35rem 0.6rem;
            border-radius: 999px;
            background: rgba(168, 184, 165, 0.18);
            color: #5f6b57;
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 0.35rem;
        }

        .sidebar-card {
            padding: 0.85rem;
            border-radius: 16px;
            background: rgba(255, 251, 245, 0.74);
            border: 1px solid rgba(122, 96, 72, 0.1);
            margin: 0.8rem 0;
        }

        .sidebar-card-title {
            margin: 0 0 0.4rem;
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #7b6957;
        }

        .sidebar-card-text {
            margin: 0;
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.5;
        }

        .control-note {
            margin-top: 0.5rem;
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.5;
        }

        .analyze-button > button {
            width: 100%;
            border-radius: 16px;
            border: 1px solid rgba(184, 156, 90, 0.45);
            background: linear-gradient(180deg, #f6eddc 0%, #ead8b5 100%);
            color: #4b3a1b;
            font-weight: 800;
            padding: 0.95rem 1rem;
            box-shadow: none;
        }

        .analyze-button > button:hover {
            background: linear-gradient(180deg, #f8f0e0 0%, #e7d1a0 100%);
        }

        .result-card {
            padding: 1rem 1rem 0.95rem;
            margin-top: 1rem;
        }

        .stChatMessage {
            background: transparent;
        }

        .stChatMessage [data-testid="stChatMessage"] {
            background: #fffdf8;
            border: 1px solid #e6dcc9;
            border-radius: 18px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            border: 1px solid #dfd3bf;
            background: #fff;
            color: #5e5349;
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: #f3ead8 !important;
            color: #423520 !important;
            border-color: rgba(184, 156, 90, 0.4) !important;
        }

        .stInfo, .stWarning, .stError, .stSuccess {
            border-radius: 14px;
        }

        @media (max-width: 900px) {
            .main .block-container {
                padding-left: 0.7rem;
                padding-right: 0.7rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        f"""
        <div class="top-card">
            <div class="title-row">
                <div class="logo-mark">MI</div>
                <div>
                    <div class="eyebrow">Medical AI Assistant</div>
                    <h1 class="page-title">{APP_TITLE}</h1>
                    <p class="page-subtitle">AI-powered Clinical Intelligence • PHI Protected • Document-only analysis</p>
                </div>
            </div>
            <div class="gold-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _summary_length_label(length: int) -> str:
    if length <= 2:
        return "Brief"
    if length == 3:
        return "Balanced"
    return "Detailed"


def render_sidebar_settings():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Settings</div>', unsafe_allow_html=True)
        st.caption("Simple controls for the demo")
        st.markdown('<div class="sidebar-chip">PHI Masker Active</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="sidebar-card-title">Privacy</div>', unsafe_allow_html=True)
            st.markdown('<p class="sidebar-card-text">Choose which personal details should be redacted before the report is sent to the model.</p>', unsafe_allow_html=True)
            mask_name = st.toggle("Patient Name", value=True)
            mask_patient_number = st.toggle("Patient Number / Hospital ID", value=True)
            mask_dob = st.toggle("Date of Birth", value=True)
            mask_contact_details = st.toggle("Contact Details", value=True)
            mask_physician_names = st.toggle("Physician Names", value=True)

        with st.container(border=True):
            st.markdown('<div class="sidebar-card-title">Summary</div>', unsafe_allow_html=True)
            st.markdown('<p class="sidebar-card-text">These options control how the final summary is written and how much detail it includes.</p>', unsafe_allow_html=True)
            summary_style = st.selectbox(
                "Summary Style",
                ["Clinical", "Concise", "Detailed", "Patient Friendly"],
            )
            summary_length = st.slider("Summary Length", 1, 5, 3, help="1 = shortest, 5 = most detailed")
            st.caption(f"Current length: {_summary_length_label(summary_length)}")

        with st.container(border=True):
            st.markdown('<div class="sidebar-card-title">Output Behavior</div>', unsafe_allow_html=True)
            st.markdown('<p class="sidebar-card-text">These settings are still simple, but they help the model combine files and surface important findings.</p>', unsafe_allow_html=True)
            merge_multiple = st.toggle("Merge multiple files", value=True)
            extract_entities = st.toggle("Extract medical entities", value=True)
            highlight_abnormal = st.toggle("Highlight abnormal findings", value=True)

        st.markdown("---")
        analyze_button = st.button("Analyze & Generate Unified Summary", use_container_width=True)

    return {
        "mask_name": mask_name,
        "mask_patient_number": mask_patient_number,
        "mask_dob": mask_dob,
        "mask_contact_details": mask_contact_details,
        "mask_physician_names": mask_physician_names,
        "summary_style": summary_style,
        "summary_length": summary_length,
        "merge_multiple": merge_multiple,
        "extract_entities": extract_entities,
        "highlight_abnormal": highlight_abnormal,
        "analyze_button": analyze_button,
    }


def render_upload_card() -> list:
    st.markdown('<div class="section-title">Documents</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<p class="upload-copy">Upload PDF, DOCX, or TXT files. Summary generation uses document content only.</p>',
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "Upload medical documents",
            type=SUPPORTED_TYPES,
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="medical_uploads",
        )

        if uploaded_files:
            st.markdown('<div class="file-list">', unsafe_allow_html=True)
            for uploaded in uploaded_files:
                size_kb = max(1, round(len(uploaded.getvalue()) / 1024))
                kind = Path(uploaded.name).suffix.replace(".", "").upper()
                st.markdown(
                    f"""
                    <div class="file-row">
                        <div>
                            <div class="file-name">{uploaded.name}</div>
                            <div class="file-meta">{kind} • {size_kb} KB</div>
                        </div>
                        <div class="status-badge">Ready</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

    return uploaded_files or []


def build_masked_bundle(uploaded_files: list, settings: dict):
    extracted_documents = []
    errors = []

    for uploaded in uploaded_files:
        suffix = Path(uploaded.name).suffix or ".txt"
        file_bytes = uploaded.getvalue()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        try:
            extracted_text = extract_text_from_file(tmp_path)
            if extracted_text:
                extracted_documents.append(
                    {
                        "name": uploaded.name,
                        "type": uploaded.type,
                        "text": extracted_text,
                    }
                )
            else:
                errors.append(f"No text found in {uploaded.name}.")
        except Exception as exc:
            errors.append(f"{uploaded.name}: {exc}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    combined_sections = []
    for doc in extracted_documents:
        masked_text = mask_phi(
            doc["text"],
            mask_name=settings["mask_name"],
            mask_patient_number=settings["mask_patient_number"],
            mask_dob=settings["mask_dob"],
            mask_contact_details=settings["mask_contact_details"],
            mask_physician_names=settings["mask_physician_names"],
        )
        combined_sections.append(f"FILE: {doc['name']}\n{masked_text}")

    return extracted_documents, combined_sections, errors


def render_summary(response: str, extracted_documents: list) -> None:
    st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.chat_message("assistant"):
            st.markdown(response or "No summary available yet.")

    if extracted_documents:
        with st.expander(f"Reviewed files ({len(extracted_documents)})", expanded=False):
            for idx, doc in enumerate(extracted_documents):
                st.markdown(f"**{doc['name']}**")
                st.text_area(
                    "Source preview",
                    doc["text"][:1800],
                    height=160,
                    label_visibility="collapsed",
                    key=f"preview_{idx}",
                )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")
    local_css()
    render_header()

    settings = render_sidebar_settings()
    uploaded_files = render_upload_card()

    if uploaded_files and settings["analyze_button"]:
        with st.spinner("Reading documents and generating summary..."):
            extracted_documents, combined_sections, errors = build_masked_bundle(uploaded_files, settings)

            if extracted_documents:
                prompt_text = "\n\n---\n\n".join(combined_sections)
                prompt = build_medical_prompt(
                    prompt_text,
                    summary_style=settings["summary_style"],
                    summary_length=settings["summary_length"],
                    merge_multiple_files=settings["merge_multiple"],
                    extract_medical_entities=settings["extract_entities"],
                    highlight_abnormal_findings=settings["highlight_abnormal"],
                )
                response = ask_gemini(prompt)
                st.session_state["summary_response"] = response
                st.session_state["reviewed_documents"] = extracted_documents
            else:
                st.session_state["summary_response"] = "No supported document content was found."
                st.session_state["reviewed_documents"] = []

            if errors:
                st.warning("\n".join(errors))

    response = st.session_state.get("summary_response", "Upload files and run analysis to see the summary here.")
    reviewed_documents = st.session_state.get("reviewed_documents", [])
    render_summary(response, reviewed_documents)

    st.markdown(
        '<p style="text-align:center; color:#7a6f64; margin-top:1rem; font-size:0.88rem;">Medical AI Summarizer • Privacy First • PHI Protected • Document Intelligence</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
