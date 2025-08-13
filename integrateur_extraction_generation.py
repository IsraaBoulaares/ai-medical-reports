

import json
import pandas as pd
from typing import Dict, List, Any
import os
from datetime import datetime

class IntegrateurExtractionGeneration:
    """
    Classe principale pour intégrer l'extraction de données médicales avec la génération de rapports
    """
    
    def __init__(self):
        self.donnees_extraites = {}
        self.donnees_structurees = {}
        
    def charger_notes_consultation(self, chemin_fichier: str) -> Dict:
        """Charger les notes de consultation depuis un fichier JSON"""
        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des notes: {e}")
            return {}
    
    def extraire_donnees_medicales(self, notes_consultation: Dict) -> Dict:
        """
        Extraire les données médicales des notes de consultation
        Utilise l'approche de Nour pour l'extraction
        """
        donnees_extraites = {}
        
        for patient_id, notes in notes_consultation.items():
            if isinstance(notes, list):
                texte_complet = " ".join(str(note) for note in notes)
            else:
                texte_complet = str(notes)
                
            # Extraction des diagnostics
            diagnostics = self._extraire_diagnostics(texte_complet)
            
            # Extraction des médicaments
            medicaments = self._extraire_medicaments(texte_complet)
            
            # Extraction de l'historique médical
            historique = self._extraire_historique(texte_complet)
            
            # Extraction des explorations
            explorations = self._extraire_explorations(texte_complet)
            
            donnees_extraites[patient_id] = {
                'diagnostics': diagnostics,
                'medicaments': medicaments,
                'historique': historique,
                'explorations': explorations,
                'texte_original': texte_complet
            }
            
        return donnees_extraites
    
    def _extraire_diagnostics(self, texte: str) -> List[str]:
        """Extraire les diagnostics du texte"""
        diagnostics = []
        
        # Patterns pour identifier les diagnostics
        patterns_diagnostic = [
            r'(?:diagnostic|diagnostique|pathologie|maladie)\s*:?\s*([^.]+)',
            r'(?:souffre de|atteint de|présente)\s+([^,]+)',
            r'(?:diagnostic retenu|conclusion)\s*:?\s*([^.]+)'
        ]
        
        import re
        for pattern in patterns_diagnostic:
            matches = re.findall(pattern, texte, re.IGNORECASE)
            diagnostics.extend([match.strip() for match in matches])
        
        # Nettoyer et dédupliquer
        diagnostics = list(set([d for d in diagnostics if len(d) > 3]))
        return diagnostics
    
    def _extraire_medicaments(self, texte: str) -> List[Dict]:
        """Extraire les médicaments avec posologie"""
        medicaments = []
        
        # Patterns pour les médicaments
        patterns_medicament = [
            r'(\w+)\s+(?:\d+(?:mg|g|ml|cp)?)\s*(?:x\s*\d+)?\s*(?:fois\s*par\s*(?:jour|semaine|mois))?',
            r'(?:prescrit|prescription)\s*:?\s*([^,]+)'
        ]
        
        import re
        for pattern in patterns_medicament:
            matches = re.findall(pattern, texte, re.IGNORECASE)
            for match in matches:
                medicaments.append({
                    'nom': match.strip(),
                    'posologie': 'À déterminer selon contexte'
                })
        
        return medicaments
    
    def _extraire_historique(self, texte: str) -> List[str]:
        """Extraire l'historique médical"""
        historique = []
        
        # Patterns pour l'historique
        patterns_historique = [
            r'(?:atcd|antecedent|historique)\s*:?\s*([^.]+)',
            r'(?:patient|malade)\s+(?:a|avec)\s+([^,]+)'
        ]
        
        import re
        for pattern in patterns_historique:
            matches = re.findall(pattern, texte, re.IGNORECASE)
            historique.extend([match.strip() for match in matches])
        
        return historique
    
    def _extraire_explorations(self, texte: str) -> List[str]:
        """Extraire les explorations médicales"""
        explorations = []
        
        # Patterns pour les explorations
        patterns_exploration = [
            r'(?:examen|test|bilan|echographie|scanner|irm)\s*:?\s*([^.]+)',
            r'(?:realise|effectue)\s+([^,]+)'
        ]
        
        import re
        for pattern in patterns_exploration:
            matches = re.findall(pattern, texte, re.IGNORECASE)
            explorations.extend([match.strip() for match in matches])
        
        return explorations
    
    def structurer_pour_generation(self, donnees_extraites: Dict) -> Dict:
        """
        Structurer les données extraites pour le générateur de rapports
        Transforme le format d'extraction au format attendu par le générateur
        """
        donnees_structurees = {}
        
        for patient_id, donnees in donnees_extraites.items():
            # Structure conforme au format attendu par le générateur
            # Le générateur attend une liste de strings comme contenu
            contenu_liste = []
            
            # Ajouter les diagnostics
            if donnees.get('diagnostics'):
                contenu_liste.extend([f"Diagnostic: {diag}" for diag in donnees['diagnostics']])
            
            # Ajouter les médicaments
            if donnees.get('medicaments'):
                for med in donnees['medicaments']:
                    if isinstance(med, dict):
                        contenu_liste.append(f"Traitement: {med.get('nom', '')}")
                    else:
                        contenu_liste.append(f"Traitement: {med}")
            
            # Ajouter l'historique
            if donnees.get('historique'):
                contenu_liste.extend([f"Antécédent: {hist}" for hist in donnees['historique']])
            
            # Ajouter les explorations
            if donnees.get('explorations'):
                contenu_liste.extend([f"Exploration: {expl}" for expl in donnees['explorations']])
            
            # Ajouter le texte original découpé
            texte_original = donnees.get('texte_original', '')
            if texte_original:
                phrases = [p.strip() for p in texte_original.split('.') if p.strip()]
                contenu_liste.extend(phrases)
            
            donnees_structurees[patient_id] = contenu_liste
            
        return donnees_structurees
    
    def sauvegarder_donnees_extraites(self, donnees: Dict, chemin_sortie: str):
        """Sauvegarder les données extraites dans un fichier JSON"""
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)
    
    def generer_pipeline_complet(self, chemin_notes_entree: str, chemin_rapport_sortie: str):
        """
        Pipeline complet: notes → extraction → structuration → génération → rapport
        """
        print("Étape 1: Chargement des notes de consultation...")
        notes = self.charger_notes_consultation(chemin_notes_entree)
        
        print("Étape 2: Extraction des données médicales...")
        donnees_extraites = self.extraire_donnees_medicales(notes)
        
        print("Étape 3: Structuration des données...")
        donnees_structurees = self.structurer_pour_generation(donnees_extraites)
        
        print("Étape 4: Génération des rapports...")
        # Importer et utiliser le générateur de rapports
        try:
            from generateur_comptes_rendus_ameliore_complet import GenerateurComptesRendus
            generateur = GenerateurComptesRendus()
            
            for patient_id, donnees in donnees_structurees.items():
                rapport = generateur.generer_compte_rendu(donnees)
                
                # Sauvegarder le rapport
                nom_fichier = f"CR_Patient_{patient_id}_genere.txt"
                chemin_complet = os.path.join(chemin_rapport_sortie, nom_fichier)
                
                with open(chemin_complet, 'w', encoding='utf-8') as f:
                    f.write(rapport)
                
                print(f"Rapport généré pour le patient {patient_id}: {nom_fichier}")
                
        except ImportError as e:
            print(f"Erreur lors de l'import du générateur: {e}")
            print("Utilisation du générateur de base...")
            # Fallback vers le générateur de base
            
        return donnees_structurees

