import re


_DATE_PATTERN = r"(?:\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}|\d{4}-\d{2}-\d{2})"


def _mask_line_value(text: str, labels: list[str], replacement: str) -> str:
    pattern = rf"(?im)^(\s*(?:{'|'.join(labels)})\s*[:\-]\s*)(.+)$"
    return re.sub(pattern, lambda match: f"{match.group(1)}{replacement}", text)


def mask_phi(
    text: str,
    mask_name: bool = True,
    mask_dob: bool = True,
    mask_hospital_id: bool = True,
    mask_patient_number: bool | None = None,
    mask_contact_details: bool = True,
    mask_physician_names: bool = True,
) -> str:
    """Mask common PHI markers in report text."""

    if mask_patient_number is None:
        mask_patient_number = mask_hospital_id

    masked = text

    if mask_name:
        masked = _mask_line_value(masked, ["Patient Name", "Name"], "[REDACTED_NAME]")
        masked = re.sub(
            rf"(?im)^(\s*(?:Patient Name|Name)\s*[:\-]\s*)(.+)$",
            lambda match: f"{match.group(1)}[REDACTED_NAME]",
            masked,
        )

    if mask_dob:
        masked = re.sub(
            rf"(?im)^(\s*(?:Date of Birth|DOB|Birth Date)\s*[:\-]\s*)({_DATE_PATTERN})$",
            lambda match: f"{match.group(1)}[REDACTED_DOB]",
            masked,
        )

    if mask_hospital_id or mask_patient_number:
        masked = _mask_line_value(masked, ["Hospital ID", "Patient ID", "MRN", "Medical Record Number"], "[REDACTED_ID]")

    if mask_contact_details:
        masked = _mask_line_value(masked, ["Phone", "Telephone", "Mobile", "Email", "Address", "Contact Information", "Contact"], "[REDACTED_CONTACT]")
        masked = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", masked)
        masked = re.sub(r"\b\d{10}\b", "[REDACTED_PHONE]", masked)

    if mask_physician_names:
        masked = _mask_line_value(masked, ["Physician", "Referring Physician", "Attending Physician", "Consultant", "Doctor"], "[REDACTED_PHYSICIAN]")

    masked = re.sub(r"\b\d{12}\b", "[REDACTED_ID]", masked)
    return masked
