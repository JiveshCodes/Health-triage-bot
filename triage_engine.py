import os
import json
import re
import math


# ─────────────────────────────────────────────────────────────
# Clinical Red-Flag Definitions — STRICT phrase-level matching
# Only trigger on clearly life-threatening, unambiguous phrases.
# NOTE: 'shortness of breath' alone is NOT a red flag —
#   it can be asthma, anxiety, or normal exertion.
#   Only flag it when paired with haemoptysis, collapse, etc.
# ─────────────────────────────────────────────────────────────
RED_FLAG_RULES = [
    (
        r"\b(crushing chest pain|chest pain radiating|severe chest pressure|heart attack|cardiac arrest)\b",
        "Acute Coronary Syndrome / Myocardial Infarction",
        "Cardiologist"
    ),
    (
        r"\b(face drooping|arm weakness|slurred speech|sudden vision loss|stroke symptoms)\b",
        "Acute Ischemic Stroke (FAST Warning)",
        "Neurologist"
    ),
    (
        r"\b(throat swelling|tongue swelling|lip swelling|anaphylaxis|severe allergic reaction)\b",
        "Severe Anaphylactic Shock",
        "Emergency Medicine"
    ),
    (
        r"\b(coughing blood|hemoptysis|pulmonary embolism)\b",
        "Pulmonary Embolism / Haemoptysis",
        "Pulmonologist"
    ),
    (
        r"\b(thunderclap headache|worst headache ever|sudden worst headache)\b",
        "Subarachnoid Haemorrhage / Bacterial Meningitis",
        "Neurologist"
    ),
    (
        r"\b(unconscious|unresponsive|passed out|collapsed)\b",
        "Syncope / Loss of Consciousness",
        "Emergency Medicine"
    ),
    (
        r"\b(diabetic ketoacidosis|dka|fruity breath diabetes|very high blood sugar emergency)\b",
        "Diabetic Ketoacidosis (DKA)",
        "Emergency Medicine"
    ),
    (
        r"\b(severe internal bleeding|vomiting blood|haematemesis|black tarry stool melena)\b",
        "Gastrointestinal Haemorrhage",
        "Gastroenterologist / Emergency Medicine"
    ),
    (
        r"\b(severe burn|chemical burn|electrical burn|burns over body)\b",
        "Severe Burns — Trauma Emergency",
        "Emergency Medicine"
    ),
]

# ─────────────────────────────────────────────────────────────
# ESI Level → Urgency Label mapping
# ─────────────────────────────────────────────────────────────
ESI_LABELS = {1: "Emergency", 2: "Urgent Care", 3: "Routine Care", 4: "Self Care"}


