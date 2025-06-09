#!/usr/bin/env python3
"""
Lanceur pour l'interface web de SophIA
"""

import sys
import os

# Configuration des imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Lance l'interface web"""
    
    print("🌐 Lancement de l'interface web SophIA...")
    
    try:
        from sophia.ui.web_interface import run_web_interface
        
        # Lance le serveur
        run_web_interface(
            host='localhost',
            port=5000,
            debug=True  # Mode développement
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Installez les dépendances: pip install flask flask-socketio")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    main()