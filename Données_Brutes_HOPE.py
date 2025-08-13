import json
import pandas as pd
import difflib
import re
from bs4 import BeautifulSoup

print("🏥 EXTRACTION DE DONNÉES MÉDICALES")
print("=" * 50)

# 1. CHARGEMENT ET NETTOYAGE DES DONNÉES
print("\n📂 Chargement des données...")
with open("donnees_nettoyees_finales.json", "r", encoding="utf-8") as file:
    data = json.load(file)

notes_text = {}
for key, content in data.items():
    if isinstance(content, list):
        # Si c'est une liste, joindre tous les éléments
        text = " ".join(str(item) for item in content if item)
        notes_text[key] = text
    elif isinstance(content, str) and content.strip():
        # Si c'est du HTML, parser avec BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        notes_text[key] = text
    else:
        # Convertir en string si autre type
        notes_text[key] = str(content) if content else ""

print(f"✅ {len(notes_text)} patients chargés")

# 2. EXTRACTION DES MÉDICAMENTS
print("\n💊 Extraction des médicaments...")
try:
    meds = pd.read_excel("liste_amm.xls")
    liste_medicaments = meds['Nom'].str.lower().tolist()
    print(f"✅ {len(liste_medicaments)} médicaments de référence chargés")
except FileNotFoundError:
    print("⚠️ Fichier liste_amm.xls non trouvé - extraction basique")
    liste_medicaments = []

