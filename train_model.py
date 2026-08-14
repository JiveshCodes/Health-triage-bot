import os
import json

def train_and_export_models():
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "symptoms_dataset.json")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # 1. Build Fallback JSON Model for zero-dependency execution
    fallback_model = {
        "dataset": dataset,
        "vocabulary": list(set([kw for item in dataset for kw in item.get("keywords", [])]))
    }
    fallback_path = os.path.join(models_dir, "fallback_model.json")
    with open(fallback_path, "w", encoding="utf-8") as f:
        json.dump(fallback_model, f, indent=2)
    print(f"[+] Fallback JSON model exported to {fallback_path}")

    # 2. Train Scikit-Learn Model if available
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import make_pipeline
        import joblib

        corpus = [item["symptoms"] for item in dataset]
        labels = [item["urgency"] for item in dataset]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        X = vectorizer.fit_transform(corpus)

        clf = MultinomialNB()
        clf.fit(X, labels)

        pipeline = make_pipeline(vectorizer, clf)
        model_path = os.path.join(models_dir, "triage_model.joblib")
        joblib.dump(pipeline, model_path)
        print(f"[+] Scikit-learn model successfully saved to {model_path}")
    except ImportError:
        print("[!] Scikit-learn or joblib not installed in current environment. Using fallback JSON model.")

if __name__ == "__main__":
    train_and_export_models()
