"""
MediTriage AI - Self-Evaluation Diagnostic Script
Tests 25 clinical cases: predicted vs expected
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from triage_engine import analyze_symptoms

# ─────────────────────────────────────────────────────────────
# Test Cases: (description, symptoms, vitals, expected_urgency, expected_esi)
# ─────────────────────────────────────────────────────────────
TEST_CASES = [
    # ── SIMPLE / SELF-CARE ──────────────────────────────────
    {
        "id": 1, "label": "Common Cold",
        "symptoms": "runny nose sneezing mild sore throat nasal congestion",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 2, "label": "Tension Headache",
        "symptoms": "dull headache pressure across forehead stress both sides",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 3, "label": "Neck & Shoulder Pain",
        "symptoms": "neck pain stiffness around shoulders while moving",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 4, "label": "Lower Back Pain",
        "symptoms": "lower back pain lumbar ache stiffness after sitting",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 5, "label": "Fatigue / Tiredness",
        "symptoms": "fatigue tiredness weakness lack of energy not feeling well",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 6, "label": "Mild Skin Rash",
        "symptoms": "itchy red skin rash dry patches eczema contact dermatitis",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 7, "label": "Allergic Rhinitis",
        "symptoms": "sneezing itchy watery eyes runny nose hay fever seasonal allergy",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    {
        "id": 8, "label": "Insomnia",
        "symptoms": "unable to sleep insomnia waking up at night poor sleep",
        "vitals": {},
        "expected_urgency": "Self Care", "expected_esi": 4
    },
    # ── ROUTINE / DOCTOR VISIT ──────────────────────────────
    {
        "id": 9, "label": "Migraine Headache",
        "symptoms": "throbbing one sided headache light sensitivity nausea migraine aura",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 10, "label": "UTI (Uncomplicated)",
        "symptoms": "burning urination frequent urination cloudy urine bladder infection uti",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 11, "label": "GERD / Acid Reflux",
        "symptoms": "heartburn acid reflux burning stomach pain after eating gerd",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 12, "label": "Sore Throat / Tonsillitis",
        "symptoms": "sore throat difficulty swallowing swollen tonsils strep throat",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 13, "label": "Pink Eye (Conjunctivitis)",
        "symptoms": "red eye discharge crusting eyelids conjunctivitis pink eye morning sticky",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 14, "label": "Dizziness / Vertigo",
        "symptoms": "room spinning dizziness vertigo balance problems lightheaded nausea",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 15, "label": "Toothache / Dental Abscess",
        "symptoms": "toothache dental pain jaw throbbing tooth abscess gum swelling",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    {
        "id": 16, "label": "Anxiety / Panic Attack",
        "symptoms": "anxiety panic attack racing heart rapid breathing excessive worry nervousness",
        "vitals": {},
        "expected_urgency": "Routine Care", "expected_esi": 3
    },
    # ── URGENT ───────────────────────────────────────────────
    {
        "id": 17, "label": "Influenza / COVID-19",
        "symptoms": "high fever dry cough body aches fatigue sore throat loss of taste flu",
        "vitals": {},
        "expected_urgency": "Urgent Care", "expected_esi": 2
    },
    {
        "id": 18, "label": "Acute Appendicitis",
        "symptoms": "severe right lower abdominal pain fever nausea appendicitis pain walking",
        "vitals": {},
        "expected_urgency": "Urgent Care", "expected_esi": 2
    },
    {
        "id": 19, "label": "Asthma Attack",
        "symptoms": "severe wheezing asthma attack shortness of breath chest tightness inhaler not helping",
        "vitals": {},
        "expected_urgency": "Urgent Care", "expected_esi": 2
    },
    {
        "id": 20, "label": "Kidney Infection",
        "symptoms": "high fever flank pain kidney infection blood in urine chills painful urination fever",
        "vitals": {},
        "expected_urgency": "Urgent Care", "expected_esi": 2
    },
    {
        "id": 21, "label": "Elderly with Fever (Vitals)",
        "symptoms": "fever cough fatigue",
        "vitals": {"age": "78", "temperature": "102.5"},
        "expected_urgency": "Urgent Care", "expected_esi": 2
    },
    # ── EMERGENCY ────────────────────────────────────────────
    {
        "id": 22, "label": "Heart Attack",
        "symptoms": "crushing chest pain radiating to left arm jaw sweating heart attack",
        "vitals": {},
        "expected_urgency": "Emergency", "expected_esi": 1
    },
    {
        "id": 23, "label": "Stroke (FAST)",
        "symptoms": "face drooping arm weakness slurred speech sudden stroke symptoms",
        "vitals": {},
        "expected_urgency": "Emergency", "expected_esi": 1
    },
    {
        "id": 24, "label": "Anaphylactic Shock",
        "symptoms": "throat swelling tongue swelling severe allergic reaction difficulty breathing anaphylaxis",
        "vitals": {},
        "expected_urgency": "Emergency", "expected_esi": 1
    },
    {
        "id": 25, "label": "Subarachnoid Haemorrhage",
        "symptoms": "thunderclap headache worst headache ever sudden severe head pain",
        "vitals": {},
        "expected_urgency": "Emergency", "expected_esi": 1
    },
]

def run_evaluation():
    print("\n" + "="*95)
    print(f"  {'MediTriage AI — Self-Evaluation Report':^91}")
    print("="*95)
    print(f"  {'#':<4} {'Test Case':<30} {'Expected':<14} {'Predicted':<14} {'ESI E/P':<10} {'Status':<8} {'Top Diagnosis'}")
    print("-"*95)

    passed = 0
    failed = 0
    failures = []

    for tc in TEST_CASES:
        res = analyze_symptoms(tc["symptoms"], vitals=tc["vitals"])

        predicted_urgency = res["urgency_level"]
        predicted_esi = res["esi_score"]
        expected_urgency = tc["expected_urgency"]
        expected_esi = tc["expected_esi"]
        top_diag = res["differential_diagnosis"][0]["condition"] if res["differential_diagnosis"] else "N/A"
        top_prob = res["differential_diagnosis"][0]["probability"] if res["differential_diagnosis"] else 0

        ok = (predicted_urgency == expected_urgency and predicted_esi == expected_esi)
        status = "✅ PASS" if ok else "❌ FAIL"

        if ok:
            passed += 1
        else:
            failed += 1
            failures.append({
                "id": tc["id"],
                "label": tc["label"],
                "symptoms": tc["symptoms"],
                "expected_urgency": expected_urgency,
                "expected_esi": expected_esi,
                "predicted_urgency": predicted_urgency,
                "predicted_esi": predicted_esi,
                "top_diag": top_diag,
                "top_prob": top_prob,
                "confidence": res["confidence_score"],
                "risk_factors": res["risk_factors_triggered"],
                "diff_diag": res["differential_diagnosis"]
            })

        top_short = (top_diag[:38] + "..") if len(top_diag) > 40 else top_diag
        print(f"  {tc['id']:<4} {tc['label']:<30} {expected_urgency:<14} {predicted_urgency:<14} {expected_esi}/{predicted_esi:<8} {status} {top_short} ({top_prob}%)")

    print("="*95)
    accuracy = round((passed / len(TEST_CASES)) * 100, 1)
    print(f"\n  RESULTS: {passed}/{len(TEST_CASES)} passed | Accuracy: {accuracy}%\n")

    if failures:
        print("─"*95)
        print("  FAILURE ANALYSIS — Cases requiring fixes:")
        print("─"*95)
        for f in failures:
            print(f"\n  [Case {f['id']}] {f['label']}")
            print(f"    Symptoms      : {f['symptoms']}")
            print(f"    Expected      : {f['expected_urgency']} (ESI {f['expected_esi']})")
            print(f"    Predicted     : {f['predicted_urgency']} (ESI {f['predicted_esi']})")
            print(f"    Top Diagnosis : {f['top_diag']} ({f['top_prob']}%)")
            print(f"    Confidence    : {f['confidence']}%")
            if f['risk_factors']:
                print(f"    Risk Factors  : {', '.join(f['risk_factors'])}")
            print(f"    Full Diff     : {[(d['condition'][:35], d['probability']) for d in f['diff_diag']]}")
    else:
        print("  All cases passed! Engine is accurate.")

    print("\n" + "="*95 + "\n")
    return failures

if __name__ == "__main__":
    failures = run_evaluation()
    sys.exit(0 if not failures else 1)
