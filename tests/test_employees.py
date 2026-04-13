"""Tests for the employee (dipendenti) management and retirement prediction endpoints."""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from src.app import app, employees, RETIREMENT_AGE


@pytest.fixture(autouse=True)
def _reset_employees():
    """Reset the in-memory employee store before each test."""
    import src.app as mod
    original = dict(mod.employees)
    original_next_id = mod._next_id
    yield
    mod.employees.clear()
    mod.employees.update(original)
    mod._next_id = original_next_id


client = TestClient(app)


# ---- GET /employees ----

def test_get_employees_returns_list():
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # three seed employees


def test_employee_has_computed_fields():
    response = client.get("/employees")
    emp = response.json()[0]
    assert "eta_attuale" in emp
    assert "anni_di_servizio" in emp
    assert "eta_pensione_prevista" in emp
    assert emp["eta_pensione_prevista"] == RETIREMENT_AGE


# ---- POST /employees ----

def test_add_employee():
    payload = {
        "nome": "Anna",
        "cognome": "Neri",
        "data_di_nascita": "1990-05-20",
        "data_inizio_lavoro": "2015-09-01",
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Anna"
    assert data["cognome"] == "Neri"
    assert "id" in data

    # Verify it shows up in the list
    all_emps = client.get("/employees").json()
    assert len(all_emps) == 4


def test_add_employee_missing_field():
    payload = {"nome": "Anna"}
    response = client.post("/employees", json=payload)
    assert response.status_code == 422  # validation error


# ---- GET /employees/retirement-prediction ----

def test_retirement_prediction():
    response = client.get("/employees/retirement-prediction")
    assert response.status_code == 200
    data = response.json()
    assert data["eta_pensionamento_legale"] == RETIREMENT_AGE
    assert data["numero_dipendenti"] == 3
    assert "eta_media_pensionamento_prevista" in data
    assert "dettaglio_dipendenti" in data
    assert len(data["dettaglio_dipendenti"]) == 3


def test_retirement_prediction_detail_fields():
    response = client.get("/employees/retirement-prediction")
    detail = response.json()["dettaglio_dipendenti"][0]
    for key in ("id", "nome", "cognome", "eta_attuale",
                "anni_di_servizio", "eta_pensione_prevista", "anni_alla_pensione"):
        assert key in detail


def test_retirement_prediction_empty():
    """When there are no employees the endpoint should return 404."""
    import src.app as mod
    mod.employees.clear()
    response = client.get("/employees/retirement-prediction")
    assert response.status_code == 404
