#!/usr/bin/env python3
"""
🧠 SophIA CLI 🧠
Interface complète pour le système d'IA philosophique hybride
"""

import sys
import os
import json
import time
import pickle
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

# Setup du path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Imports SophIA
from sophia.core.sophia_hybrid import HybridSophIA
from sophia.storage.session import TrainingSession
from sophia.storage.serializer import LCMSerializer
from sophia.training.trainer import SimpleLCMTrainer
from sophia.core.ontology import SimpleOntology, Concept
from sophia.core.concept_types import ConceptType, RelationType

class SophIACLIUltimate:
    """Interface CLI ultime pour SophIA"""
    
    def __init__(self):
        self.sophia = None
        self.session = None
        self.verbose = True
        self.auto_save = True
        self.config = {
            'max_response_length': 500,
            'confidence_threshold': 0.5,
            'auto_learn': True,
            'save_frequency': 10,
            'visualization_enabled': True,
            'debug_mode': False
        }
        self.stats = {
            'questions_posed': 0,
            'concepts_learned': 0,
            'relations_added': 0,
            'session_start': None,
            'training_sessions': 0,
            'avg_response_time': 0.0,
            'total_concepts_used': set()
        }
    
    def show_banner(self):
        """Affiche le banner SophIA"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       🧠 SophIA CLI 🧠                             ║
║                    Intelligence Artificielle Philosophique                  ║
║                        Système Hybride LCM + LLaMA                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Fonctionnalités disponibles:
   💬 Chat philosophique intelligent        🧠 Entraînement du modèle
   📊 Analyse des performances              🔍 Exploration de l'ontologie  
   💾 Gestion des sessions                  ⚙️ Configuration système
   📈 Statistiques détaillées              🔬 Mode laboratoire
""")
    
    def show_menu(self):
        """Affiche le menu principal"""
        print("""
╔═══════════════════ MENU PRINCIPAL ═══════════════════╗
║                                                       ║
║  1️⃣  💬 Chat Philosophique (Mode Verbose)            ║
║  2️⃣  🧠 Entraînement du Modèle                       ║
║  3️⃣  📊 Analyse & Statistiques                       ║
║  4️⃣  🔍 Explorer l'Ontologie                         ║
║  5️⃣  💾 Gestion des Sessions                         ║
║  6️⃣  ⚙️  Configuration Système                       ║
║  7️⃣  🔬 Mode Laboratoire                             ║
║  8️⃣  📈 Benchmarks & Tests                           ║
║  9️⃣  🎓 Entraînement Conversationnel                 ║
║  🔟  📚 Import/Export Connaissances                   ║
║                                                       ║
║  0️⃣  🚪 Quitter                                      ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
""")
    
    def init_sophia(self, session_name: str = None) -> bool:
        """Initialise SophIA avec verbose complet"""
        
        if session_name is None:
            session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            print("🚀 INITIALISATION SOPHIA")
            print("=" * 50)
            
            print("1️⃣ Chargement de l'ontologie...")
            start_time = time.time()
            
            self.sophia = HybridSophIA(session_name=session_name, auto_save=self.auto_save)
            
            load_time = time.time() - start_time
            
            # Stats détaillées
            ontology_stats = self.sophia.ontology.get_stats()
            model_info = self.sophia.llm.get_model_info()
            
            print(f"   ✅ Ontologie chargée en {load_time:.2f}s")
            print(f"   📚 {ontology_stats['total_concepts']} concepts")
            print(f"   🔗 {ontology_stats['total_relations']} relations")
            print(f"   🧠 LCM: {len(self.sophia.lcm_model.transitions)} transitions")
            print(f"   🤖 LLaMA: {model_info['model_name']} ({model_info['status']})")
            
            self.stats['session_start'] = datetime.now()
            
            print("✅ SophIA initialisée avec succès !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def chat_mode(self):
        """Mode chat avec verbose complet"""
        
        if not self.sophia:
            print("⚠️ SophIA non initialisée. Initialisation...")
            if not self.init_sophia():
                return
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        💬 CHAT PHILOSOPHIQUE VERBOSE                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Mode verbose activé - tous les processus internes seront affichés
💡 Commandes spéciales:
   • '/stats' - Afficher les statistiques
   • '/save' - Sauvegarder la session
   • '/concepts' - Lister les concepts actifs
   • '/clear' - Effacer l'historique
   • '/quit' - Retour au menu

Posez votre question philosophique:
""")
        
        while True:
            try:
                question = input("🤔 Vous: ").strip()
                
                # Commandes spéciales
                if question.lower() in ['/quit', '/exit', '/menu']:
                    break
                elif question.lower() == '/stats':
                    self.show_chat_stats()
                    continue
                elif question.lower() == '/save':
                    self.manual_save()
                    continue
                elif question.lower() == '/concepts':
                    self.show_active_concepts()
                    continue
                elif question.lower() == '/clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif not question:
                    continue
                
                # Traitement verbose de la question
                self.process_question_verbose(question)
                self.stats['questions_posed'] += 1
                
            except KeyboardInterrupt:
                print("\n👋 Retour au menu principal...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
    
    def process_question_verbose(self, question: str):
        """Traite une question avec affichage verbose complet"""
        
        print(f"\n🔍 ANALYSE VERBOSE: {question}")
        print("=" * 60)
        
        # Phase 1: Pré-analyse
        start_time = time.time()
        print("📋 Phase 1: Analyse conceptuelle...")
        
        # Extraction directe pour verbose
        concepts_available = list(self.sophia.ontology.concepts.keys())
        extraction = self.sophia.llm.extract_concepts_from_text(question, concepts_available)
        
        print(f"   🎯 Concepts détectés: {extraction['concepts_detected']}")
        print(f"   🔗 Relations: {len(extraction['relations_implied'])}")
        print(f"   ✅ Confiance: {extraction['confidence']:.0%}")
        
        # Phase 2: Raisonnement LCM
        print("\n🧠 Phase 2: Raisonnement conceptuel...")
        initial_transitions = len(self.sophia.lcm_model.transitions)
        
        # Phase 3: Génération
        print("\n🤖 Phase 3: Génération de la réponse...")
        response = self.sophia.ask(question)
        
        generation_time = time.time() - start_time
        
        # Phase 4: Post-analyse
        print(f"\n📊 Phase 4: Résultats (temps: {generation_time:.2f}s)")
        final_transitions = len(self.sophia.lcm_model.transitions)
        
        print(f"   📈 Nouvelles transitions: +{final_transitions - initial_transitions}")
        print(f"   📏 Longueur réponse: {len(response.natural_response)} caractères")
        print(f"   🎯 Concepts utilisés: {len(response.conceptual_analysis['concepts_detected'])}")
        
        # Affichage de la réponse
        print(f"\n🧠 SophIA: {response.natural_response}")
        
        # Méta-informations
        if response.conceptual_analysis['concepts_detected']:
            concepts_str = ', '.join(response.conceptual_analysis['concepts_detected'][:5])
            print(f"\n💡 Concepts: {concepts_str} | Confiance: {response.conceptual_analysis['confidence']:.0%}")
        
        print("-" * 60)
    
    def training_mode(self):
        """Mode entraînement verbose"""
        
        if not self.sophia:
            if not self.init_sophia():
                return
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🧠 ENTRAÎNEMENT DU MODÈLE                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Options d'entraînement:
   1️⃣ Entraînement conversationnel (questions-réponses)
   2️⃣ Entraînement sur corpus philosophique
   3️⃣ Entraînement par séquences conceptuelles
   4️⃣ Entraînement interactif guidé
   5️⃣ Benchmark des performances
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.conversational_training()
        elif choice == '2':
            self.corpus_training()
        elif choice == '3':
            self.conceptual_training()
        elif choice == '4':
            self.guided_training()
        elif choice == '5':
            self.performance_benchmark()
        elif choice == '0':
            return
    
    def conversational_training(self):
        """Entraînement conversationnel verbose"""
        
        print("\n🎓 ENTRAÎNEMENT CONVERSATIONNEL")
        print("=" * 40)
        print("Posez des questions pour entraîner SophIA. Tapez '/done' pour terminer.")
        
        training_questions = []
        
        while True:
            question = input("\n📚 Question d'entraînement: ").strip()
            
            if question.lower() in ['/done', '/finish']:
                break
            
            if not question:
                continue
            
            print("🔄 Traitement et apprentissage...")
            
            # Traitement avec apprentissage forcé
            response = self.sophia.ask(question)
            training_questions.append({
                'question': question,
                'concepts_detected': response.conceptual_analysis['concepts_detected'],
                'confidence': response.conceptual_analysis['confidence']
            })
            
            print(f"✅ Appris! Concepts: {', '.join(response.conceptual_analysis['concepts_detected'][:3])}")
        
        # Résumé de l'entraînement
        print(f"\n📊 RÉSUMÉ DE L'ENTRAÎNEMENT:")
        print(f"   📚 Questions traitées: {len(training_questions)}")
        print(f"   🧠 Transitions LCM: {len(self.sophia.lcm_model.transitions)}")
        
        unique_concepts = set()
        for tq in training_questions:
            unique_concepts.update(tq['concepts_detected'])
        
        print(f"   🎯 Concepts uniques activés: {len(unique_concepts)}")
        print(f"   ✅ Confiance moyenne: {sum(tq['confidence'] for tq in training_questions) / len(training_questions):.0%}")
    
    def ontology_explorer(self):
        """Explorateur d'ontologie interactif"""
        
        if not self.sophia:
            if not self.init_sophia():
                return
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🔍 EXPLORATEUR D'ONTOLOGIE                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        while True:
            print("""
🎯 Options d'exploration:
   1️⃣ Lister tous les concepts
   2️⃣ Explorer un concept spécifique  
   3️⃣ Visualiser les relations
   4️⃣ Ajouter un nouveau concept
   5️⃣ Statistiques de l'ontologie
   6️⃣ Graphe des connexions
   0️⃣ Retour au menu
""")
            
            choice = input("Choix: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.list_all_concepts()
            elif choice == '2':
                self.explore_concept()
            elif choice == '3':
                self.show_relations()
            elif choice == '4':
                self.add_concept_interactive()
            elif choice == '5':
                self.ontology_stats()
            elif choice == '6':
                self.concept_graph()
    
    def list_all_concepts(self):
        """Liste tous les concepts avec détails"""
        
        concepts = self.sophia.ontology.concepts
        
        print(f"\n📚 TOUS LES CONCEPTS ({len(concepts)})")
        print("=" * 50)
        
        by_type = {}
        for name, concept in concepts.items():
            concept_type = concept.concept_type.value
            if concept_type not in by_type:
                by_type[concept_type] = []
            by_type[concept_type].append(name)
        
        for concept_type, concept_list in by_type.items():
            print(f"\n🏷️ {concept_type.upper()} ({len(concept_list)}):")
            for i, concept_name in enumerate(sorted(concept_list), 1):
                # Compte les relations pour ce concept
                relations_count = len(self.sophia.ontology.get_concept_relations(concept_name))
                print(f"   {i:2d}. {concept_name} ({relations_count} relations)")
    
    def explore_concept(self):
        """Explore un concept spécifique en détail"""
        
        concept_name = input("\n🔍 Nom du concept à explorer: ").strip().upper()
        
        if concept_name not in self.sophia.ontology.concepts:
            print(f"❌ Concept '{concept_name}' introuvable.")
            return
        
        concept = self.sophia.ontology.concepts[concept_name]
        relations = self.sophia.ontology.get_concept_relations(concept_name)
        
        print(f"\n🎯 EXPLORATION: {concept_name}")
        print("=" * 40)
        print(f"📋 Type: {concept.concept_type.value}")
        print(f"📝 Description: {concept.description}")
        print(f"🔗 Relations: {len(relations)}")
        
        if relations:
            print("\n🌐 Relations détaillées:")
            for rel in relations:
                print(f"   • {rel['from']} --{rel['relation'].value}--> {rel['to']}")
        
        # Transitions LCM
        if concept_name in self.sophia.lcm_model.concept_to_index:
            concept_idx = self.sophia.lcm_model.concept_to_index[concept_name]
            transitions_from = []
            transitions_to = []
            
            for (from_idx, to_idx), transition in self.sophia.lcm_model.transitions.items():
                if from_idx == concept_idx:
                    to_concept = self.sophia.lcm_model.index_to_concept[to_idx]
                    transitions_from.append(f"{to_concept} ({transition.weight:.3f})")
                elif to_idx == concept_idx:
                    from_concept = self.sophia.lcm_model.index_to_concept[from_idx]
                    transitions_to.append(f"{from_concept} ({transition.weight:.3f})")
            
            print(f"\n🧠 Transitions LCM:")
            print(f"   Vers: {', '.join(transitions_from[:5]) if transitions_from else 'Aucune'}")
            print(f"   Depuis: {', '.join(transitions_to[:5]) if transitions_to else 'Aucune'}")
    
    def performance_benchmark(self):
        """Benchmark des performances"""
        
        if not self.sophia:
            if not self.init_sophia():
                return
        
        print("\n⚡ BENCHMARK DES PERFORMANCES")
        print("=" * 40)
        
        test_questions = [
            "Qu'est-ce que la vérité ?",
            "Peut-on être libre et déterminé ?",
            "La justice est-elle subjective ?",
            "Comment définir l'authenticité ?",
            "Le doute mène-t-il à la certitude ?"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🧪 Test {i}/{len(test_questions)}: {question}")
            
            start_time = time.time()
            response = self.sophia.ask(question)
            end_time = time.time()
            
            result = {
                'question': question,
                'response_time': end_time - start_time,
                'response_length': len(response.natural_response),
                'concepts_detected': len(response.conceptual_analysis['concepts_detected']),
                'confidence': response.conceptual_analysis['confidence']
            }
            
            results.append(result)
            
            print(f"   ⏱️ Temps: {result['response_time']:.2f}s")
            print(f"   📏 Longueur: {result['response_length']} chars")
            print(f"   🎯 Concepts: {result['concepts_detected']}")
            print(f"   ✅ Confiance: {result['confidence']:.0%}")
        
        # Statistiques globales
        avg_time = sum(r['response_time'] for r in results) / len(results)
        avg_length = sum(r['response_length'] for r in results) / len(results)
        avg_concepts = sum(r['concepts_detected'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n📊 RÉSULTATS GLOBAUX:")
        print(f"   ⏱️ Temps moyen: {avg_time:.2f}s")
        print(f"   📏 Longueur moyenne: {avg_length:.0f} chars")
        print(f"   🎯 Concepts moyens: {avg_concepts:.1f}")
        print(f"   ✅ Confiance moyenne: {avg_confidence:.0%}")
    
    def show_chat_stats(self):
        """Affiche les statistiques de la session"""
        
        if self.stats['session_start']:
            duration = datetime.now() - self.stats['session_start']
            duration_str = str(duration).split('.')[0]  # Enlève les microsecondes
        else:
            duration_str = "N/A"
        
        print(f"""
📊 STATISTIQUES DE LA SESSION:
   ⏰ Durée: {duration_str}
   💬 Questions posées: {self.stats['questions_posed']}
   🧠 Transitions LCM: {len(self.sophia.lcm_model.transitions) if self.sophia else 0}
   🔗 Relations ontologiques: {self.sophia.ontology.get_stats()['total_relations'] if self.sophia else 0}
""")
    
    def manual_save(self):
        """Sauvegarde manuelle"""
        
        if not self.sophia:
            print("❌ Aucune session SophIA active")
            return
        
        try:
            serializer = LCMSerializer()
            
            # Sauvegarde complète
            session_data = {
                'ontology': self.sophia.ontology,
                'lcm_model': self.sophia.lcm_model,
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            serializer.save_session(session_data, filename)
            
            print(f"💾 Session sauvegardée: {filename}")
            
        except Exception as e:
            print(f"❌ Erreur de sauvegarde: {e}")
    
    def run(self):
        """Boucle principale du CLI"""
        
        self.show_banner()
        
        while True:
            try:
                self.show_menu()
                choice = input("🎯 Votre choix: ").strip()
                
                if choice == '0':
                    print("👋 Au revoir ! Merci d'avoir utilisé SophIA Ultimate !")
                    if self.sophia and self.auto_save:
                        print("💾 Sauvegarde automatique...")
                        self.manual_save()
                    break
                
                elif choice == '1':
                    self.chat_mode()
                elif choice == '2':
                    self.training_mode()
                elif choice == '3':
                    self.analytics_mode()
                elif choice == '4':
                    self.ontology_explorer()
                elif choice == '5':
                    self.session_manager()
                elif choice == '6':
                    self.configuration_mode()
                elif choice == '7':
                    self.laboratory_mode()
                elif choice == '8':
                    self.performance_benchmark()
                elif choice == '9':
                    self.conversational_training()
                elif choice == '10':
                    self.import_export_mode()
                else:
                    print("❌ Choix invalide, veuillez réessayer.")
                
                input("\n⏸️ Appuyez sur Entrée pour continuer...")
                
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
    
    # Méthodes stubs pour les autres fonctionnalités
    def analytics_mode(self):
        print("📊 Mode analytique - En développement...")
    
    def session_manager(self):
        print("💾 Gestionnaire de sessions - En développement...")
    
    def configuration_mode(self):
        print("⚙️ Configuration système - En développement...")
    
    def laboratory_mode(self):
        print("🔬 Mode laboratoire - En développement...")
    
    def import_export_mode(self):
        print("📚 Import/Export - En développement...")
    
    def concept_graph(self):
        """Génère et affiche un graphique des connexions conceptuelles"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        print("\n🌐 GRAPHIQUE DES CONNEXIONS CONCEPTUELLES")
        print("=" * 50)
        
        try:
            # Création du graphe NetworkX
            G = nx.Graph()
            
            # Ajout des concepts comme nœuds
            concepts = list(self.sophia.ontology.concepts.keys())
            for concept in concepts:
                concept_obj = self.sophia.ontology.concepts[concept]
                G.add_node(concept, type=concept_obj.concept_type.value)
            
            # Ajout des relations comme arêtes
            relations = []
            for concept_name in concepts:
                concept_relations = self.sophia.ontology.get_concept_relations(concept_name)
                for rel in concept_relations:
                    G.add_edge(rel['from'], rel['to'], relation=rel['relation'].value)
                    relations.append(rel)
            
            print(f"📊 Graphique généré:")
            print(f"   🎯 Nœuds (concepts): {G.number_of_nodes()}")
            print(f"   🔗 Arêtes (relations): {G.number_of_edges()}")
            print(f"   🌐 Composants connexes: {nx.number_connected_components(G)}")
            
            # Analyse topologique
            if G.number_of_nodes() > 0:
                centrality = nx.degree_centrality(G)
                most_central = max(centrality, key=centrality.get)
                print(f"   ⭐ Concept le plus central: {most_central} ({centrality[most_central]:.3f})")
                
                # Densité du graphe
                density = nx.density(G)
                print(f"   📈 Densité du graphe: {density:.3f}")
            
            # Visualisation si possible
            if self.config['visualization_enabled']:
                try:
                    plt.figure(figsize=(12, 8))
                    pos = nx.spring_layout(G, k=1, iterations=50)
                    
                    # Couleurs par type de concept
                    color_map = {
                        'FUNDAMENTAL': 'red',
                        'VIRTUE': 'green', 
                        'EMOTION': 'blue',
                        'ACTION': 'orange',
                        'ABSTRACT': 'purple',
                        'RELATION': 'pink'
                    }
                    
                    node_colors = []
                    for node in G.nodes():
                        node_type = G.nodes[node].get('type', 'ABSTRACT')
                        node_colors.append(color_map.get(node_type, 'gray'))
                    
                    # Dessin du graphe
                    nx.draw(G, pos, node_color=node_colors, with_labels=True, 
                           node_size=1000, font_size=8, font_weight='bold',
                           edge_color='gray', alpha=0.7)
                    
                    plt.title("Graphe des Concepts Philosophiques SophIA", fontsize=14, fontweight='bold')
                    plt.axis('off')
                    
                    # Sauvegarde
                    filename = f"sophia_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"   💾 Graphique sauvegardé: {filename}")
                    
                    plt.show()
                    
                except ImportError:
                    print("   ⚠️ Matplotlib non disponible pour la visualisation")
                except Exception as e:
                    print(f"   ❌ Erreur de visualisation: {e}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la génération du graphique: {e}")
    
    def analytics_mode(self):
        """Mode analytique complet avec statistiques avancées"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           📊 MODE ANALYTIQUE AVANCÉ                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Analyses disponibles:
   1️⃣ Statistiques détaillées de l'ontologie
   2️⃣ Analyse des performances LCM
   3️⃣ Distribution des types de concepts
   4️⃣ Métriques de connectivité
   5️⃣ Analyse temporelle des apprentissages
   6️⃣ Rapport de performance globale
   7️⃣ Export des métriques (JSON/CSV)
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.detailed_ontology_stats()
        elif choice == '2':
            self.lcm_performance_analysis()
        elif choice == '3':
            self.concept_distribution_analysis()
        elif choice == '4':
            self.connectivity_metrics()
        elif choice == '5':
            self.temporal_learning_analysis()
        elif choice == '6':
            self.global_performance_report()
        elif choice == '7':
            self.export_metrics()
    
    def detailed_ontology_stats(self):
        """Statistiques détaillées de l'ontologie"""
        
        print("\n📈 STATISTIQUES DÉTAILLÉES DE L'ONTOLOGIE")
        print("=" * 55)
        
        # Stats de base
        ontology_stats = self.sophia.ontology.get_stats()
        concepts = self.sophia.ontology.concepts
        
        print(f"📚 Concepts totaux: {ontology_stats['total_concepts']}")
        print(f"🔗 Relations totales: {ontology_stats['total_relations']}")
        
        # Distribution par type
        type_counts = Counter()
        for concept in concepts.values():
            type_counts[concept.concept_type.value] += 1
        
        print(f"\n🏷️ Distribution par type:")
        for concept_type, count in type_counts.most_common():
            percentage = (count / len(concepts)) * 100
            print(f"   {concept_type}: {count} ({percentage:.1f}%)")
        
        # Concepts les plus connectés
        connectivity = {}
        for concept_name in concepts.keys():
            relations = self.sophia.ontology.get_concept_relations(concept_name)
            connectivity[concept_name] = len(relations)
        
        print(f"\n🌐 Concepts les plus connectés:")
        for concept, conn_count in sorted(connectivity.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {concept}: {conn_count} connexions")
        
        # Densité relationnelle
        max_possible_relations = len(concepts) * (len(concepts) - 1) // 2
        if max_possible_relations > 0:
            density = ontology_stats['total_relations'] / max_possible_relations
            print(f"\n📊 Densité relationnelle: {density:.3f} ({density*100:.1f}%)")
    
    def lcm_performance_analysis(self):
        """Analyse des performances du modèle LCM"""
        
        print("\n🧠 ANALYSE DES PERFORMANCES LCM")
        print("=" * 40)
        
        lcm = self.sophia.lcm_model
        
        print(f"🔄 Transitions totales: {len(lcm.transitions)}")
        print(f"🎯 Concepts mappés: {len(lcm.concept_to_index)}")
        
        # Analyse des poids de transition
        if lcm.transitions:
            weights = [t.weight for t in lcm.transitions.values()]
            avg_weight = sum(weights) / len(weights)
            max_weight = max(weights)
            min_weight = min(weights)
            
            print(f"\n⚖️ Poids des transitions:")
            print(f"   Moyen: {avg_weight:.4f}")
            print(f"   Maximum: {max_weight:.4f}")
            print(f"   Minimum: {min_weight:.4f}")
            
            # Distribution des poids
            strong_transitions = sum(1 for w in weights if w > 0.5)
            weak_transitions = sum(1 for w in weights if w < 0.1)
            
            print(f"\n💪 Transitions fortes (>0.5): {strong_transitions}")
            print(f"🔸 Transitions faibles (<0.1): {weak_transitions}")
        
        # Concepts les plus actifs
        concept_activity = defaultdict(int)
        for (from_idx, to_idx) in lcm.transitions.keys():
            from_concept = lcm.index_to_concept.get(from_idx, f"Unknown_{from_idx}")
            to_concept = lcm.index_to_concept.get(to_idx, f"Unknown_{to_idx}")
            concept_activity[from_concept] += 1
            concept_activity[to_concept] += 1
        
        print(f"\n🔥 Concepts les plus actifs:")
        for concept, activity in sorted(concept_activity.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {concept}: {activity} transitions")
    
    def configuration_mode(self):
        """Mode configuration système avancé"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ⚙️ CONFIGURATION SYSTÈME                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Paramètres configurables:
   1️⃣ Paramètres de réponse
   2️⃣ Seuils d'apprentissage
   3️⃣ Options de sauvegarde
   4️⃣ Paramètres de visualisation
   5️⃣ Mode debug
   6️⃣ Configuration LLaMA
   7️⃣ Sauvegarder la configuration
   8️⃣ Charger une configuration
   9️⃣ Réinitialiser par défaut
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.configure_response_params()
        elif choice == '2':
            self.configure_learning_thresholds()
        elif choice == '3':
            self.configure_save_options()
        elif choice == '4':
            self.configure_visualization()
        elif choice == '5':
            self.toggle_debug_mode()
        elif choice == '6':
            self.configure_llama()
        elif choice == '7':
            self.save_configuration()
        elif choice == '8':
            self.load_configuration()
        elif choice == '9':
            self.reset_configuration()
    
    def configure_response_params(self):
        """Configuration des paramètres de réponse"""
        
        print(f"\n📝 PARAMÈTRES DE RÉPONSE")
        print(f"Longueur max actuelle: {self.config['max_response_length']}")
        
        new_length = input("Nouvelle longueur max (ou Entrée pour ignorer): ").strip()
        if new_length.isdigit():
            self.config['max_response_length'] = int(new_length)
            print(f"✅ Longueur max mise à jour: {new_length}")
        
        print(f"Seuil de confiance actuel: {self.config['confidence_threshold']}")
        new_threshold = input("Nouveau seuil (0.0-1.0, ou Entrée pour ignorer): ").strip()
        try:
            if new_threshold:
                threshold = float(new_threshold)
                if 0.0 <= threshold <= 1.0:
                    self.config['confidence_threshold'] = threshold
                    print(f"✅ Seuil de confiance mis à jour: {threshold}")
                else:
                    print("❌ Seuil doit être entre 0.0 et 1.0")
        except ValueError:
            print("❌ Valeur invalide pour le seuil")
    
    def laboratory_mode(self):
        """Mode laboratoire pour expérimentations"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🔬 MODE LABORATOIRE                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

🧪 Expérimentations disponibles:
   1️⃣ Test de cohérence conceptuelle
   2️⃣ Simulation de dialogues philosophiques
   3️⃣ Analyse comparative de réponses
   4️⃣ Test de robustesse aux paradoxes
   5️⃣ Mesure de créativité conceptuelle
   6️⃣ Benchmark contre corpus philosophique
   7️⃣ Test d'apprentissage adaptatif
   8️⃣ Expérience de perturbation ontologique
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.test_conceptual_coherence()
        elif choice == '2':
            self.simulate_philosophical_dialogue()
        elif choice == '3':
            self.comparative_response_analysis()
        elif choice == '4':
            self.paradox_robustness_test()
        elif choice == '5':
            self.creativity_measurement()
        elif choice == '6':
            self.philosophical_corpus_benchmark()
        elif choice == '7':
            self.adaptive_learning_test()
        elif choice == '8':
            self.ontological_perturbation_experiment()
    
    def test_conceptual_coherence(self):
        """Test de cohérence conceptuelle"""
        
        print("\n🧪 TEST DE COHÉRENCE CONCEPTUELLE")
        print("=" * 40)
        
        # Questions de cohérence
        coherence_tests = [
            ("La vérité peut-elle être relative ?", "VERITE"),
            ("L'injustice peut-elle être juste ?", "JUSTICE"),
            ("Peut-on être libre sans responsabilité ?", "LIBERTE"),
            ("L'amour peut-il être rationnel ?", "AMOUR"),
            ("Le mal peut-il être nécessaire au bien ?", "BIEN")
        ]
        
        results = []
        
        for question, expected_concept in coherence_tests:
            print(f"\n🔍 Test: {question}")
            response = self.sophia.ask(question)
            
            concepts_detected = response.conceptual_analysis['concepts_detected']
            contains_expected = expected_concept in concepts_detected
            
            coherence_score = response.conceptual_analysis['confidence']
            
            result = {
                'question': question,
                'expected_concept': expected_concept,
                'found_expected': contains_expected,
                'confidence': coherence_score,
                'concepts': concepts_detected
            }
            
            results.append(result)
            
            print(f"   ✅ Concept attendu trouvé: {contains_expected}")
            print(f"   📊 Confiance: {coherence_score:.0%}")
        
        # Rapport final
        coherence_rate = sum(r['found_expected'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"\n📋 RAPPORT DE COHÉRENCE:")
        print(f"   🎯 Taux de cohérence: {coherence_rate:.0%}")
        print(f"   📊 Confiance moyenne: {avg_confidence:.0%}")
        
        if coherence_rate >= 0.8:
            print("   ✅ Excellente cohérence conceptuelle")
        elif coherence_rate >= 0.6:
            print("   ⚠️ Cohérence modérée - amélioration possible")
        else:
            print("   ❌ Cohérence faible - révision nécessaire")
    
    def corpus_training(self):
        """Entraînement sur corpus philosophique à partir d'un fichier"""
        
        print("\n📚 ENTRAÎNEMENT SUR CORPUS PHILOSOPHIQUE")
        print("=" * 45)
        
        # Demande du fichier
        file_path = input("📁 Chemin vers le fichier texte philosophique: ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ Fichier introuvable: {file_path}")
            return
        
        try:
            # Lecture du fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📖 Fichier chargé: {len(content)} caractères")
            
            # Paramètres d'entraînement
            chunk_size = int(input("📏 Taille des chunks (défaut 500): ") or "500")
            max_chunks = int(input("🔢 Nombre max de chunks (défaut 50): ") or "50")
            
            # Division en chunks
            chunks = []
            words = content.split()
            
            for i in range(0, min(len(words), max_chunks * chunk_size), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                if len(chunk.strip()) > 100:  # Ignorer les chunks trop courts
                    chunks.append(chunk)
            
            print(f"📝 {len(chunks)} chunks créés pour l'entraînement")
            
            # Entraînement progressif
            concepts_learned = set()
            relations_added = 0
            
            for i, chunk in enumerate(chunks, 1):
                print(f"\n🔄 Traitement chunk {i}/{len(chunks)}...")
                
                # Extraction des concepts
                available_concepts = list(self.sophia.ontology.concepts.keys())
                extraction = self.sophia.llm.extract_concepts_from_text(chunk, available_concepts)
                
                concepts_in_chunk = extraction['concepts_detected']
                concepts_learned.update(concepts_in_chunk)
                
                # Apprentissage forcé des relations
                if len(concepts_in_chunk) >= 2:
                    # Simule une question pour déclencher l'apprentissage
                    question = f"Quelle relation existe entre {concepts_in_chunk[0]} et {concepts_in_chunk[1]} ?"
                    response = self.sophia.ask(question)
                    relations_added += 1
                
                # Affichage du progrès
                if i % 5 == 0:
                    print(f"   📊 Progrès: concepts activés = {len(concepts_learned)}")
            
            # Rapport final
            print(f"\n✅ ENTRAÎNEMENT TERMINÉ:")
            print(f"   📚 Chunks traités: {len(chunks)}")
            print(f"   🎯 Concepts uniques activés: {len(concepts_learned)}")
            print(f"   🔗 Relations potentielles ajoutées: {relations_added}")
            print(f"   🧠 Transitions LCM finales: {len(self.sophia.lcm_model.transitions)}")
            
            # Sauvegarde optionnelle
            save_choice = input("\n💾 Sauvegarder cette session d'entraînement ? (o/N): ").strip().lower()
            if save_choice == 'o':
                filename = f"corpus_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                self.manual_save()
                print(f"💾 Session sauvegardée")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'entraînement: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def session_manager(self):
        """Gestionnaire complet des sessions"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         💾 GESTIONNAIRE DE SESSIONS                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Options disponibles:
   1️⃣ Lister les sessions existantes
   2️⃣ Charger une session
   3️⃣ Sauvegarder la session actuelle
   4️⃣ Créer une nouvelle session
   5️⃣ Supprimer une session
   6️⃣ Comparer des sessions
   7️⃣ Merger des sessions
   8️⃣ Export/Import de sessions
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.list_sessions()
        elif choice == '2':
            self.load_session()
        elif choice == '3':
            self.save_current_session()
        elif choice == '4':
            self.create_new_session()
        elif choice == '5':
            self.delete_session()
        elif choice == '6':
            self.compare_sessions()
        elif choice == '7':
            self.merge_sessions()
        elif choice == '8':
            self.import_export_sessions()
    
    def list_sessions(self):
        """Liste toutes les sessions disponibles"""
        
        print("\n📋 SESSIONS DISPONIBLES")
        print("=" * 30)
        
        session_dir = Path("sessions")
        if not session_dir.exists():
            print("❌ Aucun dossier de sessions trouvé")
            return
        
        session_files = list(session_dir.glob("*.pkl"))
        
        if not session_files:
            print("📭 Aucune session sauvegardée")
            return
        
        for i, session_file in enumerate(session_files, 1):
            try:
                # Lecture des métadonnées
                with open(session_file, 'rb') as f:
                    data = pickle.load(f)
                
                timestamp = data.get('timestamp', 'Inconnu')
                stats = data.get('stats', {})
                
                print(f"{i:2d}. {session_file.name}")
                print(f"     📅 {timestamp}")
                print(f"     💬 Questions: {stats.get('questions_posed', 0)}")
                print(f"     🧠 Concepts: {len(data.get('ontology', {}).get('concepts', {}))}")
                print()
                
            except Exception as e:
                print(f"{i:2d}. {session_file.name} (❌ Erreur: {e})")
    
    def import_export_mode(self):
        """Mode import/export pour les connaissances"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      📚 IMPORT/EXPORT CONNAISSANCES                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Options disponibles:
   1️⃣ Exporter l'ontologie (JSON)
   2️⃣ Importer une ontologie (JSON)
   3️⃣ Exporter le modèle LCM
   4️⃣ Importer un modèle LCM
   5️⃣ Export complet (backup)
   6️⃣ Import complet (restore)
   7️⃣ Export statistiques (CSV)
   8️⃣ Export pour analyse externe
   0️⃣ Retour au menu
""")
        
        choice = input("Choix: ").strip()
        
        if choice == '1':
            self.export_ontology()
        elif choice == '2':
            self.import_ontology()
        elif choice == '3':
            self.export_lcm_model()
        elif choice == '4':
            self.import_lcm_model()
        elif choice == '5':
            self.full_backup()
        elif choice == '6':
            self.full_restore()
        elif choice == '7':
            self.export_statistics_csv()
        elif choice == '8':
            self.export_for_analysis()
    
    def export_ontology(self):
        """Export de l'ontologie en JSON"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            ontology_data = {
                'concepts': {},
                'relations': [],
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_concepts': len(self.sophia.ontology.concepts),
                    'version': '1.0'
                }
            }
            
            # Export des concepts
            for name, concept in self.sophia.ontology.concepts.items():
                ontology_data['concepts'][name] = {
                    'type': concept.concept_type.value,
                    'description': concept.description
                }
            
            # Export des relations
            for concept_name in self.sophia.ontology.concepts.keys():
                relations = self.sophia.ontology.get_concept_relations(concept_name)
                for rel in relations:
                    ontology_data['relations'].append({
                        'from': rel['from'],
                        'to': rel['to'],
                        'relation': rel['relation'].value
                    })
            
            # Sauvegarde
            filename = f"ontology_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ontology_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Ontologie exportée: {filename}")
            print(f"   📚 {len(ontology_data['concepts'])} concepts")
            print(f"   🔗 {len(ontology_data['relations'])} relations")
            
        except Exception as e:
            print(f"❌ Erreur d'export: {e}")
    
    def import_ontology(self):
        """Import d'une ontologie depuis un fichier JSON"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            file_path = input("📁 Chemin vers le fichier JSON d'ontologie: ").strip()
            
            if not os.path.exists(file_path):
                print(f"❌ Fichier introuvable: {file_path}")
                return
            
            # Chargement des données
            with open(file_path, 'r', encoding='utf-8') as f:
                ontology_data = json.load(f)
            
            # Vérification de la structure
            if 'concepts' not in ontology_data or 'relations' not in ontology_data:
                print("❌ Format de fichier invalide: clés manquantes")
                return
            
            # Import des concepts
            for name, concept in ontology_data['concepts'].items():
                concept_type = ConceptType[concept['type']] if 'type' in concept else ConceptType.ABSTRACT
                description = concept.get('description', '')
                
                self.sophia.ontology.add_concept(name, concept_type, description)
            
            # Import des relations
            for rel in ontology_data['relations']:
                self.sophia.ontology.add_relation(rel['from'], rel['to'], rel['relation'])
            
            print(f"✅ Ontologie importée: {file_path}")
            print(f"   📚 {len(ontology_data['concepts'])} concepts ajoutés")
            print(f"   🔗 {len(ontology_data['relations'])} relations ajoutées")
            
            # Mise à jour du modèle LCM
            self.sophia.lcm_model.update_model()
            print("🧠 Modèle LCM mis à jour")
        
        except Exception as e:
            print(f"❌ Erreur d'import: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def export_lcm_model(self):
        """Export du modèle LCM"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            # Sérialisation du modèle LCM
            serializer = LCMSerializer()
            file_path = f"lcm_model_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            serializer.save_model(self.sophia.lcm_model, file_path)
            
            print(f"✅ Modèle LCM exporté: {file_path}")
        
        except Exception as e:
            print(f"❌ Erreur d'export LCM: {e}")
    
    def import_lcm_model(self):
        """Import d'un modèle LCM"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            file_path = input("📁 Chemin vers le fichier de modèle LCM: ").strip()
            
            if not os.path.exists(file_path):
                print(f"❌ Fichier introuvable: {file_path}")
                return
            
            # Désérialisation du modèle LCM
            serializer = LCMSerializer()
            lcm_model = serializer.load_model(file_path)
            
            # Remplacement de l'ancien modèle par le nouveau
            self.sophia.lcm_model = lcm_model
            print(f"✅ Modèle LCM importé: {file_path}")
        
        except Exception as e:
            print(f"❌ Erreur d'import LCM: {e}")
    
    def full_backup(self):
        """Export complet (ontologie + modèle LCM)"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ontology_file = f"ontology_backup_{timestamp}.json"
            lcm_file = f"lcm_model_backup_{timestamp}.pkl"
            
            # Export de l'ontologie
            self.export_ontology()
            
            # Export du modèle LCM
            self.export_lcm_model()
            
            print(f"✅ Sauvegarde complète terminée")
            print(f"   📁 Ontologie: {ontology_file}")
            print(f"   📁 Modèle LCM: {lcm_file}")
        
        except Exception as e:
            print(f"❌ Erreur de sauvegarde complète: {e}")
    
    def full_restore(self):
        """Import complet (ontologie + modèle LCM)"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            # Liste des fichiers de sauvegarde
            backup_files = sorted(Path(".").glob("*_backup_*.json"), key=os.path.getmtime)
            if not backup_files:
                print("❌ Aucune sauvegarde trouvée")
                return
            
            # Choix du fichier de sauvegarde
            print("📂 Sauvegardes disponibles:")
            for i, file in enumerate(backup_files, 1):
                print(f"   {i}. {file.name}")
            
            choice = input("Choix du fichier à restaurer (ou Entrée pour annuler): ").strip()
            if not choice:
                print("❌ Restauration annulée")
                return
            
            # Chargement de la sauvegarde sélectionnée
            backup_file = backup_files[int(choice) - 1]
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Import de l'ontologie
            self.sophia.ontology.clear()
            for name, concept in backup_data['concepts'].items():
                concept_type = ConceptType[concept['type']] if 'type' in concept else ConceptType.ABSTRACT
                description = concept.get('description', '')
                self.sophia.ontology.add_concept(name, concept_type, description)
            
            for rel in backup_data['relations']:
                self.sophia.ontology.add_relation(rel['from'], rel['to'], rel['relation'])
            
            print(f"✅ Ontologie restaurée depuis {backup_file}")
            
            # Import du modèle LCM
            lcm_file = backup_file.with_name(backup_file.name.replace("ontology", "lcm_model"))
            if lcm_file.exists():
                serializer = LCMSerializer()
                lcm_model = serializer.load_model(str(lcm_file))
                self.sophia.lcm_model = lcm_model
                print(f"✅ Modèle LCM restauré depuis {lcm_file}")
            else:
                print("⚠️ Aucune sauvegarde du modèle LCM trouvée")
        
        except Exception as e:
            print(f"❌ Erreur de restauration complète: {e}")
    
    def export_statistics_csv(self):
        """Export des statistiques de session en CSV"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            import csv
            
            file_path = f"session_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Statistique', 'Valeur']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for key, value in self.stats.items():
                    writer.writerow({'Statistique': key, 'Valeur': value})
            
            print(f"✅ Statistiques exportées: {file_path}")
        
        except Exception as e:
            print(f"❌ Erreur d'export statistiques: {e}")
    
    def export_for_analysis(self):
        """Export des données pour analyse externe (JSON)"""
        
        if not self.sophia:
            print("❌ SophIA non initialisée")
            return
        
        try:
            data = {
                'ontology': self.sophia.ontology.export_to_dict(),
                'lcm_model': self.sophia.lcm_model.export_to_dict(),
                'stats': self.stats
            }
            
            file_path = f"export_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Données exportées pour analyse: {file_path}")
        
        except Exception as e:
            print(f"❌ Erreur d'export pour analyse: {e}")

def main():
    """Point d'entrée principal"""
    
    try:
        cli = SophIACLIUltimate()
        cli.run()
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()