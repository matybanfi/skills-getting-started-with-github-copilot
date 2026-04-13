"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

It also includes an employee (dipendenti) management module with a
retirement-age prediction system based on Italian pension rules.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import date
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


# ---------------------------------------------------------------------------
# Dipendenti (Employees) – management & retirement prediction
# ---------------------------------------------------------------------------

# Italian statutory retirement age (years)
RETIREMENT_AGE = 67


class EmployeeIn(BaseModel):
    """Schema for creating a new employee."""
    nome: str
    cognome: str
    data_di_nascita: date
    data_inizio_lavoro: date


class EmployeeOut(EmployeeIn):
    """Schema returned to the client, enriched with computed fields."""
    id: int
    eta_attuale: float
    anni_di_servizio: float
    eta_pensione_prevista: int


# In-memory employee store (mirrors the Oracle DIPENDENTI table)
_next_id = 4
employees: dict[int, dict] = {
    1: {
        "nome": "Mario",
        "cognome": "Rossi",
        "data_di_nascita": date(1975, 3, 15),
        "data_inizio_lavoro": date(2000, 9, 1),
    },
    2: {
        "nome": "Giulia",
        "cognome": "Bianchi",
        "data_di_nascita": date(1988, 7, 22),
        "data_inizio_lavoro": date(2012, 1, 10),
    },
    3: {
        "nome": "Luca",
        "cognome": "Verdi",
        "data_di_nascita": date(1992, 11, 5),
        "data_inizio_lavoro": date(2018, 6, 15),
    },
}


def _years_between(start: date, end: date) -> float:
    """Return the number of years (fractional) between two dates."""
    return (end - start).days / 365.25


def _enrich(emp_id: int, emp: dict) -> dict:
    """Add computed fields to an employee record."""
    today = date.today()
    eta_attuale = _years_between(emp["data_di_nascita"], today)
    anni_di_servizio = _years_between(emp["data_inizio_lavoro"], today)
    return {
        "id": emp_id,
        **emp,
        "eta_attuale": round(eta_attuale, 2),
        "anni_di_servizio": round(anni_di_servizio, 2),
        "eta_pensione_prevista": RETIREMENT_AGE,
    }


@app.get("/employees")
def get_employees():
    """Return all employees with computed age and service years."""
    return [_enrich(eid, e) for eid, e in employees.items()]


@app.post("/employees", status_code=201)
def add_employee(emp: EmployeeIn):
    """Add a new employee."""
    global _next_id
    emp_id = _next_id
    _next_id += 1
    employees[emp_id] = emp.model_dump()
    return _enrich(emp_id, employees[emp_id])


@app.get("/employees/retirement-prediction")
def retirement_prediction():
    """
    Predict the average retirement age for all employees.

    Uses the Italian statutory retirement age of 67.  For each employee the
    predicted retirement date is ``data_di_nascita + 67 years``.  The endpoint
    returns the average predicted age at retirement, plus per-employee detail.
    """
    if not employees:
        raise HTTPException(status_code=404, detail="No employees registered")

    today = date.today()
    details = []
    total_retirement_age = 0.0

    for eid, emp in employees.items():
        eta_attuale = _years_between(emp["data_di_nascita"], today)
        anni_servizio = _years_between(emp["data_inizio_lavoro"], today)

        # Predicted retirement date: birth + RETIREMENT_AGE years
        retirement_year = emp["data_di_nascita"].year + RETIREMENT_AGE
        retirement_date = emp["data_di_nascita"].replace(year=retirement_year)

        years_to_retirement = _years_between(today, retirement_date)

        total_retirement_age += RETIREMENT_AGE

        details.append({
            "id": eid,
            "nome": emp["nome"],
            "cognome": emp["cognome"],
            "eta_attuale": round(eta_attuale, 2),
            "anni_di_servizio": round(anni_servizio, 2),
            "eta_pensione_prevista": RETIREMENT_AGE,
            "anni_alla_pensione": round(max(years_to_retirement, 0), 2),
        })

    avg_retirement_age = total_retirement_age / len(employees)

    return {
        "eta_pensionamento_legale": RETIREMENT_AGE,
        "eta_media_pensionamento_prevista": round(avg_retirement_age, 2),
        "numero_dipendenti": len(employees),
        "dettaglio_dipendenti": details,
    }