# Fonction utilitaire pour tester l'intégration
def tester_integration():
    """Fonction de test pour valider l'intégration"""
    integrateur = IntegrateurExtractionGeneration()
    
    # Test avec les données existantes
    chemin_notes = "consultations_notes_clean.json"
    chemin_rapports = "comptes_rendus"
    
    if os.path.exists(chemin_notes):
        resultat = integrateur.generer_pipeline_complet(chemin_notes, chemin_rapports)
        print(f"Intégration réussie! {len(resultat)} rapports générés.")
    else:
        print("Fichier de notes non trouvé. Création d'un exemple...")
        
        # Créer un exemple de données
        exemple_notes = {
            "1": [
                "Patient présente une hypertension artérielle. Diagnostic: HTA essentielle. Traitement: Amlodipine 5mg/jour.",
                "Antécédents: diabète type 2. Examens: bilan biologique complet."
            ],
            "2": [
                "Consultation pour douleur thoracique. Diagnostic: angor stable. Prescription: Trinitrine 0.4mg si besoin.",
                "Explorations: ECG, échographie cardiaque. Historique: tabagisme 30 PA."
            ]
        }
        
        with open(chemin_notes, 'w', encoding='utf-8') as f:
            json.dump(exemple_notes, f, ensure_ascii=False, indent=4)
        
        print("Exemple créé. Relancez le test.")

if __name__ == "__main__":
    tester_integration()
