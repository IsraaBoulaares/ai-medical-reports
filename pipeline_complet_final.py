
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List

# Import conditionnel pour PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class PipelineMedical:
    def __init__(self, format_sortie="both"):
        self.format_sortie = format_sortie
        self.repertoire = "comptes_rendus"
        os.makedirs(self.repertoire, exist_ok=True)
        
        # Styles PDF améliorés
        if PDF_AVAILABLE:
            self.styles = getSampleStyleSheet()
            # Titre principal
            self.styles.add(ParagraphStyle(
                'TitrePrincipal',
                fontSize=16,
                spaceAfter=20,
                alignment=1,  # Centré
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            ))
            # Sections
            self.styles.add(ParagraphStyle(
                'TitreSection',
                fontSize=12,
                spaceBefore=15,
                spaceAfter=8,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=colors.lightgrey,
                borderPadding=5,
                backColor=colors.lightgrey
            ))
            # Contenu
            self.styles.add(ParagraphStyle(
                'ContenuSection',
                fontSize=10,
                spaceAfter=6,
                leftIndent=15,
                alignment=0,  # Justifié
                fontName='Helvetica'
            ))
            # Info patient
            self.styles.add(ParagraphStyle(
                'InfoPatient',
                fontSize=11,
                spaceAfter=10,
                textColor=colors.darkgreen,
                fontName='Helvetica-Bold'
            ))

    def charger_donnees_extraites(self, patient_id: str) -> Dict:
        """Charger les données extraites pour un patient spécifique"""
        donnees = {}
        
        try:
            # Médicaments
            if os.path.exists("medicaments_extraits.csv"):
                df_med = pd.read_csv("medicaments_extraits.csv")
                meds = df_med[df_med['Patient'] == int(patient_id)]
                if not meds.empty:
                    donnees['medicaments'] = eval(meds.iloc[0]['Medicaments']) if meds.iloc[0]['Medicaments'] != '[]' else []
            
            # Diagnostics
            if os.path.exists("diagnostics_extraits.csv"):
                df_diag = pd.read_csv("diagnostics_extraits.csv")
                diags = df_diag[df_diag['Patient'] == int(patient_id)]
                if not diags.empty:
                    donnees['diagnostics'] = [
                        f"{row['Diagnostic_CIM10']} ({row['Code_CIM10']})" 
                        for _, row in diags.iterrows() 
                        if pd.notna(row['Diagnostic_CIM10'])
                    ]
            
            # Antécédents
            if os.path.exists("antecedents_extraits.csv"):
                df_atcd = pd.read_csv("antecedents_extraits.csv")
                atcds = df_atcd[df_atcd['Patient'] == int(patient_id)]
                if not atcds.empty:
                    donnees['antecedents'] = eval(atcds.iloc[0]['Antecedents']) if atcds.iloc[0]['Antecedents'] != '[]' else []
            
            # Explorations
            if os.path.exists("explorations_extraites.csv"):
                df_expl = pd.read_csv("explorations_extraites.csv")
                expls = df_expl[df_expl['Patient'] == int(patient_id)]
                if not expls.empty:
                    donnees['explorations'] = eval(expls.iloc[0]['Explorations']) if expls.iloc[0]['Explorations'] != '[]' else []
                
        except Exception as e:
            print(f"⚠️ Erreur chargement données patient {patient_id}: {e}")
        
        return donnees

    def charger_donnees(self) -> Dict:
        """Charger toutes les données disponibles"""
        donnees = {}
        
        # Données principales
        if os.path.exists("donnees_nettoyees_finales.json"):
            with open("donnees_nettoyees_finales.json", 'r', encoding='utf-8') as f:
                donnees['patients'] = json.load(f)
        
        # Médicaments CSV
        if os.path.exists("medicaments_extraits.csv"):
            df = pd.read_csv("medicaments_extraits.csv")
            donnees['medicaments'] = df.set_index('Patient')['Medicaments'].to_dict()
        
        # Diagnostics CSV
        if os.path.exists("diagnostics_extraits.csv"):
            df = pd.read_csv("diagnostics_extraits.csv")
            donnees['diagnostics'] = df.groupby('Patient')['Diagnostic_CIM10'].apply(list).to_dict()
        
        return donnees

    def extraire_info(self, texte: str, patient_id: str = None) -> Dict:
        """Extraction enrichie avec les données CSV"""
        # Extraction de base du texte
        info_base = {
            'type': self._detecter_type_consultation(texte),
            'antecedents': self._extraire_du_texte(texte, ['atcd', 'antécédent', 'historique']),
            'traitements': self._extraire_du_texte(texte, ['mg', 'cp', 'traitement', 'prescription']),
            'examens': self._extraire_du_texte(texte, ['examen', 'test', 'bilan'])
        }
        
        # Enrichissement avec les données extraites
        if patient_id:
            donnees_extraites = self.charger_donnees_extraites(patient_id)
            
            # Ajouter médicaments extraits
            if donnees_extraites.get('medicaments'):
                info_base['traitements'].extend([f"Médicament prescrit: {med}" for med in donnees_extraites['medicaments'] if med])
            
            # Ajouter antécédents extraits
            if donnees_extraites.get('antecedents'):
                info_base['antecedents'].extend([f"ATCD: {atcd}" for atcd in donnees_extraites['antecedents'] if atcd])
            
            # Ajouter explorations extraites
            if donnees_extraites.get('explorations'):
                info_base['examens'].extend([f"Exploration: {expl}" for expl in donnees_extraites['explorations'] if expl])
        
        # Nettoyer et dédupliquer
        for key in ['antecedents', 'traitements', 'examens']:
            info_base[key] = list(set([item for item in info_base[key] if item and len(str(item).strip()) > 3]))
        
        return info_base

    def _detecter_type_consultation(self, texte: str) -> str:
        """Détection améliorée du type de consultation"""
        texte_lower = texte.lower()
        
        # Spécialités médicales
        if any(term in texte_lower for term in ['acné', 'alopécie', 'mycose', 'psoriasis', 'eczéma', 'dermatite']):
            return "Dermatologie"
        elif any(term in texte_lower for term in ['anxiété', 'dépression', 'stress', 'psychiatrie']):
            return "Psychiatrie"
        elif any(term in texte_lower for term in ['esthétique', 'botox', 'injection']):
            return "Médecine Esthétique"
        else:
            return "Consultation Générale"

    def _extraire_du_texte(self, texte: str, mots_cles: list) -> list:
        """Extraction basique du texte"""
        resultats = []
        for ligne in texte.split('\n'):
            if any(mot in ligne.lower() for mot in mots_cles):
                resultats.append(ligne.strip())
        return resultats

    def generer_txt(self, patient_id: str, donnees: Dict) -> str:
        """Génération rapport texte enrichi"""
        info = self.extraire_info(' '.join(donnees.get('notes', [])), patient_id)
        
        # Récupérer diagnostics extraits
        donnees_extraites = self.charger_donnees_extraites(patient_id)
        diagnostics_extraits = donnees_extraites.get('diagnostics', [])
        
        rapport = f"""COMPTE RENDU DE CONSULTATION

Date: {datetime.now().strftime('%d/%m/%Y')}
Patient: {patient_id}
Type: {info['type']}

ANTÉCÉDENTS:
{chr(10).join(f"• {ant}" for ant in info['antecedents']) if info['antecedents'] else "• Pas d'antécédents particuliers"}

EXAMEN CLINIQUE:
{chr(10).join(f"• {ex}" for ex in info['examens']) if info['examens'] else "• Examen clinique réalisé"}

DIAGNOSTICS:
{chr(10).join(f"• {diag}" for diag in diagnostics_extraits) if diagnostics_extraits else "• Diagnostic en cours"}

TRAITEMENTS:
{chr(10).join(f"• {trait}" for trait in info['traitements']) if info['traitements'] else "• Pas de traitement prescrit"}

RECOMMANDATIONS:
• Suivi selon évolution
• Respecter les prescriptions
• Revoir si aggravation

Dr. [Nom du médecin]
"""
        return rapport

    def generer_pdf(self, patient_id: str, donnees: Dict) -> str:
        """Génération PDF avec mise en page améliorée"""
        if not PDF_AVAILABLE:
            return None
        
        nom_fichier = f"CR_Patient_{patient_id}.pdf"
        chemin = os.path.join(self.repertoire, nom_fichier)
        
        doc = SimpleDocTemplate(
            chemin, 
            pagesize=A4, 
            topMargin=2*cm, 
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        story = []
        
        # Charger les données extraites pour ce patient
        donnees_extraites = self.charger_donnees_extraites(patient_id)
        
        # En-tête avec style amélioré
        story.append(Paragraph("COMPTE RENDU DE CONSULTATION", self.styles['TitrePrincipal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Informations patient dans un tableau stylé
        from reportlab.platypus import Table, TableStyle
        data_info = [
            ['Date:', datetime.now().strftime('%d/%m/%Y')],
            ['Patient ID:', str(patient_id)],
            ['Type de consultation:', "Consultation Générale"]
        ]
        
        table_info = Table(data_info, colWidths=[4*cm, 8*cm])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table_info)
        story.append(Spacer(1, 0.7*cm))
        
        # Sections avec contenu amélioré - UTILISER LES VRAIES DONNÉES
        sections = [
            ("ANTÉCÉDENTS MÉDICAUX", donnees_extraites.get('antecedents', []) or ["Pas d'antécédents particuliers mentionnés"]),
            ("EXAMEN CLINIQUE", donnees_extraites.get('explorations', []) or ["Examen clinique détaillé réalisé"]),
            ("DIAGNOSTICS", donnees_extraites.get('diagnostics', []) or ["Diagnostic en cours d'évaluation"]),
            ("TRAITEMENTS PRESCRITS", donnees_extraites.get('medicaments', []) or ["Aucun traitement médicamenteux prescrit"]),
            ("RECOMMANDATIONS ET SUIVI", [
                "Suivi médical selon l'évolution clinique",
                "Respecter strictement la posologie prescrite",
                "Revoir en consultation si aggravation des symptômes",
                "Surveillance des effets secondaires éventuels"
            ])
        ]
        
        for titre, contenu_section in sections:
            # Titre de section avec style amélioré
            story.append(Paragraph(titre, self.styles['TitreSection']))
            
            # Contenu de la section
            for item in contenu_section:
                item_clean = str(item).replace('•', '').strip()
                if item_clean:
                    story.append(Paragraph(f"• {item_clean}", self.styles['ContenuSection']))
            
            story.append(Spacer(1, 0.4*cm))
        
        # Signature avec ligne
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("_" * 50, self.styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Dr. [Nom du médecin]", self.styles['InfoPatient']))
        story.append(Paragraph("Médecin spécialiste", self.styles['Normal']))
        
        try:
            doc.build(story)
            return chemin
        except Exception as e:
            print(f"❌ Erreur PDF pour patient {patient_id}: {e}")
            return None

    def generer_compte_rendu(self, patient_id: str, notes: List[str], donnees_extraites: Dict) -> str:
        """Générer un compte rendu intégrant les vraies données"""
        
        # En-tête
        cr = f"""COMPTE RENDU DE CONSULTATION

Date: {datetime.now().strftime('%d/%m/%Y')}
Patient: {patient_id}
Type: Générale

"""
        
        # ANTÉCÉDENTS - Utiliser les vraies données
        cr += "ANTÉCÉDENTS:\n"
        if donnees_extraites.get('antecedents'):
            for atcd in donnees_extraites['antecedents'][:3]:
                cr += f"• {atcd}\n"
        else:
            cr += "• Pas d'antécédents particuliers\n"
        
        cr += "\n"
        
        # EXAMEN CLINIQUE - Utiliser les explorations
        cr += "EXAMEN CLINIQUE:\n"
        if donnees_extraites.get('explorations'):
            for expl in donnees_extraites['explorations'][:2]:
                cr += f"• Exploration: {expl}\n"
        else:
            cr += "• Examen clinique réalisé\n"
        
        cr += "\n"
        
        # DIAGNOSTICS - Utiliser les vrais diagnostics
        cr += "DIAGNOSTICS:\n"
        if donnees_extraites.get('diagnostics'):
            for diag in donnees_extraites['diagnostics'][:5]:
                cr += f"• {diag}\n"
        else:
            cr += "• Diagnostic en cours\n"
        
        cr += "\n"
        
        # TRAITEMENTS - Utiliser les vrais médicaments
        cr += "TRAITEMENTS:\n"
        if donnees_extraites.get('medicaments'):
            for med in donnees_extraites['medicaments'][:3]:
                cr += f"• Médicament prescrit: {med}\n"
        else:
            cr += "• Pas de traitement prescrit\n"
        
        cr += "\n\n"
        
        # Recommandations
        cr += """RECOMMANDATIONS:
• Suivi selon évolution
• Respecter les prescriptions
• Revoir si aggravation

Dr. [Nom du médecin]
"""
        
        return cr

    def traiter_patient(self, patient_id: str, donnees_patient: Dict) -> Dict:
        """Traiter un patient avec intégration des données extraites"""
        
        # Charger les données extraites
        donnees_extraites = self.charger_donnees_extraites(patient_id)
        
        # Sauvegarder
        fichiers = {}
        if self.format_sortie in ['txt', 'both']:
            # Générer le compte rendu avec les vraies données
            compte_rendu = self.generer_compte_rendu(
                patient_id, 
                donnees_patient.get('notes', []),
                donnees_extraites
            )
            
            fichier_txt = f"CR_Patient_{patient_id}.txt"
            chemin_txt = os.path.join(self.repertoire, fichier_txt)
            with open(chemin_txt, 'w', encoding='utf-8') as f:
                f.write(compte_rendu)
            fichiers['txt'] = chemin_txt
        
        if self.format_sortie in ['pdf', 'both']:
            chemin_pdf = self.generer_pdf(patient_id, donnees_patient)
            if chemin_pdf:
                fichiers['pdf'] = chemin_pdf
        
        return fichiers

    def executer(self, max_patients: int = None) -> Dict:
        """Exécution optimisée du pipeline"""
        print(f"🚀 Pipeline médical - Format: {self.format_sortie.upper()}")
        
        # Chargement
        donnees = self.charger_donnees()
        if not donnees.get('patients'):
            print("❌ Aucune donnée trouvée")
            return {}
        
        patients = list(donnees['patients'].keys())
        if max_patients:
            patients = patients[:max_patients]
        
        print(f"📊 Traitement de {len(patients)} patients...")
        
        # Traitement
        resultats = {}
        for i, patient_id in enumerate(patients, 1):
            donnees_patient = {
                'notes': donnees['patients'].get(patient_id, []),
                'medicaments': self._parse_medicaments(donnees.get('medicaments', {}).get(patient_id, '')),
                'diagnostics': donnees.get('diagnostics', {}).get(patient_id, [])
            }
            
            fichiers = self.traiter_patient(patient_id, donnees_patient)
            if fichiers:
                resultats[patient_id] = fichiers
            
            if i % 100 == 0:
                print(f"  ✅ {i} patients traités...")
        
        # Rapport final
        self._rapport_final(len(patients), len(resultats))
        
        print(f"✅ Terminé: {len(resultats)} rapports générés dans {self.repertoire}/")
        return resultats

    def _parse_medicaments(self, meds_str: str) -> List[str]:
        """Parser les médicaments du CSV"""
        if not meds_str or meds_str == '[]':
            return []
        try:
            import ast
            return ast.literal_eval(meds_str)
        except:
            return [meds_str] if meds_str else []

    def _rapport_final(self, total: int, generes: int):
        """Rapport final minimal"""
        rapport = f"""RAPPORT PIPELINE MÉDICAL
========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Patients traités: {generes}/{total} ({generes/total*100:.1f}%)
Format: {self.format_sortie.upper()}
Dossier: {self.repertoire}/
"""
        with open(os.path.join(self.repertoire, "rapport_final.txt"), 'w', encoding='utf-8') as f:
            f.write(rapport)

def main():
    """Interface utilisateur pour choisir le format"""
    print("🏥 PIPELINE MÉDICAL OPTIMISÉ")
    print("=" * 40)
    
    # Choix du format
    print("\n📄 Choisissez le format de sortie:")
    print("1. TXT uniquement")
    print("2. PDF uniquement") 
    print("3. TXT + PDF (les deux)")
    
    while True:
        choix = input("\nVotre choix (1/2/3): ").strip()
        if choix in ['1', '2', '3']:
            break
        print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
    
    # Mapping des choix
    formats = {
        '1': 'txt',
        '2': 'pdf', 
        '3': 'both'
    }
    format_sortie = formats[choix]
    
    # Vérification PDF
    if format_sortie in ['pdf', 'both'] and not PDF_AVAILABLE:
        print("\n⚠️ ATTENTION: reportlab non installé!")
        print("📦 Installez avec: pip install reportlab")
        if format_sortie == 'pdf':
            print("🔄 Basculement vers format TXT")
            format_sortie = 'txt'
        else:
            print("🔄 Génération TXT uniquement")
            format_sortie = 'txt'
    
    # Confirmation
    format_names = {'txt': 'TXT', 'pdf': 'PDF', 'both': 'TXT + PDF'}
    print(f"\n✅ Format sélectionné: {format_names[format_sortie]}")
    
    # Lancement du pipeline
    print(f"\n🚀 Démarrage du pipeline médical...")
    pipeline = PipelineMedical(format_sortie)
    resultats = pipeline.executer()
    
    print(f"\n🎉 Pipeline terminé avec succès!")
    print(f"📊 {len(resultats)} patients traités")
    print(f"📁 Rapports disponibles dans: {pipeline.repertoire}/")

if __name__ == "__main__":
    main()
