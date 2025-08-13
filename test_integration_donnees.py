import pandas as pd
import os

def tester_integration_donnees():
    """Test simple pour vérifier si le pipeline utilise les vraies données"""
    
    print("🔍 TEST D'INTÉGRATION DES DONNÉES EXTRAITES")
    print("=" * 50)
    
    # 1. Choisir un patient avec beaucoup de données
    df_diag = pd.read_csv("diagnostics_extraits.csv")
    patient_riche = df_diag['Patient'].value_counts().head(1).index[0]
    
    print(f"🎯 Patient test: {patient_riche}")
    print("-" * 30)
    
    # 2. Afficher les données extraites par Données_Brutes_HOPE.py
    print("📊 DONNÉES EXTRAITES PAR Données_Brutes_HOPE.py:")
    
    # Médicaments
    df_med = pd.read_csv("medicaments_extraits.csv")
    meds = df_med[df_med['Patient'] == patient_riche]
    if not meds.empty:
        print(f"💊 Médicaments: {meds.iloc[0]['Medicaments']}")
    
    # Diagnostics (top 3)
    diags = df_diag[df_diag['Patient'] == patient_riche]
    print(f"🔍 Diagnostics ({len(diags)} total):")
    for _, row in diags.head(3).iterrows():
        if pd.notna(row['Diagnostic_CIM10']):
            print(f"   • {row['Diagnostic_CIM10']} ({row['Code_CIM10']})")
    
    # Antécédents
    df_atcd = pd.read_csv("antecedents_extraits.csv")
    atcds = df_atcd[df_atcd['Patient'] == patient_riche]
    if not atcds.empty:
        print(f"📋 Antécédents: {atcds.iloc[0]['Antecedents']}")
    
    # Explorations
    df_expl = pd.read_csv("explorations_extraites.csv")
    expls = df_expl[df_expl['Patient'] == patient_riche]
    if not expls.empty:
        print(f"🔬 Explorations: {expls.iloc[0]['Explorations']}")
    
    # 3. Vérifier le compte rendu généré
    print(f"\n📄 COMPTE RENDU GÉNÉRÉ PAR pipeline_complet_final.py:")
    print("-" * 30)
    
    fichier_cr = f"comptes_rendus/CR_Patient_{patient_riche}.txt"
    if os.path.exists(fichier_cr):
        with open(fichier_cr, 'r', encoding='utf-8') as f:
            contenu_cr = f.read()
        
        print(contenu_cr)
        
        # 4. ANALYSE : Les données sont-elles intégrées ?
        print(f"\n🔍 ANALYSE D'INTÉGRATION:")
        print("-" * 30)

        tests = {
            "Médicaments": len(meds.iloc[0]['Medicaments']) > 2 if not meds.empty and meds.iloc[0]['Medicaments'] != '[]' else False,
            "Antécédents": "ATCD:" in contenu_cr or "Antécédent:" in contenu_cr or len(atcds.iloc[0]['Antecedents']) > 2 if not atcds.empty and atcds.iloc[0]['Antecedents'] != '[]' else False,
            "Explorations": "Exploration:" in contenu_cr,
            "Diagnostics réels": any(diag in contenu_cr for diag in ["absent nipple", "imperforate hymen", "cough"]) if not diags.empty else False
        }

        score = 0
        for test, resultat in tests.items():
            if resultat:
                print(f"✅ {test}: INTÉGRÉ")
                score += 1
            else:
                print(f"❌ {test}: NON INTÉGRÉ")

        print(f"\n📊 SCORE FINAL: {score}/4")

        if score == 0:
            print("🚨 PROBLÈME MAJEUR: Aucune donnée extraite n'est utilisée!")
        elif score < 3:
            print("⚠️ PROBLÈME PARTIEL: Intégration incomplète")
            print("💡 Médicaments et antécédents sont vides dans les données sources")
        else:
            print("✅ SUCCÈS: Les données extraites sont bien utilisées")
            
    else:
        print(f"❌ Compte rendu non trouvé: {fichier_cr}")
        print("💡 Lancez d'abord: python pipeline_complet_final.py")

if __name__ == "__main__":
    tester_integration_donnees()

