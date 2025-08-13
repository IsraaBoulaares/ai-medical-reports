def analyser_generation_pdf():
    """Analyser le code de génération PDF pour confirmer l'utilisation des données"""
    
    print("🔍 ANALYSE DU CODE PDF")
    print("=" * 30)
    
    # Lire le fichier pipeline_complet_final.py
    with open("pipeline_complet_final.py", 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Chercher les fonctions PDF
    lignes = code.split('\n')
    
    print("🔍 RECHERCHE DANS LE CODE PDF:")
    
    # Mots-clés à chercher
    mots_cles = [
        'charger_donnees_extraites',
        'medicaments',
        'diagnostics', 
        'antecedents',
        'explorations',
        'generer_pdf'
    ]
    
    for i, ligne in enumerate(lignes):
        for mot in mots_cles:
            if mot in ligne and 'def ' not in ligne:
                print(f"✅ Ligne {i+1}: {ligne.strip()}")
    
    # Vérifier la fonction generer_pdf
    print(f"\n📄 FONCTION generer_pdf UTILISE:")
    
    in_pdf_function = False
    for ligne in lignes:
        if 'def generer_pdf' in ligne:
            in_pdf_function = True
            print(f"✅ Fonction trouvée: {ligne.strip()}")
        elif in_pdf_function and ligne.strip().startswith('def '):
            break
        elif in_pdf_function and any(mot in ligne for mot in ['donnees_extraites', 'medicaments', 'diagnostics']):
            print(f"✅ Utilise données: {ligne.strip()}")

if __name__ == "__main__":
    analyser_generation_pdf()