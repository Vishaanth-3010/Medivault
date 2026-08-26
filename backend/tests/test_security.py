from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import User
from app.services.auth import register_user
from app.models import UserRole


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    register_user(db, "a@demo.medivault", "password123", UserRole.patient, "Patient A")
    register_user(db, "b@demo.medivault", "password123", UserRole.patient, "Patient B")
    register_user(db, "doctor@demo.medivault", "password123", UserRole.doctor, "Dr X", specialization="Medicine")
    db.close()


client = TestClient(app)


def _login(email: str) -> str:
    r = client.post("/v1/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_patient_cannot_access_other_patient_timeline():
    token_a = _login("a@demo.medivault")
    patient_b = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {_login('b@demo.medivault')}"}).json()
    r = client.get(f"/v1/records/timeline?patient_id={patient_b['patient_id']}", headers={"Authorization": f"Bearer {token_a}"})
    assert r.status_code == 403


def test_doctor_denied_without_consent():
    token_doc = _login("doctor@demo.medivault")
    patient_a = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {_login('a@demo.medivault')}"}).json()
    r = client.get(f"/v1/doctor/patients/{patient_a['patient_id']}/timeline", headers={"Authorization": f"Bearer {token_doc}"})
    assert r.status_code == 403


def test_doctor_access_with_consent():
    token_a = _login("a@demo.medivault")
    token_doc = _login("doctor@demo.medivault")
    me_a = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"}).json()
    me_doc = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token_doc}"}).json()
    exp = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    c = client.post(
        "/v1/consents",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "doctor_id": me_doc["doctor_id"],
            "scope": {"record_types": ["observations", "medications", "conditions", "procedures"]},
            "permissions": ["read"],
            "expires_at": exp,
        },
    )
    assert c.status_code == 200
    r = client.get(f"/v1/doctor/patients/{me_a['patient_id']}/timeline", headers={"Authorization": f"Bearer {token_doc}"})
    assert r.status_code == 200


def test_revoked_consent_denied():
    token_b = _login("b@demo.medivault")
    token_doc = _login("doctor@demo.medivault")
    me_b = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token_b}"}).json()
    me_doc = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token_doc}"}).json()
    exp = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    grant = client.post(
        "/v1/consents",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"doctor_id": me_doc["doctor_id"], "scope": {"record_types": ["observations"]}, "permissions": ["read"], "expires_at": exp},
    ).json()
    client.patch(f"/v1/consents/{grant['id']}/revoke", headers={"Authorization": f"Bearer {token_b}"})
    r = client.get(f"/v1/doctor/patients/{me_b['patient_id']}/timeline", headers={"Authorization": f"Bearer {token_doc}"})
    assert r.status_code == 403
