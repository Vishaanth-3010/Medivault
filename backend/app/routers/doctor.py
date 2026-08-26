from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, get_request_id
from app.models import AuditOutcome, GrantStatus, MedicalDocument, ShareGrant, User, UserRole
from app.schemas import DocumentResponse, TimelineResponse
from app.routers.records import _build_timeline
from app.services.authorization import AuthorizationError, get_active_grant, write_audit

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get("/patients")
def list_granted_patients(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.doctor or not user.doctor:
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "Doctors only"})

    grants = (
        db.query(ShareGrant)
        .options(joinedload(ShareGrant.patient))
        .filter(ShareGrant.doctor_id == user.doctor.id, ShareGrant.status == GrantStatus.active)
        .all()
    )
    active = []
    for grant in grants:
        if get_active_grant(db, grant.patient_id, user.doctor.id):
            active.append(
                {
                    "patient_id": grant.patient_id,
                    "patient_name": grant.patient.name if grant.patient else None,
                    "grant_id": grant.id,
                    "expires_at": grant.expires_at,
                    "scope": grant.scope,
                }
            )
    return active


@router.get("/patients/{patient_id}/timeline", response_model=TimelineResponse)
def doctor_timeline(patient_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db), request_id: str = Depends(get_request_id)):
    if user.role != UserRole.doctor or not user.doctor:
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "Doctors only"})
    grant = get_active_grant(db, patient_id, user.doctor.id)
    if not grant:
        write_audit(db, action="ACCESS_DENIED", outcome=AuditOutcome.failure, request_id=request_id, actor=user, patient_id=patient_id, resource_type="timeline")
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "No active share grant"})

    items = _build_timeline(db, patient_id)
    write_audit(db, action="ACCESS_GRANTED", outcome=AuditOutcome.success, request_id=request_id, actor=user, patient_id=patient_id, resource_type="timeline")
    return TimelineResponse(items=items, total=len(items))


@router.get("/patients/{patient_id}/documents", response_model=list[DocumentResponse])
def doctor_documents(patient_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db), request_id: str = Depends(get_request_id)):
    if user.role != UserRole.doctor or not user.doctor:
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "Doctors only"})
    grant = get_active_grant(db, patient_id, user.doctor.id)
    if not grant:
        write_audit(db, action="ACCESS_DENIED", outcome=AuditOutcome.failure, request_id=request_id, actor=user, patient_id=patient_id, resource_type="documents")
        raise HTTPException(status_code=403, detail={"code": "ACCESS_DENIED", "message": "No active share grant"})

    docs = db.query(MedicalDocument).filter(MedicalDocument.patient_id == patient_id, MedicalDocument.deleted_at.is_(None)).all()
    scoped = [d for d in docs if not (grant.scope.get("document_ids") or []) or d.id in grant.scope["document_ids"]]
    write_audit(db, action="ACCESS_GRANTED", outcome=AuditOutcome.success, request_id=request_id, actor=user, patient_id=patient_id, resource_type="documents")
    return [DocumentResponse.model_validate(d) for d in scoped]
