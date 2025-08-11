# 🏥 Medical Consultation Report Automation

This project integrates **medical data extraction**  with **automatic medical report generation**  into a **single pipeline**.

The system:
1. **Reads raw consultation notes** (in JSON, CSV, or Excel format)
2. **Extracts structured medical information**  
   - Diagnoses (ICD-10 and ICD-11 codes)  
   - Medications  
3. **Generates a complete medical report** in **Text, PDF, Word, and HTML** formats.

---

## 📌 Features
- **Flexible input**: Accepts consultation notes in `.json`, `.csv`, or `.xlsx`
- **Automatic extraction**:
  - Diagnoses with ICD-10 and ICD-11 mappings
  - Medications from the official AMM list
- **Automated report generation** from structured data
- **Multiple output formats**: `.txt`, `.pdf`, `.docx`, `.html`
- **One command execution** for the entire pipeline

---

## 📂 Project Structure

📁 project-root/
│── consultation_notes.json # Example input (raw notes in JSON)
│── consultation_notes.csv # Example input (raw notes in CSV)
│── liste_amm.xls # Medication reference list
│── section111validicd10-jan2025_0.xlsx # ICD-10 codes
│── SimpleTabulation-ICD-11-MMS-fr.xlsx # ICD-11 codes
│── medicaments_extraits.csv # Extracted medications 
│── diagnostics_extraits.csv # Extracted diagnoses 
│── generateur_comptes_rendus.py # Report generator
│── pipeline.py # Full integration script
│── requirements.txt # Python dependencies
│── README.md # This file

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/medical-report-automation.git
cd medical-report-automation
2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
3. Install dependencies
pip install -r requirements.txt
requirements.txt

beautifulsoup4
pandas
openpyxl
python-docx
reportlab
difflib
🚀 Usage
Run the entire pipeline with:

python pipeline.py
Pipeline steps:

Reads the raw consultation notes (.json, .csv, .xlsx)

Extracts medications and diagnoses (Nour's scripts)

Saves the results in:

medicaments_extraits.csv

diagnostics_extraits.csv

Generates a formatted medical report (Text, PDF, Word, HTML)

📄 Example
Input (consultation_notes.json):

{
  "Patient_001": "<p>Patient presenting hypertension and prescribed Paracetamol</p>"
}
Output:

medicaments_extraits.csv

Patient,Medicaments
Patient_001,Paracetamol
diagnostics_extraits.csv

Patient,Mot_extrait,Code_CIM10,Diagnostic_CIM10,Code_CIM11
Patient_001,hypertension,I10,Essential (primary) hypertension,BA00
Generated Report (PDF/Word/HTML):

Medical Consultation Report
----------------------------
Patient: Patient_001

Diagnoses:
- Essential (primary) hypertension (ICD-10: I10, ICD-11: BA00)

Medications:
- Paracetamol
🔄 Workflow Diagram

[Raw Consultation Notes]
       ↓
 [ Extraction]
       ↓
 [medicaments_extraits.csv + diagnostics_extraits.csv]
       ↓
 [Report Generator]
       ↓
 [Text, PDF, Word, HTML Reports]

