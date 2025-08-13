import pandas as pd

def debug_pipeline():
    """Débugger pourquoi les données ne sont pas intégrées"""
    
    print("🔍 DEBUG PIPELINE - INTÉGRATION DES DONNÉES")
    print("=" * 50)
    
    # Vérifier les données pour le patient 938
    patient_id = 938
    
    print(f"📊 DONNÉES DISPONIBLES POUR PATIENT {patient_id}:")
    print("-" * 40)
    
    # Médicaments
    df_med = pd.read_csv("medicaments_extraits.csv")
    meds = df_med[df_med['Patient'] == patient_id]
    print(f"💊 Médicaments: {meds.iloc[0]['Medicaments'] if not meds.empty else 'Aucun'}")
    
    # Diagnostics
    df_diag = pd.read_csv("diagnostics_extraits.csv")
    diags = df_diag[df_diag['Patient'] == patient_id]
    print(f"🔍 Diagnostics: {len(diags)} trouvés")
    if not diags.empty:
        for i, (_, row) in enumerate(diags.head(3).iterrows()):
            if pd.notna(row['Diagnostic_CIM10']):
                print(f"   {i+1}. {row['Diagnostic_CIM10']} ({row['Code_CIM10']})")
    
    # Antécédents
    df_atcd = pd.read_csv("antecedents_extraits.csv")
    atcds = df_atcd[df_atcd['Patient'] == patient_id]
    print(f"📋 Antécédents: {atcds.iloc[0]['Antecedents'] if not atcds.empty else 'Aucun'}")
    
    # Explorations
    df_expl = pd.read_csv("explorations_extraites.csv")
    expls = df_expl[df_expl['Patient'] == patient_id]
    print(f"🔬 Explorations: {expls.iloc[0]['Explorations'] if not expls.empty else 'Aucune'}")
    
    print("\n" + "=" * 50)
    print("🚨 PROBLÈME : Les données sont disponibles mais pas intégrées !")
    print("💡 SOLUTION : Le pipeline doit être modifié pour utiliser ces données")

if __name__ == "__main__":
    debug_pipeline()