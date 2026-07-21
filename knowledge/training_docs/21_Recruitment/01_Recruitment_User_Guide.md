# Recruitment — User Guide

**Module:** job_spec  
**Applies to:** Odoo 18  
**Role:** HR User / Recruitment Officer / Hiring Manager  

---

## 1. Overview

The Recruitment module (`job_spec`) manages the full hiring lifecycle: **job positions**, **application intake**, **resume parsing**, **interview stage tracking**, and **candidate validation** (including South African ID number checks). It extends Odoo's base Recruitment app with specialised features for the South African market.

---

## 2. Prerequisites

- *Recruitment* app installed.
- HR department structure configured.
- (Optional) Email alias set per job position for auto-creation of applications.
- SA ID validation requires a registered DHA or third-party validation service (configured in Settings → Recruitment → ID Validation).

---

## 3. Key Concepts

| Term | Definition |
|---|---|
| **Job Position** | A formal role with a description, requirements, and hiring team. |
| **Application** | A candidate's submission for a specific job. |
| **Resume Import** | Parsing of CV/PDF/Docx files into structured candidate data. |
| **Interview Stage** | A step in the hiring pipeline (e.g. Screening, Phone Interview, Face-to-Face, Offer). |
| **SA ID Validation** | Checks the 13-digit ID number against the Luhn algorithm and date-of-birth logic. |
| **Stage Funnel** | Visual pipeline showing how many candidates are at each stage. |

---

## 4. Step-by-Step Instructions

### 4.1 Create a Job Position

1. Go to **Recruitment → Jobs → Job Positions**.
2. Click **New**.
3. Enter:

   | Field | Description |
   |---|---|
   | **Job Title** | e.g. *Senior Software Developer* |
   | **Department** | Select the department |
   | **Recruitment Responsible** | HR user who owns the position |
   | **Target** | Number of hires needed |
   | **Description** | Rich text job ad (published on portal) |
   | **Requirements** | Skills, education, experience |
   | **Email Alias** | e.g. `jobs-dev@company.com` — emails to this address become applications |

4. Configure **Interview Stages** under the *Stages* tab:
   - *New Application* → *Screening* → *Phone Interview* → *Technical Test* → *Panel Interview* → *Offer*.
   - Drag to reorder.
5. Click **Save**.

### 4.2 Manage Applications

**Method A — Manual entry:**

1. Open the job position.
2. Click **Applications** smart button → **New**.
3. Fill in:
   - **Candidate Name**
   - **Email** and **Phone**
   - **LinkedIn / Portfolio URL**
   - **Attach Resume** (PDF or Docx)
4. Click **Save**.

**Method B — Auto-creation from email:**

- Send an email with CV attachment to the job's email alias. Odoo creates a new application automatically.

**Method C — Resume import:**

1. From an open application, scroll to the *Resume* section.
2. Click **Import Resume** and select the file.
3. The system parses:
   - Work experience (company, role, dates)
   - Education (institution, degree, year)
   - Skills
4. Review the parsed data and correct any mismatches.
5. Click **Confirm Import**.

### 4.3 Move a Candidate Through Interview Stages

1. Open the application.
2. In the **Stages** kanban (or form view), change the stage by clicking **Next Stage** or dragging the card.
3. At each stage you can:
   - Schedule an **Interview Meeting** (calendar event is created automatically).
   - Log **Internal Notes** with interviewer feedback.
   - Attach test results, assessment scores, or scored rubrics.

### 4.4 Validate a South African ID Number

1. Open the candidate record (or application).
2. Locate the **SA ID Number** field on the *Personal Details* tab.
3. Enter the 13-digit ID number.
4. Click **Validate ID** (or the field auto-validates on save).
5. The system checks:
   - **Length** — must be exactly 13 digits.
   - **Date of Birth** — digits 0–5 encode YYMMDD; must be a real date.
   - **Gender** — digit 6: 0–4 = Female, 5–9 = Male.
   - **Citizenship** — digit 10: 0 = SA citizen, 1 = permanent resident.
   - **Luhn Checksum** — the 13th digit must be a valid checksum.
6. A green checkmark (✓) means the ID is valid; a red cross (✗) means it failed one or more checks.

### 4.5 Hire and Close

1. When the candidate accepts the offer, click **Hire** on the application.
2. Odoo automatically:
   - Marks the application as *Hired*.
   - Creates an Employee record.
   - Sends an automated welcome email.
3. The job position's *Hired* count increments; if it reaches the *Target*, the position is marked as *Fulfilled*.

---

## 5. Common Tasks

| Task | Steps |
|---|---|
| **Publish a job on the portal** | Job Position → *Website* tab → check *Publish on Website* |
| **Reject a candidate** | Application → click **Refuse** → enter reason |
| **Bulk-advance candidates** | Kanban view → select multiple → Action → Change Stage |
| **Generate an interview scorecard** | Settings → Recruitment → enable *Scorecards* → then open Interview → Scorecard tab |
| **Export application data** | Applications → select → Action → Export → choose fields |
| **Re-open a fulfilled position** | Job Position → toggle *Fulfilled* → clear target or increase it |

---

## 6. Tips & Best Practices

- **Email aliases**: Set a unique alias per position (e.g. `jobs-qa@company.com`, `jobs-dev@company.com`) to auto-categorise incoming applications.
- **Interview stages**: Keep stages to 4–6 maximum. Too many stages slow down the pipeline.
- **Resume parsing**: Best results come from single-column PDF CVs. Multi-column or heavily formatted documents may need manual correction.
- **SA ID validation**: Enable the ID check on the candidate form as a mandatory field in Settings → Recruitment → *Require SA ID Validation*. This prevents non-compliant hires.
- **Duplicate detection**: When importing a resume, Odoo checks for existing candidates with the same email or phone. Always merge duplicates before progressing.
- **Automated actions**: Use Automated Actions (Settings → Technical → Automated Actions) to send follow-up emails after a candidate stays in a stage for 7+ days.

---

## 7. Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Resume import shows no data | File format unsupported or corrupted | Convert to plain PDF or Docx; max file size 25 MB |
| SA ID validation fails | Typo in ID number or invalid checksum | Re-enter the ID; verify against the candidate's ID document |
| Application not created from email | Email alias not configured or mail server down | Check Job Position → Email Alias; test mail server in Settings → General Settings → Incoming Mail Servers |
| Candidate not appearing on kanban | Stage filter is active | Clear stage filter or set to *All Stages* |
| "Hire" button is greyed out | Applicant status is *Refused* or *Hired* | Only *In Progress* applications can be hired |

---

*End of Recruitment User Guide*
