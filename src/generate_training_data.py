# -*- coding: utf-8 -*-
"""
generate_training_data.py — membuat data latih sintetis dari knowledge_base.py.

Untuk tiap penyakit, kita "mensimulasikan" banyak pasien: tiap gejala inti
penyakit itu punya peluang muncul sesuai bobotnya. Ditambah tiga fitur baru:
kategori BMI, kategori tensi, dan kategori durasi sakit — masing-masing
disimulasikan berdasarkan bias penyakit itu (kalau ada), DITAMBAH suntikan
"tidak_tahu" secara acak & MERATA ke semua penyakit (independen dari
penyakitnya), supaya model belajar bahwa "tidak tahu/tidak mau jawab" itu
netral, bukan sinyal negatif untuk kondisi manapun.
"""

import csv
import random
from pathlib import Path

from knowledge_base import (
    DISEASES, ALL_SYMPTOMS, DISEASE_LIST,
    DURATION_ARCHETYPES, BMI_BIAS_HIGH, BMI_BIAS_NEUTRAL,
    TENSI_BIAS_HIGH, TENSI_BIAS_NEUTRAL,
    AGE_BIAS_OLD, AGE_BIAS_YOUNG, AGE_BIAS_NEUTRAL,
)

SEED = 42
random.seed(SEED)

SAMPLES_PER_DISEASE = 120
NOISE_PROBABILITY = 0.03
UNKNOWN_PROBABILITY = 0.15  # peluang "tidak_tahu" muncul, SAMA untuk semua penyakit

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

symptom_keys = list(ALL_SYMPTOMS.keys())


def weighted_choice(prob_dict):
    keys = list(prob_dict.keys())
    weights = list(prob_dict.values())
    return random.choices(keys, weights=weights, k=1)[0]


def simulate_patient(disease_name):
    info = DISEASES[disease_name]
    profile = info["symptoms"]
    row = {s: 0 for s in symptom_keys}

    for symptom, weight in profile.items():
        if random.random() < weight:
            row[symptom] = 1

    for s in symptom_keys:
        if s not in profile and random.random() < NOISE_PROBABILITY:
            row[s] = 1

    if sum(row.values()) == 0:
        dominant = max(profile, key=profile.get)
        row[dominant] = 1

    # --- durasi sakit ---
    if random.random() < UNKNOWN_PROBABILITY:
        row["duration_category"] = "tidak_tahu"
    else:
        row["duration_category"] = weighted_choice(DURATION_ARCHETYPES[info["duration_typical"]])

    # --- kategori BMI ---
    if random.random() < UNKNOWN_PROBABILITY:
        row["bmi_category"] = "tidak_tahu"
    else:
        dist = BMI_BIAS_HIGH if info["bmi_bias"] == "tinggi" else BMI_BIAS_NEUTRAL
        row["bmi_category"] = weighted_choice(dist)

    # --- kategori tensi ---
    if random.random() < UNKNOWN_PROBABILITY:
        row["tensi_category"] = "tidak_tahu"
    else:
        dist = TENSI_BIAS_HIGH if info["tensi_bias"] == "tinggi" else TENSI_BIAS_NEUTRAL
        row["tensi_category"] = weighted_choice(dist)

    # --- kategori umur ---
    if random.random() < UNKNOWN_PROBABILITY:
        row["age_category"] = "tidak_tahu"
    else:
        age_bias = info.get("age_bias")
        if age_bias == "tua":
            dist = AGE_BIAS_OLD
        elif age_bias == "muda":
            dist = AGE_BIAS_YOUNG
        else:
            dist = AGE_BIAS_NEUTRAL
        row["age_category"] = weighted_choice(dist)

    row["disease"] = disease_name
    return row


def main():
    rows = []
    for disease in DISEASE_LIST:
        for _ in range(SAMPLES_PER_DISEASE):
            rows.append(simulate_patient(disease))

    random.shuffle(rows)

    out_path = DATA_DIR / "symptom_training_data.csv"
    fieldnames = symptom_keys + ["duration_category", "bmi_category", "tensi_category", "age_category", "disease"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total baris data latih: {len(rows)}")
    print(f"Jumlah penyakit       : {len(DISEASE_LIST)}")
    print(f"Jumlah gejala (fitur) : {len(symptom_keys)}")
    print(f"Fitur tambahan        : duration_category, bmi_category, tensi_category")
    print(f"Tersimpan di          : {out_path}")


if __name__ == "__main__":
    main()
