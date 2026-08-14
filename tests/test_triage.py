import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from triage_engine import analyze_symptoms, triage_engine
from app import app

# ── Dataset Integrity ─────────────────────────────────────────

def test_dataset_loaded():
    """Dataset must have at least 20 clinical entries."""
    assert len(triage_engine.dataset) >= 20


# ── Accuracy Fixes Regression Tests ──────────────────────────

def test_neck_shoulder_pain_is_self_care():
    """Neck and shoulder pain while moving must NOT trigger emergency. ESI 4, green."""
    res = analyze_symptoms("neck pain around shoulders while moving")
    assert res["urgency_level"] == "Self Care", f"Got: {res['urgency_level']}"
    assert res["esi_score"] == 4, f"Got ESI: {res['esi_score']}"
    assert res["urgency_code"] == "green"
    assert res["safety_override"] is False

def test_normal_temperature_does_not_trigger_risk():
    """98.8°F is normal — must NOT generate fever risk factors."""
    res = analyze_symptoms("neck pain", vitals={"temperature": "98.8"})
    fever_flags = [r for r in res["risk_factors_triggered"] if "Fever" in r]
    assert len(fever_flags) == 0, f"False fever triggered: {fever_flags}"

def test_normal_celsius_does_not_trigger():
    """37.0°C is normal body temperature — must NOT flag fever."""
    res = analyze_symptoms("mild headache", vitals={"temperature": "37.0"})
    fever_flags = [r for r in res["risk_factors_triggered"] if "Fever" in r]
    assert len(fever_flags) == 0, f"False fever triggered: {fever_flags}"


# ── Red-Flag Emergency Tests ──────────────────────────────────

def test_crushing_chest_pain_is_emergency():
    """Crushing chest pain radiating to arm = Emergency (cardiac red flag)."""
    res = analyze_symptoms("crushing chest pain radiating to left arm")
    assert res["urgency_level"] == "Emergency"
    assert res["esi_score"] == 1
    assert res["safety_override"] is True

def test_stroke_symptoms_are_emergency():
    """FAST stroke symptoms must trigger Emergency."""
    res = analyze_symptoms("face drooping arm weakness slurred speech")
    assert res["urgency_level"] == "Emergency"
    assert res["esi_score"] == 1

def test_thunderclap_headache_is_emergency():
    """Thunderclap headache = potential subarachnoid haemorrhage."""
    res = analyze_symptoms("thunderclap headache worst headache ever sudden")
    assert res["urgency_level"] == "Emergency"
    assert res["esi_score"] == 1

def test_anaphylaxis_is_emergency():
    """Throat/tongue swelling = anaphylactic shock = Emergency."""
    res = analyze_symptoms("throat swelling tongue swelling after eating")
    assert res["urgency_level"] == "Emergency"
    assert res["esi_score"] == 1


# ── Urgency Level Accuracy Tests ─────────────────────────────

def test_high_fever_cough_is_urgent():
    """High fever + dry cough + body aches = Influenza/COVID-19, Urgent Care."""
    res = analyze_symptoms("high fever dry cough body aches fatigue sore throat")
    assert res["esi_score"] <= 2

def test_migraine_is_routine_care():
    """Migraine headache = Routine Care, ESI 3."""
    res = analyze_symptoms("throbbing headache light sensitivity nausea migraine")
    assert res["urgency_level"] in ["Routine Care", "Urgent Care"]
    assert res["esi_score"] <= 3

def test_mild_headache_is_self_care():
    """Tension headache = Self Care, ESI 4."""
    res = analyze_symptoms("dull mild headache forehead pressure stress")
    assert res["urgency_level"] == "Self Care"
    assert res["esi_score"] == 4

def test_runny_nose_is_self_care():
    """Common cold = Self Care, ESI 4."""
    res = analyze_symptoms("runny nose sneezing mild sore throat common cold")
    assert res["esi_score"] == 4

def test_burning_urination_is_routine():
    """UTI symptoms = Routine Care, ESI 3."""
    res = analyze_symptoms("burning urination frequent urination cloudy urine uti")
    assert res["esi_score"] <= 3

def test_diarrhea_vomiting_is_self_care():
    """Gastroenteritis = Self Care, ESI 4."""
    res = analyze_symptoms("diarrhea vomiting nausea gastroenteritis stomach cramps")
    assert res["esi_score"] == 4


# ── Vitals Risk Adjuster Tests ────────────────────────────────

def test_high_fahrenheit_fever_triggers():
    """103°F = High Fever, must elevate ESI."""
    res = analyze_symptoms("mild symptoms", vitals={"temperature": "103.0"})
    fever_flags = [r for r in res["risk_factors_triggered"] if "Fever" in r]
    assert len(fever_flags) > 0

def test_high_celsius_fever_triggers():
    """39.5°C = High Fever."""
    res = analyze_symptoms("mild symptoms", vitals={"temperature": "39.5"})
    fever_flags = [r for r in res["risk_factors_triggered"] if "Fever" in r]
    assert len(fever_flags) > 0

def test_critical_spo2_triggers_emergency():
    """SpO2 < 90% must escalate to ESI 1."""
    res = analyze_symptoms("shortness of breath", vitals={"spo2": "88"})
    assert res["esi_score"] == 1

def test_elderly_patient_elevates_esi():
    """Age > 75 must add geriatric risk flag."""
    res = analyze_symptoms("mild fatigue", vitals={"age": "80"})
    age_flags = [r for r in res["risk_factors_triggered"] if "Geriatric" in r or "Advanced" in r]
    assert len(age_flags) > 0


# ── Differential Diagnosis Tests ──────────────────────────────

def test_differential_probabilities_sum_to_100():
    """Differential diagnosis probabilities must sum to ~100%."""
    res = analyze_symptoms("throbbing headache nausea light sensitivity migraine aura")
    total = sum(d["probability"] for d in res["differential_diagnosis"])
    assert abs(total - 100.0) < 2.0, f"Probabilities sum to {total}"

def test_differential_not_all_equal():
    """Probabilities must NOT all be 15% flat — must reflect actual match strength."""
    res = analyze_symptoms("severe right lower abdominal pain fever nausea appendicitis")
    probs = [d["probability"] for d in res["differential_diagnosis"]]
    assert max(probs) > 40.0, f"Top prob too low: {max(probs)}"


# ── Image Upload Tests ────────────────────────────────────────

def test_image_attached_returns_visual_notes():
    """Image attachment must return visual assessment notes."""
    res = analyze_symptoms("red skin rash itchy eczema", image_attached=True)
    assert res["visual_assessment_notes"] is not None

def test_no_image_no_visual_notes():
    """No image = no visual assessment notes."""
    res = analyze_symptoms("headache", image_attached=False)
    assert res["visual_assessment_notes"] is None


# ── Flask API Tests ───────────────────────────────────────────

def test_flask_index_loads():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"MediTriage" in response.data

def test_api_triage_emergency():
    client = app.test_client()
    payload = {"symptoms": "crushing chest pain radiating to arm", "vitals": {}}
    response = client.post("/api/v1/triage", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["urgency_level"] == "Emergency"

def test_api_triage_self_care():
    client = app.test_client()
    payload = {"symptoms": "runny nose sneezing mild cold"}
    response = client.post("/api/v1/triage", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["esi_score"] == 4

def test_api_bad_request():
    client = app.test_client()
    response = client.post("/api/v1/triage", json={})
    assert response.status_code == 400

def test_api_metrics():
    client = app.test_client()
    response = client.get("/api/v1/model/metrics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["dataset_samples"] >= 20
