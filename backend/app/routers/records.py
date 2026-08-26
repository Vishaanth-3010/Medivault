from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_request_id
from app.models import AuditOutcome, Condition, Medication, Observation, Procedure, User, UserRole
from app.schemas import TimelineItem, TimelineResponse
from app.services.authorization import AuthorizationError, authorize_patient_access, authorize_record, write_audit

router = APIRouter(prefix="/records", tags=["records"])


def _build_timeline(db: Session, patient_id: str) -> list[TimelineItem]:
    items: list[TimelineItem] = []
    for obs in db.query(Observation).filter(Observation.patient_id == patient_id).all():
        items.append(
            TimelineItem(
                type="observation",
                id=obs.id,
                display_name=obs.display_name,
                value=obs.value,
                effective_time=obs.effective_time,
                document_id=obs.document_id,
            )
        )
    for med in db.query(Medication).filter(Medication.patient_id == patient_id).all():
        items.append(
            TimelineItem(
                type="medication",
                id=med.id,
                display_name=med.medication_name,
                value=med.dosage,
                document_id=med.document_id,
            )
        )
    for cond in db.query(Condition).filter(Condition.patient_id == patient_id).all():
        items.append(
            TimelineItem(
                type="condition",
                id=cond.id,
                display_name=cond.display_name,
                effective_time=cond.onset_date,
                document_id=cond.document_id,
            )
        )
    for proc in db.query(Procedure).filter(Procedure.patient_id == patient_id).all():
        items.append(
            TimelineItem(
                type="procedure",
                id=proc.id,
                display_name=proc.display_name,
                effective_time=proc.performed_date,
                document_id=proc.document_id,
            )
        )
    items.sort(key=lambda x: x.effective_time or "", reverse=True)
    return items


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    patient_id: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
):
    target_patient_id = patient_id
    if user.role == UserRole.patient and user.patient:
        if patient_id and patient_id != user.patient.id:
            write_audit(db, action="ACCESS_DENIED", outcome=AuditOutcome.failure, request_id=request_id, actor=user, patient_id=patient_id, resource_type="timeline")
            raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "Not authorized for this patient"})
        target_patient_id = user.patient.id
    if not target_patient_id:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "patient_id required"})

    try:
        authorize_patient_access(db, user, target_patient_id)
    except AuthorizationError as exc:
        write_audit(db, action="ACCESS_DENIED", outcome=AuditOutcome.failure, request_id=request_id, actor=user, patient_id=target_patient_id, resource_type="timeline")
        raise HTTPException(status_code=403, detail={"code": exc.code, "message": exc.message})

    items = _build_timeline(db, target_patient_id)
    write_audit(db, action="RECORD_VIEW", outcome=AuditOutcome.success, request_id=request_id, actor=user, patient_id=target_patient_id, resource_type="timeline")
    return TimelineResponse(items=items, total=len(items))


@router.get("/observations")
def list_observations(patient_id: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db), request_id: str = Depends(get_request_id)):
    target_patient_id = patient_id or (user.patient.id if user.patient else None)
    if not target_patient_id:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "patient_id required"})
    try:
        authorize_record(db, user, target_patient_id, "observations")
    except AuthorizationError as exc:
        write_audit(db, action="ACCESS_DENIED", outcome=AuditOutcome.failure, request_id=request_id, actor=user, patient_id=target_patient_id, resource_type="observations")
        raise HTTPException(status_code=403, detail={"code": exc.code, "message": exc.message})
    rows = db.query(Observation).filter(Observation.patient_id == target_patient_id).all()
    write_audit(db, action="RECORD_VIEW", outcome=AuditOutcome.success, request_id=request_id, actor=user, patient_id=target_patient_id, resource_type="observations")
    return rows
