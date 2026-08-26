import hashlib
import re
import secrets
from datetime import datetime
from io import BytesIO
from pathlib import Path

import aiofiles
from pypdf import PdfReader

from app.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def ensure_storage_root() -> Path:
    root = Path(settings.storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_upload(mime_type: str, file_size: int) -> None:
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Unsupported file type")
    if file_size <= 0 or file_size > settings.max_upload_bytes:
        raise ValueError("Invalid file size")


def build_object_key(patient_id: str, document_id: str, content_hash: str, mime_type: str) -> str:
    ext = ALLOWED_MIME_TYPES[mime_type]
    return f"{patient_id}/{document_id}/{content_hash}{ext}"


def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def save_document(content: bytes, storage_path: str) -> None:
    full_path = ensure_storage_root() / storage_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(full_path, "wb") as f:
        await f.write(content)


def read_document_bytes(storage_path: str) -> bytes:
    full_path = ensure_storage_root() / storage_path
    return full_path.read_bytes()


def extract_text_from_document(content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    if mime_type.startswith("image/"):
        return "[image document uploaded — OCR provider required for image text in production]"
    return content.decode("utf-8", errors="ignore")


def mock_structured_extraction(text: str) -> dict:
    """Extract explicitly pattern-matched facts only. No inference."""
    result = {
        "document_date": None,
        "hospital": None,
        "physician": None,
        "diagnoses": [],
        "medications": [],
        "vitals": [],
        "laboratory_results": [],
        "procedures": [],
        "allergies": [],
        "source_text_references": [],
    }

    date_match = re.search(r"(?:Date|Dated)\s*[:\-]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})", text, re.I)
    if date_match:
        result["document_date"] = date_match.group(1)
        result["source_text_references"].append(date_match.group(0))

    hospital_match = re.search(r"(?:Hospital|Clinic|Medical Center)\s*[:\-]?\s*([A-Za-z0-9 .,&-]{3,80})", text, re.I)
    if hospital_match:
        result["hospital"] = hospital_match.group(1).strip()
        result["source_text_references"].append(hospital_match.group(0))

    physician_match = re.search(r"(?:Dr\.|Doctor|Physician)\s*([A-Za-z .]{3,60})", text, re.I)
    if physician_match:
        result["physician"] = physician_match.group(1).strip()
        result["source_text_references"].append(physician_match.group(0))

    for diag in re.findall(r"(?:Diagnosis|Impression)\s*[:\-]?\s*([^\n\r]{3,120})", text, re.I):
        result["diagnoses"].append({"display_name": diag.strip(), "source": diag.strip()})

    for med in re.findall(r"(?:Rx|Prescription|Medication)\s*[:\-]?\s*([^\n\r]{3,120})", text, re.I):
        result["medications"].append({"medication_name": med.strip(), "source": med.strip()})

    for vital in re.findall(r"(?:BP|Blood Pressure|HR|Heart Rate)\s*[:\-]?\s*([0-9/ .a-zA-Z]{2,20})", text, re.I):
        result["vitals"].append({"display_name": "Vital", "value": vital.strip(), "source": vital.strip()})

    for lab in re.findall(r"(?:HbA1c|WBC|RBC|Hemoglobin|Glucose)\s*[:\-]?\s*([0-9.]+ ?%?)", text, re.I):
        result["laboratory_results"].append({"display_name": "Lab Result", "value": lab.strip(), "source": lab.strip()})

    for proc in re.findall(r"(?:Procedure|Surgery)\s*[:\-]?\s*([^\n\r]{3,120})", text, re.I):
        result["procedures"].append({"display_name": proc.strip(), "source": proc.strip()})

    for allergy in re.findall(r"(?:Allergy|Allergic to)\s*[:\-]?\s*([^\n\r]{3,80})", text, re.I):
        result["allergies"].append({"display_name": allergy.strip(), "source": allergy.strip()})

    return result


def validate_extraction_schema(data: dict) -> dict:
    required_keys = {
        "document_date",
        "hospital",
        "physician",
        "diagnoses",
        "medications",
        "vitals",
        "laboratory_results",
        "procedures",
        "allergies",
        "source_text_references",
    }
    if not required_keys.issubset(data.keys()):
        raise ValueError("Extraction schema validation failed")
    for key in ["diagnoses", "medications", "vitals", "laboratory_results", "procedures", "allergies", "source_text_references"]:
        if not isinstance(data[key], list):
            raise ValueError(f"Invalid type for {key}")
    return data


def generate_token_identifier() -> str:
    return secrets.token_urlsafe(24)
