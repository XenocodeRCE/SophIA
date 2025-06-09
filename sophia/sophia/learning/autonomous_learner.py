"""
Autonomous Learner - Apprentissage autonome pour SophIA
Apprentissage continu basé sur les interactions et feedback
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class LearningExample:
    """Exemple d'apprentissage capturé"""
    question: str
    response: str
    concepts_detected: List[str]
    confidence: float
    validation_score: float
    feedback_score: Optional[float]
    timestamp: datetime
    interaction_id: str
    context_metadata: Dict[str, Any]

@dataclass
class ConceptPattern:
    """Pattern conceptuel appris"""
    concept: str
    associated_terms: List[str]
    contexts: List[str]
    confidence: float
    usage_count: int
    last_updated: datetime

@dataclass
class ResponsePattern:
    """Pattern de réponse appris"""
    question_type: str
    response_template: str
    concepts_involved: List[str]
    success_rate: float
    usage_count: int
    last_used: datetime

class PerformanceTrend:
    """Analyse des tendances de performance"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.confidence_history = deque(maxlen=window_size)
        self.validation_history = deque(maxlen=window_size)
        self.response_times = deque(maxlen=window_size)
        self.concept_accuracy = deque(maxlen=window_size)
    
    def add_interaction(self, confidence: float, validation: float, 
                       response_time: float, concept_accuracy: float):
        """Ajoute une nouvelle interaction aux tendances"""
        self.confidence_history.append(confidence)
        self.validation_history.append(validation)
        self.response_times.append(response_time)
        self.concept_accuracy.append(concept_accuracy)
    
    def get_trends(self) -> Dict[str, Any]:
        """Calcule les tendances actuelles"""
        if not self.confidence_history:
            return {}
        
        # Calcul des moyennes
        avg_confidence = sum(self.confidence_history) / len(self.confidence_history)
        avg_validation = sum(self.validation_history) / len(self.validation_history)
        avg_response_time = sum(self.response_times) / len(self.response_times)
        avg_concept_accuracy = sum(self.concept_accuracy) / len(self.concept_accuracy)
        
        # Calcul des tendances (derniers 10 vs 10 précédents)
        def calculate_trend(values):
            if len(values) < 20:
                return 'stable'
            recent = sum(values[-10:]) / 10
            previous = sum(list(values)[-20:-10]) / 10
            change = (recent - previous) / previous * 100
            
            if change > 5:
                return 'improving'
            elif change < -5:
                return 'declining'
            else:
                return 'stable'
        
        return {
            'averages': {
                'confidence': avg_confidence,
                'validation': avg_validation,
                'response_time': avg_response_time,
                'concept_accuracy': avg_concept_accuracy
            },
            'trends': {
                'confidence': calculate_trend(self.confidence_history),
                'validation': calculate_trend(self.validation_history),
                'response_time': calculate_trend(self.response_times),
                'concept_accuracy': calculate_trend(self.concept_accuracy)
            },
            'sample_size': len(self.confidence_history)
        }

class AutonomousLearner:
    """
    Système d'apprentissage autonome pour SophIA
    - Apprentissage par interaction
    - Détection de patterns
    - Amélioration continue
    - Adaptation aux domaines
    """
    
    def __init__(self, learning_rate: float = 0.1, 
                 adaptation_threshold: float = 0.7,
                 save_directory: str = "sophia_learning"):
        
        self.learning_rate = learning_rate
        self.adaptation_threshold = adaptation_threshold
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # Bases de connaissances apprises
        self.learned_examples: List[LearningExample] = []
        self.concept_patterns: Dict[str, ConceptPattern] = {}
        self.response_patterns: Dict[str, ResponsePattern] = {}
        
        # Analyse des performances
        self.performance_trends = PerformanceTrend()
        
        # Métadonnées d'apprentissage
        self.learning_session_start = datetime.now()
        self.total_interactions = 0
        self.successful_adaptations = 0
        
        # Cache et optimisations
        self._pattern_cache = {}
        self._learning_lock = threading.Lock()
        
        # Statistiques
        self.stats = {
            'interactions_learned': 0,
            'patterns_discovered': 0,
            'adaptations_made': 0,
            'concept_improvements': defaultdict(int),
            'domain_specializations': defaultdict(int)
        }
        
        # Chargement des connaissances existantes
        self._load_learned_knowledge()
        
        logger.info("🧠 Autonomous Learner initialisé")
        logger.info(f"📚 Connaissances chargées: {len(self.learned_examples)} exemples")
        logger.info(f"🎯 Patterns conceptuels: {len(self.concept_patterns)}")
    
    def learn_from_interaction(self, question: str, response_data: Dict[str, Any], 
                              feedback_score: Optional[float] = None) -> Dict[str, Any]:
        """Apprend d'une interaction utilisateur"""
        
        with self._learning_lock:
            interaction_id = f"interaction_{int(time.time() * 1000000) % 1000000}"
            
            # Extraction des données d'apprentissage
            concepts_detected = response_data.get('conceptual_analysis', {}).get('concepts_detected', [])
            confidence = response_data.get('confidence', 0.0)
            validation_score = response_data.get('validation_report', {}).get('global_score', 0.0)
            natural_response = response_data.get('natural_response', '')
            
            # Création de l'exemple d'apprentissage
            learning_example = LearningExample(
                question=question,
                response=natural_response,
                concepts_detected=concepts_detected,
                confidence=confidence,
                validation_score=validation_score,
                feedback_score=feedback_score,
                timestamp=datetime.now(),
                interaction_id=interaction_id,
                context_metadata=self._extract_context_metadata(response_data)
            )
            
            # Ajout à la base d'apprentissage
            self.learned_examples.append(learning_example)
            self.total_interactions += 1
            self.stats['interactions_learned'] += 1
            
            # Apprentissage des patterns
            learning_insights = self._discover_patterns(learning_example)
            
            # Mise à jour des tendances
            concept_accuracy = self._calculate_concept_accuracy(learning_example)
            response_time = response_data.get('performance_metrics', {}).get('duration', 0)
            
            self.performance_trends.add_interaction(
                confidence, validation_score, response_time, concept_accuracy
            )
            
            # Auto-amélioration si seuil atteint
            if self._should_trigger_adaptation():
                adaptation_results = self._trigger_autonomous_adaptation()
                learning_insights['adaptations'] = adaptation_results
            
            # Sauvegarde périodique
            if self.total_interactions % 10 == 0:
                self._save_learned_knowledge()
            
            logger.debug(f"🧠 Apprentissage: {interaction_id}, concepts: {len(concepts_detected)}")
            
            return {
                'interaction_id': interaction_id,
                'learning_applied': True,
                'patterns_discovered': learning_insights.get('new_patterns', 0),
                'concepts_improved': learning_insights.get('concepts_improved', []),
                'adaptations_triggered': learning_insights.get('adaptations', {}),
                'learning_confidence': self._calculate_learning_confidence()
            }
    
    def _extract_context_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les métadonnées contextuelles pour l'apprentissage"""
        
        return {
            'extraction_method': response_data.get('conceptual_analysis', {}).get('extraction_details', {}).get('metadata', {}).get('extraction_method', 'unknown'),
            'relations_found': len(response_data.get('conceptual_analysis', {}).get('relations_implied', [])),
            'lcm_reasoning_paths': len(response_data.get('lcm_reasoning', {}).get('reasoning_paths', [])),
            'constraint_violations': len(response_data.get('validation_report', {}).get('violations', [])),
            'response_length': len(response_data.get('natural_response', '')),
            'processing_time': response_data.get('performance_metrics', {}).get('duration', 0)
        }
    
    def _discover_patterns(self, example: LearningExample) -> Dict[str, Any]:
        """Découvre de nouveaux patterns à partir d'un exemple"""
        
        insights = {'new_patterns': 0, 'concepts_improved': []}
        
        # 1. Apprentissage des patterns conceptuels
        for concept in example.concepts_detected:
            if concept not in self.concept_patterns:
                # Nouveau concept découvert
                self.concept_patterns[concept] = ConceptPattern(
                    concept=concept,
                    associated_terms=self._extract_associated_terms(example.question, concept),
                    contexts=[example.question],
                    confidence=example.confidence,
                    usage_count=1,
                    last_updated=datetime.now()
                )
                insights['new_patterns'] += 1
                self.stats['patterns_discovered'] += 1
                logger.debug(f"🆕 Nouveau pattern conceptuel: {concept}")
            else:
                # Amélioration d'un pattern existant
                pattern = self.concept_patterns[concept]
                
                # Mise à jour des termes associés
                new_terms = self._extract_associated_terms(example.question, concept)
                for term in new_terms:
                    if term not in pattern.associated_terms:
                        pattern.associated_terms.append(term)
                
                # Mise à jour du contexte
                if example.question not in pattern.contexts:
                    pattern.contexts.append(example.question)
                    if len(pattern.contexts) > 10:  # Limite la taille
                        pattern.contexts.pop(0)
                
                # Mise à jour de la confiance (moyenne mobile)
                pattern.confidence = (pattern.confidence * pattern.usage_count + example.confidence) / (pattern.usage_count + 1)
                pattern.usage_count += 1
                pattern.last_updated = datetime.now()
                
                insights['concepts_improved'].append(concept)
                self.stats['concept_improvements'][concept] += 1
        
        # 2. Apprentissage des patterns de réponse
        question_type = self._classify_question_type(example.question)
        if question_type:
            self._update_response_pattern(question_type, example)
        
        # 3. Détection de spécialisations de domaine
        domain = self._detect_philosophical_domain(example.concepts_detected)
        if domain:
            self.stats['domain_specializations'][domain] += 1
        
        return insights
    
    def _extract_associated_terms(self, question: str, concept: str) -> List[str]:
        """Extrait les termes associés à un concept dans une question"""
        
        # Mots à proximité du concept (contexte local)
        question_lower = question.lower()
        concept_lower = concept.lower()
        
        if concept_lower in question_lower:
            words = question_lower.split()
            try:
                concept_index = words.index(concept_lower)
                # Prend 2 mots avant et après
                start = max(0, concept_index - 2)
                end = min(len(words), concept_index + 3)
                context_words = words[start:end]
                # Filtre les mots non significatifs
                significant_words = [w for w in context_words 
                                   if len(w) > 2 and w not in ['que', 'est', 'une', 'des', 'les', 'la', 'le']]
                return significant_words[:5]  # Maximum 5 termes
            except ValueError:
                pass
        
        return []
    
    def _classify_question_type(self, question: str) -> Optional[str]:
        """Classifie le type de question philosophique"""
        
        question_lower = question.lower()
        
        # Types de questions philosophiques
        if question_lower.startswith(('qu\'est-ce que', 'qu\'est-ce qu\'', 'que signifie')):
            return 'definition'
        elif 'pourquoi' in question_lower:
            return 'causal'
        elif 'comment' in question_lower:
            return 'processual'
        elif question_lower.startswith(('peut-on', 'est-il possible')):
            return 'possibility'
        elif question_lower.startswith(('doit-on', 'faut-il')):
            return 'normative'
        elif '?' in question and ('relation' in question_lower or 'lien' in question_lower):
            return 'relational'
        elif 'existe' in question_lower:
            return 'existential'
        else:
            return 'general'
    
    def _update_response_pattern(self, question_type: str, example: LearningExample):
        """Met à jour les patterns de réponse"""
        
        if question_type not in self.response_patterns:
            # Nouveau pattern de réponse
            self.response_patterns[question_type] = ResponsePattern(
                question_type=question_type,
                response_template=self._extract_response_template(example.response),
                concepts_involved=example.concepts_detected,
                success_rate=example.validation_score,
                usage_count=1,
                last_used=datetime.now()
            )
        else:
            # Mise à jour du pattern existant
            pattern = self.response_patterns[question_type]
            
            # Mise à jour du taux de succès (moyenne mobile)
            pattern.success_rate = (pattern.success_rate * pattern.usage_count + example.validation_score) / (pattern.usage_count + 1)
            
            # Mise à jour des concepts
            for concept in example.concepts_detected:
                if concept not in pattern.concepts_involved:
                    pattern.concepts_involved.append(concept)
            
            pattern.usage_count += 1
            pattern.last_used = datetime.now()
    
    def _extract_response_template(self, response: str) -> str:
        """Extrait un template de réponse généralizable"""
        
        # Simplifie la réponse en template
        if len(response) > 200:
            # Prend les premières phrases comme template
            sentences = response.split('.')
            return '. '.join(sentences[:2]) + '...'
        return response[:100] + '...'
    
    def _detect_philosophical_domain(self, concepts: List[str]) -> Optional[str]:
        """Détecte le domaine philosophique principal"""
        
        domain_concepts = {
            'epistemology': ['VÉRITÉ', 'CONNAISSANCE', 'CROYANCE', 'JUSTIFICATION', 'VALIDITÉ'],
            'ethics': ['BIEN', 'MAL', 'JUSTICE', 'VERTU', 'DEVOIR', 'MORALE'],
            'metaphysics': ['ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ', 'SUBSTANCE'],
            'aesthetics': ['BEAUTÉ', 'ART', 'SUBLIME', 'HARMONIE', 'CRÉATION'],
            'logic': ['LOGIQUE', 'RAISONNEMENT', 'ARGUMENT', 'VALIDITÉ', 'COHÉRENCE']
        }
        
        domain_scores = {}
        for domain, domain_concepts_list in domain_concepts.items():
            score = len(set(concepts) & set(domain_concepts_list))
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _calculate_concept_accuracy(self, example: LearningExample) -> float:
        """Calcule la précision conceptuelle d'un exemple"""
        
        # Heuristique simple basée sur la cohérence conceptuelle
        if not example.concepts_detected:
            return 0.0
        
        # Utilise la confiance et le score de validation
        return (example.confidence + example.validation_score) / 2
    
    def _should_trigger_adaptation(self) -> bool:
        """Détermine si une adaptation autonome doit être déclenchée"""
        
        # Adaptation si performance en baisse ou seuil d'interactions atteint
        trends = self.performance_trends.get_trends()
        
        if not trends:
            return False
        
        # Critères d'adaptation
        declining_performance = (
            trends.get('trends', {}).get('confidence') == 'declining' or
            trends.get('trends', {}).get('validation') == 'declining'
        )
        
        enough_data = trends.get('sample_size', 0) >= 20
        periodic_adaptation = self.total_interactions % 50 == 0  # Adaptation périodique
        
        return enough_data and (declining_performance or periodic_adaptation)
    
    def _trigger_autonomous_adaptation(self) -> Dict[str, Any]:
        """Déclenche une adaptation autonome du système"""
        
        adaptation_results = {}
        
        # 1. Optimisation des seuils de confiance
        confidence_optimization = self._optimize_confidence_thresholds()
        adaptation_results['confidence_optimization'] = confidence_optimization
        
        # 2. Amélioration des patterns conceptuels
        pattern_improvements = self._improve_concept_patterns()
        adaptation_results['pattern_improvements'] = pattern_improvements
        
        # 3. Adaptation des stratégies de réponse
        response_adaptations = self._adapt_response_strategies()
        adaptation_results['response_adaptations'] = response_adaptations
        
        self.successful_adaptations += 1
        self.stats['adaptations_made'] += 1
        
        logger.info(f"🔄 Adaptation autonome #{self.successful_adaptations} appliquée")
        
        return adaptation_results
    
    def _optimize_confidence_thresholds(self) -> Dict[str, Any]:
        """Optimise les seuils de confiance basés sur l'historique"""
        
        if len(self.learned_examples) < 10:
            return {'status': 'insufficient_data'}
        
        # Analyse des exemples réussis vs échoués
        successful_examples = [ex for ex in self.learned_examples 
                             if ex.validation_score > 0.7]
        failed_examples = [ex for ex in self.learned_examples 
                          if ex.validation_score < 0.5]
        
        if successful_examples and failed_examples:
            avg_successful_confidence = sum(ex.confidence for ex in successful_examples) / len(successful_examples)
            avg_failed_confidence = sum(ex.confidence for ex in failed_examples) / len(failed_examples)
            
            optimal_threshold = (avg_successful_confidence + avg_failed_confidence) / 2
            
            return {
                'status': 'optimized',
                'old_threshold': 0.5,  # Valeur par défaut
                'new_threshold': optimal_threshold,
                'successful_examples': len(successful_examples),
                'failed_examples': len(failed_examples)
            }
        
        return {'status': 'no_optimization_needed'}
    
    def _improve_concept_patterns(self) -> Dict[str, Any]:
        """Améliore les patterns conceptuels basés sur l'usage"""
        
        improvements = []
        
        for concept, pattern in self.concept_patterns.items():
            if pattern.usage_count >= 5:  # Seuil pour amélioration
                # Trouve les termes les plus fréquents dans les contextes
                all_words = []
                for context in pattern.contexts:
                    all_words.extend(context.lower().split())
                
                # Compte la fréquence
                word_freq = defaultdict(int)
                for word in all_words:
                    if len(word) > 3:  # Filtre les mots courts
                        word_freq[word] += 1
                
                # Ajoute les termes fréquents aux termes associés
                frequent_terms = [word for word, freq in word_freq.items() 
                                if freq >= 2 and word not in pattern.associated_terms]
                
                if frequent_terms:
                    pattern.associated_terms.extend(frequent_terms[:3])  # Max 3 nouveaux termes
                    improvements.append({
                        'concept': concept,
                        'new_terms': frequent_terms[:3]
                    })
        
        return {
            'concepts_improved': len(improvements),
            'improvements': improvements
        }
    
    def _adapt_response_strategies(self) -> Dict[str, Any]:
        """Adapte les stratégies de réponse basées sur les succès"""
        
        adaptations = []
        
        for question_type, pattern in self.response_patterns.items():
            if pattern.usage_count >= 5:
                if pattern.success_rate > 0.8:
                    # Stratégie réussie - renforce
                    adaptations.append({
                        'question_type': question_type,
                        'action': 'reinforce',
                        'success_rate': pattern.success_rate
                    })
                elif pattern.success_rate < 0.5:
                    # Stratégie échoue - marque pour révision
                    adaptations.append({
                        'question_type': question_type,
                        'action': 'revise',
                        'success_rate': pattern.success_rate
                    })
        
        return {
            'strategies_adapted': len(adaptations),
            'adaptations': adaptations
        }
    
    def _calculate_learning_confidence(self) -> float:
        """Calcule la confiance du système d'apprentissage"""
        
        if not self.learned_examples:
            return 0.0
        
        # Facteurs de confiance
        data_quality = min(len(self.learned_examples) / 100, 1.0)  # Qualité basée sur la quantité
        
        recent_performance = 0.0
        if len(self.learned_examples) >= 10:
            recent_examples = self.learned_examples[-10:]
            recent_performance = sum(ex.validation_score for ex in recent_examples) / len(recent_examples)
        
        pattern_richness = min(len(self.concept_patterns) / 20, 1.0)  # Richesse des patterns
        
        adaptation_success = min(self.successful_adaptations / 5, 1.0)  # Succès des adaptations
        
        # Confiance globale
        learning_confidence = (data_quality * 0.3 + recent_performance * 0.4 + 
                             pattern_richness * 0.2 + adaptation_success * 0.1)
        
        return learning_confidence
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Génère des insights sur l'apprentissage"""
        
        trends = self.performance_trends.get_trends()
        learning_confidence = self._calculate_learning_confidence()
        
        # Top concepts appris
        top_concepts = sorted(
            self.concept_patterns.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )[:5]
        
        # Domaines de spécialisation
        top_domains = sorted(
            self.stats['domain_specializations'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            'learning_summary': {
                'total_interactions': self.total_interactions,
                'examples_learned': len(self.learned_examples),
                'patterns_discovered': len(self.concept_patterns),
                'adaptations_made': self.successful_adaptations,
                'learning_confidence': learning_confidence,
                'session_duration_hours': (datetime.now() - self.learning_session_start).total_seconds() / 3600
            },
            'performance_trends': trends,
            'top_learned_concepts': [
                {
                    'concept': concept,
                    'usage_count': pattern.usage_count,
                    'confidence': pattern.confidence,
                    'associated_terms': pattern.associated_terms[:3]
                } for concept, pattern in top_concepts
            ],
            'domain_specializations': [
                {'domain': domain, 'interaction_count': count}
                for domain, count in top_domains
            ],
            'learning_recommendations': self._generate_learning_recommendations()
        }
    
    def _generate_learning_recommendations(self) -> List[Dict[str, str]]:
        """Génère des recommandations d'apprentissage"""
        
        recommendations = []
        
        # Basé sur les tendances de performance
        trends = self.performance_trends.get_trends()
        if trends:
            if trends.get('trends', {}).get('confidence') == 'declining':
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'recommendation': 'Améliorer la précision conceptuelle',
                    'action': 'Réviser les patterns de détection de concepts'
                })
            
            if trends.get('averages', {}).get('response_time', 0) > 10:
                recommendations.append({
                    'type': 'efficiency',
                    'priority': 'medium',
                    'recommendation': 'Optimiser les temps de réponse',
                    'action': 'Implémenter plus de cache et optimisations'
                })
        
        # Basé sur les données d'apprentissage
        if len(self.learned_examples) < 50:
            recommendations.append({
                'type': 'data',
                'priority': 'medium',
                'recommendation': 'Augmenter le volume d\'apprentissage',
                'action': 'Encourager plus d\'interactions variées'
            })
        
        # Basé sur la diversité conceptuelle
        if len(self.concept_patterns) < 10:
            recommendations.append({
                'type': 'diversity',
                'priority': 'low',
                'recommendation': 'Diversifier les domaines philosophiques',
                'action': 'Explorer des questions dans de nouveaux domaines'
            })
        
        return recommendations
    
    def _save_learned_knowledge(self):
        """Sauvegarde les connaissances apprises"""
        
        try:
            # Sauvegarde des exemples
            examples_file = self.save_directory / "learned_examples.json"
            with open(examples_file, 'w', encoding='utf-8') as f:
                examples_data = []
                for example in self.learned_examples:
                    example_dict = asdict(example)
                    example_dict['timestamp'] = example.timestamp.isoformat()
                    examples_data.append(example_dict)
                json.dump(examples_data, f, indent=2, ensure_ascii=False)
            
            # Sauvegarde des patterns
            patterns_file = self.save_directory / "concept_patterns.pickle"
            with open(patterns_file, 'wb') as f:
                pickle.dump(self.concept_patterns, f)
            
            response_patterns_file = self.save_directory / "response_patterns.pickle"
            with open(response_patterns_file, 'wb') as f:
                pickle.dump(self.response_patterns, f)
            
            # Sauvegarde des statistiques
            stats_file = self.save_directory / "learning_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                stats_data = dict(self.stats)
                stats_data['session_start'] = self.learning_session_start.isoformat()
                stats_data['total_interactions'] = self.total_interactions
                stats_data['successful_adaptations'] = self.successful_adaptations
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Connaissances sauvegardées: {len(self.learned_examples)} exemples")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde apprentissage: {e}")
    
    def _load_learned_knowledge(self):
        """Charge les connaissances apprises existantes"""
        
        try:
            # Chargement des exemples
            examples_file = self.save_directory / "learned_examples.json"
            if examples_file.exists():
                with open(examples_file, 'r', encoding='utf-8') as f:
                    examples_data = json.load(f)
                    for example_dict in examples_data:
                        example_dict['timestamp'] = datetime.fromisoformat(example_dict['timestamp'])
                        self.learned_examples.append(LearningExample(**example_dict))
            
            # Chargement des patterns
            patterns_file = self.save_directory / "concept_patterns.pickle"
            if patterns_file.exists():
                with open(patterns_file, 'rb') as f:
                    self.concept_patterns = pickle.load(f)
            
            response_patterns_file = self.save_directory / "response_patterns.pickle"
            if response_patterns_file.exists():
                with open(response_patterns_file, 'rb') as f:
                    self.response_patterns = pickle.load(f)
            
            # Chargement des statistiques
            stats_file = self.save_directory / "learning_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
                    self.total_interactions = stats_data.get('total_interactions', 0)
                    self.successful_adaptations = stats_data.get('successful_adaptations', 0)
                    if 'session_start' in stats_data:
                        self.learning_session_start = datetime.fromisoformat(stats_data['session_start'])
            
            logger.info(f"📚 Connaissances chargées: {len(self.learned_examples)} exemples")
            
        except Exception as e:
            logger.warning(f"Erreur chargement apprentissage: {e}")
    
    def clear_learning_data(self):
        """Efface toutes les données d'apprentissage"""
        
        self.learned_examples.clear()
        self.concept_patterns.clear()
        self.response_patterns.clear()
        self.stats = {
            'interactions_learned': 0,
            'patterns_discovered': 0,
            'adaptations_made': 0,
            'concept_improvements': defaultdict(int),
            'domain_specializations': defaultdict(int)
        }
        self.total_interactions = 0
        self.successful_adaptations = 0
        self.learning_session_start = datetime.now()
        
        logger.info("🗑️ Données d'apprentissage effacées")