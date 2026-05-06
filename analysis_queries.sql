-- ============================================================
--  HealthPulse: Hospital Readmission Risk Analysis
--  SQL Analysis Queries
--  Author: Jahnav Jayanth Reddy Kukkala
-- ============================================================

-- ── Table Setup (SQLite / PostgreSQL compatible) ──────────────
CREATE TABLE IF NOT EXISTS hospital_patients (
    patient_id          TEXT PRIMARY KEY,
    age                 INTEGER,
    gender              TEXT,
    diagnosis           TEXT,
    department          TEXT,
    length_of_stay      INTEGER,
    prev_admissions     INTEGER,
    num_medications     INTEGER,
    comorbidities       INTEGER,
    insurance_type      TEXT,
    discharge_disposition TEXT,
    readmitted_30d      INTEGER,   -- 0 or 1
    admit_date          DATE,
    discharge_date      DATE,
    risk_score          REAL
);

-- ── 1. Overall Readmission Rate ───────────────────────────────
SELECT
    COUNT(*)                                        AS total_patients,
    SUM(readmitted_30d)                             AS readmitted,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct
FROM hospital_patients;


-- ── 2. Readmission Rate by Diagnosis (ranked) ────────────────
SELECT
    diagnosis,
    COUNT(*)                                        AS total,
    SUM(readmitted_30d)                             AS readmitted,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct
FROM hospital_patients
GROUP BY diagnosis
ORDER BY readmission_rate_pct DESC;


-- ── 3. Readmission Rate by Age Group ─────────────────────────
SELECT
    CASE
        WHEN age BETWEEN 18 AND 39 THEN '18–39'
        WHEN age BETWEEN 40 AND 59 THEN '40–59'
        WHEN age BETWEEN 60 AND 74 THEN '60–74'
        ELSE '75+'
    END                                             AS age_group,
    COUNT(*)                                        AS total,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                   AS avg_length_of_stay
FROM hospital_patients
GROUP BY age_group
ORDER BY age_group;


-- ── 4. Insurance Type Impact ──────────────────────────────────
SELECT
    insurance_type,
    COUNT(*)                                        AS total,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct,
    ROUND(AVG(num_medications), 1)                  AS avg_medications,
    ROUND(AVG(comorbidities), 1)                    AS avg_comorbidities
FROM hospital_patients
GROUP BY insurance_type
ORDER BY readmission_rate_pct DESC;


-- ── 5. High-Risk Patients (risk score ≥ 0.4) ─────────────────
SELECT
    patient_id,
    age,
    diagnosis,
    insurance_type,
    prev_admissions,
    comorbidities,
    risk_score,
    readmitted_30d
FROM hospital_patients
WHERE risk_score >= 0.4
ORDER BY risk_score DESC
LIMIT 20;


-- ── 6. Monthly Admissions & Readmissions Trend ───────────────
SELECT
    SUBSTR(admit_date, 1, 7)                        AS month,
    COUNT(*)                                        AS admissions,
    SUM(readmitted_30d)                             AS readmissions,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct
FROM hospital_patients
GROUP BY month
ORDER BY month;


-- ── 7. Discharge Disposition & Readmission ───────────────────
SELECT
    discharge_disposition,
    COUNT(*)                                        AS total,
    SUM(readmitted_30d)                             AS readmitted,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                   AS avg_los
FROM hospital_patients
GROUP BY discharge_disposition
ORDER BY readmission_rate_pct DESC;


-- ── 8. Department-Level Summary ───────────────────────────────
SELECT
    department,
    COUNT(*)                                        AS total_patients,
    ROUND(AVG(age), 1)                              AS avg_age,
    ROUND(AVG(length_of_stay), 1)                   AS avg_los,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct,
    ROUND(AVG(risk_score), 3)                       AS avg_risk_score
FROM hospital_patients
GROUP BY department
ORDER BY avg_risk_score DESC;


-- ── 9. Patients with Multiple Prior Admissions ────────────────
SELECT
    prev_admissions,
    COUNT(*)                                        AS patients,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS readmission_rate_pct
FROM hospital_patients
GROUP BY prev_admissions
ORDER BY prev_admissions;


-- ── 10. Risk Segmentation Summary ────────────────────────────
SELECT
    CASE
        WHEN risk_score < 0.2  THEN 'Low  (<20%)'
        WHEN risk_score < 0.4  THEN 'Medium (20–40%)'
        ELSE                        'High (≥40%)'
    END                                             AS risk_tier,
    COUNT(*)                                        AS patients,
    SUM(readmitted_30d)                             AS actual_readmissions,
    ROUND(AVG(readmitted_30d) * 100, 1)             AS actual_rate_pct
FROM hospital_patients
GROUP BY risk_tier
ORDER BY MIN(risk_score);
