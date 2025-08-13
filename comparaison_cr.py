import os
import pandas as pd
import random

def comparer_comptes_rendus():
    """Comparer un compte rendu avec les données extraites"""
    
    # Choisir un patient au hasard - SEULEMENT les fichiers .txt
    fichiers = [f for f in os.listdir("comptes_rendus") if f.startswith("CR_Patient_") and f.endswith(".txt")]
    if not fichiers:
        print("❌ Aucun compte rendu .txt trouvé")
        return
    
    fichier = random.choice(fichiers)
    patient_id = fichier.replace("CR_Patient_", "").replace(".txt", "")
    
    print(f"🔍 ANALYSE DÉTAILLÉE - PATIENT {patient_id}")
    print("=" * 50)
    
    # Lire le compte rendu
    try:
        with open(f"comptes_rendus/{fichier}", 'r', encoding='utf-8') as f:
            cr_contenu = f.read()
    except UnicodeDecodeError:
        # Essayer avec un autre encodage
        with open(f"comptes_rendus/{fichier}", 'r', encoding='latin-1') as f:
            cr_contenu = f.read()
    
    print("📄 COMPTE RENDU GÉNÉRÉ:")
    print("-" * 30)
    print(cr_contenu[:500] + "..." if len(cr_contenu) > 500 else cr_contenu)
    
    print("\n📊 DONNÉES EXTRAITES CORRESPONDANTES:")
    print("-" * 30)
    
    # Afficher les données extraites pour ce patient
    try:
        # Médicaments
        df_med = pd.read_csv("medicaments_extraits.csv")
        meds = df_med[df_med['Patient'] == int(patient_id)]
        if not meds.empty:
            print(f"💊 Médicaments: {meds.iloc[0]['Medicaments']}")
        else:
            print("💊 Médicaments: Aucun trouvé")
        
        # Diagnostics
        df_diag = pd.read_csv("diagnostics_extraits.csv")
        diags = df_diag[df_diag['Patient'] == int(patient_id)]
        if not diags.empty:
            print(f"🔍 Diagnostics: {len(diags)} trouvés")
            for _, row in diags.head(3).iterrows():
                if pd.notna(row['Diagnostic_CIM10']):
                    print(f"   • {row['Diagnostic_CIM10']} ({row['Code_CIM10']})")
        else:
            print("🔍 Diagnostics: Aucun trouvé")
        
        # Antécédents
        df_atcd = pd.read_csv("antecedents_extraits.csv")
        atcds = df_atcd[df_atcd['Patient'] == int(patient_id)]
        if not atcds.empty:
            print(f"📋 Antécédents: {atcds.iloc[0]['Antecedents']}")
        else:
            print("📋 Antécédents: Aucun trouvé")
        
        # Explorations
        df_expl = pd.read_csv("explorations_extraites.csv")
        expls = df_expl[df_expl['Patient'] == int(patient_id)]
        if not expls.empty:
            print(f"🔬 Explorations: {expls.iloc[0]['Explorations']}")
        else:
            print("🔬 Explorations: Aucune trouvée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    comparer_comptes_rendus()