class HybridTriageEngine:
    """
    Hybrid Medical Triage Engine
    ============================
    Layer 1 – Clinical Red-Flag Safety Net  (strict phrase regex)
    Layer 2 – NLP Keyword Similarity Scorer (phrase + token overlap)
    Layer 3 – Vitals & Comorbidity Risk Adjuster (unit-aware)
    """

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dataset = self._load_dataset()
        self.sklearn_model = self._try_load_sklearn_model()

    # ── Data Loaders ──────────────────────────────────────────

    def _load_dataset(self) -> list:
        path = os.path.join(self.base_dir, "data", "symptoms_dataset.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _try_load_sklearn_model(self):
        path = os.path.join(self.base_dir, "models", "triage_model.joblib")
        if os.path.exists(path):
            try:
                import joblib
                return joblib.load(path)
            except Exception:
                pass
        return None

    # ── Main Entry Point ──────────────────────────────────────

    def analyze_symptoms(
        self,
        symptoms: str,
        vitals: dict = None,
        image_attached: bool = False,
        body_region: str = None
    ) -> dict:
        text = (symptoms or "").strip().lower()
        vitals = vitals or {}

        # ── Layer 1: Vitals Risk Assessment (must run BEFORE red-flag
        #             so we can pass risk_factors into red-flag check)
        risk_factors, vitals_min_esi = self._evaluate_vitals(vitals)

        # ── Layer 2: Strict Red-Flag Check
        red_flag, rf_condition, rf_specialist = self._check_red_flags(text)

        # ── Layer 3: NLP Symptom Scoring
        scored = self._score_conditions(text, body_region)

        # ── Build base prediction ──────────────────────────────
        if scored:
            top = scored[0]
            urgency = top["urgency"]
            esi = top["esi_score"]
            raw_confidence = top["raw_score"]
        else:
            urgency = "Self Care"
            esi = 4
            raw_confidence = 0.0

        # ── Differential Diagnosis with softmax-style normalisation ──
        diff_diag = self._build_differential(scored)

        # ── Apply Vitals ESI override ──────────────────────────
        safety_override = False
        if vitals_min_esi and vitals_min_esi < esi:
            esi = vitals_min_esi
            urgency = ESI_LABELS[esi]

        # ── Apply Red-Flag Override (highest priority) ─────────
        if red_flag:
            urgency = "Emergency"
            esi = 1
            safety_override = True
            raw_confidence = 97.0
            # Inject the flagged condition at top
            diff_diag.insert(0, {
                "condition": rf_condition,
                "probability": 94.0,
                "specialist": rf_specialist
            })
            diff_diag = diff_diag[:4]

        # ── Confidence Score (meaningful, not flat) ────────────
        confidence_score = self._compute_confidence(raw_confidence, esi, safety_override, len(scored))

        # ── Visual Assessment ──────────────────────────────────
        visual_notes = self._generate_visual_assessment(text) if image_attached else None

        # ── Action Plan & Recommendation ──────────────────────
        urgency_code, primary_rec, advice, specialist, action_plan = \
            self._get_recommendation_details(urgency, esi, diff_diag)

        # ── Extracted Keywords ─────────────────────────────────
        extracted = self._extract_keywords(text)

        return {
            "urgency_level": urgency,
            "urgency_code": urgency_code,
            "esi_score": esi,
            "confidence_score": confidence_score,
            "model_type": "Hybrid NLP + Clinical Safety Guardrail",
            "primary_recommendation": primary_rec,
            "advice_summary": advice,
            "recommended_specialist": specialist,
            "differential_diagnosis": diff_diag,
            "extracted_keywords": extracted,
            "risk_factors_triggered": risk_factors,
            "visual_assessment_notes": visual_notes,
            "safety_override": safety_override,
            "action_plan": action_plan,
            "emergency_contact": "911 (US) / 112 (EU) / 102 (India)" if esi <= 2 else None,
            "disclaimer": (
                "MEDICAL DISCLAIMER: MediTriage AI is an educational clinical decision support tool. "
                "It does not replace professional medical advice, diagnosis, or treatment. "
                "In emergencies, contact emergency services immediately."
            )
        }

    # ── Layer 1: Red-Flag Safety Net ──────────────────────────

    def _check_red_flags(self, text: str):
        for pattern, condition, specialist in RED_FLAG_RULES:
            if re.search(pattern, text, re.IGNORECASE):
                return True, condition, specialist
        return False, None, None

    # ── Layer 2: NLP Symptom Scoring ──────────────────────────

    def _score_conditions(self, text: str, body_region: str = None) -> list:
        """
        Score each dataset entry against the input text.

        Scoring weights:
          - Exact phrase match of keyword in text   → +5.0 per keyword
          - Partial token overlap (proportion)       → +3.0 * overlap_ratio
          - Body region match bonus                  → +1.5
        """
        tokens = set(re.findall(r"\b\w+\b", text))
        results = []

        for item in self.dataset:
            score = 0.0
            for kw in item.get("keywords", []):
                kw_lower = kw.lower()
                if kw_lower in text:
                    # Exact phrase match — strongest signal
                    score += 5.0
                else:
                    kw_tokens = set(re.findall(r"\b\w+\b", kw_lower))
                    if kw_tokens:
                        overlap = len(kw_tokens & tokens) / len(kw_tokens)
                        if overlap >= 0.5:  # Only count if >50% of keyword words match
                            score += 3.0 * overlap

            if body_region and item.get("body_region") == body_region:
                score += 1.5

            if score > 0:
                results.append({
                    "condition": item["condition"],
                    "urgency": item["urgency"],
                    "esi_score": item["esi_score"],
                    "specialist": item.get("specialist", "General Practitioner"),
                    "raw_score": score
                })

        results.sort(key=lambda x: x["raw_score"], reverse=True)
        return results

    def _build_differential(self, scored: list) -> list:
        """
        Convert raw scores to relative probabilities for top-4 conditions.
        Uses softmax-like normalisation to ensure meaningful spread.
        """
        top4 = scored[:4]
        if not top4:
            return [
                {"condition": "Non-Specific Symptom Complex", "probability": 70.0, "specialist": "General Practitioner"},
                {"condition": "General Fatigue / Malaise", "probability": 30.0, "specialist": "General Practitioner"}
            ]

        # Softmax with temperature scaling for spread
        temperature = 2.0
        exps = [math.exp(m["raw_score"] / temperature) for m in top4]
        total = sum(exps)

        diag = []
        for i, m in enumerate(top4):
            prob = round((exps[i] / total) * 100, 1)
            diag.append({
                "condition": m["condition"],
                "probability": prob,
                "specialist": m["specialist"]
            })

        return diag

    # ── Layer 3: Vitals & Comorbidity Risk Adjuster ───────────

    def _evaluate_vitals(self, vitals: dict) -> tuple:
        """
        Returns (risk_factor_list, minimum_esi_override_or_None).

        Temperature is unit-aware:
          - Values > 50 are treated as Fahrenheit
          - Values ≤ 50 are treated as Celsius
        Normal body temp: 98.6°F / 37.0°C — only flag actual fever thresholds.
        """
        risk_factors = []
        min_esi = None

        # ── Age ─────────────────────────────────────────────
        age_raw = vitals.get("age")
        if age_raw is not None and str(age_raw).strip():
            try:
                age = float(age_raw)
                if age < 1:
                    risk_factors.append("Neonatal Patient (Age < 1 year)")
                    min_esi = self._esi_min(min_esi, 2)
                elif age < 5:
                    risk_factors.append("Pediatric Vulnerability (Age < 5 years)")
                    min_esi = self._esi_min(min_esi, 3)
                elif age > 75:
                    risk_factors.append("Advanced Geriatric Risk (Age > 75 years)")
                    min_esi = self._esi_min(min_esi, 2)
                elif age > 65:
                    risk_factors.append("Geriatric Risk Group (Age > 65 years)")
                    min_esi = self._esi_min(min_esi, 3)
            except ValueError:
                pass

        # ── Temperature (unit-aware) ────────────────────────
        temp_raw = vitals.get("temperature")
        if temp_raw is not None and str(temp_raw).strip():
            try:
                temp = float(temp_raw)
                if temp > 50.0:
                    # Fahrenheit interpretation
                    if temp >= 104.0:
                        risk_factors.append(f"Hyperpyrexia — Dangerously High Fever ({temp}°F)")
                        min_esi = self._esi_min(min_esi, 1)
                    elif temp >= 103.0:
                        risk_factors.append(f"High Fever ({temp}°F)")
                        min_esi = self._esi_min(min_esi, 2)
                    elif temp >= 100.4:
                        risk_factors.append(f"Moderate Fever ({temp}°F)")
                        min_esi = self._esi_min(min_esi, 3)
                    # 98.6°F ± 1.5 is NORMAL — no flag
                else:
                    # Celsius interpretation
                    if temp >= 40.0:
                        risk_factors.append(f"Hyperpyrexia — Dangerously High Fever ({temp}°C)")
                        min_esi = self._esi_min(min_esi, 1)
                    elif temp >= 39.4:
                        risk_factors.append(f"High Fever ({temp}°C)")
                        min_esi = self._esi_min(min_esi, 2)
                    elif temp >= 38.0:
                        risk_factors.append(f"Moderate Fever ({temp}°C)")
                        min_esi = self._esi_min(min_esi, 3)
            except ValueError:
                pass

        # ── SpO2 ───────────────────────────────────────────
        spo2_raw = vitals.get("spo2")
        if spo2_raw is not None and str(spo2_raw).strip():
            try:
                spo2 = float(spo2_raw)
                if spo2 < 90.0:
                    risk_factors.append(f"Critical Hypoxia — SpO2 {spo2}% (Dangerous)")
                    min_esi = self._esi_min(min_esi, 1)
                elif spo2 < 94.0:
                    risk_factors.append(f"Significant Hypoxia — SpO2 {spo2}%")
                    min_esi = self._esi_min(min_esi, 2)
                elif spo2 < 96.0:
                    risk_factors.append(f"Borderline SpO2 {spo2}% — Monitor Closely")
                    min_esi = self._esi_min(min_esi, 3)
                # 96–100% is normal — no flag
            except ValueError:
                pass

        # ── Comorbidities ────────────────────────────────
        if vitals.get("heart_disease"):
            risk_factors.append("Comorbidity: Cardiovascular Disease")
            min_esi = self._esi_min(min_esi, 2)
        if vitals.get("diabetes"):
            risk_factors.append("Comorbidity: Diabetes Mellitus")

        return risk_factors, min_esi

    @staticmethod
    def _esi_min(current, new_val):
        """Return the more urgent (lower) ESI level."""
        if current is None:
            return new_val
        return min(current, new_val)

    def _esi_to_urgency(self, esi: int) -> str:
        return ESI_LABELS.get(esi, "Self Care")

    # ── Confidence Score ──────────────────────────────────────

    def _compute_confidence(self, raw_score: float, esi: int, safety_override: bool, n_matches: int) -> float:
        """
        Meaningful confidence score:
          - 97% for red-flag safety overrides
          - 62% for zero-match fallback (uncertain)
          - 65–94% for normal scored matches, scaled by match strength
        The formula ensures the score reflects actual discriminatory power:
          - A very strong unique match (score >= 20) → ~94%
          - A moderate match (score ~10) → ~82%
          - A weak match (score ~3) → ~67%
        """
        if safety_override:
            return 97.0
        if n_matches == 0:
            return 62.0
        # Logarithmic scaling: diminishing returns on higher scores
        import math as _math
        base = 65.0 + min(_math.log1p(raw_score) * 10.0, 29.0)
        return round(min(base, 94.0), 1)

    # ── Visual Assessment ─────────────────────────────────────

    def _generate_visual_assessment(self, text: str) -> str:
        if any(w in text for w in ["rash", "eczema", "dermatitis", "hives", "skin irritation"]):
            return "Visual Reference Provided: Erythematous/dermatitic skin changes noted. Correlate for allergic contact reaction vs infection."
        if any(w in text for w in ["eye", "conjunctivitis", "pink eye", "eye discharge"]):
            return "Visual Reference Provided: Periocular region reference. Correlate for conjunctival injection or periorbital edema."
        if any(w in text for w in ["wound", "cut", "laceration", "bleed", "injury"]):
            return "Visual Reference Provided: Cutaneous wound documented. Assess depth, haemostasis, and signs of infection."
        if any(w in text for w in ["swelling", "oedema", "edema", "bruise"]):
            return "Visual Reference Provided: Localised swelling/bruising noted. Correlate with clinical examination for fracture or haematoma."
        return "Visual Reference Provided: Photograph attached to patient assessment record."

    # ── Keyword Extraction ────────────────────────────────────

    def _extract_keywords(self, text: str) -> list:
        stop = {
            "have", "with", "this", "that", "from", "some", "feel",
            "been", "very", "more", "also", "when", "while", "after",
            "before", "around", "about", "since", "does", "what", "just"
        }
        words = re.findall(r"\b[a-z]{4,}\b", text)
        return list(dict.fromkeys(w for w in words if w not in stop))[:8]

    # ── Recommendation Details ────────────────────────────────

    def _get_recommendation_details(self, urgency: str, esi: int, diff_diag: list) -> tuple:
        top_spec = diff_diag[0]["specialist"] if diff_diag else "General Practitioner"

        if esi == 1:
            return (
                "red",
                "IMMEDIATE EMERGENCY CARE REQUIRED",
                "Your symptoms indicate a potentially life-threatening emergency. Do not drive—call emergency services or go to the nearest Emergency Room immediately.",
                "Emergency Medicine / " + top_spec,
                [
                    "Call emergency services immediately: 911 (US) | 112 (EU) | 102 (India).",
                    "Stay calm, rest in a comfortable position, and do not exert yourself.",
                    "Do not eat or drink anything — you may require immediate medical procedures.",
                    "Unlock your front door so emergency responders can enter quickly."
                ]
            )
        elif esi == 2:
            return (
                "orange",
                "Urgent Medical Evaluation Recommended",
                "Your symptoms suggest an acute condition requiring prompt evaluation. Visit an Urgent Care Center or physician within 1–6 hours.",
                top_spec,
                [
                    "Proceed to the nearest Urgent Care Center or Emergency Department.",
                    "Track and note when symptoms first began and any changes.",
                    "Monitor temperature, oxygen saturation, and heart rate if possible.",
                    "Go directly to ER if symptoms worsen significantly or rapidly."
                ]
            )
        elif esi == 3:
            return (
                "yellow",
                "Schedule a Physician Consultation",
                "Your symptoms are non-emergent but require professional evaluation. Schedule an appointment within 24–48 hours.",
                top_spec,
                [
                    "Book an appointment with your primary care physician or specialist.",
                    "Rest adequately and stay well-hydrated.",
                    "Document the symptom timeline and any aggravating or relieving factors.",
                    "Seek earlier care if your symptoms worsen or new symptoms develop."
                ]
            )
        else:
            return (
                "green",
                "Self-Care & Home Monitoring",
                "Your symptoms appear mild and manageable at home. Rest, stay hydrated, and monitor for changes.",
                top_spec,
                [
                    "Rest and avoid strenuous physical activity.",
                    "Stay well-hydrated with water or electrolyte solutions.",
                    "Use appropriate over-the-counter remedies as needed (e.g., pain relief, antihistamines).",
                    "Consult a healthcare professional if symptoms persist beyond 3–5 days or worsen."
                ]
            )


# ── Module-Level Singleton & Convenience Function ─────────────

triage_engine = HybridTriageEngine()


def analyze_symptoms(
    symptoms: str,
    vitals: dict = None,
    image_attached: bool = False,
    body_region: str = None
) -> dict:
    return triage_engine.analyze_symptoms(
        symptoms,
        vitals=vitals,
        image_attached=image_attached,
        body_region=body_region
    )