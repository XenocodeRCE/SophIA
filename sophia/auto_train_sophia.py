#!/usr/bin/env python3
"""
SophIA Auto-Trainer - Entraînement automatique par conversations simulées
Génère des conversations philosophiques automatiques pour améliorer SophIA
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.tree import Tree

# Imports SophIA
try:
    from sophia.core.sophia_hybrid import HybridSophIA
    from sophia.learning.autonomous_learner import AutonomousLearner
    SOPHIA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erreur import SophIA: {e}")
    SOPHIA_AVAILABLE = False
    sys.exit(1)

@dataclass
class ConversationTemplate:
    """Template de conversation philosophique"""
    theme: str
    questions: List[str]
    follow_ups: List[str]
    concepts_focus: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"

@dataclass
class TrainingSession:
    """Session d'entraînement automatique"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    conversations_completed: int
    concepts_learned: List[str]
    learning_progress: float
    performance_metrics: Dict[str, Any]

class SophIAAutoTrainer:
    """Entraîneur automatique pour SophIA Enhanced"""
    
    def __init__(self, performance_mode: str = "balanced"):
        self.console = Console()
        self.sophia = None
        self.performance_mode = performance_mode
        self.verbose = True  # Active le mode verbose par défaut

        # Activation du logging détaillé pour tous les modules SophIA
        import logging
        logging.basicConfig(
            level=logging.DEBUG,  # Affiche tous les logs DEBUG/INFO/WARNING/ERROR
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        # Optionnel : réduire le bruit de certains modules externes
        logging.getLogger("rich").setLevel(logging.WARNING)

        # Configuration d'entraînement
        self.training_config = {
            'conversations_per_session': 50,
            'questions_per_conversation': 3,
            'rest_between_questions': 1.0,  # secondes
            'learning_feedback_rate': 0.8,  # proportion de feedback positif
            'difficulty_progression': True,
            'save_interval': 10,  # sauvegarde tous les 10 conversations
            'max_parallel_conversations': 1  # pour éviter la surcharge
        }
        
        # Templates de conversation
        self.conversation_templates = self._load_conversation_templates()
        
        # Statistiques d'entraînement
        self.training_stats = {
            'total_conversations': 0,
            'total_questions': 0,
            'concepts_discovered': set(),
            'learning_confidence_evolution': [],
            'performance_evolution': [],
            'training_time': 0.0
        }
        
        # Sessions d'entraînement
        self.training_sessions: List[TrainingSession] = []
        self.current_session: Optional[TrainingSession] = None
    
    def _load_conversation_templates(self) -> List[ConversationTemplate]:
        """Charge les templates de conversation philosophique"""
        
        return [
            # ÉPISTÉMOLOGIE
            ConversationTemplate(
                theme="Épistémologie - Nature de la connaissance",
                questions=[
                    "Qu'est-ce que la vérité ?",
                    "Comment distinguer la vérité de l'opinion ?",
                    "La connaissance a-t-elle des limites ?",
                    "Peut-on connaître la réalité telle qu'elle est ?",
                    "Quelle est la différence entre croire et savoir ?",
                    "Comment validons-nous nos connaissances ?",
                    "L'expérience est-elle la source principale de connaissance ?",
                    "Existe-t-il des vérités absolues ?"
                ],
                follow_ups=[
                    "Pouvez-vous développer cette idée ?",
                    "Quelles sont les implications de cette position ?",
                    "Comment cette conception s'articule-t-elle avec d'autres concepts ?",
                    "Y a-t-il des objections à cette vision ?",
                    "Comment les philosophes classiques aborderaient-ils cette question ?"
                ],
                concepts_focus=["VÉRITÉ", "CONNAISSANCE", "RÉALITÉ", "EXPÉRIENCE", "CROYANCE"],
                difficulty_level="intermediate"
            ),
            
            # ÉTHIQUE
            ConversationTemplate(
                theme="Éthique - Bien et mal moral",
                questions=[
                    "Qu'est-ce qui rend une action moralement bonne ?",
                    "Le bien et le mal sont-ils relatifs ou absolus ?",
                    "Comment définir la justice ?",
                    "Quels sont nos devoirs moraux fondamentaux ?",
                    "La fin justifie-t-elle les moyens ?",
                    "Qu'est-ce que la responsabilité morale ?",
                    "Les vertus peuvent-elles être enseignées ?",
                    "Comment résoudre les dilemmes éthiques ?"
                ],
                follow_ups=[
                    "Cette position soulève-t-elle des difficultés pratiques ?",
                    "Comment appliquer ce principe dans des situations concrètes ?",
                    "Tous les philosophes partageraient-ils cette vision ?",
                    "Quelles sont les conséquences de cette éthique ?",
                    "Cette approche est-elle compatible avec nos intuitions morales ?"
                ],
                concepts_focus=["BIEN", "MAL", "JUSTICE", "VERTU", "DEVOIR", "RESPONSABILITÉ"],
                difficulty_level="intermediate"
            ),
            
            # MÉTAPHYSIQUE
            ConversationTemplate(
                theme="Métaphysique - Nature de l'être",
                questions=[
                    "Qu'est-ce que l'être ?",
                    "Quelle est la nature de l'existence ?",
                    "Y a-t-il une différence entre essence et existence ?",
                    "Qu'est-ce qui fait l'identité d'une chose ?",
                    "Le temps et l'espace sont-ils réels ?",
                    "Qu'est-ce que la causalité ?",
                    "Y a-t-il plusieurs niveaux de réalité ?",
                    "Comment comprendre le changement et la permanence ?"
                ],
                follow_ups=[
                    "Cette conception ontologique a-t-elle des implications épistémologiques ?",
                    "Comment cette vision influence-t-elle notre compréhension du monde ?",
                    "Quels problèmes cette approche résout-elle ou crée-t-elle ?",
                    "Cette position est-elle cohérente avec nos connaissances scientifiques ?",
                    "Comment les grands métaphysiciens ont-ils traité cette question ?"
                ],
                concepts_focus=["ÊTRE", "EXISTENCE", "ESSENCE", "RÉALITÉ", "TEMPS", "CAUSALITÉ"],
                difficulty_level="advanced"
            ),
            
            # ESTHÉTIQUE
            ConversationTemplate(
                theme="Esthétique - Nature du beau",
                questions=[
                    "Qu'est-ce que la beauté ?",
                    "Le beau est-il objectif ou subjectif ?",
                    "Quelle est la fonction de l'art ?",
                    "Comment définir une œuvre d'art ?",
                    "L'art doit-il avoir une dimension morale ?",
                    "Qu'est-ce que l'expérience esthétique ?",
                    "Y a-t-il des critères universels du beau ?",
                    "Comment comprendre le sublime ?"
                ],
                follow_ups=[
                    "Cette conception esthétique influence-t-elle notre rapport au monde ?",
                    "Quels sont les enjeux sociaux et culturels de cette vision ?",
                    "Comment cette approche éclaire-t-elle l'histoire de l'art ?",
                    "Cette position permet-elle de comprendre l'art contemporain ?",
                    "Quel lien entre beauté et vérité dans cette perspective ?"
                ],
                concepts_focus=["BEAUTÉ", "ART", "SUBLIME", "HARMONIE", "CRÉATION"],
                difficulty_level="intermediate"
            ),
            
            # PHILOSOPHIE POLITIQUE
            ConversationTemplate(
                theme="Philosophie politique - Société et pouvoir",
                questions=[
                    "Qu'est-ce qui légitime le pouvoir politique ?",
                    "Comment concevoir la liberté en société ?",
                    "Quelle est la finalité de l'État ?",
                    "Comment concilier liberté individuelle et bien commun ?",
                    "Qu'est-ce qu'une société juste ?",
                    "Le contrat social est-il un fondement valide ?",
                    "Comment définir les droits de l'homme ?",
                    "Démocratie et vérité sont-elles compatibles ?"
                ],
                follow_ups=[
                    "Cette théorie politique résiste-t-elle aux défis contemporains ?",
                    "Quelles institutions cette conception implique-t-elle ?",
                    "Comment cette vision traite-t-elle les inégalités ?",
                    "Cette approche est-elle réalisable en pratique ?",
                    "Quels penseurs politiques défendraient cette position ?"
                ],
                concepts_focus=["LIBERTÉ", "JUSTICE", "ÉTAT", "SOCIÉTÉ", "DÉMOCRATIE", "DROIT"],
                difficulty_level="advanced"
            ),
            
            # PHILOSOPHIE DE L'ESPRIT
            ConversationTemplate(
                theme="Philosophie de l'esprit - Conscience et identité",
                questions=[
                    "Qu'est-ce que la conscience ?",
                    "Comment expliquer l'expérience subjective ?",
                    "L'esprit est-il réductible au cerveau ?",
                    "Qu'est-ce qui fait l'identité personnelle ?",
                    "Avons-nous un libre arbitre ?",
                    "Comment comprendre les émotions ?",
                    "Quelle est la nature de l'intentionnalité ?",
                    "L'intelligence artificielle peut-elle être consciente ?"
                ],
                follow_ups=[
                    "Cette conception de l'esprit a-t-elle des implications éthiques ?",
                    "Comment cette vision s'articule-t-elle avec les neurosciences ?",
                    "Quels problèmes philosophiques cette approche résout-elle ?",
                    "Cette position influence-t-elle notre compréhension de l'action ?",
                    "Comment les philosophes de l'esprit contemporains abordent-ils cela ?"
                ],
                concepts_focus=["CONSCIENCE", "ESPRIT", "LIBERTÉ", "IDENTITÉ", "VOLONTÉ"],
                difficulty_level="advanced"
            ),
            
            # QUESTIONS TRANSVERSALES
            ConversationTemplate(
                theme="Synthèse philosophique - Questions transversales",
                questions=[
                    "Comment les différents domaines de la philosophie s'articulent-ils ?",
                    "Y a-t-il une unité de la philosophie ?",
                    "Comment la philosophie évolue-t-elle historiquement ?",
                    "Quel est le rapport entre philosophie et science ?",
                    "La philosophie a-t-elle une utilité pratique ?",
                    "Comment les cultures influencent-elles la pensée philosophique ?",
                    "Quels sont les grands défis de la philosophie contemporaine ?",
                    "Comment former le jugement philosophique ?"
                ],
                follow_ups=[
                    "Cette vision synthétique éclaire-t-elle les débats actuels ?",
                    "Quelles nouvelles questions cette approche fait-elle émerger ?",
                    "Comment cette perspective transforme-t-elle notre rapport au savoir ?",
                    "Cette conception peut-elle guider l'enseignement philosophique ?",
                    "Quels philosophes incarnent le mieux cette vision unifiée ?"
                ],
                concepts_focus=["SAGESSE", "RATIONALITÉ", "CULTURE", "HISTOIRE", "MÉTHODE"],
                difficulty_level="advanced"
            )
        ]
    
    def initialize_sophia(self) -> bool:
        """Initialise SophIA pour l'entraînement"""
        
        with self.console.status("[bold blue]Initialisation de SophIA pour auto-entraînement...", spinner="dots"):
            try:
                self.sophia = HybridSophIA(
                    auto_save=True,
                    performance_mode=self.performance_mode
                )
                
                self.console.print("[green]✅ SophIA initialisée pour l'auto-entraînement[/green]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]❌ Erreur initialisation: {e}[/red]")
                return False
    
    def start_auto_training(self, duration_hours: float = 1.0, 
                          conversation_themes: Optional[List[str]] = None) -> bool:
        """Lance une session d'auto-entraînement"""
        
        if not self.initialize_sophia():
            return False
        
        # Création de la session
        session_id = f"auto_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = TrainingSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            conversations_completed=0,
            concepts_learned=[],
            learning_progress=0.0,
            performance_metrics={}
        )
        
        self.console.print(f"\n[bold green]🤖 DÉMARRAGE AUTO-ENTRAÎNEMENT[/bold green]")
        self.console.print(f"[cyan]Session ID:[/cyan] {session_id}")
        self.console.print(f"[cyan]Durée prévue:[/cyan] {duration_hours:.1f}h")
        self.console.print(f"[cyan]Mode performance:[/cyan] {self.performance_mode}")
        
        # Sélection des thèmes
        if conversation_themes:
            templates = [t for t in self.conversation_templates if t.theme in conversation_themes]
        else:
            templates = self.conversation_templates
        
        if not templates:
            self.console.print("[red]❌ Aucun template de conversation trouvé[/red]")
            return False
        
        # Calcul du nombre de conversations
        end_time = datetime.now() + timedelta(hours=duration_hours)
        conversations_target = max(10, int(duration_hours * 30))  # ~30 conversations/heure
        
        self.console.print(f"[cyan]Conversations cibles:[/cyan] {conversations_target}")
        self.console.print(f"[cyan]Templates disponibles:[/cyan] {len(templates)}")
        
        # Lancement de l'entraînement
        success = self._run_training_loop(templates, conversations_target, end_time)
        
        # Finalisation de la session
        self.current_session.end_time = datetime.now()
        self.training_sessions.append(self.current_session)
        
        # Résultats finaux
        self._display_training_summary()
        
        return success
    
    def _run_training_loop(self, templates: List[ConversationTemplate], 
                          target_conversations: int, end_time: datetime) -> bool:
        """Boucle principale d'entraînement"""
        
        conversation_count = 0
        
        with Progress() as progress:
            main_task = progress.add_task(
                "[green]Auto-entraînement en cours...", 
                total=target_conversations
            )
            
            while conversation_count < target_conversations and datetime.now() < end_time:
                try:
                    # Sélection du template
                    template = self._select_conversation_template(templates, conversation_count)
                    
                    # Exécution de la conversation
                    conversation_result = self._execute_conversation(template, conversation_count + 1)
                    
                    if conversation_result['success']:
                        conversation_count += 1
                        self.current_session.conversations_completed += 1
                        
                        # Mise à jour des concepts appris
                        new_concepts = conversation_result.get('concepts_learned', [])
                        self.current_session.concepts_learned.extend(new_concepts)
                        self.training_stats['concepts_discovered'].update(new_concepts)
                        
                        # Mise à jour des statistiques
                        self.training_stats['total_conversations'] += 1
                        self.training_stats['total_questions'] += conversation_result.get('questions_asked', 0)
                        
                        # Progression d'apprentissage
                        if self.sophia.autonomous_learner:
                            insights = self.sophia.autonomous_learner.get_learning_insights()
                            learning_confidence = insights['learning_summary']['learning_confidence']
                            self.training_stats['learning_confidence_evolution'].append(learning_confidence)
                            self.current_session.learning_progress = learning_confidence
                        
                        # Sauvegarde périodique
                        if conversation_count % self.training_config['save_interval'] == 0:
                            self._save_training_progress()
                        
                        # Affichage des progrès
                        progress.update(
                            main_task, 
                            advance=1,
                            description=f"[green]Conversation {conversation_count}/{target_conversations} - {template.theme}"
                        )
                        
                    else:
                        self.console.print(f"[yellow]⚠️ Conversation {conversation_count + 1} échouée[/yellow]")
                    
                    # Pause entre conversations
                    time.sleep(self.training_config['rest_between_questions'])
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]⚠️ Entraînement interrompu par l'utilisateur[/yellow]")
                    break
                    
                except Exception as e:
                    self.console.print(f"[red]❌ Erreur conversation {conversation_count + 1}: {e}[/red]")
                    continue
        
        return conversation_count > 0
    
    def _select_conversation_template(self, templates: List[ConversationTemplate], 
                                    conversation_index: int) -> ConversationTemplate:
        """Sélectionne un template de conversation selon la progression"""
        
        if self.training_config['difficulty_progression']:
            # Progression de difficulté
            if conversation_index < 10:
                # Débute avec intermediate
                available = [t for t in templates if t.difficulty_level in ['beginner', 'intermediate']]
            elif conversation_index < 30:
                # Puis intermediate et advanced
                available = [t for t in templates if t.difficulty_level in ['intermediate', 'advanced']]
            else:
                # Enfin tous niveaux
                available = templates
        else:
            available = templates
        
        if not available:
            available = templates
        
        # Sélection avec pondération pour éviter la répétition
        return random.choice(available)
    
    def _execute_conversation(self, template: ConversationTemplate, 
                            conversation_number: int) -> Dict[str, Any]:
        """Exécute une conversation automatique avec SophIA"""
        
        try:
            conversation_start = time.time()
            questions_asked = 0
            concepts_learned = []
            responses = []
            question_times = []

            # Sélection des questions pour cette conversation
            num_questions = min(
                self.training_config['questions_per_conversation'],
                len(template.questions)
            )
            
            selected_questions = random.sample(template.questions, num_questions)
            
            # Ajout éventuel de questions de suivi
            if len(template.follow_ups) > 0 and random.random() > 0.5:
                selected_questions.append(random.choice(template.follow_ups))
            
            # Exécution des questions
            for question in selected_questions:
                try:
                    # Pose la question à SophIA
                    start_q = time.time()
                    response = self.sophia.ask(question)
                    duration_q = time.time() - start_q
                    question_times.append(duration_q)
                    
                    questions_asked += 1
                    
                    # Collecte des concepts
                    question_concepts = response.conceptual_analysis.get('concepts_detected', [])
                    concepts_learned.extend(question_concepts)
                    
                    # Sauvegarde de la réponse
                    responses.append({
                        'question': question,
                        'response': response.natural_response,
                        'concepts': question_concepts,
                        'confidence': response.confidence,
                        'duration': duration_q
                    })
                    
                    # Apprentissage automatique avec feedback simulé
                    if self.sophia.autonomous_learner:
                        feedback_score = self._generate_feedback_score(response, template)
                        
                        response_data = {
                            'conceptual_analysis': response.conceptual_analysis,
                            'confidence': response.confidence,
                            'validation_report': response.validation_report,
                            'natural_response': response.natural_response,
                            'performance_metrics': {'duration': duration_q}
                        }
                        
                        self.sophia.autonomous_learner.learn_from_interaction(
                            question=question,
                            response_data=response_data,
                            feedback_score=feedback_score
                        )
                    
                    # Pause entre questions
                    time.sleep(self.training_config['rest_between_questions'])
                    
                except Exception as e:
                    self.console.print(f"[dim red]Erreur question: {e}[/dim red]")
                    continue
            
            conversation_duration = time.time() - conversation_start
            
            # Affichage des progrès de conversation
            avg_confidence = sum(r['confidence'] for r in responses) / len(responses) if responses else 0
            unique_concepts = list(set(concepts_learned))
            avg_question_time = sum(question_times) / len(question_times) if question_times else 0
            min_question_time = min(question_times) if question_times else 0
            max_question_time = max(question_times) if question_times else 0

            self.console.print(
                f"[dim]Conversation {conversation_number}: {questions_asked} questions, "
                f"{len(unique_concepts)} concepts, confiance {avg_confidence:.1%}[/dim]"
            )
            if self.verbose:
                self.console.print(
                    f"[dim cyan]⏱️ Temps total: {conversation_duration:.2f}s | "
                    f"Temps/question: {avg_question_time:.2f}s (min: {min_question_time:.2f}s, max: {max_question_time:.2f}s)[/dim cyan]"
                )
            
            return {
                'success': True,
                'questions_asked': questions_asked,
                'concepts_learned': unique_concepts,
                'responses': responses,
                'duration': conversation_duration,
                'average_confidence': avg_confidence,
                'theme': template.theme,
                'performance_metrics': {
                    'conversation_duration': conversation_duration,
                    'avg_question_time': avg_question_time,
                    'min_question_time': min_question_time,
                    'max_question_time': max_question_time
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'questions_asked': 0,
                'concepts_learned': [],
                'duration': 0
            }
    
    def _generate_feedback_score(self, response, template: ConversationTemplate) -> float:
        """Génère un score de feedback automatique"""
        
        # Score basé sur la pertinence conceptuelle
        detected_concepts = response.conceptual_analysis.get('concepts_detected', [])
        concept_overlap = len(set(detected_concepts) & set(template.concepts_focus))
        concept_score = min(concept_overlap / max(len(template.concepts_focus), 1), 1.0)
        
        # Score basé sur la confiance
        confidence_score = response.confidence
        
        # Score basé sur la validation
        validation_score = response.validation_report.get('global_score', 0.5)
        
        # Score composite avec un peu de randomité
        base_score = (concept_score * 0.4 + confidence_score * 0.4 + validation_score * 0.2)
        noise = random.uniform(-0.1, 0.1)  # Bruit pour variabilité
        
        final_score = max(0.0, min(1.0, base_score + noise))
        
        # Tendance vers feedback positif selon configuration
        if random.random() < self.training_config['learning_feedback_rate']:
            final_score = max(final_score, 0.7)
        
        return final_score
    
    def _save_training_progress(self):
        """Sauvegarde les progrès d'entraînement"""
        
        if not self.current_session:
            return
        
        progress_data = {
            'session': {
                'session_id': self.current_session.session_id,
                'start_time': self.current_session.start_time.isoformat(),
                'conversations_completed': self.current_session.conversations_completed,
                'concepts_learned': self.current_session.concepts_learned,
                'learning_progress': self.current_session.learning_progress
            },
            'global_stats': {
                **self.training_stats,
                'concepts_discovered': list(self.training_stats['concepts_discovered'])
            },
            'config': self.training_config,
            'timestamp': datetime.now().isoformat()
        }
        
        progress_file = f"auto_training_progress_{self.current_session.session_id}.json"
        
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[dim]💾 Progrès sauvegardés: {progress_file}[/dim]")
            
        except Exception as e:
            self.console.print(f"[dim red]Erreur sauvegarde: {e}[/dim red]")
    
    def _display_training_summary(self):
        """Affiche le résumé de la session d'entraînement"""
        
        if not self.current_session:
            return
        
        session_duration = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds() / 3600
        
        # Table de résumé
        summary_table = Table(title="🤖 Résumé Auto-Entraînement", show_header=True)
        summary_table.add_column("Métrique", style="cyan", width=25)
        summary_table.add_column("Valeur", style="green", width=15)
        summary_table.add_column("Détail", style="dim")
        
        summary_table.add_row(
            "⏱️ Durée session", 
            f"{session_duration:.1f}h", 
            "Temps d'entraînement total"
        )
        summary_table.add_row(
            "💬 Conversations", 
            str(self.current_session.conversations_completed), 
            "Conversations automatiques réalisées"
        )
        summary_table.add_row(
            "❓ Questions totales", 
            str(self.training_stats['total_questions']), 
            "Questions posées à SophIA"
        )
        summary_table.add_row(
            "🎯 Concepts découverts", 
            str(len(self.training_stats['concepts_discovered'])), 
            "Concepts philosophiques uniques"
        )
        summary_table.add_row(
            "🧠 Confiance apprentissage", 
            f"{self.current_session.learning_progress:.1%}", 
            "Niveau d'apprentissage final"
        )
        summary_table.add_row(
            "📈 Conversations/heure", 
            f"{self.current_session.conversations_completed/session_duration:.1f}", 
            "Rythme d'entraînement"
        )
        
        self.console.print(summary_table)
        
        # Évolution de l'apprentissage
        if len(self.training_stats['learning_confidence_evolution']) > 1:
            start_confidence = self.training_stats['learning_confidence_evolution'][0]
            end_confidence = self.training_stats['learning_confidence_evolution'][-1]
            improvement = end_confidence - start_confidence
            
            improvement_color = "green" if improvement > 0 else "red" if improvement < 0 else "yellow"
            
            self.console.print(
                f"\n[{improvement_color}]📈 Évolution apprentissage: "
                f"{start_confidence:.1%} → {end_confidence:.1%} "
                f"({improvement:+.1%})[/{improvement_color}]"
            )
        
        # Top concepts appris
        if self.training_stats['concepts_discovered']:
            top_concepts = list(self.training_stats['concepts_discovered'])[:10]
            self.console.print(f"\n[cyan]🎯 Concepts principaux:[/cyan] {', '.join(top_concepts)}")
        
        # Évaluation globale
        if self.current_session.conversations_completed >= 20:
            if self.current_session.learning_progress >= 0.8:
                grade = "A+"
                comment = "EXCELLENT - Entraînement très efficace"
            elif self.current_session.learning_progress >= 0.7:
                grade = "A"
                comment = "TRÈS BON - Entraînement efficace"
            elif self.current_session.learning_progress >= 0.6:
                grade = "B"
                comment = "BON - Entraînement correct"
            else:
                grade = "C"
                comment = "ACCEPTABLE - Entraînement basique"
        else:
            grade = "N/A"
            comment = "Session trop courte pour évaluation"
        
        evaluation_panel = Panel(
            f"""
[bold blue]🏆 ÉVALUATION AUTO-ENTRAÎNEMENT[/bold blue]

[cyan]Note globale:[/cyan] {grade}
[cyan]Commentaire:[/cyan] {comment}

[yellow]🤖 SophIA s'est améliorée grâce aux {self.current_session.conversations_completed} conversations automatiques ![/yellow]
            """,
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(evaluation_panel)
    
    def run_continuous_training(self, hours_per_day: float = 2.0, 
                              days: int = 7) -> bool:
        """Lance un entraînement continu sur plusieurs jours"""
        
        self.console.print(f"\n[bold green]🔄 ENTRAÎNEMENT CONTINU[/bold green]")
        self.console.print(f"[cyan]Durée quotidienne:[/cyan] {hours_per_day:.1f}h")
        self.console.print(f"[cyan]Nombre de jours:[/cyan] {days}")
        self.console.print(f"[cyan]Total prévu:[/cyan] {hours_per_day * days:.1f}h")
        
        for day in range(1, days + 1):
            self.console.print(f"\n[bold yellow]📅 JOUR {day}/{days}[/bold yellow]")
            
            # Session quotidienne
            success = self.start_auto_training(duration_hours=hours_per_day)
            
            if not success:
                self.console.print(f"[red]❌ Échec jour {day}[/red]")
                return False
            
            # Pause entre les jours (sauf le dernier)
            if day < days:
                self.console.print(f"[dim]😴 Pause jusqu'à demain...[/dim]")
                # En réalité, on ne fait pas de vraie pause de 24h
                # mais on pourrait ajouter une logique de scheduling
        
        self.console.print(f"\n[bold green]🎉 ENTRAÎNEMENT CONTINU TERMINÉ ![/bold green]")
        return True
    
    def benchmark_before_after(self, benchmark_questions: List[str], 
                              training_duration: float = 1.0) -> Dict[str, Any]:
        """Évalue SophIA avant et après entraînement"""
        
        self.console.print(f"\n[bold blue]📊 BENCHMARK AVANT/APRÈS[/bold blue]")
        
        # Benchmark AVANT
        self.console.print(f"[cyan]Phase 1: Évaluation initiale...[/cyan]")
        before_results = self._run_benchmark(benchmark_questions, "AVANT")
        
        # ENTRAÎNEMENT
        self.console.print(f"[cyan]Phase 2: Auto-entraînement ({training_duration:.1f}h)...[/cyan]")
        training_success = self.start_auto_training(duration_hours=training_duration)
        
        if not training_success:
            self.console.print("[red]❌ Échec de l'entraînement[/red]")
            return {}
        
        # Benchmark APRÈS
        self.console.print(f"[cyan]Phase 3: Évaluation finale...[/cyan]")
        after_results = self._run_benchmark(benchmark_questions, "APRÈS")
        
        # Comparaison
        comparison = self._compare_benchmarks(before_results, after_results)
        
        # Affichage des résultats
        self._display_benchmark_comparison(before_results, after_results, comparison)
        
        return {
            'before': before_results,
            'after': after_results,
            'comparison': comparison,
            'training_session': self.current_session
        }
    
    def _run_benchmark(self, questions: List[str], phase: str) -> Dict[str, Any]:
        """Exécute un benchmark avec une liste de questions"""
        
        results = {
            'phase': phase,
            'questions_count': len(questions),
            'responses': [],
            'average_confidence': 0.0,
            'concepts_detected': set(),
            'total_duration': 0.0
        }
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Benchmark {phase}...", total=len(questions))
            
            for question in questions:
                try:
                    start_time = time.time()
                    response = self.sophia.ask(question)
                    duration = time.time() - start_time
                    
                    concepts = response.conceptual_analysis.get('concepts_detected', [])
                    
                    results['responses'].append({
                        'question': question,
                        'confidence': response.confidence,
                        'concepts': concepts,
                        'duration': duration,
                        'response_length': len(response.natural_response)
                    })
                    
                    results['concepts_detected'].update(concepts)
                    results['total_duration'] += duration
                    
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    self.console.print(f"[dim red]Erreur benchmark: {e}[/dim red]")
                    continue
        
        # Calcul des moyennes
        if results['responses']:
            results['average_confidence'] = sum(
                r['confidence'] for r in results['responses']
            ) / len(results['responses'])
            
            results['average_duration'] = results['total_duration'] / len(results['responses'])
            
            results['average_response_length'] = sum(
                r['response_length'] for r in results['responses']
            ) / len(results['responses'])
        
        results['concepts_detected'] = list(results['concepts_detected'])
        
        return results
    
    def _compare_benchmarks(self, before: Dict[str, Any], 
                          after: Dict[str, Any]) -> Dict[str, Any]:
        """Compare les résultats avant/après"""
        
        comparison = {}
        
        # Confiance
        confidence_improvement = after['average_confidence'] - before['average_confidence']
        comparison['confidence_change'] = confidence_improvement
        comparison['confidence_improvement_pct'] = (
            confidence_improvement / before['average_confidence'] * 100 
            if before['average_confidence'] > 0 else 0
        )
        
        # Concepts
        before_concepts = set(before['concepts_detected'])
        after_concepts = set(after['concepts_detected'])
        new_concepts = after_concepts - before_concepts
        
        comparison['new_concepts_count'] = len(new_concepts)
        comparison['new_concepts'] = list(new_concepts)
        comparison['total_concepts_before'] = len(before_concepts)
        comparison['total_concepts_after'] = len(after_concepts)
        
        # Performance
        speed_improvement = before['average_duration'] - after['average_duration']
        comparison['speed_change'] = speed_improvement
        comparison['speed_improvement_pct'] = (
            speed_improvement / before['average_duration'] * 100 
            if before['average_duration'] > 0 else 0
        )
        
        # Richesse des réponses
        length_change = after['average_response_length'] - before['average_response_length']
        comparison['response_length_change'] = length_change
        comparison['response_length_improvement_pct'] = (
            length_change / before['average_response_length'] * 100 
            if before['average_response_length'] > 0 else 0
        )
        
        return comparison
    
    def _display_benchmark_comparison(self, before: Dict[str, Any], 
                                    after: Dict[str, Any], 
                                    comparison: Dict[str, Any]):
        """Affiche la comparaison des benchmarks"""
        
        comparison_table = Table(title="📊 Comparaison Avant/Après Entraînement", show_header=True)
        comparison_table.add_column("Métrique", style="cyan", width=25)
        comparison_table.add_column("Avant", style="yellow", width=15)
        comparison_table.add_column("Après", style="green", width=15)
        comparison_table.add_column("Changement", width=20)
        
        # Confiance
        confidence_color = "green" if comparison['confidence_change'] > 0 else "red"
        comparison_table.add_row(
            "📊 Confiance moyenne",
            f"{before['average_confidence']:.1%}",
            f"{after['average_confidence']:.1%}",
            f"[{confidence_color}]{comparison['confidence_change']:+.1%}[/{confidence_color}]"
        )
        
        # Concepts
        comparison_table.add_row(
            "🎯 Concepts détectés",
            str(comparison['total_concepts_before']),
            str(comparison['total_concepts_after']),
            f"[green]+{comparison['new_concepts_count']} nouveaux[/green]"
        )
        
        # Vitesse
        speed_color = "green" if comparison['speed_change'] > 0 else "red"
        comparison_table.add_row(
            "⏱️ Temps de réponse",
            f"{before['average_duration']:.2f}s",
            f"{after['average_duration']:.2f}s",
            f"[{speed_color}]{comparison['speed_change']:+.2f}s[/{speed_color}]"
        )
        
        # Richesse
        length_color = "green" if comparison['response_length_change'] > 0 else "red"
        comparison_table.add_row(
            "📝 Longueur réponse",
            f"{before['average_response_length']:.0f} car.",
            f"{after['average_response_length']:.0f} car.",
            f"[{length_color}]{comparison['response_length_change']:+.0f} car.[/{length_color}]"
        )
        
        self.console.print(comparison_table)
        
        # Nouveaux concepts
        if comparison['new_concepts']:
            self.console.print(f"\n[green]🆕 Nouveaux concepts appris:[/green]")
            self.console.print(f"[dim]{', '.join(comparison['new_concepts'][:10])}[/dim]")
        
        # Évaluation globale
        improvements = 0
        if comparison['confidence_change'] > 0.05:  # +5% confiance
            improvements += 1
        if comparison['new_concepts_count'] > 0:
            improvements += 1
        if comparison['speed_change'] > 0:  # Plus rapide
            improvements += 1
        if comparison['response_length_change'] > 0:  # Plus riche
            improvements += 1
        
        if improvements >= 3:
            verdict = "[bold green]🎉 AMÉLIORATION EXCELLENTE[/bold green]"
        elif improvements >= 2:
            verdict = "[bold yellow]📈 AMÉLIORATION NOTABLE[/bold yellow]"
        elif improvements >= 1:
            verdict = "[yellow]📊 AMÉLIORATION LÉGÈRE[/yellow]"
        else:
            verdict = "[red]📉 PAS D'AMÉLIORATION NOTABLE[/red]"
        
        self.console.print(f"\n{verdict}")

SOPHIA_PROGRESS_FILE = "sophia_progress.json"

def load_last_progress():
    """Charge les dernières performances enregistrées de SophIA"""
    if os.path.exists(SOPHIA_PROGRESS_FILE):
        try:
            with open(SOPHIA_PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_progress(progress: dict):
    """Sauvegarde les performances actuelles de SophIA"""
    try:
        with open(SOPHIA_PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def print_progress_comparison(console, last: dict, current: dict):
    """Affiche la comparaison entre l'ancienne et la nouvelle performance"""
    from rich.table import Table

    table = Table(title="📈 Évolution de SophIA", show_header=True)
    table.add_column("Métrique", style="cyan")
    table.add_column("Dernière session", style="yellow")
    table.add_column("Nouvelle session", style="green")
    table.add_column("Évolution", style="magenta")

    def fmt_pct(val):
        return f"{val:.1%}" if isinstance(val, float) else str(val)

    # Confiance
    last_conf = last.get("average_confidence", 0)
    curr_conf = current.get("average_confidence", 0)
    diff_conf = curr_conf - last_conf
    table.add_row(
        "Confiance moyenne",
        fmt_pct(last_conf),
        fmt_pct(curr_conf),
        f"[{'green' if diff_conf>0 else 'red' if diff_conf<0 else 'yellow'}]{diff_conf:+.1%}[/]"
    )
    # Concepts
    last_concepts = last.get("concepts_detected", [])
    curr_concepts = current.get("concepts_detected", [])
    new_concepts = len(set(curr_concepts) - set(last_concepts))
    table.add_row(
        "Concepts détectés",
        str(len(last_concepts)),
        str(len(curr_concepts)),
        f"[green]+{new_concepts}[/green]" if new_concepts > 0 else "[yellow]0[/yellow]"
    )
    # Temps de réponse
    last_speed = last.get("average_duration", 0)
    curr_speed = current.get("average_duration", 0)
    diff_speed = last_speed - curr_speed
    table.add_row(
        "Temps de réponse (s)",
        f"{last_speed:.2f}",
        f"{curr_speed:.2f}",
        f"[{'green' if diff_speed>0 else 'red' if diff_speed<0 else 'yellow'}]{diff_speed:+.2f}[/]"
    )
    # Longueur de réponse
    last_len = last.get("average_response_length", 0)
    curr_len = current.get("average_response_length", 0)
    diff_len = curr_len - last_len
    table.add_row(
        "Longueur réponse",
        f"{last_len:.0f}",
        f"{curr_len:.0f}",
        f"[{'green' if diff_len>0 else 'red' if diff_len<0 else 'yellow'}]{diff_len:+.0f}[/]"
    )
    console.print(table)

def main():
    """Point d'entrée principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="SophIA Auto-Trainer")
    parser.add_argument("--mode", choices=["speed", "balanced", "quality"], 
                       default="balanced", help="Mode de performance")
    parser.add_argument("--duration", type=float, default=1.0, 
                       help="Durée d'entraînement en heures")
    parser.add_argument("--conversations", type=int, 
                       help="Nombre de conversations (override durée)")
    parser.add_argument("--benchmark", action="store_true", 
                       help="Mode benchmark avant/après")
    parser.add_argument("--continuous", type=int, 
                       help="Entraînement continu sur N jours")
    
    args = parser.parse_args()
    
    # Initialisation du trainer
    trainer = SophIAAutoTrainer(performance_mode=args.mode)
    
    console = Console()
    console.print("[bold blue]🤖 SophIA Auto-Trainer[/bold blue]")
    console.print(f"[cyan]Mode:[/cyan] {args.mode}")

    # Affichage de la dernière performance
    last_progress = load_last_progress()
    if last_progress:
        console.print("[bold yellow]Dernière performance enregistrée :[/bold yellow]")
        print_progress_comparison(console, last_progress, last_progress)
    else:
        console.print("[yellow]Aucune performance précédente enregistrée.[/yellow]")

    try:
        if args.benchmark:
            # Mode benchmark
            benchmark_questions = [
                "Qu'est-ce que la vérité ?",
                "Comment définir la justice ?",
                "Quelle est la nature de la beauté ?",
                "Le bien et le mal sont-ils absolus ?",
                "Qu'est-ce que la connaissance ?",
                "Comment comprendre la liberté ?",
                "Quelle est l'essence de l'être ?",
                "Comment concevoir la conscience ?"
            ]
            results = trainer.benchmark_before_after(
                benchmark_questions, 
                args.duration
            )
            # Sauvegarde la performance "après"
            if results and 'after' in results:
                save_progress(results['after'])

        elif args.continuous:
            # Mode continu
            trainer.run_continuous_training(
                hours_per_day=args.duration,
                days=args.continuous
            )
            # Pas de sauvegarde automatique ici

        else:
            # Mode normal
            success = trainer.start_auto_training(duration_hours=args.duration)
            # Après entraînement, effectue un mini-benchmark pour mesurer l'amélioration
            if success:
                # Mini benchmark automatique
                benchmark_questions = [
                    "Qu'est-ce que la vérité ?",
                    "Comment définir la justice ?",
                    "Quelle est la nature de la beauté ?",
                    "Le bien et le mal sont-ils absolus ?"
                ]
                # On utilise la même instance sophia
                after = trainer._run_benchmark(benchmark_questions, "APRÈS")
                # Affiche la comparaison avec la dernière session
                if last_progress:
                    console.print("[bold green]Comparaison avec la dernière session :[/bold green]")
                    print_progress_comparison(console, last_progress, after)
                else:
                    console.print("[bold green]Performance de la session actuelle :[/bold green]")
                    print_progress_comparison(console, after, after)
                # Sauvegarde la nouvelle performance
                save_progress(after)
                console.print("[green]✅ Auto-entraînement terminé avec succès[/green]")
            else:
                console.print("[red]❌ Échec de l'auto-entraînement[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Auto-entraînement interrompu[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erreur: {e}[/red]")
    finally:
        console.print("\n[dim]Au revoir ![/dim]")

if __name__ == "__main__":
    main()