"""
HealthPulse: Hospital Readmission Risk Analysis
================================================
Author : Jahnav Jayanth Reddy Kukkala
Project: Data Analyst Portfolio – Daxwell Interview Submission
Dataset: Synthetic hospital patient dataset (1,000 patients)

Objectives:
  1. Generate and explore a realistic hospital dataset
  2. Identify key drivers of 30-day readmission
  3. Build a risk-scoring model using logistic regression
  4. Export clean outputs for SQL analysis and dashboard
"""

import random
import math
import csv
import json
import os
from datetime import datetime, timedelta

random.seed(42)

# ─────────────────────────────────────────────
# 1. SYNTHETIC DATA GENERATION
# ─────────────────────────────────────────────

DIAGNOSES = [
    "Heart Failure", "Pneumonia", "COPD", "Diabetes",
    "Sepsis", "Hip Fracture", "Stroke", "Renal Failure"
]
DEPARTMENTS = ["Cardiology", "Pulmonology", "Endocrinology", "Orthopedics", "Neurology", "Nephrology"]
INSURANCE = ["Medicare", "Medicaid", "Private", "Uninsured"]


def generate_patient(pid):
    age = int(random.gauss(62, 16))
    age = max(18, min(95, age))
    diagnosis = random.choice(DIAGNOSES)
    dept = random.choice(DEPARTMENTS)
    los = max(1, int(random.expovariate(1 / 5)))          # length of stay (days)
    prev_admissions = random.choices([0, 1, 2, 3, 4], weights=[40, 30, 15, 10, 5])[0]
    num_meds = random.randint(1, 15)
    comorbidities = random.randint(0, 5)
    insurance = random.choice(INSURANCE)
    discharge_disposition = random.choices(
        ["Home", "SNF", "Home Health", "AMA"],
        weights=[55, 20, 20, 5]
    )[0]

    # Readmission probability (logistic model)
    log_odds = (
        -3.5
        + 0.03 * age
        + 0.25 * prev_admissions
        + 0.15 * comorbidities
        + 0.08 * num_meds
        - 0.10 * los
        + (0.5 if discharge_disposition == "AMA" else 0)
        + (0.3 if insurance == "Uninsured" else 0)
        + (0.2 if diagnosis in ["Heart Failure", "Sepsis", "COPD"] else 0)
    )
    prob = 1 / (1 + math.exp(-log_odds))
    readmitted = 1 if random.random() < prob else 0

    admit_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
    discharge_date = admit_date + timedelta(days=los)

    return {
        "patient_id": f"P{pid:04d}",
        "age": age,
        "gender": random.choice(["M", "F"]),
        "diagnosis": diagnosis,
        "department": dept,
        "length_of_stay": los,
        "prev_admissions": prev_admissions,
        "num_medications": num_meds,
        "comorbidities": comorbidities,
        "insurance_type": insurance,
        "discharge_disposition": discharge_disposition,
        "readmitted_30d": readmitted,
        "admit_date": admit_date.strftime("%Y-%m-%d"),
        "discharge_date": discharge_date.strftime("%Y-%m-%d"),
        "risk_score": round(prob, 4)
    }


patients = [generate_patient(i) for i in range(1, 1001)]
print(f"✅ Generated {len(patients)} patient records")

# ─────────────────────────────────────────────
# 2. SAVE RAW CSV
# ─────────────────────────────────────────────

csv_path = "data/hospital_patients.csv"
fieldnames = list(patients[0].keys())
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(patients)
print(f"✅ Raw data saved → {csv_path}")

# ─────────────────────────────────────────────
# 3. EXPLORATORY DATA ANALYSIS
# ─────────────────────────────────────────────

total = len(patients)
readmitted = [p for p in patients if p["readmitted_30d"] == 1]
readmission_rate = len(readmitted) / total * 100

