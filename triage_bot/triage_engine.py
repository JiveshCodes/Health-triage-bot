# triage_engine.py
def analyze_symptoms(symptoms: str) -> dict:
    text = symptoms.lower()

    # Very simple rules
    if "chest pain" in text or "shortness of breath" in text:
        return {
            "recommendation": "Emergency",
            "advice": "Seek emergency care immediately.",
            "conditions": ["Possible heart or lung emergency"]
        }
    elif "fever" in text and "cough" in text:
        return {
            "recommendation": "See Doctor",
            "advice": "Consult a doctor soon.",
            "conditions": ["Flu or Viral Infection", "COVID-19"]
        }
    elif "headache" in text:
        return {
            "recommendation": "Home Care",
            "advice": "Rest, drink water, use over-the-counter pain relief.",
            "conditions": ["Tension headache", "Migraine"]
        }
    else:
        return {
            "recommendation": "Home Care",
            "advice": "Monitor your symptoms. See a doctor if it worsens.",
            "conditions": ["Minor illness", "Allergic reaction"]
        }