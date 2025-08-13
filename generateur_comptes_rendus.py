import json
from datetime import datetime
import os

# Ajout des imports pour PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ reportlab non installé. Installez avec: pip install reportlab")

class GenerateurComptesRendus:
    def __init__(self, donnees_fichier=None):
        """Initialise le générateur avec ou sans fichier de données"""
        self.donnees = {}
        if donnees_fichier and os.path.exists(donnees_fichier):
            self.charger_donnees(donnees_fichier)
        
        # Styles pour PDF
        if PDF_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self.setup_pdf_styles()
    
    def setup_pdf_styles(self):
        """Configuration des styles PDF personnalisés"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='TitrePrincipal',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Style pour les sections
        self.styles.add(ParagraphStyle(
            name='TitreSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5
        ))
        
        # Style pour le contenu
        self.styles.add(ParagraphStyle(
            name='ContenuSection',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=20,
            alignment=TA_JUSTIFY
        ))
        
        # Style pour les informations patient
        self.styles.add(ParagraphStyle(
            name='InfoPatient',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=5,
            textColor=colors.darkgreen
        ))

    def ajouter_patient(self, patient_id, contenu):
        """Ajouter manuellement les données d'un patient"""
        self.donnees[patient_id] = contenu

    def charger_donnees(self, fichier_donnees):
        """Charge les données depuis un fichier JSON"""
        with open(fichier_donnees, "r", encoding="utf-8") as f:
            self.donnees = json.load(f)

    def detecter_type_consultation(self, contenu, diagnostics_csv=None):
        """Détecte le type de consultation basé sur le contenu et les diagnostics CSV"""
        contenu_str = " ".join(str(c) for c in contenu).lower()
        
        # Utiliser d'abord les diagnostics CSV si disponibles
        if diagnostics_csv:
            for diag in diagnostics_csv:
                diag_lower = diag.lower()
                if any(term in diag_lower for term in ["acné", "sebiaclear", "tetralysal"]):
                    return "Dermatologie - Acné"
                elif any(term in diag_lower for term in ["alopécie", "chute", "cheveux"]):
                    return "Dermatologie - Alopécie"
                elif any(term in diag_lower for term in ["mycose", "candidose", "dermatophytie"]):
                    return "Dermatologie - Mycose"
                elif any(term in diag_lower for term in ["psoriasis"]):
                    return "Dermatologie - Psoriasis"
                elif any(term in diag_lower for term in ["dépression", "anxiété", "trouble"]):
                    return "Psychiatrie"
                elif any(term in diag_lower for term in ["esthétique", "botox", "comblement"]):
                    return "Médecine Esthétique"
        
        # Fallback sur l'analyse du contenu
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
    
    def extraire_traitements_ameliore(self, contenu, medicaments_csv=None):
        """Extraire les traitements en combinant contenu et données CSV"""
        traitements = []
        
        # Ajouter les médicaments du CSV en priorité
        if medicaments_csv:
            for med in medicaments_csv:
                if med and med.strip():
                    # Nettoyer et formater le médicament
                    med_clean = med.strip().replace("'", "").replace('"', '')
                    if med_clean and med_clean != "[]":
                        traitements.append(f"Prescription: {med_clean}")
        
        # Compléter avec les traitements du contenu
        for ligne in contenu:
            ligne_str = str(ligne)
            if any(term in ligne_str for term in ["1/", "2/", "3/", "4/", "5/", "mg", "cp", "application"]):
                if not any(med in ligne_str for med in [t.split(": ", 1)[1] for t in traitements if ": " in t]):
                    traitements.append(f"Traitement: {ligne_str}")
        
        return traitements

    def extraire_examen_clinique(self, contenu):
        """Extrait les éléments d'examen clinique"""
        examen = []
        mots_cles = ["examen", "lésion", "présente", "observe", "palpation", "inspection"]
        
        for ligne in contenu:
            if any(mot in ligne.lower() for mot in mots_cles) and not any(term in ligne for term in ["1/", "2/", "3/"]):
                examen.append(ligne)
        
        return examen if examen else ["Examen clinique détaillé réalisé"]

    def extraire_diagnostics_ameliore(self, contenu, diagnostics_csv=None):
        """Extraire les diagnostics en combinant contenu et données CSV"""
        diagnostics = []
        
        # Ajouter les diagnostics du CSV en priorité
        if diagnostics_csv:
            for diag in diagnostics_csv:
                if diag and diag.strip():
                    diagnostics.append(f"Diagnostic confirmé: {diag}")
        
        # Compléter avec les diagnostics du contenu
        for ligne in contenu:
            ligne_str = str(ligne)
            if "diagnostic:" in ligne_str.lower():
                diag_extrait = ligne_str.split(":", 1)[1].strip()
                if diag_extrait not in [d.split(": ", 1)[1] for d in diagnostics]:
                    diagnostics.append(f"Diagnostic clinique: {diag_extrait}")
        
        return diagnostics if diagnostics else ["Consultation de suivi"]

    def generer_compte_rendu_ameliore(self, patient_id, diagnostics_csv=None, medicaments_csv=None):
        """Génère un compte rendu amélioré utilisant toutes les données disponibles"""
        if patient_id not in self.donnees:
            return None
        
        contenu = self.donnees[patient_id]
        type_consultation = self.detecter_type_consultation(contenu, diagnostics_csv)
        antecedents = self.extraire_antecedents(contenu)
        traitements = self.extraire_traitements_ameliore(contenu, medicaments_csv)
        examen = self.extraire_examen_clinique(contenu)
        diagnostics = self.extraire_diagnostics_ameliore(contenu, diagnostics_csv)
        
        # Générer des recommandations personnalisées
        recommandations = self.generer_recommandations_personnalisees(
            type_consultation, diagnostics_csv, medicaments_csv
        )
        
        compte_rendu = f"""
COMPTE RENDU DE CONSULTATION
============================

Date: {datetime.now().strftime("%d/%m/%Y")}
Patient ID: {patient_id}
Type de consultation: {type_consultation}

ANTÉCÉDENTS:
{chr(10).join(f"• {ant}" for ant in antecedents) if antecedents else "• Pas d'antécédents particuliers mentionnés"}

EXAMEN CLINIQUE:
{chr(10).join(f"• {ex}" for ex in examen) if examen else "• Examen clinique détaillé réalisé"}

DIAGNOSTIC ET CONDUITE À TENIR:
{chr(10).join(f"• {diag}" for diag in diagnostics)}

TRAITEMENT PRESCRIT:
{chr(10).join(f"• {trait}" for trait in traitements) if traitements else "• Pas de traitement médicamenteux prescrit"}

RECOMMANDATIONS ET SUIVI:
{chr(10).join(f"• {rec}" for rec in recommandations)}

Dr. [Nom du médecin]
"""
        return compte_rendu

    def generer_recommandations_personnalisees(self, type_consultation, diagnostics_csv, medicaments_csv):
        """Générer des recommandations personnalisées selon le type de consultation"""
        recommandations = []
        
        if "Dermatologie - Acné" in type_consultation:
            recommandations.extend([
                "Nettoyage doux du visage matin et soir",
                "Éviter les produits comédogènes",
                "Contrôle dans 6-8 semaines"
            ])
        elif "Dermatologie - Alopécie" in type_consultation:
            recommandations.extend([
                "Éviter les traumatismes capillaires",
                "Alimentation équilibrée riche en fer",
                "Contrôle dans 3 mois pour évaluer l'évolution"
            ])
        elif "Psychiatrie" in type_consultation:
            recommandations.extend([
                "Suivi psychologique régulier",
                "Observance stricte du traitement",
                "Contrôle dans 15 jours puis mensuel"
            ])
        elif "Dermatologie - Mycose" in type_consultation:
            recommandations.extend([
                "Hygiène rigoureuse des zones atteintes",
                "Séchage soigneux après toilette",
                "Contrôle dans 2-3 semaines"
            ])
        
        # Recommandations générales
        recommandations.extend([
            "Revoir si aggravation ou nouveaux symptômes",
            "Respecter la posologie prescrite"
        ])
        
        if medicaments_csv:
            recommandations.append("Surveillance des effets secondaires du traitement")
        
        return recommandations

    def generer_pdf_ameliore(self, patient_id, diagnostics_csv=None, medicaments_csv=None, 
                           dossier_sortie="comptes_rendus"):
        """Génère un compte rendu en format PDF"""
        if not PDF_AVAILABLE:
            print("❌ Impossible de générer le PDF - reportlab non installé")
            return None
        
        if patient_id not in self.donnees:
            return None
        
        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(dossier_sortie):
            os.makedirs(dossier_sortie)
        
        # Nom du fichier PDF
        nom_fichier = f"CR_Patient_{patient_id}.pdf"
        chemin_pdf = os.path.join(dossier_sortie, nom_fichier)
        
        # Extraire les données
        contenu = self.donnees[patient_id]
        type_consultation = self.detecter_type_consultation(contenu, diagnostics_csv)
        antecedents = self.extraire_antecedents(contenu)
        traitements = self.extraire_traitements_ameliore(contenu, medicaments_csv)
        examen = self.extraire_examen_clinique(contenu)
        diagnostics = self.extraire_diagnostics_ameliore(contenu, diagnostics_csv)
        recommandations = self.generer_recommandations_personnalisees(
            type_consultation, diagnostics_csv, medicaments_csv
        )
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            chemin_pdf,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenu du PDF
        story = []
        
        # En-tête
        story.append(Paragraph("COMPTE RENDU DE CONSULTATION", self.styles['TitrePrincipal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Informations générales dans un tableau
        data_info = [
            ['Date:', datetime.now().strftime("%d/%m/%Y")],
            ['Patient ID:', str(patient_id)],
            ['Type de consultation:', type_consultation]
        ]
        
        table_info = Table(data_info, colWidths=[4*cm, 10*cm])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table_info)
        story.append(Spacer(1, 0.5*cm))
        
        # Sections du rapport
        sections = [
            ("ANTÉCÉDENTS", antecedents if antecedents else ["Pas d'antécédents particuliers mentionnés"]),
            ("EXAMEN CLINIQUE", examen if examen else ["Examen clinique détaillé réalisé"]),
            ("DIAGNOSTIC ET CONDUITE À TENIR", diagnostics),
            ("TRAITEMENT PRESCRIT", traitements if traitements else ["Pas de traitement médicamenteux prescrit"]),
            ("RECOMMANDATIONS ET SUIVI", recommandations)
        ]
        
        for titre, contenu_section in sections:
            # Titre de section
            story.append(Paragraph(titre, self.styles['TitreSection']))
            
            # Contenu de la section
            for item in contenu_section:
                # Nettoyer le texte
                item_clean = str(item).replace('•', '').strip()
                story.append(Paragraph(f"• {item_clean}", self.styles['ContenuSection']))
            
            story.append(Spacer(1, 0.3*cm))
        
        # Signature
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("Dr. [Nom du médecin]", self.styles['InfoPatient']))
        
        # Générer le PDF
        try:
            doc.build(story)
            return chemin_pdf
        except Exception as e:
            print(f"❌ Erreur lors de la génération du PDF pour {patient_id}: {e}")
            return None

    def generer_compte_rendu_complet(self, patient_id, diagnostics_csv=None, medicaments_csv=None,
                                   format_sortie="both", dossier_sortie="comptes_rendus"):
        """Génère un compte rendu en format texte et/ou PDF"""
        resultats = {}
        
        # Générer le format texte
        if format_sortie in ["txt", "both"]:
            rapport_txt = self.generer_compte_rendu_ameliore(patient_id, diagnostics_csv, medicaments_csv)
            if rapport_txt:
                nom_fichier_txt = f"CR_Patient_{patient_id}.txt"
                chemin_txt = os.path.join(dossier_sortie, nom_fichier_txt)
                
                if not os.path.exists(dossier_sortie):
                    os.makedirs(dossier_sortie)
                
                with open(chemin_txt, 'w', encoding='utf-8') as f:
                    f.write(rapport_txt)
                
                resultats['txt'] = chemin_txt
        
        # Générer le format PDF
        if format_sortie in ["pdf", "both"] and PDF_AVAILABLE:
            chemin_pdf = self.generer_pdf_ameliore(patient_id, diagnostics_csv, medicaments_csv, dossier_sortie)
            if chemin_pdf:
                resultats['pdf'] = chemin_pdf
        
        return resultats

    def generer_tous_comptes_rendus_pdf(self, format_sortie="both", dossier_sortie="comptes_rendus"):
        """Génère tous les comptes rendus en format spécifié"""
        if not os.path.exists(dossier_sortie):
            os.makedirs(dossier_sortie)
        
        resultats = {}
        total_generes = 0
        
        for patient_id in self.donnees.keys():
            fichiers = self.generer_compte_rendu_complet(
                patient_id, 
                format_sortie=format_sortie,
                dossier_sortie=dossier_sortie
            )
            
            if fichiers:
                resultats[patient_id] = fichiers
                total_generes += 1
                
                if total_generes % 50 == 0:
                    print(f"📄 {total_generes} comptes rendus générés...")
        
        print(f"✅ {total_generes} comptes rendus générés dans le dossier '{dossier_sortie}'")
        
        if format_sortie in ["pdf", "both"] and PDF_AVAILABLE:
            print(f"📄 Fichiers PDF disponibles")
        if format_sortie in ["txt", "both"]:
            print(f"📝 Fichiers TXT disponibles")
        
        return resultats

if __name__ == "__main__":
    generateur = GenerateurComptesRendus()
    
    generateur.generer_tous_comptes_rendus_pdf()
    
    