# Age bins
def age_group(age):
    if age < 40: return "18-39"
    elif age < 60: return "40-59"
    elif age < 75: return "60-74"
    else: return "75+"

# Readmission by diagnosis
diag_stats = {}
for p in patients:
    d = p["diagnosis"]
    diag_stats.setdefault(d, {"total": 0, "readmitted": 0})
    diag_stats[d]["total"] += 1
    diag_stats[d]["readmitted"] += p["readmitted_30d"]

for d in diag_stats:
    t = diag_stats[d]["total"]
    r = diag_stats[d]["readmitted"]
    diag_stats[d]["rate"] = round(r / t * 100, 1)

# Readmission by age group
age_stats = {}
for p in patients:
    g = age_group(p["age"])
    age_stats.setdefault(g, {"total": 0, "readmitted": 0})
    age_stats[g]["total"] += 1
    age_stats[g]["readmitted"] += p["readmitted_30d"]

for g in age_stats:
    t = age_stats[g]["total"]
    r = age_stats[g]["readmitted"]
    age_stats[g]["rate"] = round(r / t * 100, 1)

# Readmission by insurance
ins_stats = {}
for p in patients:
    i = p["insurance_type"]
    ins_stats.setdefault(i, {"total": 0, "readmitted": 0})
    ins_stats[i]["total"] += 1
    ins_stats[i]["readmitted"] += p["readmitted_30d"]

for i in ins_stats:
    t = ins_stats[i]["total"]
    r = ins_stats[i]["readmitted"]
    ins_stats[i]["rate"] = round(r / t * 100, 1)

# Readmission by discharge disposition
disch_stats = {}
for p in patients:
    d = p["discharge_disposition"]
    disch_stats.setdefault(d, {"total": 0, "readmitted": 0})
    disch_stats[d]["total"] += 1
    disch_stats[d]["readmitted"] += p["readmitted_30d"]

for d in disch_stats:
    t = disch_stats[d]["total"]
    r = disch_stats[d]["readmitted"]
    disch_stats[d]["rate"] = round(r / t * 100, 1)

# Average LOS
avg_los_readmitted = sum(p["length_of_stay"] for p in readmitted) / len(readmitted)
avg_los_not = sum(p["length_of_stay"] for p in patients if p["readmitted_30d"] == 0) / (total - len(readmitted))

# Monthly trend
monthly = {}
for p in patients:
    m = p["admit_date"][:7]
    monthly.setdefault(m, {"total": 0, "readmitted": 0})
    monthly[m]["total"] += 1
    monthly[m]["readmitted"] += p["readmitted_30d"]