def extraire_medicaments(note):
    """Extraction améliorée des médicaments"""
    medicaments_trouves = []
    
    # Patterns plus larges pour médicaments
    patterns_med = [
        r'(\w+(?:ine|ol|ide|ate|um|ex))\s*(\d+(?:mg|g|ml|cp)?)',  # Médicaments avec dosage
        r'(\w+)\s+(\d+(?:mg|g|ml|cp))',  # Nom + dosage
        r'([A-Z][a-z]+(?:ine|ol|ide|ate|um|ex))',  # Noms typiques
        r'(emadine|aldactone|metformine|amlodipine|cytolim|vaseline|folicum|methotrexate|glucalcium|estrado|hypolactine|noractone|indocine|levostamine|ketozol|celiprol)',  # Médicaments connus
        r'(\w+)\s*:\s*(\d+[-]\d+[-]\d+)',  # Format dose: 2-1-2
        r'(\w+\d+)',  # Médicaments avec chiffres (Taver200, LEVET500)
    ]
    
    for pattern in patterns_med:
        matches = re.findall(pattern, note, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                med_name = match[0].lower()
            else:
                med_name = match.lower()
            
            # Filtrer les mots trop courts ou communs
            if len(med_name) > 3 and med_name not in ['pour', 'dans', 'avec', 'sans', 'bien', 'très']:
                medicaments_trouves.append(med_name)
    
    return list(set(medicaments_trouves))

# Extraction des médicaments
medicaments_resultats = {}
for patient, note in notes_text.items():
    medicaments_resultats[patient] = extraire_medicaments(note)

# Sauvegarde médicaments
df_medicaments = pd.DataFrame(list(medicaments_resultats.items()), columns=['Patient', 'Medicaments'])
df_medicaments.to_csv("medicaments_extraits.csv", index=False, encoding="utf-8")
print(f"✅ Médicaments extraits et sauvegardés dans medicaments_extraits.csv")

# 3. EXTRACTION DES DIAGNOSTICS
print("\n🔍 Extraction des diagnostics...")
try:
    df_cim10 = pd.read_excel("section111validicd10-jan2025_0.xlsx")
    codes_cim10 = df_cim10['CODE'].astype(str).tolist()
    desc_cim10 = df_cim10['LONG DESCRIPTION (VALID ICD-10 FY2025)'].astype(str).str.lower().tolist()
    print(f"✅ {len(codes_cim10)} codes CIM-10 chargés")
except FileNotFoundError:
    print("⚠️ Fichier CIM-10 non trouvé - extraction basique")
    codes_cim10, desc_cim10 = [], []

try:
    df_cim11 = pd.read_excel("SimpleTabulation-ICD-11-MMS-fr.xlsx")
    
    # Détection automatique des colonnes
    if 'CODE' in df_cim11.columns:
        codes_cim11 = df_cim11['CODE'].astype(str).tolist()
    elif 'Code' in df_cim11.columns:
        codes_cim11 = df_cim11['Code'].astype(str).tolist()
    else:
        codes_cim11 = df_cim11.iloc[:, 0].astype(str).tolist()

    if 'title' in df_cim11.columns:
        titles_cim11 = df_cim11['title'].astype(str).str.lower().tolist()
    elif 'Title' in df_cim11.columns:
        titles_cim11 = df_cim11['Title'].astype(str).str.lower().tolist()
    else:
        titles_cim11 = df_cim11.iloc[:, 1].astype(str).str.lower().tolist()

    dico_cim11 = dict(zip(codes_cim11, titles_cim11))
    print(f"✅ {len(codes_cim11)} codes CIM-11 chargés")
except FileNotFoundError:
    print("⚠️ Fichier CIM-11 non trouvé - extraction basique")
    dico_cim11 = {}

def extraire_diagnostics_ameliore(note):
    """Extraction améliorée des diagnostics"""
    diagnostics = []
    
    # Patterns pour diagnostics médicaux
    patterns_diag = [
        r'(?:diagnostic|pathologie|maladie)\s*:?\s*([^.]+)',
        r'(?:souffre de|atteint de|présente)\s+([^,]+)',
        r'(?:hypertension|diabète|asthme|dépression|anxiété|acné|alopécie)',
        r'(?:trouble|syndrome|infection|inflammation)\s+([^,]+)'
    ]
    
    
    for pattern in patterns_diag:
        matches = re.findall(pattern, note, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str) and len(match.strip()) > 3:
                diagnostics.append(match.strip().lower())
    
    return list(set(diagnostics))

# Extraction des diagnostics avec CIM
resultats_diagnostics = {}
for patient, note in notes_text.items():
    diagnostics_trouves = []
    
    if desc_cim10:  # Si CIM-10 disponible
        mots = note.lower().split()
        for mot in mots:
            match_desc = difflib.get_close_matches(mot, desc_cim10, n=1, cutoff=0.6)
            if match_desc:
                idx = desc_cim10.index(match_desc[0])
                code10 = codes_cim10[idx]
                titre_cim11 = dico_cim11.get(code10, "")
                
                diagnostics_trouves.append({
                    "mot_extrait": mot,
                    "diagnostic_cim10": match_desc[0],
                    "code_cim10": code10,
                    "code_cim11": titre_cim11
                })
    else:  # Extraction basique sans CIM
        diags_basiques = extraire_diagnostics_ameliore(note)
        for diag in diags_basiques:
            diagnostics_trouves.append({
                "mot_extrait": diag,
                "diagnostic_cim10": diag,
                "code_cim10": "N/A",
                "code_cim11": "N/A"
            })
    
    # Suppression des doublons
    diagnostics_trouves = [dict(t) for t in {tuple(d.items()) for d in diagnostics_trouves}]
    resultats_diagnostics[patient] = diagnostics_trouves

# Sauvegarde diagnostics
diagnostics_data = []
for patient, diags in resultats_diagnostics.items():
    for d in diags:
        diagnostics_data.append({
            'Patient': patient,
            'Mot_extrait': d['mot_extrait'],
            'Code_CIM10': d['code_cim10'],
            'Diagnostic_CIM10': d['diagnostic_cim10'],
            'Code_CIM11': d['code_cim11']
        })

df_diagnostics = pd.DataFrame(diagnostics_data)
df_diagnostics.to_csv("diagnostics_extraits.csv", index=False, encoding="utf-8")
print(f"✅ Diagnostics extraits et sauvegardés dans diagnostics_extraits.csv")

# 4. EXTRACTION DES ANTÉCÉDENTS
print("\n📋 Extraction des antécédents...")
def extraire_antecedents(note):
    """Extraction améliorée des antécédents"""
    antecedents = []
    
    patterns_atcd = [
        r'(?:atcd|antécédent|historique)\s*:?\s*([^.]+)',
        r'(?:patient|malade)\s+(?:a|avec|souffre de)\s+([^,\.]+)',
        r'(?:depuis|il y a)\s+(\d+\s+(?:ans|mois|années))',
        r'(?:diabète|hypertension|asthme|épilepsie|allergie)\s*[^,\.]*',
        r'(?:pas d\'atcd|ras|pas de traitement)',  # Même les "ras" sont informatifs
        r'(?:bien équilibré|dernière intervention)',
        r'(?:allergies?\s+médicamenteuses?)\s*:?\s*([^,\.]+)',
    ]
    
    for pattern in patterns_atcd:
        matches = re.findall(pattern, note, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str) and len(match.strip()) > 2:
                antecedents.append(match.strip())
    
    # Ajouter des lignes complètes qui contiennent des mots-clés
    lignes = note.split('\n')
    for ligne in lignes:
        if any(mot in ligne.lower() for mot in ['atcd', 'antécédent', 'allergie', 'traitement', 'épilepsie', 'diabète']):
            if len(ligne.strip()) > 10:
                antecedents.append(ligne.strip())
    
    return list(set(antecedents))

antecedents_resultats = {}
for patient, note in notes_text.items():
    antecedents_resultats[patient] = extraire_antecedents(note)

# Sauvegarde antécédents
df_antecedents = pd.DataFrame(list(antecedents_resultats.items()), columns=['Patient', 'Antecedents'])
df_antecedents.to_csv("antecedents_extraits.csv", index=False, encoding="utf-8")
print(f"✅ Antécédents extraits et sauvegardés dans antecedents_extraits.csv")

# 5. EXTRACTION DES EXPLORATIONS
print("\n🔬 Extraction des explorations...")
def extraire_explorations(note):
    """Extraction des explorations médicales"""
    explorations = []
    
    patterns_expl = [
        r'(?:examen|test|bilan|échographie|scanner|irm|ecg)\s*:?\s*([^.]+)',
        r'(?:réalisé|effectué|prescrit)\s+([^,]+)',
        r'(?:biologie|radiologie|cardiologie)',
        r'(?:prise de sang|analyse|contrôle)',
    ]
    
    for pattern in patterns_expl:
        matches = re.findall(pattern, note, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str) and len(match.strip()) > 3:
                explorations.append(match.strip())
    
    return list(set(explorations))

explorations_resultats = {}
for patient, note in notes_text.items():
    explorations_resultats[patient] = extraire_explorations(note)

# Sauvegarde explorations
df_explorations = pd.DataFrame(list(explorations_resultats.items()), columns=['Patient', 'Explorations'])
df_explorations.to_csv("explorations_extraites.csv", index=False, encoding="utf-8")
print(f"✅ Explorations extraites et sauvegardées dans explorations_extraites.csv")

# 6. RAPPORT FINAL
print("\n📊 RAPPORT D'EXTRACTION")
print("=" * 50)
print(f"👥 Patients traités: {len(notes_text)}")
print(f"💊 Médicaments extraits: {sum(len(meds) for meds in medicaments_resultats.values())}")
print(f"🔍 Diagnostics extraits: {len(diagnostics_data)}")
print(f"📋 Antécédents extraits: {sum(len(atcd) for atcd in antecedents_resultats.values())}")
print(f"🔬 Explorations extraites: {sum(len(expl) for expl in explorations_resultats.values())}")

print("\n📁 Fichiers générés:")
print("• medicaments_extraits.csv")
print("• diagnostics_extraits.csv") 
print("• antecedents_extraits.csv")
print("• explorations_extraites.csv")

print("\n✅ Extraction terminée avec succès!")
