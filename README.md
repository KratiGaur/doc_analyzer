# Medical AI Summarizer

A Streamlit-based medical report summarizer that supports multiple uploads and extracts text from PDFs, DOCX, TXT, and image files (PNG/JPEG) using OCR.

## Project Structure

- `app.py` - Root entrypoint for the Streamlit app.
- `frontend/app.py` - Streamlit frontend UI and upload workflow.
- `backend/utils/` - Backend utilities for file parsing, PHI masking, prompt generation, and LLM calls.
- `requirements.txt` - Python dependencies.
- `test_llm.py`, `test_parser.py` - Simple backend validation scripts.

## Features

- Multi-file upload support
- PDF, DOCX, TXT, PNG, JPG, JPEG input
- OCR for image and scanned PDF text extraction
- PHI redaction toggles for names, DOB, and hospital IDs
- Unified prompt builder for clinical JSON extraction
- AI analysis via Gemini model call

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Install Tesseract OCR on Windows:

- Download from https://github.com/tesseract-ocr/tesseract
- Add the installation path to your PATH environment variable

4. Configure environment variables in `.env`:

```text
GOOGLE_API_KEY=your_api_key_here
```

## Run

```powershell
streamlit run app.py
```

## Notes

- The frontend is implemented in `frontend/app.py`, while supporting backend utilities are kept in `backend/utils/`.
- `app.py` delegates to `frontend.app.main()` so the root file remains the launch entrypoint.
- If you add new file types or models, update `backend/utils/file_parser.py` and `backend/utils/prompt_builder.py`.
