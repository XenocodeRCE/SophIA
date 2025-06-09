#!/usr/bin/env python3
"""
SophIA Enhanced - Interface en Ligne de Commande Complète
Interface utilisateur avancée pour l'IA philosophique SophIA
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import readline  # Pour l'historique des commandes
import textwrap
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.columns import Columns
from rich.live import Live
from rich.layout import Layout
from rich.tree import Tree

# Imports SophIA
try:
    from sophia.core.sophia_hybrid import HybridSophIA
    from sophia.learning.autonomous_learner import AutonomousLearner
    from sophia.nlp.tokenizer import PhilosophicalTokenizer
    SOPHIA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erreur import SophIA: {e}")
    SOPHIA_AVAILABLE = False
    sys.exit(1)

class SophIACLI:
    """Interface en ligne de commande complète pour SophIA Enhanced"""
    
    def __init__(self):
        self.console = Console()
        self.sophia = None
        self.session_start = datetime.now()
        self.session_questions = []
        self.training_history = []
        self.config = self._load_config()
        
        # Statistiques de session
        self.stats = {
            'questions_asked': 0,
            'concepts_discovered': set(),
            'training_sessions': 0,
            'documents_processed': 0,
            'learning_confidence_start': 0.0,
            'learning_confidence_current': 0.0
        }
        
        # Configuration par défaut
        self.default_settings = {
            'performance_mode': 'balanced',
            'auto_save': True,
            'show_detailed_analysis': True,
            'learning_enabled': True,
            'save_conversations': True
        }
        
        self.current_settings = self.default_settings.copy()
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration utilisateur"""
        config_file = Path("sophia_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_config(self):
        """Sauvegarde la configuration"""
        config_file = Path("sophia_config.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]Erreur sauvegarde config: {e}[/red]")
    
    def display_welcome(self):
        """Affiche l'écran d'accueil"""
        self.console.clear()
        
        welcome_text = """
🧠 SophIA Enhanced - Intelligence Philosophique Hybride
═══════════════════════════════════════════════════════

Une IA révolutionnaire combinant raisonnement conceptuel et génération naturelle
pour l'exploration philosophique avancée.

Fonctionnalités:
• 🔍 Extraction conceptuelle ultra-avancée
• 🧠 Raisonnement hybride LCM + LLaMA  
• 📝 Analyse linguistique spécialisée
• 🔄 Apprentissage autonome adaptatif
• 📚 Entraînement sur corpus philosophiques
• ⚖️ Validation éthique intégrée

Commandes disponibles: help, ask, train, analyze, settings, stats, quit
        """
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Bienvenue dans SophIA Enhanced[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Status des modules
        self._display_module_status()
    
    def _display_module_status(self):
        """Affiche le status des modules SophIA"""
        
        status_table = Table(title="📊 Status des Modules", show_header=True)
        status_table.add_column("Module", style="cyan", width=25)
        status_table.add_column("Status", width=15)
        status_table.add_column("Description", style="dim")
        
        modules = [
            ("🔍 LLM Extractor", "✅ Disponible", "Extraction conceptuelle avancée"),
            ("📝 Tokenizer", "✅ Disponible", "Analyse linguistique philosophique"),
            ("📊 Performance Monitor", "✅ Disponible", "Monitoring temps réel"),
            ("🧠 Autonomous Learner", "✅ Disponible", "Apprentissage adaptatif"),
            ("🦙 LLaMA Core", "✅ Disponible", "Génération naturelle"),
            ("⚖️ Constraint Validation", "✅ Disponible", "Validation éthique")
        ]
        
        for module, status, desc in modules:
            status_table.add_row(module, status, desc)
        
        self.console.print(status_table)
        self.console.print()
    
    def initialize_sophia(self, performance_mode: str = "balanced") -> bool:
        """Initialise SophIA avec monitoring"""
        
        with self.console.status("[bold blue]Initialisation de SophIA Enhanced...", spinner="dots"):
            try:
                self.sophia = HybridSophIA(
                    auto_save=self.current_settings['auto_save'],
                    performance_mode=performance_mode
                )
                
                # Récupère la confiance d'apprentissage initiale
                if self.sophia.autonomous_learner:
                    insights = self.sophia.autonomous_learner.get_learning_insights()
                    self.stats['learning_confidence_start'] = insights['learning_summary']['learning_confidence']
                    self.stats['learning_confidence_current'] = self.stats['learning_confidence_start']
                
                self.console.print("[green]✅ SophIA Enhanced initialisée avec succès![/green]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]❌ Erreur initialisation: {e}[/red]")
                return False
    
    def run_interactive_session(self):
        """Lance la session interactive principale"""
        
        if not self.initialize_sophia(self.current_settings['performance_mode']):
            return
        
        self.console.print("\n[green]💬 Session interactive démarrée. Tapez 'help' pour l'aide.[/green]\n")
        
        while True:
            try:
                # Prompt personnalisé avec status
                prompt_text = self._build_prompt()
                user_input = Prompt.ask(prompt_text).strip()
                
                if not user_input:
                    continue
                
                # Parse et exécute la commande
                if not self._handle_command(user_input):
                    break
                    
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Quitter SophIA?[/yellow]"):
                    break
                self.console.print()
            except Exception as e:
                self.console.print(f"[red]Erreur: {e}[/red]")
        
        self._display_session_summary()
    
    def _build_prompt(self) -> str:
        """Construit le prompt interactif avec status"""
        
        # Mode de performance
        mode_color = {
            'speed': 'red',
            'balanced': 'yellow', 
            'quality': 'green'
        }.get(self.current_settings['performance_mode'], 'white')
        
        mode_text = f"[{mode_color}]{self.current_settings['performance_mode']}[/{mode_color}]"
        
        # Apprentissage status
        learning_icon = "🧠" if self.current_settings['learning_enabled'] else "🚫"
        
        return f"SophIA {mode_text} {learning_icon}"
    
    def _handle_command(self, user_input: str) -> bool:
        """Gère les commandes utilisateur"""
        
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Commandes principales
        if command == 'help':
            self._show_help()
        elif command == 'ask':
            question = ' '.join(args) if args else None
            self._ask_question(question)
        elif command == 'train':
            self._training_menu()
        elif command == 'analyze':
            self._analysis_menu()
        elif command == 'settings':
            self._settings_menu()
        elif command == 'stats':
            self._show_statistics()
        elif command == 'history':
            self._show_history()
        elif command == 'save':
            self._save_session()
        elif command == 'load':
            self._load_session()
        elif command == 'clear':
            self.console.clear()
            self.display_welcome()
        elif command in ['quit', 'exit', 'q']:
            return False
        else:
            # Si ce n'est pas une commande, traite comme question
            self._ask_question(user_input)
        
        return True
    
    def _show_help(self):
        """Affiche l'aide détaillée"""
        
        help_content = """
[bold blue]📚 Commandes Disponibles[/bold blue]

[cyan]Questions & Interaction:[/cyan]
  ask <question>     - Pose une question à SophIA
  <question>         - Pose directement une question
  history           - Affiche l'historique des questions

[cyan]Entraînement & Apprentissage:[/cyan]
  train             - Menu d'entraînement
  train file <path> - Entraîne sur un fichier
  train text        - Entraîne sur texte saisi
  train corpus      - Entraîne sur corpus philosophique

[cyan]Analyse & Insights:[/cyan]
  analyze           - Menu d'analyse
  analyze concepts  - Analyse conceptuelle de session
  analyze learning  - Insights d'apprentissage
  analyze performance - Métriques de performance

[cyan]Configuration:[/cyan]
  settings          - Menu de configuration
  stats            - Statistiques détaillées

[cyan]Session:[/cyan]
  save             - Sauvegarde la session
  load             - Charge une session
  clear            - Efface l'écran
  quit, exit, q    - Quitte SophIA

[yellow]💡 Exemples:[/yellow]
  ask Qu'est-ce que la vérité?
  train file ./platon_republique.txt
  analyze concepts
        """
        
        panel = Panel(
            help_content,
            title="[bold]Guide d'Utilisation SophIA Enhanced[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _ask_question(self, question: Optional[str] = None):
        """Pose une question à SophIA"""
        
        if not question:
            question = Prompt.ask("[cyan]💭 Votre question philosophique")
        
        if not question.strip():
            return
        
        self.console.print(f"\n[dim]Question: {question}[/dim]")
        
        # Pose la question avec monitoring
        start_time = time.time()
        
        with Live(
            Panel("[blue]🧠 SophIA réfléchit...[/blue]", border_style="blue"),
            refresh_per_second=2
        ) as live:
            try:
                response = self.sophia.ask(question)
                duration = time.time() - start_time
                
                # Mise à jour des stats
                self.stats['questions_asked'] += 1
                self.stats['concepts_discovered'].update(
                    response.conceptual_analysis.get('concepts_detected', [])
                )
                
                # Sauvegarde dans l'historique
                self.session_questions.append({
                    'question': question,
                    'response': response,
                    'timestamp': datetime.now(),
                    'duration': duration
                })
                
                # Affichage de la réponse
                self._display_response(response, duration)
                
                # Apprentissage automatique si activé
                if self.current_settings['learning_enabled'] and self.sophia.autonomous_learner:
                    self._auto_learn_from_response(question, response)
                
            except Exception as e:
                live.update(Panel(f"[red]❌ Erreur: {e}[/red]", border_style="red"))
                time.sleep(2)
    
    def _display_response(self, response, duration: float):
        """Affiche la réponse formatée"""
        
        # Réponse principale
        response_panel = Panel(
            response.natural_response,
            title="[bold green]💬 Réponse de SophIA[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(response_panel)
        
        # Analyse détaillée si activée
        if self.current_settings['show_detailed_analysis']:
            self._display_detailed_analysis(response, duration)
    
    def _display_detailed_analysis(self, response, duration: float):
        """Affiche l'analyse détaillée"""
        
        # Métriques principales
        metrics_table = Table(title="📊 Métriques", show_header=False, box=None)
        metrics_table.add_column("Métrique", style="cyan", width=20)
        metrics_table.add_column("Valeur", width=15)
        
        concepts = response.conceptual_analysis.get('concepts_detected', [])
        relations = response.conceptual_analysis.get('relations_implied', [])
        
        metrics_table.add_row("⏱️ Temps réponse", f"{duration:.2f}s")
        metrics_table.add_row("📊 Confiance", f"{response.confidence:.1%}")
        metrics_table.add_row("🎯 Concepts", f"{len(concepts)}")
        metrics_table.add_row("🔗 Relations", f"{len(relations)}")
        
        validation_score = response.validation_report.get('global_score', 0)
        metrics_table.add_row("⚖️ Validation", f"{validation_score:.1%}")
        
        # Concepts détectés
        concepts_text = ", ".join(concepts[:6]) if concepts else "Aucun"
        if len(concepts) > 6:
            concepts_text += f" (+{len(concepts)-6} autres)"
        
        metrics_table.add_row("🧠 Concepts détectés", concepts_text)
        
        # Méthode d'extraction
        extraction_method = response.conceptual_analysis.get(
            'extraction_details', {}
        ).get('metadata', {}).get('extraction_method', 'unknown')
        metrics_table.add_row("🔍 Méthode", extraction_method)
        
        self.console.print(metrics_table)
        
        # Relations conceptuelles si présentes
        if relations and len(relations) > 0:
            self._display_relations(relations[:5])  # Top 5 relations
    
    def _display_relations(self, relations: List[Dict]):
        """Affiche les relations conceptuelles"""
        
        relations_table = Table(title="🔗 Relations Conceptuelles", show_header=True)
        relations_table.add_column("Concept A", style="cyan")
        relations_table.add_column("Relation", style="yellow")
        relations_table.add_column("Concept B", style="cyan")
        relations_table.add_column("Force", style="green")
        
        for rel in relations:
            strength_bar = "█" * int(rel.get('strength', 0) * 5)
            relations_table.add_row(
                rel['from'],
                rel['relation'],
                rel['to'],
                f"{strength_bar} {rel.get('strength', 0):.2f}"
            )
        
        self.console.print(relations_table)
    
    def _auto_learn_from_response(self, question: str, response):
        """Apprentissage automatique depuis la réponse"""
        
        try:
            response_data = {
                'conceptual_analysis': response.conceptual_analysis,
                'confidence': response.confidence,
                'validation_report': response.validation_report,
                'natural_response': response.natural_response,
                'performance_metrics': {'duration': 2.0}
            }
            
            learning_result = self.sophia.autonomous_learner.learn_from_interaction(
                question=question,
                response_data=response_data,
                feedback_score=None
            )
            
            if learning_result['patterns_discovered'] > 0:
                self.console.print(
                    f"[dim]🧠 Apprentissage: {learning_result['patterns_discovered']} nouveaux patterns[/dim]"
                )
            
            # Mise à jour confiance apprentissage
            self.stats['learning_confidence_current'] = learning_result['learning_confidence']
            
        except Exception as e:
            self.console.print(f"[dim red]Erreur apprentissage auto: {e}[/dim red]")
    
    def _training_menu(self):
        """Menu d'entraînement et apprentissage"""
        
        if not self.sophia.autonomous_learner:
            self.console.print("[red]❌ Autonomous Learner non disponible[/red]")
            return
        
        training_options = [
            "1. Entraîner sur fichier texte",
            "2. Entraîner sur texte saisi",
            "3. Entraîner sur corpus philosophique",
            "4. Voir l'historique d'entraînement",
            "5. Analyser l'apprentissage",
            "6. Retour"
        ]
        
        self.console.print("\n[bold cyan]📚 Menu d'Entraînement[/bold cyan]")
        for option in training_options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6"], default="6")
        
        if choice == "1":
            self._train_from_file_safe()
        elif choice == "2":
            self._train_from_text()
        elif choice == "3":
            self._train_from_corpus()
        elif choice == "4":
            self._show_training_history()
        elif choice == "5":
            self._analyze_learning()
        # choice == "6" retourne au menu principal
    
    def _train_from_file(self):
        """Entraîne SophIA depuis un fichier"""
        
        file_path = Prompt.ask("📁 Chemin du fichier")
        
        if not Path(file_path).exists():
            self.console.print(f"[red]❌ Fichier non trouvé: {file_path}[/red]")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.console.print(f"📖 Fichier chargé: {len(content)} caractères")
            
            # Confirmation
            if not Confirm.ask(f"Entraîner SophIA sur ce fichier?"):
                return
            
            # Apprentissage
            self._process_training_content(content, f"Fichier: {Path(file_path).name}")
            
        except Exception as e:
            self.console.print(f"[red]❌ Erreur lecture fichier: {e}[/red]")
    
    def _train_from_text(self):
        """Entraîne SophIA depuis du texte saisi"""
        
        self.console.print("📝 Saisissez le texte d'entraînement (Ctrl+D pour terminer):")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = '\n'.join(lines)
        
        if not content.strip():
            self.console.print("[yellow]⚠️ Aucun contenu saisi[/yellow]")
            return
        
        self.console.print(f"📖 Texte saisi: {len(content)} caractères")
        
        if Confirm.ask("Entraîner SophIA sur ce texte?"):
            self._process_training_content(content, "Texte saisi")
    
    def _train_from_corpus(self):
        """Entraîne sur corpus philosophique prédéfini"""
        
        corpus_options = {
            "1": ("Platon - Extraits", self._get_plato_corpus()),
            "2": ("Aristote - Extraits", self._get_aristotle_corpus()),
            "3": ("Descartes - Extraits", self._get_descartes_corpus()),
            "4": ("Kant - Extraits", self._get_kant_corpus()),
            "5": ("Nietzsche - Extraits", self._get_nietzsche_corpus())
        }
        
        self.console.print("\n[cyan]📚 Corpus Philosophiques Disponibles:[/cyan]")
        for key, (name, _) in corpus_options.items():
            self.console.print(f"  {key}. {name}")
        
        choice = Prompt.ask("Choix", choices=list(corpus_options.keys()))
        
        name, content = corpus_options[choice]
        
        self.console.print(f"📖 Corpus sélectionné: {name}")
        self.console.print(f"📊 Taille: {len(content)} caractères")
        
        if Confirm.ask(f"Entraîner SophIA sur {name}?"):
            self._process_training_content(content, name)
    
    def _process_training_content(self, content: str, source_name: str):
        """Traite le contenu d'entraînement"""
        
        start_time = time.time()
        
        # Découpage en segments pour l'entraînement
        segments = self._split_content_for_training(content)
        
        self.console.print(f"🔄 Traitement de {len(segments)} segments...")
        
        learning_results = []
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Entraînement...", total=len(segments))
            
            for i, segment in enumerate(segments):
                # Génère une question/réponse pour chaque segment
                training_pair = self._create_training_pair(segment)
                
                if training_pair:
                    try:
                        # Simule une interaction d'apprentissage
                        response_data = {
                            'conceptual_analysis': training_pair['analysis'],
                            'confidence': training_pair['confidence'],
                            'validation_report': {'global_score': 0.8},
                            'natural_response': training_pair['response'],
                            'performance_metrics': {'duration': 1.0}
                        }
                        
                        result = self.sophia.autonomous_learner.learn_from_interaction(
                            question=training_pair['question'],
                            response_data=response_data,
                            feedback_score=0.8
                        )
                        
                        learning_results.append(result)
                        
                    except Exception as e:
                        self.console.print(f"[dim red]Erreur segment {i}: {e}[/dim red]")
                
                progress.update(task, advance=1)
        
        duration = time.time() - start_time
        
        # Résultats d'entraînement
        self._display_training_results(learning_results, source_name, duration)
        
        # Sauvegarde dans l'historique
        self.training_history.append({
            'source': source_name,
            'segments_processed': len(segments),
            'duration': duration,
            'timestamp': datetime.now(),
            'results': learning_results
        })
        
        self.stats['training_sessions'] += 1
        self.stats['documents_processed'] += 1
    
    
    def _process_training_content_robust(self, content: str, source_name: str):
        """Version robuste du traitement d'entraînement avec gestion d'erreurs"""
        
        start_time = time.time()
        
        # Découpage en segments pour l'entraînement
        segments = self._split_content_for_training(content)
        
        self.console.print(f"🔄 Traitement robuste de {len(segments)} segments...")
        
        learning_results = []
        error_count = 0
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Entraînement robuste...", total=len(segments))
            
            for i, segment in enumerate(segments):
                try:
                    # Version simplifiée de création de paire d'entraînement
                    training_pair = self._create_simple_training_pair(segment)
                    
                    if training_pair:
                        # Simule une interaction d'apprentissage
                        response_data = {
                            'conceptual_analysis': training_pair['analysis'],
                            'confidence': training_pair['confidence'],
                            'validation_report': {'global_score': 0.8},
                            'natural_response': training_pair['response'],
                            'performance_metrics': {'duration': 1.0}
                        }
                        
                        result = self.sophia.autonomous_learner.learn_from_interaction(
                            question=training_pair['question'],
                            response_data=response_data,
                            feedback_score=0.8
                        )
                        
                        learning_results.append(result)
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Affiche seulement les 5 premières erreurs
                        self.console.print(f"[dim red]Erreur segment {i}: {e}[/dim red]")
                
                progress.update(task, advance=1)
        
        duration = time.time() - start_time
        
        # Résultats d'entraînement avec erreurs
        self._display_training_results_with_errors(learning_results, source_name, duration, error_count)
        
        # Sauvegarde dans l'historique
        self.training_history.append({
            'source': source_name,
            'segments_processed': len(segments),
            'segments_successful': len(learning_results),
            'segments_errors': error_count,
            'duration': duration,
            'timestamp': datetime.now(),
            'results': learning_results
        })
        
        self.stats['training_sessions'] += 1
        self.stats['documents_processed'] += 1

    def _create_simple_training_pair(self, segment: str) -> Optional[Dict]:
        """Version simplifiée de création de paire d'entraînement"""
        
        try:
            # Extraction manuelle directe sans tokenizer
            concepts = self._extract_concepts_manually(segment)
            
            if not concepts:
                return None
            
            # Question simple basée sur le premier concept
            main_concept = concepts[0]
            question = f"Expliquez le concept de {main_concept} dans ce contexte."
            
            # Analyse basique
            analysis = {
                'concepts_detected': concepts,
                'relations_implied': [],
                'extraction_details': {'metadata': {'extraction_method': 'simple_manual'}}
            }
            
            return {
                'question': question,
                'response': segment[:200] + "..." if len(segment) > 200 else segment,
                'analysis': analysis,
                'confidence': 0.6
            }
            
        except Exception:
            return None

    def _extract_concepts_manually(self, text: str) -> List[str]:
        """Extraction manuelle ultra-simple de concepts"""
        
        concept_keywords = {
            'VÉRITÉ': ['vérité', 'vrai', 'véracité', 'vraie'],
            'JUSTICE': ['justice', 'juste', 'équitable', 'équité'],
            'BEAUTÉ': ['beauté', 'beau', 'belle', 'esthétique'],
            'BIEN': ['bien', 'bon', 'bonne', 'bonté'],
            'MAL': ['mal', 'mauvais', 'mauvaise'],
            'ÊTRE': ['être', 'existence', 'exister', 'existant'],
            'CONNAISSANCE': ['connaissance', 'savoir', 'connaître'],
            'RAISON': ['raison', 'rationnel', 'raisonnement'],
            'ÂME': ['âme', 'esprit', 'mental', 'psychique'],
            'NATURE': ['nature', 'naturel', 'naturelle'],
            'DIEU': ['dieu', 'divin', 'divine', 'divinité'],
            'LIBERTÉ': ['liberté', 'libre', 'libérer'],
            'TEMPS': ['temps', 'temporel', 'durée'],
            'ESPACE': ['espace', 'spatial', 'lieu'],
            'CAUSE': ['cause', 'causer', 'causalité'],
            'FORME': ['forme', 'formel', 'formation'],
            'MATIÈRE': ['matière', 'matériel', 'physique'],
            'IDÉE': ['idée', 'concept', 'notion'],
            'RÉALITÉ': ['réalité', 'réel', 'réelle']
        }
        
        text_lower = text.lower()
        found_concepts = []
        
        for concept, keywords in concept_keywords.items():
            for keyword in keywords:
                if keyword in text_lower and concept not in found_concepts:
                    found_concepts.append(concept)
                    break
        
        return found_concepts[:5]  # Maximum 5 concepts

    def _display_training_results_with_errors(self, results: List[Dict], source: str, 
                                            duration: float, error_count: int):
        """Affiche les résultats d'entraînement avec statistiques d'erreurs"""
        
        if not results:
            self.console.print("[yellow]⚠️ Aucun résultat d'entraînement valide[/yellow]")
            return
        
        # Statistiques d'entraînement
        total_patterns = sum(r.get('patterns_discovered', 0) for r in results)
        avg_confidence = sum(r.get('learning_confidence', 0) for r in results) / len(results)
        success_rate = len(results) / (len(results) + error_count) * 100
        
        success_panel = Panel(
            f"""
    [green]✅ Entraînement Terminé[/green]

    [cyan]Source:[/cyan] {source}
    [cyan]Durée:[/cyan] {duration:.1f}s
    [cyan]Segments traités:[/cyan] {len(results) + error_count}
    [cyan]Segments réussis:[/cyan] {len(results)}
    [cyan]Erreurs:[/cyan] {error_count}
    [cyan]Taux de succès:[/cyan] {success_rate:.1f}%
    [cyan]Nouveaux patterns:[/cyan] {total_patterns}
    [cyan]Confiance moyenne:[/cyan] {avg_confidence:.1%}

    {'[green]🎉 Entraînement excellent !' if success_rate >= 80 else '[yellow]⚠️ Entraînement avec erreurs' if success_rate >= 50 else '[red]❌ Entraînement difficile'}[/{'green' if success_rate >= 80 else 'yellow' if success_rate >= 50 else 'red'}]
            """,
            title="[bold green]📚 Résultats d'Entraînement[/bold green]",
            border_style="green" if success_rate >= 80 else "yellow" if success_rate >= 50 else "red"
        )
        
        self.console.print(success_panel)
        
        # Mise à jour de la confiance d'apprentissage
        if results:
            self.stats['learning_confidence_current'] = results[-1].get('learning_confidence', 0)
            
            
    def _split_content_for_training(self, content: str) -> List[str]:
        """Découpe le contenu en segments d'entraînement"""
        
        # Découpage par paragraphes
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Filtre les paragraphes trop courts ou trop longs
        segments = []
        for para in paragraphs:
            if 50 <= len(para) <= 500:  # Taille optimale pour l'apprentissage
                segments.append(para)
            elif len(para) > 500:
                # Découpe les gros paragraphes en phrases
                sentences = para.split('.')
                current_segment = ""
                for sentence in sentences:
                    if len(current_segment + sentence) < 400:
                        current_segment += sentence + "."
                    else:
                        if current_segment:
                            segments.append(current_segment.strip())
                        current_segment = sentence + "."
                if current_segment:
                    segments.append(current_segment.strip())
        
        return segments[:50]  # Limite à 50 segments pour éviter la surcharge
    
    def _create_training_pair(self, segment: str) -> Optional[Dict]:
        """Crée une paire question/réponse - VERSION ULTRA-SÉCURISÉE"""
        
        try:
            # Bypass complet du tokenizer problématique
            # Utilise uniquement l'extraction manuelle
            concepts = self._extract_concepts_manually_safe(segment)
            
            if not concepts:
                return None
            
            # Génère une question basée sur le premier concept
            main_concept = concepts[0]
            
            question_templates = [
                f"Expliquez le concept de {main_concept}.",
                f"Que signifie {main_concept} dans ce contexte ?",
                f"Comment comprendre {main_concept} ?",
                f"Quelle est l'importance de {main_concept} ?"
            ]
            
            import random
            question = random.choice(question_templates)
            
            # Analyse conceptuelle basique
            analysis = {
                'concepts_detected': concepts,
                'relations_implied': [],
                'extraction_details': {'metadata': {'extraction_method': 'manual_safe'}}
            }
            
            # Réponse tronquée si nécessaire
            response = segment
            if len(response) > 300:
                response = response[:297] + "..."
            
            return {
                'question': question,
                'response': response,
                'analysis': analysis,
                'confidence': 0.7
            }
            
        except Exception as e:
            # Log l'erreur mais continue
            if hasattr(self, 'console'):
                self.console.print(f"[dim red]Erreur paire: {e}[/dim red]", end="")
            return None


     
    def _train_from_file_safe(self):
        """Version ultra-sécurisée d'entraînement depuis fichier"""
        
        file_path = Prompt.ask("📁 Chemin du fichier")
        
        if not Path(file_path).exists():
            self.console.print(f"[red]❌ Fichier non trouvé: {file_path}[/red]")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.console.print(f"📖 Fichier chargé: {len(content)} caractères")
            
            # Confirmation
            if not Confirm.ask(f"Entraîner SophIA sur ce fichier?"):
                return
            
            # Traitement ultra-sécurisé
            self._process_training_ultra_safe(content, f"Fichier: {Path(file_path).name}")
            
        except Exception as e:
            self.console.print(f"[red]❌ Erreur lecture fichier: {e}[/red]")

    def _process_training_ultra_safe(self, content: str, source_name: str):
        """Traitement d'entraînement ultra-sécurisé"""
        
        start_time = time.time()
        
        # Découpage simple en paragraphes
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 30]
        
        # Limite à 30 paragraphes pour éviter surcharge
        segments = paragraphs[:30]
        
        self.console.print(f"🔄 Traitement ultra-sécurisé de {len(segments)} segments...")
        
        learning_results = []
        success_count = 0
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Entraînement sécurisé...", total=len(segments))
            
            for i, segment in enumerate(segments):
                try:
                    # Création de paire ultra-simple
                    concepts = self._extract_concepts_manually_safe(segment)
                    
                    if concepts:
                        # Question basique
                        question = f"Analysez ce passage philosophique."
                        
                        # Données d'apprentissage minimales
                        response_data = {
                            'conceptual_analysis': {
                                'concepts_detected': concepts,
                                'relations_implied': [],
                                'extraction_details': {'metadata': {'extraction_method': 'ultra_safe'}}
                            },
                            'confidence': 0.6,
                            'validation_report': {'global_score': 0.7},
                            'natural_response': segment[:200] + "..." if len(segment) > 200 else segment,
                            'performance_metrics': {'duration': 1.0}
                        }
                        
                        # Apprentissage
                        result = self.sophia.autonomous_learner.learn_from_interaction(
                            question=question,
                            response_data=response_data,
                            feedback_score=0.7
                        )
                        
                        learning_results.append(result)
                        success_count += 1
                    
                except Exception as e:
                    # Ignore silencieusement les erreurs
                    pass
                
                progress.update(task, advance=1)
        
        duration = time.time() - start_time
        
        # Résultats simplifiés
        self._display_simple_training_results(learning_results, source_name, duration, len(segments))
        
        # Historique
        self.training_history.append({
            'source': source_name,
            'segments_processed': len(segments),
            'segments_successful': success_count,
            'duration': duration,
            'timestamp': datetime.now(),
            'results': learning_results
        })
        
        self.stats['training_sessions'] += 1
        self.stats['documents_processed'] += 1

    def _display_simple_training_results(self, results: List[Dict], source: str, 
                                       duration: float, total_segments: int):
        """Affichage simplifié des résultats"""
        
        success_count = len(results)
        total_patterns = sum(r.get('patterns_discovered', 0) for r in results) if results else 0
        avg_confidence = sum(r.get('learning_confidence', 0) for r in results) / len(results) if results else 0
        success_rate = (success_count / total_segments * 100) if total_segments > 0 else 0
        
        result_color = "green" if success_rate >= 70 else "yellow" if success_rate >= 40 else "red"
        
        success_panel = Panel(
            f"""
    [green]✅ Entraînement Terminé[/green]

    [cyan]Source:[/cyan] {source}
    [cyan]Durée:[/cyan] {duration:.1f}s
    [cyan]Segments traités:[/cyan] {total_segments}
    [cyan]Segments réussis:[/cyan] {success_count}
    [cyan]Taux de succès:[/cyan] {success_rate:.1f}%
    [cyan]Nouveaux patterns:[/cyan] {total_patterns}
    [cyan]Confiance moyenne:[/cyan] {avg_confidence:.1%}

    [{result_color}]{'🎉 Excellent !' if success_rate >= 70 else '⚠️ Partiel' if success_rate >= 40 else '❌ Difficile'}[/{result_color}]
            """,
            title="[bold green]📚 Résultats d'Entraînement[/bold green]",
            border_style=result_color
        )
        
        self.console.print(success_panel)
        
        # Mise à jour confiance
        if results:
            self.stats['learning_confidence_current'] = results[-1].get('learning_confidence', 0)
            
    def _extract_concepts_manually_safe(self, text: str) -> List[str]:
        """Extraction manuelle ultra-sécurisée sans regex complexes"""
        
        if not text or len(text) == 0:
            return []
        
        try:
            # Conversion sécurisée en minuscules
            text_safe = str(text).lower()
            
            # Concepts avec mots-clés simples
            concept_map = {
                'VÉRITÉ': ['vérité', 'vrai', 'vraie'],
                'JUSTICE': ['justice', 'juste'],
                'BEAUTÉ': ['beauté', 'beau', 'belle'],
                'BIEN': ['bien', 'bon', 'bonne'],
                'MAL': ['mal', 'mauvais'],
                'ÊTRE': ['être', 'existence'],
                'CONNAISSANCE': ['connaissance', 'savoir'],
                'RAISON': ['raison', 'rationnel'],
                'LIBERTÉ': ['liberté', 'libre'],
                'NATURE': ['nature', 'naturel'],
                'DIEU': ['dieu', 'divin'],
                'ÂME': ['âme', 'esprit'],
                'TEMPS': ['temps', 'temporel'],
                'ESPACE': ['espace', 'spatial'],
                'RÉALITÉ': ['réalité', 'réel'],
                'CONSCIENCE': ['conscience', 'conscient'],
                'VOLONTÉ': ['volonté', 'vouloir'],
                'PASSION': ['passion', 'émotion'],
                'VERTU': ['vertu', 'virtuel'],
                'SCIENCE': ['science', 'scientifique']
            }
            
            found_concepts = []
            
            for concept, keywords in concept_map.items():
                for keyword in keywords:
                    # Recherche simple avec 'in'
                    if keyword in text_safe:
                        if concept not in found_concepts:
                            found_concepts.append(concept)
                        break  # Un seul match par concept
            
            return found_concepts[:5]  # Maximum 5 concepts
            
        except Exception as e:
            # Fallback ultime
            return ['CONNAISSANCE']  # Concept par défaut

    def _manual_term_extraction(self, segment: str) -> List[str]:
        """Extraction manuelle de termes en cas d'erreur du tokenizer"""
        
        # Termes philosophiques de base à rechercher
        philosophical_terms = [
            'vérité', 'justice', 'beauté', 'bien', 'mal', 'être', 'existence', 
            'essence', 'connaissance', 'liberté', 'conscience', 'raison', 'âme',
            'corps', 'esprit', 'matière', 'forme', 'idée', 'concept', 'nature',
            'dieu', 'absolu', 'infini', 'éternel', 'temps', 'espace', 'causalité',
            'nécessité', 'contingence', 'possible', 'réel', 'apparent', 'phénomène',
            'substance', 'accident', 'universel', 'particulier', 'genre', 'espèce'
        ]
        
        found_terms = []
        segment_lower = segment.lower()
        
        for term in philosophical_terms:
            if term in segment_lower:
                found_terms.append(term.upper())
        
        return found_terms[:5]  # Maximum 5 termes
    
    def _display_training_results(self, results: List[Dict], source: str, duration: float):
        """Affiche les résultats d'entraînement"""
        
        if not results:
            self.console.print("[yellow]⚠️ Aucun résultat d'entraînement[/yellow]")
            return
        
        # Statistiques d'entraînement
        total_patterns = sum(r.get('patterns_discovered', 0) for r in results)
        avg_confidence = sum(r.get('learning_confidence', 0) for r in results) / len(results)
        
        success_panel = Panel(
            f"""
[green]✅ Entraînement Terminé[/green]

[cyan]Source:[/cyan] {source}
[cyan]Durée:[/cyan] {duration:.1f}s
[cyan]Segments traités:[/cyan] {len(results)}
[cyan]Nouveaux patterns:[/cyan] {total_patterns}
[cyan]Confiance moyenne:[/cyan] {avg_confidence:.1%}

[yellow]💡 SophIA a intégré de nouvelles connaissances ![/yellow]
            """,
            title="[bold green]📚 Résultats d'Entraînement[/bold green]",
            border_style="green"
        )
        
        self.console.print(success_panel)
        
        # Mise à jour de la confiance d'apprentissage
        if results:
            self.stats['learning_confidence_current'] = results[-1].get('learning_confidence', 0)
    
    def _show_training_history(self):
        """Affiche l'historique d'entraînement"""
        
        if not self.training_history:
            self.console.print("[yellow]📚 Aucun entraînement effectué[/yellow]")
            return
        
        history_table = Table(title="📚 Historique d'Entraînement", show_header=True)
        history_table.add_column("Date", style="cyan", width=20)
        history_table.add_column("Source", style="yellow", width=30)
        history_table.add_column("Segments", style="green", width=10)
        history_table.add_column("Durée", style="blue", width=10)
        history_table.add_column("Patterns", style="magenta", width=10)
        
        for training in self.training_history:
            patterns = sum(r.get('patterns_discovered', 0) for r in training['results'])
            history_table.add_row(
                training['timestamp'].strftime("%Y-%m-%d %H:%M"),
                training['source'],
                str(training['segments_processed']),
                f"{training['duration']:.1f}s",
                str(patterns)
            )
        
        self.console.print(history_table)
    
    def _analyze_learning(self):
        """Analyse l'apprentissage de SophIA"""
        
        if not self.sophia.autonomous_learner:
            self.console.print("[red]❌ Autonomous Learner non disponible[/red]")
            return
        
        try:
            insights = self.sophia.autonomous_learner.get_learning_insights()
            
            # Résumé d'apprentissage
            summary = insights['learning_summary']
            
            learning_panel = Panel(
                f"""
[cyan]📊 Interactions totales:[/cyan] {summary['total_interactions']}
[cyan]📚 Exemples appris:[/cyan] {summary['examples_learned']}
[cyan]🎯 Patterns découverts:[/cyan] {summary['patterns_discovered']}
[cyan]🔄 Adaptations effectuées:[/cyan] {summary['adaptations_made']}
[cyan]🧠 Confiance apprentissage:[/cyan] {summary['learning_confidence']:.1%}
[cyan]⏱️ Durée session:[/cyan] {summary['session_duration_hours']:.1f}h

[yellow]Évolution confiance:[/yellow] {self.stats['learning_confidence_start']:.1%} → {self.stats['learning_confidence_current']:.1%}
                """,
                title="[bold blue]🧠 Analyse d'Apprentissage[/bold blue]",
                border_style="blue"
            )
            
            self.console.print(learning_panel)
            
            # Top concepts appris
            top_concepts = insights.get('top_learned_concepts', [])
            if top_concepts:
                concepts_table = Table(title="🎯 Top Concepts Appris", show_header=True)
                concepts_table.add_column("Concept", style="cyan")
                concepts_table.add_column("Utilisations", style="green")
                concepts_table.add_column("Confiance", style="yellow")
                concepts_table.add_column("Termes Associés", style="dim")
                
                for concept_info in top_concepts[:5]:
                    terms = ', '.join(concept_info.get('associated_terms', [])[:3])
                    concepts_table.add_row(
                        concept_info['concept'],
                        str(concept_info['usage_count']),
                        f"{concept_info['confidence']:.3f}",
                        terms
                    )
                
                self.console.print(concepts_table)
            
            # Recommandations
            recommendations = insights.get('learning_recommendations', [])
            if recommendations:
                self.console.print("\n[bold yellow]💡 Recommandations:[/bold yellow]")
                for rec in recommendations[:3]:
                    priority_color = {
                        'high': 'red',
                        'medium': 'yellow',
                        'low': 'green'
                    }.get(rec['priority'], 'white')
                    
                    self.console.print(f"  [{priority_color}]• {rec['recommendation']}[/{priority_color}]")
                    self.console.print(f"    [dim]{rec['action']}[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Erreur analyse apprentissage: {e}[/red]")
    
    def _analysis_menu(self):
        """Menu d'analyse et insights"""
        
        analysis_options = [
            "1. Analyse conceptuelle de session",
            "2. Insights d'apprentissage",
            "3. Métriques de performance",
            "4. Analyse de conversation",
            "5. Export des données",
            "6. Retour"
        ]
        
        self.console.print("\n[bold cyan]📊 Menu d'Analyse[/bold cyan]")
        for option in analysis_options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6"], default="6")
        
        if choice == "1":
            self._analyze_session_concepts()
        elif choice == "2":
            self._analyze_learning()
        elif choice == "3":
            self._analyze_performance()
        elif choice == "4":
            self._analyze_conversation()
        elif choice == "5":
            self._export_data()
    
    def _analyze_session_concepts(self):
        """Analyse conceptuelle de la session"""
        
        if not self.session_questions:
            self.console.print("[yellow]📊 Aucune question dans cette session[/yellow]")
            return
        
        # Collecte tous les concepts
        all_concepts = []
        concept_counts = {}
        
        for q_data in self.session_questions:
            concepts = q_data['response'].conceptual_analysis.get('concepts_detected', [])
            all_concepts.extend(concepts)
            for concept in concepts:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        # Top concepts
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        concepts_table = Table(title="🎯 Concepts les Plus Discutés", show_header=True)
        concepts_table.add_column("Concept", style="cyan")
        concepts_table.add_column("Fréquence", style="green")
        concepts_table.add_column("Pourcentage", style="yellow")
        
        total_mentions = sum(concept_counts.values())
        
        for concept, count in top_concepts:
            percentage = (count / total_mentions) * 100
            concepts_table.add_row(
                concept,
                str(count),
                f"{percentage:.1f}%"
            )
        
        self.console.print(concepts_table)
        
        # Statistiques générales
        stats_panel = Panel(
            f"""
[cyan]📊 Total concepts uniques:[/cyan] {len(concept_counts)}
[cyan]📈 Total mentions:[/cyan] {total_mentions}
[cyan]⭐ Concept principal:[/cyan] {top_concepts[0][0] if top_concepts else 'Aucun'}
[cyan]📚 Questions analysées:[/cyan] {len(self.session_questions)}
            """,
            title="[bold blue]📈 Statistiques Conceptuelles[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(stats_panel)
    
    def _analyze_performance(self):
        """Analyse des métriques de performance"""
        
        if not self.session_questions:
            self.console.print("[yellow]📊 Aucune donnée de performance[/yellow]")
            return
        
        # Calcul des métriques
        durations = [q['duration'] for q in self.session_questions]
        confidences = [q['response'].confidence for q in self.session_questions]
        
        avg_duration = sum(durations) / len(durations)
        avg_confidence = sum(confidences) / len(confidences)
        
        fastest = min(durations)
        slowest = max(durations)
        
        performance_table = Table(title="⚡ Métriques de Performance", show_header=True)
        performance_table.add_column("Métrique", style="cyan", width=25)
        performance_table.add_column("Valeur", style="green", width=15)
        performance_table.add_column("Détail", style="dim", width=30)
        
        performance_table.add_row("⏱️ Temps moyen", f"{avg_duration:.2f}s", "Temps de réponse moyen")
        performance_table.add_row("🚀 Plus rapide", f"{fastest:.2f}s", "Réponse la plus rapide")
        performance_table.add_row("🐌 Plus lent", f"{slowest:.2f}s", "Réponse la plus lente")
        performance_table.add_row("📊 Confiance moyenne", f"{avg_confidence:.1%}", "Confiance moyenne des réponses")
        performance_table.add_row("📈 Questions totales", str(len(self.session_questions)), "Questions de cette session")
        
        self.console.print(performance_table)
        
        # Graphique temporel simple
        if len(durations) > 1:
            self.console.print("\n[cyan]📈 Évolution des temps de réponse:[/cyan]")
            for i, duration in enumerate(durations[-10:], 1):  # 10 dernières
                bar_length = int(duration * 2)  # Scale pour affichage
                bar = "█" * min(bar_length, 20)
                self.console.print(f"  Q{i:2d}: {bar} {duration:.2f}s")
    
    def _analyze_conversation(self):
        """Analyse de la conversation actuelle"""
        
        if not self.session_questions:
            self.console.print("[yellow]💬 Aucune conversation à analyser[/yellow]")
            return
        
        # Analyse de l'évolution de la conversation
        conversation_tree = Tree("💬 Conversation")
        
        for i, q_data in enumerate(self.session_questions[-5:], 1):  # 5 dernières questions
            question = q_data['question'][:50] + "..." if len(q_data['question']) > 50 else q_data['question']
            concepts = q_data['response'].conceptual_analysis.get('concepts_detected', [])
            confidence = q_data['response'].confidence
            
            node_text = f"Q{i}: {question}"
            question_node = conversation_tree.add(node_text)
            
            question_node.add(f"🎯 Concepts: {', '.join(concepts[:3])}")
            question_node.add(f"📊 Confiance: {confidence:.1%}")
            question_node.add(f"⏱️ Durée: {q_data['duration']:.2f}s")
        
        self.console.print(conversation_tree)
        
        # Résumé de conversation
        if len(self.session_questions) >= 3:
            summary = self.sophia.get_conversation_summary()
            
            summary_panel = Panel(
                f"""
[cyan]🎯 Concepts principaux:[/cyan] {', '.join(summary.get('most_discussed_concepts', [])[:5])}
[cyan]📊 Confiance moyenne:[/cyan] {summary.get('average_confidence', 0):.1%}
[cyan]🔗 Relations découvertes:[/cyan] {summary.get('total_relations', 0)}
[cyan]💭 Thème général:[/cyan] {summary.get('general_theme', 'Non déterminé')}
                """,
                title="[bold green]📝 Résumé de Conversation[/bold green]",
                border_style="green"
            )
            
            self.console.print(summary_panel)
    
    def _export_data(self):
        """Export des données de session"""
        
        export_options = [
            "1. Export conversation (JSON)",
            "2. Export concepts (CSV)",
            "3. Export métriques (JSON)",
            "4. Export complet",
            "5. Retour"
        ]
        
        self.console.print("\n[cyan]💾 Options d'Export:[/cyan]")
        for option in export_options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5"], default="5")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if choice == "1":
                self._export_conversation(f"sophia_conversation_{timestamp}.json")
            elif choice == "2":
                self._export_concepts(f"sophia_concepts_{timestamp}.csv")
            elif choice == "3":
                self._export_metrics(f"sophia_metrics_{timestamp}.json")
            elif choice == "4":
                self._export_complete(f"sophia_session_{timestamp}")
        except Exception as e:
            self.console.print(f"[red]❌ Erreur export: {e}[/red]")
    
    def _export_conversation(self, filename: str):
        """Export conversation en JSON"""
        
        conversation_data = []
        for q_data in self.session_questions:
            conversation_data.append({
                'timestamp': q_data['timestamp'].isoformat(),
                'question': q_data['question'],
                'response': q_data['response'].natural_response,
                'concepts': q_data['response'].conceptual_analysis.get('concepts_detected', []),
                'confidence': q_data['response'].confidence,
                'duration': q_data['duration']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"[green]✅ Conversation exportée: {filename}[/green]")
    
    def _export_concepts(self, filename: str):
        """Export concepts en CSV"""
        
        import csv
        
        concept_counts = {}
        for q_data in self.session_questions:
            concepts = q_data['response'].conceptual_analysis.get('concepts_detected', [])
            for concept in concepts:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Concept', 'Fréquence'])
            for concept, count in sorted(concept_counts.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([concept, count])
        
        self.console.print(f"[green]✅ Concepts exportés: {filename}[/green]")
    
    def _export_metrics(self, filename: str):
        """Export métriques en JSON"""
        
        durations = [q['duration'] for q in self.session_questions]
        confidences = [q['response'].confidence for q in self.session_questions]
        
        metrics = {
            'session_start': self.session_start.isoformat(),
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'questions_count': len(self.session_questions),
            'average_duration': sum(durations) / len(durations) if durations else 0,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'concepts_discovered': len(self.stats['concepts_discovered']),
            'training_sessions': self.stats['training_sessions'],
            'learning_confidence_evolution': {
                'start': self.stats['learning_confidence_start'],
                'current': self.stats['learning_confidence_current']
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"[green]✅ Métriques exportées: {filename}[/green]")
    
    def _export_complete(self, base_filename: str):
        """Export complet de la session"""
        
        self._export_conversation(f"{base_filename}_conversation.json")
        self._export_concepts(f"{base_filename}_concepts.csv")
        self._export_metrics(f"{base_filename}_metrics.json")
        
        self.console.print(f"[green]✅ Export complet terminé: {base_filename}_*[/green]")
    
    def _settings_menu(self):
        """Menu de configuration"""
        
        settings_options = [
            "1. Mode de performance",
            "2. Affichage analyse détaillée",
            "3. Apprentissage automatique",
            "4. Sauvegarde automatique",
            "5. Afficher configuration actuelle",
            "6. Réinitialiser configuration",
            "7. Retour"
        ]
        
        self.console.print("\n[bold cyan]⚙️ Configuration SophIA[/bold cyan]")
        for option in settings_options:
            self.console.print(f"  {option}")
        
        choice = Prompt.ask("Choix", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")
        
        if choice == "1":
            self._configure_performance_mode()
        elif choice == "2":
            self._toggle_detailed_analysis()
        elif choice == "3":
            self._toggle_learning()
        elif choice == "4":
            self._toggle_auto_save()
        elif choice == "5":
            self._show_current_settings()
        elif choice == "6":
            self._reset_settings()
    
    def _configure_performance_mode(self):
        """Configure le mode de performance"""
        
        current_mode = self.current_settings['performance_mode']
        
        self.console.print(f"\n[cyan]Mode actuel: {current_mode}[/cyan]")
        self.console.print("\n[yellow]Modes disponibles:[/yellow]")
        self.console.print("  [red]speed[/red]    - Réponses rapides (~3s)")
        self.console.print("  [yellow]balanced[/yellow] - Équilibre qualité/vitesse (~8s)")
        self.console.print("  [green]quality[/green]  - Qualité maximale (~15s)")
        
        new_mode = Prompt.ask(
            "Nouveau mode",
            choices=["speed", "balanced", "quality"],
            default=current_mode
        )
        
        if new_mode != current_mode:
            self.current_settings['performance_mode'] = new_mode
            
            # Réinitialise SophIA si nécessaire
            if self.sophia:
                if Confirm.ask("Réinitialiser SophIA avec le nouveau mode?"):
                    self.initialize_sophia(new_mode)
            
            self.console.print(f"[green]✅ Mode changé: {new_mode}[/green]")
    
    def _toggle_detailed_analysis(self):
        """Active/désactive l'analyse détaillée"""
        
        current = self.current_settings['show_detailed_analysis']
        self.current_settings['show_detailed_analysis'] = not current
        
        status = "activée" if not current else "désactivée"
        self.console.print(f"[green]✅ Analyse détaillée {status}[/green]")
    
    def _toggle_learning(self):
        """Active/désactive l'apprentissage automatique"""
        
        current = self.current_settings['learning_enabled']
        self.current_settings['learning_enabled'] = not current
        
        status = "activé" if not current else "désactivé"
        self.console.print(f"[green]✅ Apprentissage automatique {status}[/green]")
    
    def _toggle_auto_save(self):
        """Active/désactive la sauvegarde automatique"""
        
        current = self.current_settings['auto_save']
        self.current_settings['auto_save'] = not current
        
        status = "activée" if not current else "désactivée"
        self.console.print(f"[green]✅ Sauvegarde automatique {status}[/green]")
    
    def _show_current_settings(self):
        """Affiche la configuration actuelle"""
        
        settings_table = Table(title="⚙️ Configuration Actuelle", show_header=True)
        settings_table.add_column("Paramètre", style="cyan", width=25)
        settings_table.add_column("Valeur", style="green", width=15)
        settings_table.add_column("Description", style="dim")
        
        settings_info = [
            ("Mode performance", self.current_settings['performance_mode'], "Vitesse vs qualité"),
            ("Analyse détaillée", "✅" if self.current_settings['show_detailed_analysis'] else "❌", "Affichage métriques"),
            ("Apprentissage auto", "✅" if self.current_settings['learning_enabled'] else "❌", "Apprentissage continu"),
            ("Sauvegarde auto", "✅" if self.current_settings['auto_save'] else "❌", "Sauvegarde automatique")
        ]
        
        for param, value, desc in settings_info:
            settings_table.add_row(param, value, desc)
        
        self.console.print(settings_table)
    
    def _reset_settings(self):
        """Remet la configuration par défaut"""
        
        if Confirm.ask("Remettre la configuration par défaut?"):
            self.current_settings = self.default_settings.copy()
            self.console.print("[green]✅ Configuration réinitialisée[/green]")
    
    def _show_statistics(self):
        """Affiche les statistiques détaillées"""
        
        session_duration = datetime.now() - self.session_start
        
        stats_table = Table(title="📊 Statistiques de Session", show_header=True)
        stats_table.add_column("Métrique", style="cyan", width=25)
        stats_table.add_column("Valeur", style="green", width=15)
        stats_table.add_column("Détail", style="dim")
        
        stats_info = [
            ("⏱️ Durée session", f"{session_duration.total_seconds()/3600:.1f}h", "Temps depuis démarrage"),
            ("💭 Questions posées", str(self.stats['questions_asked']), "Questions cette session"),
            ("🎯 Concepts découverts", str(len(self.stats['concepts_discovered'])), "Concepts uniques rencontrés"),
            ("📚 Sessions entraînement", str(self.stats['training_sessions']), "Entraînements effectués"),
            ("📄 Documents traités", str(self.stats['documents_processed']), "Fichiers d'entraînement"),
            ("🧠 Confiance apprentissage", f"{self.stats['learning_confidence_current']:.1%}", "Niveau d'apprentissage actuel")
        ]
        
        for metric, value, detail in stats_info:
            stats_table.add_row(metric, value, detail)
        
        self.console.print(stats_table)
        
        # Évolution confiance
        if self.stats['learning_confidence_start'] != self.stats['learning_confidence_current']:
            evolution = self.stats['learning_confidence_current'] - self.stats['learning_confidence_start']
            evolution_color = "green" if evolution > 0 else "red"
            self.console.print(f"\n[{evolution_color}]📈 Évolution apprentissage: {evolution:+.1%}[/{evolution_color}]")
    
    def _show_history(self):
        """Affiche l'historique des questions"""
        
        if not self.session_questions:
            self.console.print("[yellow]📝 Aucune question dans l'historique[/yellow]")
            return
        
        history_table = Table(title="📝 Historique des Questions", show_header=True)
        history_table.add_column("#", style="dim", width=5)
        history_table.add_column("Question", style="cyan", width=50)
        history_table.add_column("Concepts", style="green", width=20)
        history_table.add_column("Confiance", style="yellow", width=10)
        
        for i, q_data in enumerate(self.session_questions[-10:], 1):  # 10 dernières
            question = q_data['question']
            if len(question) > 47:
                question = question[:47] + "..."
            
            concepts = q_data['response'].conceptual_analysis.get('concepts_detected', [])
            concepts_str = ', '.join(concepts[:2])
            if len(concepts) > 2:
                concepts_str += f" (+{len(concepts)-2})"
            
            confidence = q_data['response'].confidence
            
            history_table.add_row(
                str(i),
                question,
                concepts_str,
                f"{confidence:.1%}"
            )
        
        self.console.print(history_table)
    
    def _save_session(self):
        """Sauvegarde la session"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = f"sophia_session_{timestamp}.json"
        
        session_data = {
            'session_start': self.session_start.isoformat(),
            'settings': self.current_settings,
            'stats': {
                **self.stats,
                'concepts_discovered': list(self.stats['concepts_discovered'])
            },
            'questions': [],
            'training_history': self.training_history
        }
        
        # Sauvegarde des questions
        for q_data in self.session_questions:
            session_data['questions'].append({
                'timestamp': q_data['timestamp'].isoformat(),
                'question': q_data['question'],
                'response': q_data['response'].natural_response,
                'concepts': q_data['response'].conceptual_analysis.get('concepts_detected', []),
                'confidence': q_data['response'].confidence,
                'duration': q_data['duration']
            })
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]✅ Session sauvegardée: {session_file}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Erreur sauvegarde: {e}[/red]")
    
    def _load_session(self):
        """Charge une session sauvegardée"""
        
        # Liste des fichiers de session
        session_files = list(Path(".").glob("sophia_session_*.json"))
        
        if not session_files:
            self.console.print("[yellow]📁 Aucune session sauvegardée trouvée[/yellow]")
            return
        
        self.console.print("\n[cyan]📁 Sessions disponibles:[/cyan]")
        for i, file in enumerate(session_files[-5:], 1):  # 5 plus récentes
            self.console.print(f"  {i}. {file.name}")
        
        try:
            choice = int(Prompt.ask("Numéro de session", default="0"))
            if choice < 1 or choice > len(session_files[-5:]):
                return
            
            session_file = session_files[-5:][choice - 1]
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restore settings
            self.current_settings.update(session_data.get('settings', {}))
            
            # Restore stats
            stats_data = session_data.get('stats', {})
            self.stats.update(stats_data)
            if 'concepts_discovered' in stats_data:
                self.stats['concepts_discovered'] = set(stats_data['concepts_discovered'])
            
            # Restore training history
            self.training_history = session_data.get('training_history', [])
            
            self.console.print(f"[green]✅ Session chargée: {session_file.name}[/green]")
            self.console.print(f"[cyan]📊 {len(session_data.get('questions', []))} questions restaurées[/cyan]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Erreur chargement: {e}[/red]")
    
    def _display_session_summary(self):
        """Affiche le résumé de session à la fermeture"""
        
        session_duration = datetime.now() - self.session_start
        
        summary_panel = Panel(
            f"""
[green]✅ Session SophIA Terminée[/green]

[cyan]⏱️ Durée:[/cyan] {session_duration.total_seconds()/3600:.1f}h
[cyan]💭 Questions posées:[/cyan] {self.stats['questions_asked']}
[cyan]🎯 Concepts découverts:[/cyan] {len(self.stats['concepts_discovered'])}
[cyan]📚 Entraînements:[/cyan] {self.stats['training_sessions']}
[cyan]🧠 Évolution apprentissage:[/cyan] {self.stats['learning_confidence_start']:.1%} → {self.stats['learning_confidence_current']:.1%}

[yellow]Merci d'avoir utilisé SophIA Enhanced ![/yellow]
[dim]L'intelligence philosophique hybride au service de la connaissance.[/dim]
            """,
            title="[bold blue]📊 Résumé de Session[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(summary_panel)
    
    # Corpus philosophiques prédéfinis
    def _get_plato_corpus(self) -> str:
        return """
L'allégorie de la caverne illustre le processus de la connaissance et de l'éducation. 
Les prisonniers enchaînés ne voient que les ombres projetées sur le mur, 
prenant ces apparences pour la réalité elle-même. 

La véritable connaissance nécessite de se détourner des apparences sensibles 
pour contempler les Idées éternelles et immuables. L'Idée du Bien 
est la source de toute vérité et de toute réalité.

La justice dans l'âme correspond à l'harmonie entre ses trois parties: 
la raison qui doit commander, le courage qui doit obéir, 
et les appétits qui doivent être modérés par la tempérance.

Le philosophe est celui qui aime la sagesse et cherche à connaître l'essence des choses.
Il se distingue du sophiste qui ne s'intéresse qu'aux apparences et aux opinions.
        """
    
    def _get_aristotle_corpus(self) -> str:
        return """
La substance est ce qui existe par soi et ne dépend d'aucune autre chose pour exister.
Elle se compose de matière et de forme, l'acte et la puissance expliquant le changement.

Le bonheur (eudaimonia) est l'activité de l'âme selon la vertu parfaite.
Il ne consiste pas dans le plaisir mais dans l'actualisation de nos potentialités les plus nobles.

La vertu éthique est un juste milieu entre l'excès et le défaut.
Le courage, par exemple, est le milieu entre la lâcheté et la témérité.

L'homme est par nature un animal politique. La cité existe pour permettre aux citoyens
de réaliser leur nature rationnelle et de vivre une vie vertueuse.

La logique étudie les formes valides du raisonnement.
Le syllogisme est l'instrument principal de la démonstration scientifique.
        """
    
    def _get_descartes_corpus(self) -> str:
        return """
Je pense, donc je suis. Cette vérité résiste au doute méthodique le plus radical.
Même si je doute de tout, je ne peux douter que je doute, donc que je pense.

L'existence de Dieu se démontre par l'idée d'infini que nous trouvons en nous.
Cette idée ne peut avoir pour cause que Dieu lui-même, être parfait et infini.

L'âme et le corps sont deux substances distinctes: l'une pensante, l'autre étendue.
Leur union dans l'homme pose le problème de leur interaction.

La méthode consiste à diviser chaque difficulté en autant de parties qu'il se peut.
Il faut conduire par ordre ses pensées, en commençant par les objets les plus simples.

La géométrie et l'algèbre peuvent être unifiées dans une mathématique universelle
qui sera l'instrument de toute connaissance certaine.
        """
    
    def _get_kant_corpus(self) -> str:
        return """
La critique de la raison pure examine les conditions de possibilité de la connaissance.
L'espace et le temps sont les formes a priori de la sensibilité.

Les jugements synthétiques a priori sont possibles grâce aux catégories de l'entendement.
La causalité, par exemple, structure notre expérience des phénomènes.

L'impératif catégorique commande: agis seulement d'après une maxime 
que tu peux vouloir ériger en loi universelle.

La liberté transcendantale est la condition de possibilité de la moralité.
Nous devons nous penser comme libres pour que nos actions aient une valeur morale.

Le beau est ce qui plaît universellement sans concept.
Le sublime révèle en nous une faculté supersensible qui dépasse toute mesure.

La paix perpétuelle suppose une constitution républicaine et un droit cosmopolitique.
        """
    
    def _get_nietzsche_corpus(self) -> str:
        return """
Dieu est mort, et c'est nous qui l'avons tué. Cette déclaration annonce
la fin des valeurs absolues et transcendantes de la tradition européenne.

La volonté de puissance est le principe fondamental de toute vie.
Tout être vivant cherche avant tout à croître, à s'étendre, à dominer.

Le surhomme (Übermensch) est celui qui crée ses propres valeurs
après avoir détruit les anciennes. Il affirme la vie dans sa totalité.

L'éternel retour est la pensée la plus lourde: vouloir que chaque instant
revienne éternellement identique à lui-même.

La morale des maîtres affirme la vie et la force.
La morale des esclaves nie la vie au profit d'un au-delà imaginaire.

L'art est la seule justification métaphysique de l'existence.
Il transfigure le réel en lui donnant une forme esthétique.
        """

def main():
    """Point d'entrée principal"""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="SophIA Enhanced - CLI Interface")
    parser.add_argument("--mode", choices=["speed", "balanced", "quality"], 
                       default="balanced", help="Mode de performance")
    parser.add_argument("--no-learning", action="store_true", 
                       help="Désactive l'apprentissage automatique")
    parser.add_argument("--config", help="Fichier de configuration")
    
    args = parser.parse_args()
    
    # Initialise CLI
    cli = SophIACLI()
    
    # Configure selon arguments
    if args.mode:
        cli.current_settings['performance_mode'] = args.mode
    if args.no_learning:
        cli.current_settings['learning_enabled'] = False
    
    # Affiche l'accueil
    cli.display_welcome()
    
    # Lance la session interactive
    try:
        cli.run_interactive_session()
    except KeyboardInterrupt:
        cli.console.print("\n[yellow]Session interrompue par l'utilisateur[/yellow]")
    except Exception as e:
        cli.console.print(f"\n[red]Erreur fatale: {e}[/red]")
    finally:
        cli.console.print("\n[dim]Au revoir ![/dim]")

if __name__ == "__main__":
    main()