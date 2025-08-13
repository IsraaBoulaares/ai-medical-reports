"""
Script d'installation des dépendances pour le pipeline médical
"""

import subprocess
import sys

def installer_dependances():
    """Installer les dépendances nécessaires"""
    dependances = [
        "pandas",
        "reportlab",
        "openpyxl"
    ]
    
    print("🔧 Installation des dépendances...")
    
    for dep in dependances:
        try:
            print(f"📦 Installation de {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installé avec succès")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur lors de l'installation de {dep}")
    
    print("\n✅ Installation terminée!")
    print("🚀 Vous pouvez maintenant lancer le pipeline avec:")
    print("python pipeline_complet_final.py")

if __name__ == "__main__":
    installer_dependances()
