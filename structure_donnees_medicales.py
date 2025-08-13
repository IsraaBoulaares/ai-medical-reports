"""
Module pour structurer les données médicales extraites au format standardisé
utilisé par le système de génération de rapports
"""

import json
from typing import Dict, List, Any
from datetime import datetime

class StructureurMedical:
    """
    Classe pour structurer les données médicales dans un format standardisé
    compatible avec le générateur de rapports
    """
    
    STRUCTURE_STANDARD = {
        'patient_id': str,
        'date_consultation': str,
        'motif_consultation': str,
        'diagnostics': List[str],
        'medicaments': List[str],
        'historique': List[str],
        'explorations': List[str],
        'notes_cliniques': str,
        'symptomes': List[str],
        'traitement': List[str],
        'recommandations': List[str]
    }
    
    def __init__(self):
        self.donnees_structurees = {}
    
    def structurer_patient(self, patient_id: str, donnees_extraites: Dict) -> Dict:
        """
        Structurer les données d'un patient selon le format standard
        """
        structure = {
            'patient_id': patient_id,
            'date_consultation': self._determiner_date_consultation(donnees_extraites),
            'motif_consultation': self._determiner_motif(donnees_extraites),
            'diagnostics': self._nettoyer_liste(donnees_extraites.get('diagnostics', [])),
            'medicaments': self._nettoyer_liste([med['nom'] if isinstance(med, dict) else str(med) 
                                               for med in donnees_extraites.get('medicaments', [])]),
            'historique': self._nettoyer_liste(donnees_extraites.get('historique', [])),
            'explorations': self._nettoyer_liste(donnees_extraites.get('explorations', [])),
            'notes_cliniques': self._extraire_notes_cliniques(donnees_extraites),
            'symptomes': self._extraire_symptomes(donnees_extraites),
            'traitement': self._extraire_traitement(donnees_extraites),
            'recommandations': self._generer_recommandations(donnees_extraites)
        }
        
        return structure
    
    def _determiner_date_consultation(self, donnees: Dict) -> str:
        """Déterminer la date de consultation"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def _determiner_motif(self, donnees: Dict) -> str:
        """Déterminer le motif de consultation à partir des diagnostics"""
        diagnostics = donnees.get('diagnostics', [])
        if diagnostics:
            return f"Consultation pour {', '.join(diagnostics[:2])}"
        return "Consultation de suivi"
    
    def _nettoyer_liste(self, liste: List[str]) -> List[str]:
        """Nettoyer et dédupliquer une liste"""
        if not liste:
            return []
        
        # Nettoyer les éléments
        nettoyes = [item.strip() for item in liste if item and len(item.strip()) > 2]
        
        # Dédupliquer
        return list(set(nettoyes))
    
    def _extraire_notes_cliniques(self, donnees: Dict) -> str:
        """Extraire les notes cliniques du texte original"""
        texte = donnees.get('texte_original', '')
        
        # Limiter la longueur pour éviter les rapports trop longs
        if len(texte) > 1000:
            return texte[:1000] + "..."
        
        return texte
    
    def _extraire_symptomes(self, donnees: Dict) -> List[str]:
        """Extraire les symptômes du texte"""
        symptomes = []
        texte = donnees.get('texte_original', '').lower()
        
        # Patterns pour les symptômes
        patterns_symptomes = [
            r'(?:presente|souffre de|se plaint de|recherche)\s+([^,.]+)',
            r'(?:symptomes|signes)\s*:?\s*([^,.]+)'
        ]
        
        import re
        for pattern in patterns_symptomes:
            matches = re.findall(pattern, texte)
            symptomes.extend([match.strip() for match in matches])
        
        return self._nettoyer_liste(symptomes)
    
    def _extraire_traitement(self, donnees: Dict) -> List[str]:
        """Extraire le traitement prescrit"""
        traitement = []
        
        # Combiner médicaments et autres traitements
        medicaments = donnees.get('medicaments', [])
        
        # Gérer les différents formats de médicaments
        for med in medicaments:
            if isinstance(med, dict):
                traitement.append(med.get('nom', ''))
            elif isinstance(med, str):
                traitement.append(med)
            else:
                traitement.append(str(med))
        
        return self._nettoyer_liste(traitement)
    
    def _generer_recommandations(self, donnees: Dict) -> List[str]:
        """Générer des recommandations basées sur les données"""
        recommandations = []
        
        diagnostics = donnees.get('diagnostics', [])
        medicaments = donnees.get('medicaments', [])
        
        if diagnostics:
            recommandations.append(f"Suivi régulier pour {' et '.join(diagnostics)}")
        
        if medicaments:
            recommandations.append("Respecter le traitement prescrit")
            recommandations.append("Contrôle des effets secondaires")
        
        recommandations.extend([
            "Consultation de suivi dans 1 mois",
            "Appeler en cas d'aggravation"
        ])
        
        return self._nettoyer_liste(recommandations)
    
    def valider_structure(self, donnees: Dict) -> bool:
        """Valider que la structure contient toutes les clés requises"""
        cles_requises = ['patient_id', 'date_consultation', 'diagnostics']
        return all(cle in donnees for cle in cles_requises)

# Fonctions utilitaires
def creer_exemple_structure():
    """Créer un exemple de structure de données"""
    exemple = {
        'patient_id': '12345',
        'date_consultation': '2024-01-15',
        'motif_consultation': 'Consultation pour hypertension et diabète',
        'diagnostics': ['Hypertension artérielle essentielle', 'Diabète type 2'],
        'medicaments': ['Amlodipine 5mg', 'Metformine 1000mg'],
        'historique': ['Diabète diagnostiqué en 2020', 'HTA depuis 2 ans'],
        'explorations': ['Bilan biologique complet', 'ECG', 'Échographie cardiaque'],
        'notes_cliniques': 'Patient stable, tension contrôlée, glycémie à surveiller',
        'symptomes': ['Fatigue', 'Polyurie'],
        'traitement': ['Amlodipine 5mg/jour', 'Metformine 1000mg x2/jour'],
        'recommandations': [
            'Suivi régulier',
            'Contrôle tensionnel',
            'Régime diabétique',
            'Consultation dans 1 mois'
        ]
    }
    
    return exemple

if __name__ == "__main__":
    structureur = StructureurMedical()
    exemple = creer_exemple_structure()
    print("Structure de données médicales standardisée:")
    print(json.dumps(exemple, ensure_ascii=False, indent=2))
