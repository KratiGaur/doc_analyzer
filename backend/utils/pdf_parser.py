from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to PDF file.

    Returns:
        str: Extracted text from all pages.
    """
    extracted_text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"

        return extracted_text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    except Exception as e:
        raise RuntimeError(f"Error while reading PDF: {str(e)}")