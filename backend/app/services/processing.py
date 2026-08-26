from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import (
    Condition,
    ExtractionJob,
    MedicalDocument,
    Medication,
    Observation,
    Procedure,
    ProcessingStatus,
    Provenance,
)
from app.services.storage import (
    extract_text_from_document,
    mock_structured_extraction,
    read_document_bytes,
    validate_extraction_schema,
)


def process_document(db: Session, document: MedicalDocument) -> ExtractionJob:
    document.processing_status = ProcessingStatus.processing
    job = ExtractionJob(
        document_id=document.id,
        status=ProcessingStatus.processing,
        ocr_provider="mock-local" ,
        llm_provider="mock-local",
        model="regex-extractor-v1",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        content = read_document_bytes(document.storage_path)
        raw_text = extract_text_from_document(content, document.mime_type)
        job.raw_ocr_text = raw_text

        if not raw_text.strip():
            raise ValueError("No extractable text found")

        extracted = validate_extraction_schema(mock_structured_extraction(raw_text))
        job.extracted_json = extracted

        provenance = Provenance(
            extraction_job_id=job.id,
            document_id=document.id,
            page_number=1,
            ocr_segment=(raw_text[:500] if raw_text else None),
            model=job.model,
            provider=job.llm_provider,
            confidence=0.75,
        )
        db.add(provenance)
        db.flush()

        if extracted.get("document_date"):
            document.document_date = extracted["document_date"]

        for vital in extracted.get("vitals", []):
            db.add(
                Observation(
                    patient_id=document.patient_id,
                    document_id=document.id,
                    display_name=vital.get("display_name", "Vital"),
                    value=vital.get("value", ""),
                    provenance_id=provenance.id,
                    effective_time=extracted.get("document_date"),
                )
            )

        for lab in extracted.get("laboratory_results", []):
            db.add(
                Observation(
                    patient_id=document.patient_id,
                    document_id=document.id,
                    display_name=lab.get("display_name", "Lab Result"),
                    value=lab.get("value", ""),
                    provenance_id=provenance.id,
                    effective_time=extracted.get("document_date"),
                )
            )

        for med in extracted.get("medications", []):
            db.add(
                Medication(
                    patient_id=document.patient_id,
                    document_id=document.id,
                    medication_name=med.get("medication_name", "Unknown"),
                    provenance_id=provenance.id,
                )
            )

        for diag in extracted.get("diagnoses", []):
            db.add(
                Condition(
                    patient_id=document.patient_id,
                    document_id=document.id,
                    display_name=diag.get("display_name", "Unknown"),
                    provenance_id=provenance.id,
                    onset_date=extracted.get("document_date"),
                )
            )

        for proc in extracted.get("procedures", []):
            db.add(
                Procedure(
                    patient_id=document.patient_id,
                    document_id=document.id,
                    display_name=proc.get("display_name", "Unknown"),
                    provenance_id=provenance.id,
                    performed_date=extracted.get("document_date"),
                )
            )

        job.status = ProcessingStatus.validated
        job.completed_at = datetime.now(UTC)
        document.processing_status = ProcessingStatus.validated
        db.commit()
        db.refresh(job)
        return job
    except Exception as exc:
        job.status = ProcessingStatus.failed
        job.error_code = "PROCESSING_FAILED"
        job.error_message = str(exc)[:500]
        job.completed_at = datetime.now(UTC)
        document.processing_status = ProcessingStatus.failed
        db.commit()
        db.refresh(job)
        return job
