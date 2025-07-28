import json
from datetime import datetime
import os

class GenerateurComptesRendus:
    def __init__(self, fichier_donnees="donnees_nettoyees_finales.json"):
        with open(fichier_donnees, "r", encoding="utf-8") as f:
            self.donnees = json.load(f)
    
    def detecter_type_consultation(self, contenu):
        """Détecte le type de consultation basé sur le contenu"""
        contenu_str = " ".join(contenu).lower()
        
        if any(term in contenu_str for term in ["acné", "sebiaclear", "tetralysal", "zinc"]):
            return "Dermatologie - Acné"
        elif any(term in contenu_str for term in ["chute", "cheveux", "minoxidil", "alopécie"]):
            return "Dermatologie - Alopécie"
        elif any(term in contenu_str for term in ["mycose", "ketozol", "mycoster", "flucazol"]):
            return "Dermatologie - Mycose"
        elif any(term in contenu_str for term in ["psoriasis", "methotrexate", "pso"]):
            return "Dermatologie - Psoriasis"
        elif any(term in contenu_str for term in ["anxiété", "dépression", "psychothérapie"]):
            return "Psychiatrie"
        elif any(term in contenu_str for term in ["botox", "toxine", "comblement", "esthétique"]):
            return "Médecine Esthétique"
        else:
            return "Consultation Générale"
    
    def extraire_antecedents(self, contenu):
        """Extrait les antécédents du contenu"""
        antecedents = []
        for ligne in contenu:
            if any(term in ligne.lower() for term in ["atcd", "antécédents", "allergies"]):
                antecedents.append(ligne)
        return antecedents if antecedents else ["Pas d'antécédents particuliers mentionnés"]
    
    def extraire_traitements(self, contenu):
        """Extrait les traitements prescrits"""
        traitements = []
        for ligne in contenu:
            if any(term in ligne for term in ["1/", "2/", "3/", "4/", "5/", "mg", "cp", "application"]):
                traitements.append(ligne)
        return traitements
    
    def extraire_examen_clinique(self, contenu):
        """Extrait les éléments d'examen clinique"""
        examen = []
        mots_cles = ["examen", "lésion", "présente", "observe", "palpation", "inspection"]
        
        for ligne in contenu:
            if any(mot in ligne.lower() for mot in mots_cles) and not any(term in ligne for term in ["1/", "2/", "3/"]):
                examen.append(ligne)
        
        return examen if examen else ["Examen clinique détaillé réalisé"]
    
    def generer_compte_rendu(self, patient_id):
        """Génère un compte rendu structuré pour un patient"""
        if patient_id not in self.donnees:
            return None
        
        contenu = self.donnees[patient_id]
        type_consultation = self.detecter_type_consultation(contenu)
        antecedents = self.extraire_antecedents(contenu)
        traitements = self.extraire_traitements(contenu)
        examen = self.extraire_examen_clinique(contenu)
        
        compte_rendu = f"""
COMPTE RENDU DE CONSULTATION
============================

Date: {datetime.now().strftime("%d/%m/%Y")}
Patient ID: {patient_id}
Type de consultation: {type_consultation}

ANTÉCÉDENTS:
{chr(10).join(f"• {ant}" for ant in antecedents)}

EXAMEN CLINIQUE:
{chr(10).join(f"• {ex}" for ex in examen)}

DIAGNOSTIC ET CONDUITE À TENIR:
{chr(10).join(f"• {ligne}" for ligne in contenu if ligne not in antecedents + traitements + examen)}

TRAITEMENT PRESCRIT:
{chr(10).join(f"• {trait}" for trait in traitements) if traitements else "• Pas de traitement médicamenteux prescrit"}

SUIVI:
• Contrôle selon évolution
• Revoir si nécessaire

Dr. [Nom du médecin]
"""
        return compte_rendu
    
    def generer_tous_comptes_rendus(self, dossier_sortie="comptes_rendus"):
        """Génère tous les comptes rendus dans un dossier"""
        if not os.path.exists(dossier_sortie):
            os.makedirs(dossier_sortie)
        
        for patient_id in self.donnees.keys():
            compte_rendu = self.generer_compte_rendu(patient_id)
            if compte_rendu:
                nom_fichier = f"CR_Patient_{patient_id}.txt"
                chemin_fichier = os.path.join(dossier_sortie, nom_fichier)
                
                with open(chemin_fichier, "w", encoding="utf-8") as f:
                    f.write(compte_rendu)
        
        print(f" {len(self.donnees)} comptes rendus générés dans le dossier '{dossier_sortie}'")


if __name__ == "__main__":
    generateur = GenerateurComptesRendus()
    
    generateur.generer_tous_comptes_rendus()
    
    