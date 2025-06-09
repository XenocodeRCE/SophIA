"""
Interface ligne de commande pour SophIA
Conversation interactive avec le système hybride
"""

import sys
import os
from typing import Optional, List
import readline  # Pour l'historique de commandes
from datetime import datetime

# Configuration du path pour l'import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports absolus
from sophia.core.sophia_hybrid import HybridSophIA
from sophia.storage.session import TrainingSession
from sophia.storage.serializer import LCMSerializer

class SophIACLI:
    """Interface en ligne de commande pour SophIA"""
    
    def __init__(self):
        self.sophia: Optional[HybridSophIA] = None
        self.current_session = None
        self.conversation_active = False
        
        # Configuration de l'interface
        self.commands = {
            'help': self.show_help,
            'start': self.start_conversation,
            'load': self.load_session,
            'save': self.save_session,
            'history': self.show_conversation_history,
            'explain': self.explain_last_reasoning,
            'stats': self.show_system_stats,
            'sessions': self.list_sessions,
            'clear': self.clear_screen,
            'debug': self.toggle_debug,
            'quit': self.quit_application
        }
        
        self.debug_mode = False
        self.welcome_shown = False
    
    def run(self):
        """Lance l'interface principale"""
        
        if not self.welcome_shown:
            self.show_welcome()
            self.welcome_shown = True
        
        while True:
            try:
                if self.conversation_active and self.sophia:
                    # Mode conversation
                    user_input = input("\n🤔 Vous: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Au revoir ! Session sauvegardée automatiquement.")
                        if self.sophia:
                            self.save_session()
                        break
                    elif user_input.startswith('/'):
                        # Commande pendant la conversation
                        self.handle_command(user_input[1:])
                    elif user_input:
                        # Question philosophique
                        self.handle_philosophical_question(user_input)
                
                else:
                    # Mode commande
                    user_input = input("\nSophIA> ").strip()
                    
                    if user_input.lower() in ['quit', 'exit']:
                        print("👋 Au revoir !")
                        break
                    elif user_input:
                        self.handle_command(user_input)
            
            except KeyboardInterrupt:
                print("\n\n🛑 Interruption détectée. Tapez 'quit' pour quitter proprement.")
            except Exception as e:
                print(f"❌ Erreur: {e}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()
    
    def show_welcome(self):
        """Affiche le message de bienvenue"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🧠 SophIA - Système d'Intelligence Artificielle Philosophique 🧠          ║
║                                                                              ║
║    Version Hybride : LCM (Raisonnement) + LLaMA (Expression)               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Bienvenue ! SophIA combine :
   • Raisonnement conceptuel structuré (LCM)
   • Génération naturelle intelligente (LLaMA 3.1)
   • Apprentissage continu en temps réel

📝 Commandes disponibles :
   start          - Commencer une nouvelle conversation
   load <session> - Charger une session existante
   help           - Afficher l'aide complète
   
💡 Pendant une conversation, utilisez /commande pour les actions spéciales
""")
    
    def handle_command(self, command_input: str):
        """Traite une commande utilisateur"""
        
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](*args)
            except TypeError as e:
                print(f"❌ Erreur de commande: {e}")
                print(f"💡 Utilisez 'help {command}' pour plus d'informations")
        else:
            print(f"❓ Commande inconnue: {command}")
            print("💡 Tapez 'help' pour voir toutes les commandes")
    
    def start_conversation(self, session_name: Optional[str] = None):
        """Démarre une nouvelle conversation"""
        
        if not session_name:
            session_name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🚀 Initialisation de SophIA (session: {session_name})...")
        
        try:
            self.sophia = HybridSophIA(session_name=session_name, auto_save=True)
            self.current_session = session_name
            self.conversation_active = True
            
            # Affichage du statut système
            llm_info = self.sophia.llm.get_model_info()
            print(f"✅ SophIA initialisée !")
            print(f"   📚 Ontologie: {len(self.sophia.ontology.concepts)} concepts")
            print(f"   🧠 LCM: {len(self.sophia.lcm_model.transitions)} transitions")
            print(f"   🤖 LLaMA: {llm_info['model_name']} ({llm_info['status']})")
            
            print(f"""
┌────────────────────────────────────────────────────────────────────────────────┐
│  💬 Conversation avec SophIA activée !                                        │
│                                                                                │
│  Posez vos questions philosophiques directement.                              │
│  Commandes spéciales : /help /explain /stats /save /quit                      │
└────────────────────────────────────────────────────────────────────────────────┘
""")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def handle_philosophical_question(self, question: str):
        """Traite une question philosophique"""
        
        if not self.sophia:
            print("❌ SophIA n'est pas initialisée. Utilisez 'start' d'abord.")
            return
        
        print("🤖 SophIA réfléchit...")
        
        try:
            # Génération de la réponse
            response = self.sophia.ask(question)
            
            # Affichage de la réponse
            print(f"\n🧠 SophIA: {response.natural_response}")
            
            # Informations de débogage si activé
            if self.debug_mode:
                self.show_debug_info(response)
            else:
                # Informations minimales
                concepts = response.conceptual_analysis.get('concepts_detected', [])
                confidence = response.conceptual_analysis.get('confidence', 0)
                learning = response.metadata.get('learning_triggered', False)
                
                info_parts = []
                if concepts:
                    info_parts.append(f"📝 Concepts: {', '.join(concepts[:3])}")
                info_parts.append(f"🎯 Confiance: {confidence:.0%}")
                if learning:
                    info_parts.append("🧩 Apprentissage activé")
                
                if info_parts:
                    print(f"\n💡 {' | '.join(info_parts)}")
        
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def show_debug_info(self, response):
        """Affiche les informations de débogage détaillées"""
        
        print("\n" + "="*80)
        print("🔍 INFORMATIONS DE DÉBOGAGE")
        print("="*80)
        
        analysis = response.conceptual_analysis
        
        print(f"Concepts détectés: {analysis.get('concepts_detected', [])}")
        print(f"Confiance: {analysis.get('confidence', 0):.2f}")
        print(f"Relations détectées: {len(analysis.get('relations_implied', []))}")
        
        # Chemins conceptuels
        paths = analysis.get('conceptual_paths', [])
        if paths:
            print("\nChemins de raisonnement:")
            for i, path in enumerate(paths, 1):
                path_str = " → ".join(path['reasoning_path'])
                prob = path['path_probability']
                print(f"  {i}. {path_str} (prob: {prob:.3f})")
        
        # Métadonnées
        metadata = response.metadata
        print(f"\nApprentissage déclenché: {metadata.get('learning_triggered', False)}")
        print(f"Méthode de raisonnement: {metadata.get('reasoning_method', 'unknown')}")
        
        print("="*80)
    
    def load_session(self, session_name: str = None):
        """Charge une session existante"""
        
        if not session_name:
            print("❌ Nom de session requis. Usage: load <nom_session>")
            return
        
        print(f"📂 Chargement de la session '{session_name}'...")
        
        try:
            self.sophia = HybridSophIA(session_name="temp")  # Initialisation temporaire
            
            if self.sophia.load_session(session_name):
                self.current_session = session_name
                self.conversation_active = True
                
                print(f"✅ Session '{session_name}' chargée avec succès !")
                
                # Affichage des stats de la session
                summary = self.sophia.get_conversation_summary()
                if summary.get('total_interactions', 0) > 0:
                    print(f"   💬 Interactions précédentes: {summary['total_interactions']}")
                    print(f"   🧠 Confiance moyenne: {summary['average_confidence']:.0%}")
                
                print("💬 Vous pouvez continuer la conversation.")
            else:
                print(f"❌ Impossible de charger la session '{session_name}'")
        
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
    
    def save_session(self, notes: str = ""):
        """Sauvegarde la session actuelle"""
        
        if not self.sophia:
            print("❌ Aucune session active à sauvegarder")
            return
        
        try:
            save_path = self.sophia.save_session(" ".join(notes) if notes else "Sauvegarde manuelle")
            print(f"💾 Session sauvegardée: {save_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def show_conversation_history(self):
        """Affiche l'historique de la conversation"""
        
        if not self.sophia or not self.sophia.conversation_history:
            print("📝 Aucune conversation en cours")
            return
        
        print("\n📚 HISTORIQUE DE LA CONVERSATION")
        print("="*50)
        
        for i, response in enumerate(self.sophia.conversation_history, 1):
            concepts = response.conceptual_analysis.get('concepts_detected', [])
            concepts_str = ', '.join(concepts[:2]) if concepts else 'aucun'
            
            print(f"\n{i}. Q: {response.question}")
            print(f"   Concepts: {concepts_str}")
            print(f"   R: {response.natural_response[:100]}...")
        
        print(f"\n📊 Total: {len(self.sophia.conversation_history)} interactions")
    
    def explain_last_reasoning(self):
        """Explique le raisonnement de la dernière réponse"""
        
        if not self.sophia or not self.sophia.conversation_history:
            print("❌ Aucune interaction à expliquer")
            return
        
        last_response = self.sophia.conversation_history[-1]
        question = last_response.question
        
        print(f"\n🔍 EXPLICATION DU RAISONNEMENT pour: '{question}'")
        print("="*60)
        
        explanation = self.sophia.explain_reasoning(question)
        
        # Étape 1: Détection de concepts
        step1 = explanation['step1_concept_detection']
        print(f"\n1️⃣ DÉTECTION DE CONCEPTS ({step1['method']})")
        print(f"   Concepts trouvés: {step1['concepts_found']}")
        print(f"   Confiance: {step1['confidence']:.0%}")
        
        # Étape 2: Raisonnement conceptuel
        step2 = explanation['step2_conceptual_reasoning']
        print(f"\n2️⃣ RAISONNEMENT CONCEPTUEL ({step2['method']})")
        paths = step2['reasoning_paths']
        if paths:
            for i, path in enumerate(paths, 1):
                path_str = " → ".join(path['reasoning_path'])
                print(f"   Chemin {i}: {path_str}")
        else:
            print("   Aucun chemin conceptuel généré")
        
        # Étape 3: Relations ontologiques
        step3 = explanation['step3_ontological_relations']
        relations = step3['detected_relations']
        print(f"\n3️⃣ RELATIONS ONTOLOGIQUES")
        if relations:
            for relation in relations:
                print(f"   {relation['from']} {relation['relation']} {relation['to']}")
        else:
            print("   Aucune relation détectée")
        
        # Étape 4: Synthèse
        step4 = explanation['step4_synthesis']
        print(f"\n4️⃣ SYNTHÈSE")
        print(f"   {step4['how_response_built']}")
    
    def show_system_stats(self):
        """Affiche les statistiques du système"""
        
        if not self.sophia:
            print("❌ SophIA n'est pas initialisée")
            return
        
        print("\n📊 STATISTIQUES SYSTÈME")
        print("="*40)
        
        # Stats ontologie
        ontology_stats = self.sophia.ontology.get_stats()
        print(f"\n🏛️ ONTOLOGIE")
        print(f"   Concepts totaux: {ontology_stats['total_concepts']}")
        print(f"   Relations totales: {ontology_stats['total_relations']}")
        print(f"   Concept le + connecté: {ontology_stats['most_connected'][0]} ({ontology_stats['most_connected'][1]} liens)")
        
        # Stats LCM
        lcm_stats = self.sophia.lcm_model.get_model_stats()
        print(f"\n🧠 MODÈLE LCM")
        print(f"   Transitions apprises: {lcm_stats['total_transitions']}")
        print(f"   Couverture: {lcm_stats['coverage_ratio']:.0%}")
        print(f"   Séquences vues: {lcm_stats['total_sequences_seen']}")
        
        # Stats LLaMA
        llm_info = self.sophia.llm.get_model_info()
        print(f"\n🤖 LLaMA")
        print(f"   Modèle: {llm_info['model_name']}")
        print(f"   Statut: {llm_info['status']}")
        
        # Stats conversation
        if self.sophia.conversation_history:
            conv_summary = self.sophia.get_conversation_summary()
            print(f"\n💬 CONVERSATION ACTUELLE")
            print(f"   Interactions: {conv_summary['total_interactions']}")
            print(f"   Confiance moyenne: {conv_summary['average_confidence']:.0%}")
            print(f"   Apprentissages: {conv_summary['learning_events']}")
    
    def list_sessions(self):
        """Liste toutes les sessions sauvegardées"""
        
        try:
            serializer = LCMSerializer()
            models = serializer.list_saved_models()
            
            if not models:
                print("📁 Aucune session sauvegardée")
                return
            
            print("\n📁 SESSIONS SAUVEGARDÉES")
            print("="*50)
            
            for model in models[:10]:  # Limite à 10 sessions
                name = model['model_name']
                timestamp = model['timestamp'][:19]  # Format: YYYY-MM-DD HH:MM:SS
                size = model['size_mb']
                stats = model.get('stats', {})
                
                print(f"\n📄 {name}")
                print(f"   Date: {timestamp}")
                print(f"   Taille: {size:.1f} MB")
                if stats:
                    print(f"   Concepts: {stats.get('concepts_count', '?')}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la lecture des sessions: {e}")
    
    def clear_screen(self):
        """Efface l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def toggle_debug(self):
        """Active/désactive le mode debug"""
        self.debug_mode = not self.debug_mode
        status = "activé" if self.debug_mode else "désactivé"
        print(f"🔧 Mode debug {status}")
    
    def show_help(self, command: str = None):
        """Affiche l'aide"""
        
        if command:
            # Aide spécifique à une commande
            help_texts = {
                'start': "Démarre une nouvelle conversation. Usage: start [nom_session]",
                'load': "Charge une session existante. Usage: load <nom_session>",
                'save': "Sauvegarde la session actuelle. Usage: save [notes]",
                'history': "Affiche l'historique de la conversation",
                'explain': "Explique le raisonnement de la dernière réponse",
                'stats': "Affiche les statistiques du système",
                'sessions': "Liste toutes les sessions sauvegardées",
                'debug': "Active/désactive le mode debug",
                'clear': "Efface l'écran",
                'quit': "Quitte l'application"
            }
            
            if command in help_texts:
                print(f"💡 {command}: {help_texts[command]}")
            else:
                print(f"❓ Commande inconnue: {command}")
        else:
            # Aide générale
            print("""
📚 AIDE SOPHIA - COMMANDES DISPONIBLES

🚀 GESTION DE SESSION
   start [session]     - Nouvelle conversation
   load <session>      - Charger session existante
   save [notes]        - Sauvegarder session
   sessions           - Lister sessions

💬 CONVERSATION
   [question]         - Poser une question philosophique
   /explain          - Expliquer le dernier raisonnement
   /history          - Voir l'historique
   /stats            - Statistiques système

🔧 UTILITAIRES
   debug             - Mode debug on/off
   clear             - Effacer l'écran
   help [commande]   - Aide détaillée
   quit              - Quitter

💡 Pendant une conversation, préfixez les commandes par /
   Exemple: /explain, /stats, /save
""")
    
    def quit_application(self):
        """Quitte l'application proprement"""
        
        if self.sophia and self.conversation_active:
            print("💾 Sauvegarde automatique...")
            try:
                self.save_session("Session fermée automatiquement")
            except:
                pass
        
        print("👋 Au revoir ! Merci d'avoir utilisé SophIA.")
        sys.exit(0)

def main():
    """Point d'entrée principal"""
    
    try:
        cli = SophIACLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir !")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()