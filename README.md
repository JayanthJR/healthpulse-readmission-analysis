# 🫀 HealthPulse — Hospital Readmission Risk Analysis

**Author:** Jahnav Jayanth Reddy Kukkala  
**Stack:** Python · SQL · HTML/JS Dashboard

---

## 📌 Project Overview

HealthPulse is an end-to-end data analysis project that identifies key drivers of **30-day hospital readmissions** using a synthetic dataset of 1,000 patients. The project covers the full data analyst workflow:

- Data generation & cleaning
- Exploratory Data Analysis (EDA)
- SQL querying for business insights
- Logistic Regression risk model (built from scratch, no ML libraries)
- Interactive HTML dashboard

---

## 🗂 Project Structure

```
healthpulse/
├── analysis.py                  # Main Python script (EDA + model + export)
├── dashboard.html               # Interactive HTML/JS dashboard
├── data/
│   └── hospital_patients.csv   # Generated patient dataset (1,000 rows)
├── sql/
│   └── analysis_queries.sql    # 10 SQL queries covering key business questions
└── outputs/
    └── dashboard_data.json     # JSON export for dashboard
```

---

## 🔍 Key Findings

| Finding | Value |
|---|---|
| Overall 30-day readmission rate | **37.7%** |
| Highest-risk diagnosis | **Hip Fracture (49.6%)** |
| Age group with highest readmission | **75+ (54.1%)** |
| Uninsured vs. Private insurance gap | **44.6% vs 33.7%** |
| AMA discharge readmission rate | **44.2%** |
| Top predictive feature | **Age (weight: +0.429)** |

---

## 🤖 Model Results

A logistic regression model was trained **from scratch** (no scikit-learn) using gradient descent.

| Metric | Value |
|---|---|
| Accuracy | 70.2% |
| Precision | 0.638 |
| Recall | 0.485 |
| F1 Score | 0.551 |

**Feature importances (by absolute weight):**
1. Age (+0.429)
2. Number of Medications (+0.383)
3. Length of Stay (−0.367)
4. Prior Admissions (+0.343)
5. Comorbidities (+0.222)

---

## 🗄 SQL Analysis

The `sql/analysis_queries.sql` file contains 10 structured queries:

1. Overall readmission rate
2. Rate by diagnosis (ranked)
3. Rate by age group
4. Insurance type impact
5. High-risk patient list (score ≥ 40%)
6. Monthly trend
7. Discharge disposition analysis
8. Department-level summary
9. Prior admissions correlation
10. Risk tier segmentation

---

## ▶️ How to Run

```bash
# Clone and run
git clone https://github.com/YOUR_USERNAME/healthpulse
cd healthpulse
python analysis.py

# Open the dashboard
open dashboard.html
```

**Requirements:** Python 3.8+ · No external libraries needed (pure stdlib)

---

## 💡 Business Recommendations

1. **Target Hip Fracture & Diabetes patients** for enhanced discharge planning
2. **Deploy risk scoring at discharge** to flag high-risk patients (score ≥ 0.4)
3. **Reduce AMA discharges** through better patient communication protocols
4. **Address insurance access gaps** — uninsured patients need post-discharge follow-up programs
5. **Increase December staffing** — holiday period shows consistent readmission spikes

---

*Dataset is synthetic and generated for portfolio/demonstration purposes.*

