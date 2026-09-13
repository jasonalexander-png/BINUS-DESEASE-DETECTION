# -*- coding: utf-8 -*-
"""
api.py — BINUS Disease Detection API (versi Flask).

Kenapa Flask, bukan FastAPI? PythonAnywhere (hosting gratis yang dipakai
untuk deploy project ini, TANPA perlu kartu kredit sama sekali) versi
gratisnya hanya mendukung aplikasi WSGI (Flask/Django), bukan ASGI
(FastAPI/Starlette). Logika prediksinya 100% sama persis dengan versi
FastAPI sebelumnya — yang beda cuma cara mendefinisikan endpoint & validasi
input.

Endpoint:
  GET  /health
  GET  /symptoms
  GET  /options
  POST /predict

CATATAN KESELAMATAN (sama seperti sebelumnya):
- Setiap response SELALU menyertakan field `disclaimer`.
- `urgent_warning` aktif kalau ada RED_FLAG_SYMPTOMS, TERLEPAS dari hasil model.
- API ini TIDAK PERNAH mengembalikan info dosis obat, resep, atau instruksi pengobatan.
- Field bb/tb/tensi/durasi tetap opsional — "tidak tahu"/"tidak mau jawab"
  dipetakan ke kategori 'tidak_tahu' yang netral (lihat knowledge_base.py).
"""

from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

from knowledge_base import (
    ALL_SYMPTOMS, SYMPTOM_GROUPS, DISEASES, RED_FLAG_SYMPTOMS,
    BMI_CATEGORIES, TENSI_CATEGORIES, DURATION_CATEGORIES, AGE_CATEGORIES,
    bmi_from_bb_tb, age_category_from_years,
)


def get_contributing_symptoms(disease_name, selected_symptoms, top_n=3):
    """Dari gejala yang dipilih user, cari yang paling 'khas' untuk penyakit
    ini (bobot tertinggi di knowledge_base.py). Dipakai untuk explainability
    sederhana di level prediksi individual — BUKAN SHAP/feature importance
    dari model terlatih, tapi transparansi dari basis pengetahuan yang
    dipakai model untuk belajar. Lihat catatan di README bagian Explainability."""
    profile = DISEASES[disease_name]["symptoms"]
    matched = [(s, profile[s]) for s in selected_symptoms if s in profile]
    matched.sort(key=lambda x: x[1], reverse=True)
    return [
        {"symptom": s, "label": ALL_SYMPTOMS[s], "weight": w}
        for s, w in matched[:top_n]
    ]

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "outputs" / "models" / "disease_model.joblib"

DISCLAIMER = (
    "Hasil ini BUKAN diagnosis medis. Ini adalah alat skrining awal edukatif "
    "berbasis pola gejala umum, dibuat untuk keperluan portofolio. Untuk "
    "diagnosis dan penanganan yang akurat, selalu konsultasikan kondisi Anda "
    "langsung dengan dokter."
)

app = Flask(__name__)
CORS(app)  # izinkan diakses dari domain manapun (frontend di Vercel, dst.)

_bundle = None


def get_bundle():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Model belum tersedia. Jalankan train_model.py terlebih dahulu.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/symptoms")
def get_symptoms():
    return jsonify({"groups": SYMPTOM_GROUPS})


@app.get("/options")
def get_options():
    return jsonify({
        "tensi_category": TENSI_CATEGORIES,
        "duration_category": DURATION_CATEGORIES,
        "age_category": AGE_CATEGORIES,
    })


@app.post("/predict")
def predict():
    body = request.get_json(silent=True) or {}

    symptoms = body.get("symptoms")
    if not symptoms or not isinstance(symptoms, list):
        return jsonify({"error": "Field 'symptoms' wajib diisi (list, minimal 1 gejala)."}), 422

    unknown = [s for s in symptoms if s not in ALL_SYMPTOMS]
    if unknown:
        return jsonify({"error": f"Kode gejala tidak dikenali: {unknown}"}), 422

    bb = body.get("berat_badan_kg")
    tb = body.get("tinggi_badan_cm")
    tensi_raw = body.get("tensi_category")
    duration_raw = body.get("duration_category")
    umur_tahun = body.get("umur_tahun")

    try:
        bundle = get_bundle()
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503

    model = bundle["model"]
    symptom_keys = bundle["symptom_keys"]
    feature_columns = bundle["feature_columns"]

    bmi_cat = bmi_from_bb_tb(bb, tb) or "tidak_tahu"
    tensi_cat = tensi_raw if tensi_raw in TENSI_CATEGORIES else "tidak_tahu"
    duration_cat = duration_raw if duration_raw in DURATION_CATEGORIES else "tidak_tahu"
    age_cat = age_category_from_years(umur_tahun) or "tidak_tahu"

    row = {s: (1 if s in symptoms else 0) for s in symptom_keys}
    row[f"duration_category_{duration_cat}"] = 1
    row[f"bmi_category_{bmi_cat}"] = 1
    row[f"tensi_category_{tensi_cat}"] = 1
    row[f"age_category_{age_cat}"] = 1

    X = pd.DataFrame([row])
    X = X.reindex(columns=feature_columns, fill_value=0)

    proba = model.predict_proba(X)[0]
    classes = model.classes_

    top3_idx = proba.argsort()[::-1][:3]
    predictions = []
    any_urgent_disease = False

    for idx in top3_idx:
        disease_name = classes[idx]
        info = DISEASES[disease_name]
        is_urgent = info["urgent"]
        any_urgent_disease = any_urgent_disease or is_urgent
        predictions.append({
            "disease": disease_name,
            "probability": round(float(proba[idx]), 4),
            "specialist": info["specialist"],
            "category": info["category"],
            "description": info["description"],
            "urgent": is_urgent,
            "contributing_symptoms": get_contributing_symptoms(disease_name, symptoms),
        })

    red_flags_hit = [s for s in symptoms if s in RED_FLAG_SYMPTOMS]
    urgent_warning = bool(red_flags_hit) or any_urgent_disease
    urgent_message = None
    if urgent_warning:
        urgent_message = (
            "Beberapa gejala yang Anda pilih (atau kondisi yang terdeteksi) berpotensi serius. "
            "Sebaiknya segera periksakan diri ke IGD/dokter secepatnya, jangan menunggu."
        )

    return jsonify({
        "input_symptoms": symptoms,
        "bmi_category_used": bmi_cat,
        "tensi_category_used": tensi_cat,
        "duration_category_used": duration_cat,
        "age_category_used": age_cat,
        "top_predictions": predictions,
        "urgent_warning": urgent_warning,
        "urgent_message": urgent_message,
        "disclaimer": DISCLAIMER,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8010, debug=True)
