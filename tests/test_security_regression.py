"""Pruebas de regresion de seguridad - TransControl API (T1 a T6).
Datos sinteticos y base SQLite temporal (ver conftest.py).
Si un campo de los modelos o la firma de create_access_token difiere en tu
commit, ajusta SOLO el fixture y registra el cambio en la evidencia; no
modifiques los criterios de T4 y T6."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app  # import tardio: conftest ya fijo DATABASE_URL
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    from database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _cedula():
    return str(1_000_000_000 + uuid4().int % 8_999_999_999)


def _new_carrier_and_trip(db):
    from models.models import (EstadoViajeEnum, RolEnum, Transportista,
                               Usuario, Viaje)
    suffix = uuid4().hex
    user = Usuario(cedula=_cedula(), nombres=f"Usuario prueba {suffix[:8]}",
                   correo=f"carrier-{suffix}@example.test",
                   hashed_password="no-se-usa-en-estas-pruebas",
                   rol=RolEnum.TRANSPORTISTA, activo=True)
    db.add(user)
    db.flush()
    carrier = Transportista(usuario_id=user.id)
    db.add(carrier)
    db.flush()
    trip = Viaje(codigo=f"T-{suffix[:16]}", transportista_id=carrier.id,
                 creado_por_id=user.id, tipo_mercancia="Carga sintetica",
                 peso_total_kg=1, origen="QUITO", destino="GUAYAQUIL",
                 estado=EstadoViajeEnum.TRANSPORTISTA_ASIGNADO)
    db.add(trip)
    db.commit()
    return user, trip


def _bearer_for(user):
    from core.security import create_access_token
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_t1_me_requires_authentication(client):
    assert client.get("/api/auth/me").status_code == 401


def test_t2_me_rejects_invalid_token(client):
    r = client.get("/api/auth/me",
                   headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401


def test_t3_registration_rejects_invalid_input(client):
    r = client.post("/api/auth/registro", json={
        "cedula": "no-es-cedula", "nombres": "Persona sintetica",
        "correo": f"invalid-{uuid4().hex}@example.test",
        "password": "clave-sintetica"})
    assert r.status_code == 422


def test_t4_public_registration_cannot_create_gerente(client, db):
    from models.models import RolEnum, Usuario
    email = f"role-test-{uuid4().hex}@example.test"
    r = client.post("/api/auth/registro", json={
        "cedula": _cedula(), "nombres": "Usuario sintetico", "correo": email,
        "password": "clave-sintetica-segura", "rol": "GERENTE"})
    persisted = db.query(Usuario).filter(Usuario.correo == email).one_or_none()
    assert persisted is None or persisted.rol != RolEnum.GERENTE
    if r.status_code == 201:
        assert r.json()["rol"] == "TRANSPORTISTA"
    else:
        assert r.status_code in {400, 403, 422}


def test_t5_carrier_can_read_own_trip(client, db):
    user, trip = _new_carrier_and_trip(db)
    r = client.get(f"/api/viajes/{trip.id}", headers=_bearer_for(user))
    assert r.status_code == 200


def test_t6_carrier_cannot_read_another_carriers_trip(client, db):
    from models.models import RolEnum, Usuario
    owner, trip = _new_carrier_and_trip(db)
    suffix = uuid4().hex
    other = Usuario(cedula=_cedula(), nombres=f"Otro usuario {suffix[:8]}",
                    correo=f"other-{suffix}@example.test",
                    hashed_password="no-se-usa-en-estas-pruebas",
                    rol=RolEnum.TRANSPORTISTA, activo=True)
    db.add(other)
    db.commit()
    assert owner.id != other.id
    r = client.get(f"/api/viajes/{trip.id}", headers=_bearer_for(other))
    assert r.status_code in {403, 404}
