# -*- coding: utf-8 -*-
"""
train_model.py — melatih model klasifikasi gejala (+ BMI, tensi, durasi) -> penyakit.

Fitur kategorikal baru (duration_category, bmi_category, tensi_category)
di-encode dengan one-hot encoding (pd.get_dummies) — teknik yang sama
dipakai untuk fitur 'region'/'segment' di project churn model pada
portofolio ini, cuma diterapkan di konteks berbeda.

Metrik utama tetap **top-3 accuracy**, karena aplikasi ini menampilkan
3 kemungkinan teratas, bukan satu jawaban pasti.
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split

from knowledge_base import ALL_SYMPTOMS

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "outputs" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

SYMPTOM_KEYS = list(ALL_SYMPTOMS.keys())
CATEGORICAL_COLS = ["duration_category", "bmi_category", "tensi_category", "age_category"]


def main():
    df = pd.read_csv(DATA_DIR / "symptom_training_data.csv")

    X_symptoms = df[SYMPTOM_KEYS]
    X_categorical = pd.get_dummies(df[CATEGORICAL_COLS], prefix=CATEGORICAL_COLS)
    X = pd.concat([X_symptoms, X_categorical], axis=1)
    feature_columns = list(X.columns)  # urutan ini WAJIB direplikasi persis saat inference

    y = df["disease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300, max_depth=14, min_samples_leaf=2, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    top1_acc = accuracy_score(y_test, y_pred)

    y_proba = model.predict_proba(X_test)
    top3_acc = top_k_accuracy_score(y_test, y_proba, k=3, labels=model.classes_)

    print(f"Jumlah fitur total (gejala + BMI/tensi/durasi): {len(feature_columns)}")
    print(f"Top-1 accuracy: {top1_acc:.4f}")
    print(f"Top-3 accuracy: {top3_acc:.4f}")

    joblib.dump(
        {
            "model": model,
            "symptom_keys": SYMPTOM_KEYS,
            "categorical_cols": CATEGORICAL_COLS,
            "feature_columns": feature_columns,
            "classes": list(model.classes_),
        },
        MODEL_DIR / "disease_model.joblib",
    )

    metrics = {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_diseases": len(model.classes_),
        "n_symptoms": len(SYMPTOM_KEYS),
        "n_features_total": len(feature_columns),
        "top1_accuracy": round(float(top1_acc), 4),
        "top3_accuracy": round(float(top3_acc), 4),
    }
    with open(ROOT / "outputs" / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"Model tersimpan di {MODEL_DIR / 'disease_model.joblib'}")


if __name__ == "__main__":
    main()
