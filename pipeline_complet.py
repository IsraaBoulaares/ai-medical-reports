"""
Pipeline complet pour intégrer l'extraction de données médicales avec la génération de rapports
Ce fichier orchestre l'ensemble du processus
"""

import os
import json
import sys
from typing import Dict, List
from datetime import datetime
from integrateur_extraction_generation import IntegrateurExtractionGeneration
from structure_donnees_medicales import StructureurMedical

class PipelineMedicalComplet:
    """
    Pipeline complet pour générer des rapports médicaux à partir de notes de consultation
    """
    
    def __init__(self):
        self.extracteur = IntegrateurExtractionGeneration()
        self.structureur = StructureurMedical()
        self.repertoire_rapports = "comptes_rendus"
        
        # Créer le répertoire de sortie s'il n'existe pas
        if not os.path.exists(self.repertoire_rapports):
            os.makedirs(self.repertoire_rapports)
    
    def charger_configuration(self, chemin_config: str = None) -> Dict:
        """Charger la configuration du pipeline"""
        config_defaut = {
            'format_sortie': 'txt',
            'inclure_date': True,
            'langue': 'fr',
            'repertoire_sortie': self.repertoire_rapports,
            'prefixe_fichier': 'CR_Patient_',
            'max_patients': None
        }
        
        if chemin_config and os.path.exists(chemin_config):
            with open(chemin_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config_defaut.update(config)
        
        return config_defaut
    
    def generer_rapports_batch(self, chemin_notes: str, config: Dict = None) -> Dict:
        """
        Générer des rapports pour un batch de patients
        """
        if config is None:
            config = self.charger_configuration()
        
        print("=" * 60)
        print("PIPELINE MÉDICAL COMPLET - GÉNÉRATION DE RAPPORTS")
        print("=" * 60)
        
        # Étape 1: Charger les notes
        print("Étape 1: Chargement des notes de consultation...")
        notes = self.extracteur.charger_notes_consultation(chemin_notes)
        
        if not notes:
            print("❌ Aucune note trouvée")
            return {}
        
        print(f"✅ {len(notes)} patients trouvés")
        
        # Étape 2: Extraire les données
        print("\nÉtape 2: Extraction des données médicales...")
        donnees_extraites = self.extracteur.extraire_donnees_medicales(notes)
        print(f"✅ Données extraites pour {len(donnees_extraites)} patients")
        
        # Étape 3: Structurer les données
        print("\nÉtape 3: Structuration des données...")
        donnees_structurees = {}
        for patient_id, donnees in donnees_extraites.items():
            structure = self.structureur.structurer_patient(patient_id, donnees)
            if self.structureur.valider_structure(structure):
                donnees_structurees[patient_id] = structure
        
        print(f"✅ {len(donnees_structurees)} structures de données créées")
        
        # Étape 4: Générer les rapports
        print("\nÉtape 4: Génération des rapports...")
        rapports_genere = {}
        
        # Importer le générateur approprié
        try:
            from generateur_comptes_rendus_ameliore_complet import GenerateurComptesRendus
            generateur = GenerateurComptesRendus()
            print("✅ Utilisation du générateur amélioré")
        except ImportError:
            try:
                from generateur_comptes_rendus import GenerateurComptesRendus
                generateur = GenerateurComptesRendus()
                print("✅ Utilisation du générateur de base")
            except ImportError:
                print("❌ Aucun générateur trouvé")
                return {}
        
        # Limiter le nombre de patients si spécifié
        patients_a_traiter = list(donnees_structurees.keys())
        if config.get('max_patients'):
            patients_a_traiter = patients_a_traiter[:config['max_patients']]
        
        for patient_id in patients_a_traiter:
            try:
                # Générer le rapport
                rapport = generateur.generer_compte_rendu(donnees_structurees[patient_id])
                
                # Créer le nom de fichier
                nom_fichier = f"{config['prefixe_fichier']}{patient_id}.txt"
                chemin_complet = os.path.join(config['repertoire_sortie'], nom_fichier)
                
                # Sauvegarder le rapport
                with open(chemin_complet, 'w', encoding='utf-8') as f:
                    f.write(rapport)
                
                rapports_genere[patient_id] = {
                    'fichier': nom_fichier,
                    'chemin': chemin_complet,
                    'taille': len(rapport)
                }
                
                print(f"✅ Rapport généré pour patient {patient_id}")
                
            except Exception as e:
                print(f"❌ Erreur pour patient {patient_id}: {e}")
        
        # Étape 5: Résumé
        print("\n" + "=" * 60)
        print("RÉSUMÉ DE LA GÉNÉRATION")
        print("=" * 60)
        print(f"Total patients traités: {len(rapports_genere)}")
        print(f"Répertoire des rapports: {config['repertoire_sortie']}")
        
        return rapports_genere
    
    def generer_statistiques(self, donnees_extraites: Dict) -> Dict:
        """Générer des statistiques sur les données extraites"""
        stats = {
            'total_patients': len(donnees_extraites),
            'total_diagnostics': 0,
            'total_medicaments': 0,
            'total_explorations': 0,
            'diagnostics_uniques': set(),
            'medicaments_uniques': set(),
            'explorations_uniques': set()
        }
        
        for patient_id, donnees in donnees_extraites.items():
            stats['total_diagnostics'] += len(donnees.get('diagnostics', []))
            stats['total_medicaments'] += len(donnees.get('medicaments', []))
            stats['total_explorations'] += len(donnees.get('explorations', []))
            
            stats['diagnostics_uniques'].update(donnees.get('diagnostics', []))
            stats['medicaments_uniques'].update([med['nom'] if isinstance(med, dict) else str(med) 
                                               for med in donnees.get('medicaments', [])])
            stats['explorations_uniques'].update(donnees.get('explorations', []))
        
        # Convertir les sets en listes pour la sérialisation JSON
        stats['diagnostics_uniques'] = list(stats['diagnostics_uniques'])
        stats['medicaments_uniques'] = list(stats['medicaments_uniques'])
        stats['explorations_uniques'] = list(stats['explorations_uniques'])
        
        return stats
    
    def creer_rapport_resume(self, stats: Dict, chemin_sortie: str):
        """Créer un rapport récapitulatif"""
        rapport_resume = f"""
RAPPORT RÉCAPITULATIF - PIPELINE MÉDICAL
======================================

Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTIQUES:
- Total patients traités: {stats['total_patients']}
- Total diagnostics extraits: {stats['total_diagnostics
