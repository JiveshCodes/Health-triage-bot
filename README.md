# ⚕ MediTriage AI - Enterprise Clinical Decision & Triage Platform

> An enterprise-grade, multi-modal AI Healthcare Platform featuring a **Hybrid Machine Learning Engine**, vital signs risk scoring, interactive anatomical symptom mapping, voice speech-to-text input, visual symptom photo reference uploading, downloadable clinical reports, and RESTful APIs.

---

## 🌟 Key Features

1. **Hybrid AI & Clinical Safety Engine**:
   - **Machine Learning Text Classifier**: TF-IDF vectorization paired with statistical classification models predicting differential diagnoses and probability distributions.
   - **Multi-Factor Vitals & Comorbidities Adjuster**: Dynamically evaluates Age, Body Temperature, SpO2 (Oxygen Saturation), Heart Rate, Diabetes, and Heart Disease to elevate triage urgency.
   - **Clinical Red-Flag Guardrail**: Real-time safety override enforcing immediate ESI Level 1 Emergency response for cardiac, neurological (FAST stroke), or anaphylactic red flags.

2. **Interactive Anatomical Body Map**:
   - SVG-based interactive anatomical body part selector (Head/Neck, Chest/Heart, Abdomen, Limbs, Skin, Systemic) to intuitively filter and highlight symptoms.

3. **Multi-Modal Input (Voice + Image Upload)**:
   - **Voice Speech-to-Text**: Web Speech API integration allowing hands-free microphone dictation of symptoms.
   - **Visual Symptom Photo Reference**: Upload reference photographs (e.g. skin rashes, eye redness, swelling, cuts) with instant client-side thumbnail previews.

4. **10/10 Interactive Dashboard & Visual Analytics**:
   - **Animated Urgency Gauge Speedometer**: Displays Emergency Severity Index (ESI 1–4) with color-coded alerts (Red, Orange, Yellow, Green).
   - **Differential Diagnosis Probabilities**: Interactive progress bars showcasing confidence percentages across top matching medical conditions.
   - **Clinical Action Checklist**: Clear, actionable step-by-step guidance.

5. **Downloadable Clinical PDF / Print Summary**:
   - Print-optimized CSS rendering clean medical reports with timestamp, patient vitals summary, triage code, and attached photo reference.

6. **Enterprise RESTful API**:
   - `/api/v1/triage` - Multi-modal JSON POST endpoint.
   - `/api/v1/symptoms` - Symptom database by body region.
   - `/api/v1/model/metrics` - Model health & accuracy statistics.

---

## 📐 System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                   ENTERPRISE MULTI-MODAL FRONTEND                                 |
|  +--------------------------------+  +----------------------------------+  +-------------------+  |
|  |  Interactive SVG Body Map      |  |  Free-Text & Voice Speech Input  |  |  Image Reference  |  |
|  |  (Head, Chest, Abdomen, etc.)  |  |  Demographics & Vital Signs      |  |  Upload & Preview |  |
|  +--------------------------------+  +----------------------------------+  +-------------------+  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                        HYBRID AI CORE                                             |
|  +------------------------------+  +-------------------------------------------+  +------------+  |
|  | ML NLP Classifier            |  | Vital Signs & Comorbidity Risk Adjuster   |  | Visual     |  |
|  | (TF-IDF + Ensembled ML)     |  | (Age, SpO2, Temp, HR, BP, Diabetes, etc)  |  | Symptom    |  |
|  +------------------------------+  +-------------------------------------------+  | Assessment |  |
|  +------------------------------+  +-------------------------------------------+  | Module     |  |
|  | Differential Diagnosis Engine|  | Clinical Red-Flag Safety Net              |  +------------+  |
|  | (Probability Distributions)   |  | (Immediate Emergency Overrides)           |                 |
|  +------------------------------+  +-------------------------------------------+                 |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                    RESULTS & DIAGNOSTICS UI                                       |
|  - Animated Urgency Gauge Speedometer Meter (Red / Orange / Yellow / Green - ESI 1-4)             |
|  - Differential Diagnosis Confidence Bar / Radar Charts                                           |
|  - Visual Symptom Image Reference Card with thumbnail & observation highlights                    |
|  - Actionable Patient Guidance & Recommended Medical Specialist                                   |
|  - Downloadable Professional Clinical Report (PDF/Print) with Attached Image                      |
|  - Triage Assessment History Log (LocalStorage) & Multi-Language Toggle                           |
+---------------------------------------------------------------------------------------------------+
```

---

## 🚦 Emergency Severity Index (ESI) Standard

| Level | Urgency Category | Color Code | Response Time | Example Conditions |
| :---: | :--- | :---: | :---: | :--- |
| **ESI 1** | **Emergency** | 🔴 Red | **Immediate** | Acute Coronary Syndrome, Anaphylaxis, Stroke, Severe Dyspnea |
| **ESI 2** | **Urgent Care** | 🟠 Orange | **< 1-2 Hours** | High Fever + Cough, Acute Appendicitis, Severe Asthma Attack |
| **ESI 3** | **Routine Care** | 🟡 Yellow | **24-48 Hours** | Migraine, GERD, Sprained Ankle, Conjunctivitis, Pharyngitis |
| **ESI 4** | **Self-Care** | 🟢 Green | **Home Monitoring** | Tension Headache, Mild Allergic Rhinitis, Lumbar Strain |

---

## 🔌 RESTful API Documentation

### `POST /api/v1/triage`
Submits symptoms, vitals, and image reference flag for instant AI triage.

**Request Payload**:
```json
{
  "symptoms": "sharp chest pain radiating to left arm shortness of breath",
  "vitals": {
    "age": 58,
    "temperature": 99.2,
    "spo2": 95,
    "heart_disease": true
  },
  "image_attached": false,
  "body_region": "chest"
}
```

**Response Payload**:
```json
{
  "status": "success",
  "data": {
    "urgency_level": "Emergency",
    "urgency_code": "red",
    "esi_score": 1,
    "confidence_score": 98.5,
    "primary_recommendation": "IMMEDIATE EMERGENCY CARE REQUIRED",
    "differential_diagnosis": [
      {
        "condition": "Acute Coronary Syndrome",
        "probability": 92.0,
        "specialist": "Cardiologist"
      }
    ],
    "safety_override": true,
    "emergency_contact": "911 (US) / 112 (EU) / 102 (India)"
  }
}
```

---

## 🛠 Quick Start & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train ML Model
```bash
python train_model.py
```

### 3. Run Web Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

### 4. Run Automated Unit Tests
```bash
python -m pytest tests/
```

---

## ⚠️ Medical Safety Disclaimer
MediTriage AI is designed exclusively for educational, demonstration, and research purposes. It is **not** a certified medical diagnostic device. It does not provide definitive medical diagnosis or treatment advice. Users must always seek professional clinical advice from qualified healthcare providers.