monthly_sorted = sorted(monthly.items())

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HEALTHPULSE — EDA SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Total Patients     : {total}
 30-day Readmissions: {len(readmitted)} ({readmission_rate:.1f}%)
 Avg LOS Readmitted : {avg_los_readmitted:.1f} days
 Avg LOS Not Readmit: {avg_los_not:.1f} days

 Readmission by Diagnosis:""")
for d, s in sorted(diag_stats.items(), key=lambda x: -x[1]["rate"]):
    print(f"   {d:<20} {s['rate']:>5.1f}%  ({s['readmitted']}/{s['total']})")

print("\n Readmission by Age Group:")
for g in ["18-39", "40-59", "60-74", "75+"]:
    s = age_stats.get(g, {})
    print(f"   {g:<10} {s.get('rate', 0):>5.1f}%")

print("\n Readmission by Insurance:")
for i, s in sorted(ins_stats.items(), key=lambda x: -x[1]["rate"]):
    print(f"   {i:<15} {s['rate']:>5.1f}%")

# ─────────────────────────────────────────────
# 4. SIMPLE LOGISTIC REGRESSION (from scratch)
# ─────────────────────────────────────────────

def normalize(data, mean, std):
    return (data - mean) / std if std > 0 else 0

features_raw = [(p["age"], p["prev_admissions"], p["comorbidities"],
                 p["num_medications"], p["length_of_stay"]) for p in patients]
labels = [p["readmitted_30d"] for p in patients]

# Compute means/stds
n_feat = 5
means = [sum(f[i] for f in features_raw) / total for i in range(n_feat)]
stds = [math.sqrt(sum((f[i] - means[i])**2 for f in features_raw) / total) for i in range(n_feat)]

features = [[normalize(f[i], means[i], stds[i]) for i in range(n_feat)] for f in features_raw]

# Train logistic regression (gradient descent)
weights = [0.0] * n_feat
bias = 0.0
lr = 0.05

for epoch in range(200):
    dw = [0.0] * n_feat
    db = 0.0
    for x, y in zip(features, labels):
        z = sum(w * xi for w, xi in zip(weights, x)) + bias
        pred = 1 / (1 + math.exp(-max(-500, min(500, z))))
        err = pred - y
        for j in range(n_feat):
            dw[j] += err * x[j]
        db += err
    weights = [w - lr * d / total for w, d in zip(weights, dw)]
    bias -= lr * db / total

# Evaluate
correct = 0
tp = fp = tn = fn = 0
for x, y in zip(features, labels):
    z = sum(w * xi for w, xi in zip(weights, x)) + bias
    pred = 1 if 1 / (1 + math.exp(-z)) >= 0.5 else 0
    if pred == y:
        correct += 1
    if pred == 1 and y == 1: tp += 1
    elif pred == 1 and y == 0: fp += 1
    elif pred == 0 and y == 0: tn += 1
    else: fn += 1

accuracy = correct / total * 100
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

feat_names = ["Age", "Prev Admissions", "Comorbidities", "Num Medications", "Length of Stay"]
print(f"""
 LOGISTIC REGRESSION MODEL
 Accuracy  : {accuracy:.1f}%
 Precision : {precision:.3f}
 Recall    : {recall:.3f}
 F1 Score  : {f1:.3f}

 Feature Importances (weights):""")
for name, w in sorted(zip(feat_names, weights), key=lambda x: -abs(x[1])):
    bar = "█" * int(abs(w) * 10)
    sign = "+" if w > 0 else "-"
    print(f"   {name:<22} {sign}{abs(w):.3f}  {bar}")

# ─────────────────────────────────────────────
# 5. EXPORT JSON FOR DASHBOARD
# ─────────────────────────────────────────────

dashboard_data = {
    "summary": {
        "total_patients": total,
        "total_readmitted": len(readmitted),
        "readmission_rate": round(readmission_rate, 1),
        "avg_los_readmitted": round(avg_los_readmitted, 1),
        "avg_los_not_readmitted": round(avg_los_not, 1)
    },
    "model": {
        "accuracy": round(accuracy, 1),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "feature_weights": {name: round(w, 3) for name, w in zip(feat_names, weights)}
    },
    "by_diagnosis": {k: v for k, v in sorted(diag_stats.items(), key=lambda x: -x[1]["rate"])},
    "by_age_group": {g: age_stats.get(g, {}) for g in ["18-39", "40-59", "60-74", "75+"]},
    "by_insurance": ins_stats,
    "by_discharge": disch_stats,
    "monthly_trend": [
        {"month": m, "total": s["total"], "readmitted": s["readmitted"],
         "rate": round(s["readmitted"] / s["total"] * 100, 1)}
        for m, s in monthly_sorted
    ],
    "risk_distribution": {
        "low": len([p for p in patients if p["risk_score"] < 0.2]),
        "medium": len([p for p in patients if 0.2 <= p["risk_score"] < 0.4]),
        "high": len([p for p in patients if p["risk_score"] >= 0.4])
    }
}

with open("outputs/dashboard_data.json", "w") as f:
    json.dump(dashboard_data, f, indent=2)

print(f"\n✅ Dashboard data exported → outputs/dashboard_data.json")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
