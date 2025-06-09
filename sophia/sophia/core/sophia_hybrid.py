"""
Système hybride SophIA : LCM + LLaMA avec modules avancés
Combinaison du raisonnement conceptuel et de la génération naturelle
"""

import time 
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

from sophia.core.ontology import SimpleOntology, Concept
from sophia.models.lcm_core import SimpleLCM
from sophia.training.trainer import OntologyAwareLCMTrainer
from sophia.llm.llama_interface import OllamaLLaMAInterface
from sophia.storage.session import TrainingSession
from sophia.bridge.concept_text_bridge import EnhancedConceptTextBridge
from sophia.constraints.constraint_manager import PhilosophicalConstraintManager

# Imports des modules avancés supplémentaires
try:
    from sophia.extraction.llm_extractor import LLMConceptExtractor
    LLM_EXTRACTOR_AVAILABLE = True
    print("📦 LLM Extractor disponible")
except ImportError:
    LLM_EXTRACTOR_AVAILABLE = False
    print("⚠️ LLM Extractor non disponible")

try:
    from sophia.nlp.tokenizer import PhilosophicalTokenizer
    TOKENIZER_AVAILABLE = True
    print("📝 Tokenizer disponible")
except ImportError:
    TOKENIZER_AVAILABLE = False
    print("⚠️ Tokenizer non disponible")

try:
    from sophia.optimization.performance import PerformanceMonitor
    PERFORMANCE_MONITOR_AVAILABLE = True
    print("📊 Performance Monitor disponible")
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False
    print("⚠️ Performance Monitor non disponible")

try:
    from sophia.learning.autonomous_learner import AutonomousLearner
    AUTONOMOUS_LEARNER_AVAILABLE = True
    print("🤖 Autonomous Learner disponible")
except ImportError:
    AUTONOMOUS_LEARNER_AVAILABLE = False
    print("⚠️ Autonomous Learner non disponible")

logger = logging.getLogger(__name__)

class SophIAResponse:
    """Représente une réponse complète de SophIA avec tous les métadonnées"""
    
    def __init__(self, question: str, natural_response: str, 
                 conceptual_analysis: Dict[str, Any], 
                 lcm_reasoning: Dict[str, Any],
                 confidence: float,
                 timestamp: datetime,
                 validation_report: Optional[Dict[str, Any]] = None):
        self.question = question
        self.natural_response = natural_response
        self.conceptual_analysis = conceptual_analysis
        self.lcm_reasoning = lcm_reasoning
        self.confidence = confidence
        self.timestamp = timestamp
        self.validation_report = validation_report or {}
        
        # Attributs supplémentaires pour les modules avancés
        self.performance_metrics = {}
        self.advanced_analysis = {}
        self.learning_triggered = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'natural_response': self.natural_response,
            'conceptual_analysis': self.conceptual_analysis,
            'lcm_reasoning': self.lcm_reasoning,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'validation_report': self.validation_report,
            'performance_metrics': self.performance_metrics,
            'advanced_analysis': self.advanced_analysis
        }

class HybridSophIA:
    """
    Système hybride SophIA combinant :
    - Raisonnement conceptuel (LCM)
    - Génération naturelle (LLaMA)
    - Pont conceptuel avancé
    - Validation par contraintes
    - Apprentissage continu
    - Modules avancés (Performance, NLP, etc.)
    """
    
    def __init__(self, session_name: str = "sophia_hybrid", 
                 llm_model: str = "llama3.1:latest",
                 auto_save: bool = True,
                 performance_mode: str = "balanced"):
        
        self.session_name = session_name
        self.auto_save = auto_save
        
        # Composants principaux
        self.ontology = SimpleOntology()
        self.lcm_model = SimpleLCM(self.ontology)
        self.trainer = OntologyAwareLCMTrainer(self.lcm_model, self.ontology)
        self.llm = OllamaLLaMAInterface(model_name=llm_model)
        
        # Modules avancés principaux
        self.concept_bridge = EnhancedConceptTextBridge(self.ontology, self.llm)
        self.constraint_manager = PhilosophicalConstraintManager(self.ontology, self.llm)
        
        # Modules avancés optionnels
        self._initialize_advanced_modules()
        
        # Système de session pour persistance
        self.session = TrainingSession(session_name) if auto_save else None
        
        # Historique conversationnel
        self.conversation_history: List[SophIAResponse] = []
        self.learning_buffer: List[Dict[str, Any]] = []
        
        # Paramètres de fonctionnement
        self.response_temperature = 0.7
        self.conceptual_weight = 0.6
        self.learning_threshold = 0.3
        
        # Perf monitoring optimization
        self.performance_mode = performance_mode
        self._configure_performance_settings()
        
        logger.info(f"SophIA Hybride Enhanced initialisée : session '{session_name}'")
        self._log_system_status()
    
    def _initialize_advanced_modules(self):
        """Initialise les modules avancés disponibles"""
        
        # Performance Monitor
        self.perf_monitor = None
        if PERFORMANCE_MONITOR_AVAILABLE:
            try:
                self.perf_monitor = PerformanceMonitor()
                logger.info("📊 Performance Monitor activé")
            except Exception as e:
                logger.warning(f"Erreur Performance Monitor: {e}")
        
        # Tokenizer philosophique
        self.tokenizer = None
        if TOKENIZER_AVAILABLE:
            try:
                self.tokenizer = PhilosophicalTokenizer()
                logger.info("📝 Tokenizer philosophique activé")
            except Exception as e:
                logger.warning(f"Erreur Tokenizer: {e}")
        
        # Autonomous Learner
        self.autonomous_learner = None
        if AUTONOMOUS_LEARNER_AVAILABLE:
            try:
                self.autonomous_learner = AutonomousLearner(self.ontology, self.lcm_model)
                logger.info("🤖 Autonomous Learner activé")
            except Exception as e:
                logger.warning(f"Erreur Autonomous Learner: {e}")
    
    def _log_system_status(self):
        """Affiche le statut des composants"""
        llm_info = self.llm.get_model_info()
        logger.info(f"📚 Ontologie: {len(self.ontology.concepts)} concepts")
        logger.info(f"🧠 LCM: {len(self.lcm_model.transitions)} transitions")
        logger.info(f"🦙 LLaMA: {llm_info['status']} ({llm_info['model_name']})")
        
        # Bridge status - le cache s'appelle _cache
        bridge_cache_size = len(self.concept_bridge._cache) if hasattr(self.concept_bridge, '_cache') else 0
        logger.info(f"🔗 Bridge: {bridge_cache_size} éléments en cache")
        logger.info(f"⚖️ Contraintes: {len(self.constraint_manager.constraints)} actives")
        
        # Status modules avancés
        modules_status = []
        if self.perf_monitor:
            modules_status.append("📊 Performance")
        if self.tokenizer:
            modules_status.append("📝 Tokenizer")
        if self.autonomous_learner:
            modules_status.append("🤖 Learner")
        
        if modules_status:
            logger.info(f"🚀 Modules avancés: {', '.join(modules_status)}")
        else:
            logger.info("🚀 Modules avancés: Aucun module optionnel activé (fonctionnement core)")
            
    
    def ask(self, question: str, context: Optional[str] = None) -> SophIAResponse:
        """Interface principale pour poser une question à SophIA avec monitoring ultra-avancé"""
        
        # Performance tracking global avec métadonnées
        operation_id = None
        if self.perf_monitor:
            operation_id = self.perf_monitor.start_operation(
                "ask_question",
                metadata={
                    'question_length': len(question),
                    'has_context': context is not None,
                    'session': self.session_name
                }
            )
        
        logger.info(f"❓ Question reçue: {question}")
        
        try:
            # Phase 1: Analyse conceptuelle enrichie multi-niveaux
            concept_op_id = None
            if self.perf_monitor:
                concept_op_id = self.perf_monitor.start_operation(
                    "concept_extraction",
                    metadata={'extraction_method': 'enhanced_bridge'}
                )
            
            conceptual_analysis = self._extract_concepts_from_question(question)
            
            if self.perf_monitor and concept_op_id:
                self.perf_monitor.end_operation(
                    concept_op_id,
                    metadata={
                        'concepts_found': len(conceptual_analysis.get('concepts_detected', [])),
                        'confidence': conceptual_analysis.get('enhanced_confidence', 0)
                    }
                )
            
            # Phase 2: Raisonnement LCM
            lcm_op_id = None
            if self.perf_monitor:
                lcm_op_id = self.perf_monitor.start_operation(
                    "lcm_reasoning",
                    metadata={'input_concepts': len(conceptual_analysis.get('concepts_detected', []))}
                )
            
            lcm_reasoning = self._generate_lcm_reasoning(conceptual_analysis)
            
            if self.perf_monitor and lcm_op_id:
                self.perf_monitor.end_operation(
                    lcm_op_id,
                    metadata={
                        'reasoning_paths': len(lcm_reasoning.get('reasoning_paths', [])),
                        'reasoning_confidence': lcm_reasoning.get('reasoning_confidence', 0)
                    }
                )
            
            # Phase 3: Génération hybride
            llm_op_id = None
            if self.perf_monitor:
                llm_op_id = self.perf_monitor.start_operation(
                    "llm_generation",
                    metadata={'prompt_type': 'enhanced_conceptual'}
                )
            
            natural_response = self._generate_hybrid_response(question, conceptual_analysis, context)
            
            if self.perf_monitor and llm_op_id:
                self.perf_monitor.end_operation(
                    llm_op_id,
                    metadata={
                        'response_length': len(natural_response),
                        'words_generated': len(natural_response.split())
                    }
                )
            
            # Phase 4: Validation par contraintes
            validation_op_id = None
            if self.perf_monitor:
                validation_op_id = self.perf_monitor.start_operation(
                    "validation",
                    metadata={'constraints_count': len(self.constraint_manager.constraints)}
                )
            
            validation_context = {
                **conceptual_analysis,
                'question': question,
                'context': context
            }
            validation_report = self._validate_and_improve_response(natural_response, validation_context)
            
            if self.perf_monitor and validation_op_id:
                self.perf_monitor.end_operation(
                    validation_op_id,
                    metadata={
                        'validation_score': validation_report.get('global_score', 0),
                        'violations': len(validation_report.get('violations', []))
                    }
                )
            
            # Phase 5: Analyse avancée (tokenizer, etc.)
            advanced_analysis = self._perform_advanced_analysis(question, natural_response)
            
            # Phase 6: Calcul de confiance globale
            confidence = self._calculate_global_confidence(conceptual_analysis, validation_report)
            
            # Phase 7: Construction de la réponse complète
            response = SophIAResponse(
                question=question,
                natural_response=natural_response,
                conceptual_analysis=conceptual_analysis,
                lcm_reasoning=lcm_reasoning,
                confidence=confidence,
                timestamp=datetime.now(),
                validation_report=validation_report
            )
            
            # Ajout des analyses avancées
            response.advanced_analysis = advanced_analysis
            
            # Phase 8: Métriques de performance détaillées
            if self.perf_monitor and operation_id:
                perf_metrics = self.perf_monitor.end_operation(
                    operation_id,
                    metadata={
                        'final_confidence': confidence,
                        'concepts_processed': len(conceptual_analysis.get('concepts_detected', [])),
                        'response_quality': validation_report.get('global_score', 0),
                        'success': True
                    }
                )
                response.performance_metrics = perf_metrics
                
                duration = perf_metrics.get('duration', 0)
                logger.info(f"⏱️ Performance totale: {duration:.2f}s")
                
                # Affichage des métriques détaillées si performance dégradée
                if duration > 3.0:
                    logger.warning(f"🐌 Réponse lente détectée ({duration:.2f}s)")
                    if hasattr(self.perf_monitor, 'get_optimization_recommendations'):
                        recommendations = self.perf_monitor.get_optimization_recommendations()
                        if recommendations:
                            logger.info(f"💡 Recommandations disponibles: {len(recommendations)}")
            
            # Phase 9: Apprentissage automatique (autonome si disponible)
            if self._should_learn_from_interaction(response):
                learn_op_id = None
                if self.perf_monitor:
                    learn_op_id = self.perf_monitor.start_operation("learning")
                
                self._learn_from_interaction(response)
                
                if self.perf_monitor and learn_op_id:
                    self.perf_monitor.end_operation(learn_op_id)
            
            # Phase 10: Sauvegarde dans l'historique
            self.conversation_history.append(response)
            
            logger.info(f"✅ Réponse générée (confiance: {confidence:.3f})")
            return response
            
        except Exception as e:
            error_msg = str(e)
            if self.perf_monitor and operation_id:
                self.perf_monitor.end_operation(operation_id, error=error_msg)
            
            logger.error(f"❌ Erreur génération réponse: {e}")
            
            # Réponse d'erreur
            error_response = SophIAResponse(
                question=question,
                natural_response=f"Je rencontre une difficulté pour traiter votre question. Erreur: {error_msg}",
                conceptual_analysis={'concepts_detected': [], 'confidence': 0.0},
                lcm_reasoning={'reasoning_paths': []},
                confidence=0.0,
                timestamp=datetime.now(),
                validation_report={'error': error_msg}
            )
            return error_response
    
    
    def _patch_bridge_for_speed(self):
        """Patch temporaire pour accélérer le bridge"""
        
        original_extraction = self.concept_bridge.enhanced_concept_extraction
        
        def fast_enhanced_extraction(text, base_extraction, fast_mode=False):
            if fast_mode and self.performance_mode == "speed":
                # Mode rapide - minimal enhancement
                concepts = base_extraction.get('concepts_detected', [])
                
                # Juste une vérification rapide des synonymes principaux
                fast_synonyms = {
                    'libre': 'LIBERTÉ', 'liberte': 'LIBERTÉ',
                    'vrai': 'VÉRITÉ', 'verite': 'VÉRITÉ', 
                    'juste': 'JUSTICE', 'equitable': 'JUSTICE',
                    'beau': 'BEAUTÉ', 'bel': 'BEAUTÉ',
                    'bien': 'BIEN', 'bon': 'BIEN',
                    'mal': 'MAL', 'mauvais': 'MAL'
                }
                
                text_lower = text.lower()
                for synonym, concept in fast_synonyms.items():
                    if synonym in text_lower and concept not in concepts:
                        concepts.append(concept)
                        logger.debug(f"🚀 Synonyme rapide: {synonym} → {concept}")
                
                return {
                    'concepts_detected': concepts,
                    'enhanced_confidence': base_extraction.get('confidence', 0.7) + 0.1,
                    'method': 'fast_enhanced',
                    'relations_implied': [],
                    'conceptual_paths': []
                }
            else:
                # Mode normal
                return original_extraction(text, base_extraction)
        
        # Applique le patch
        self.concept_bridge.enhanced_concept_extraction = fast_enhanced_extraction
    
    
    def _extract_concepts_from_question(self, question: str) -> Dict[str, Any]:
        """Extraction conceptuelle ultra-robuste avec fallbacks multiples"""
        
        # Cache pour éviter les extractions répétées
        question_hash = hash(question.lower().strip())
        cache_key = f"concept_extraction_{question_hash}"
        
        if hasattr(self, '_extraction_cache') and cache_key in self._extraction_cache:
            logger.debug("🚀 Extraction concepts depuis cache")
            return self._extraction_cache[cache_key]
        
        # Initialise le cache si nécessaire
        if not hasattr(self, '_extraction_cache'):
            self._extraction_cache = {}
        
        enhanced_extraction = None
        
        # Tentative 1: LLM Extractor selon le mode
        if LLM_EXTRACTOR_AVAILABLE:
            try:
                extractor = LLMConceptExtractor(self.ontology, self.llm, enable_advanced_inference=False)
                
                if self.performance_mode == "speed":
                    # Vérifier si la méthode existe
                    if hasattr(extractor, 'extract_concepts_fast'):
                        enhanced_extraction = extractor.extract_concepts_fast(question, max_concepts=4)
                        logger.debug(f"🚀 LLM Extractor TURBO utilisé")
                    else:
                        enhanced_extraction = extractor.extract_concepts(question, max_concepts=4)
                        logger.debug(f"🚀 LLM Extractor standard utilisé")
                elif self.performance_mode == "quality":
                    enhanced_extraction = extractor.extract_concepts(question, max_concepts=8)
                    logger.debug(f"🎯 LLM Extractor QUALITY utilisé")
                else:  # balanced
                    enhanced_extraction = extractor.extract_concepts(question, max_concepts=6)
                    logger.debug(f"⚖️ LLM Extractor BALANCED utilisé")
                    
            except Exception as e:
                logger.warning(f"Erreur LLM Extractor: {e}")
                enhanced_extraction = None
        
        # Tentative 2: Fallback avec bridge enhanced
        if enhanced_extraction is None:
            try:
                base_extraction = self.llm.extract_concepts_from_text(
                    question, list(self.ontology.concepts.keys())
                )
                
                enhanced_extraction = self.concept_bridge.enhanced_concept_extraction(
                    question, base_extraction
                )
                logger.debug(f"📚 Bridge enhanced utilisé en fallback")
                
            except Exception as e:
                logger.warning(f"Erreur bridge enhancement: {e}")
                enhanced_extraction = None
        
        # Tentative 3: Fallback basique LLaMA
        if enhanced_extraction is None:
            try:
                base_extraction = self.llm.extract_concepts_from_text(
                    question, list(self.ontology.concepts.keys())
                )
                
                enhanced_extraction = {
                    'concepts_detected': base_extraction.get('concepts_detected', []),
                    'enhanced_confidence': base_extraction.get('confidence', 0.5),
                    'confidence': base_extraction.get('confidence', 0.5),
                    'relations_implied': [],
                    'conceptual_paths': [],
                    'extraction_details': {
                        'metadata': {'extraction_method': 'llama_basic'}
                    }
                }
                logger.debug(f"🦙 LLaMA basique utilisé en fallback")
                
            except Exception as e:
                logger.warning(f"Erreur extraction LLaMA: {e}")
                enhanced_extraction = None
        
        # Tentative 4: Fallback ultime - détection manuelle
        if enhanced_extraction is None:
            logger.warning("Utilisation du fallback ultime - détection manuelle")
            enhanced_extraction = self._manual_concept_detection(question)
        
        # Mise en cache
        self._extraction_cache[cache_key] = enhanced_extraction
        
        # Limite la taille du cache
        if len(self._extraction_cache) > 50:
            oldest_key = next(iter(self._extraction_cache))
            del self._extraction_cache[oldest_key]
        
        return enhanced_extraction

    def _manual_concept_detection(self, question: str) -> Dict[str, Any]:
        """Détection manuelle de concepts comme fallback ultime"""
        
        detected_concepts = []
        question_lower = question.lower()
        
        # Mapping manuel des concepts principaux
        concept_keywords = {
            'VÉRITÉ': ['vérité', 'vrai', 'véracité', 'vraie', 'véridique'],
            'JUSTICE': ['justice', 'juste', 'équitable', 'équité', 'injuste'],
            'BEAUTÉ': ['beauté', 'beau', 'belle', 'esthétique', 'sublime'],
            'BIEN': ['bien', 'bon', 'bonne', 'bonté', 'vertu'],
            'MAL': ['mal', 'mauvais', 'mauvaise', 'vice', 'méchant'],
            'ÊTRE': ['être', 'existence', 'exister', 'existant'],
            'CONNAISSANCE': ['connaissance', 'savoir', 'connaître', 'science'],
            'LIBERTÉ': ['liberté', 'libre', 'libérer', 'affranchir'],
            'ART': ['art', 'artistique', 'œuvre', 'création'],
            'CONSCIENCE': ['conscience', 'conscient', 'éveil', 'esprit'],
            'LOGIQUE': ['logique', 'raisonnement', 'argument', 'preuve'],
            'MORALE': ['morale', 'moral', 'éthique', 'éthiquement'],
            'TEMPS': ['temps', 'temporel', 'durée', 'instant'],
            'RÉALITÉ': ['réalité', 'réel', 'réelle', 'existence']
        }
        
        confidence_sum = 0.0
        
        for concept, keywords in concept_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    detected_concepts.append(concept)
                    confidence_sum += 0.8  # Confiance élevée pour détection directe
                    break  # Un seul match par concept
        
        # Calcul de confiance globale
        if detected_concepts:
            global_confidence = min(confidence_sum / len(detected_concepts), 1.0)
        else:
            global_confidence = 0.3  # Confiance minimale
            # Ajout d'un concept générique si rien trouvé
            if any(word in question_lower for word in ['?', 'que', 'qu', 'comment', 'pourquoi']):
                detected_concepts = ['CONNAISSANCE']  # Question générale
                global_confidence = 0.5
        
        return {
            'concepts_detected': detected_concepts,
            'enhanced_confidence': global_confidence,
            'confidence': global_confidence,
            'relations_implied': [],
            'conceptual_paths': [],
            'extraction_details': {
                'metadata': {'extraction_method': 'manual_detection'}
            }
        }

    def _fallback_concept_extraction_speed(self, question: str) -> Dict[str, Any]:
        """Extraction de fallback ultra-rapide pour mode speed"""
        
        # Extraction basique LLaMA
        base_extraction = self.llm.extract_concepts_from_text(
            question, list(self.ontology.concepts.keys())
        )
        
        # Enhancement simple sans fast_mode - CORRIGÉ
        try:
            enhanced_extraction = self.concept_bridge.enhanced_concept_extraction(
                question, base_extraction
            )
        except Exception as e:
            logger.warning(f"Erreur bridge enhancement: {e}")
            # Fallback ultime
            enhanced_extraction = {
                'concepts_detected': base_extraction.get('concepts_detected', []),
                'enhanced_confidence': base_extraction.get('confidence', 0.5),
                'confidence': base_extraction.get('confidence', 0.5),
                'relations_implied': [],
                'conceptual_paths': [],
                'extraction_details': {
                    'metadata': {'extraction_method': 'basic_fallback'}
                }
            }
        
        return enhanced_extraction

    def _extract_concepts_balanced_mode(self, question: str) -> Dict[str, Any]:
        """Extraction équilibrée pour mode balanced"""
        
        if LLM_EXTRACTOR_AVAILABLE:
            try:
                extractor = LLMConceptExtractor(self.ontology, self.llm, enable_advanced_inference=False)
                enhanced_extraction = extractor.extract_concepts(question, max_concepts=6)
                logger.debug(f"⚖️ LLM Extractor BALANCED: {enhanced_extraction.get('concepts_detected', [])}")
                return enhanced_extraction
            except Exception as e:
                logger.warning(f"Erreur LLM Extractor balanced: {e}")
        
        return self._fallback_concept_extraction_speed(question)

    def _extract_concepts_quality_mode(self, question: str) -> Dict[str, Any]:
        """Extraction de qualité maximale pour mode quality"""
        
        if LLM_EXTRACTOR_AVAILABLE:
            try:
                extractor = LLMConceptExtractor(self.ontology, self.llm, enable_advanced_inference=True)
                enhanced_extraction = extractor.extract_concepts(question, max_concepts=8)
                logger.debug(f"🎯 LLM Extractor QUALITY: {enhanced_extraction.get('concepts_detected', [])}")
                return enhanced_extraction
            except Exception as e:
                logger.warning(f"Erreur LLM Extractor quality: {e}")
        
        return self._fallback_concept_extraction_speed(question)
    
    def _perform_advanced_analysis(self, question: str, response: str) -> Dict[str, Any]:
        """Effectue des analyses avancées avec les modules disponibles"""
        
        analysis = {}
        
        # Analyse avec tokenizer philosophique
        if self.tokenizer:
            try:
                analysis['tokenizer'] = {
                    'question_tokens': self.tokenizer.tokenize(question),
                    'response_tokens': self.tokenizer.tokenize(response),
                    'philosophical_terms': self.tokenizer.extract_philosophical_terms(response),
                    'complexity_score': self.tokenizer.calculate_complexity(response)
                }
                logger.debug(f"📝 Analyse tokenizer: {analysis['tokenizer']['complexity_score']:.3f}")
            except Exception as e:
                logger.warning(f"Erreur analyse tokenizer: {e}")
        
        # Analyse de performance détaillée - CORRIGÉE
        if self.perf_monitor:
            try:
                analysis['performance'] = {
                    'active_operations_count': len(self.perf_monitor.active_operations),
                    'completed_operations_count': len(self.perf_monitor.completed_operations),
                    'session_duration_minutes': (time.time() - self.perf_monitor.session_start) / 60,
                    'efficiency_score': self.perf_monitor.calculate_efficiency()
                }
                
                # Ajout des métriques mémoire/CPU seulement si disponible
                try:
                    memory_info = self.perf_monitor.get_memory_usage()
                    analysis['performance']['memory_status'] = memory_info['memory_status']
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Erreur analyse performance: {e}")
                analysis['performance'] = {'error': str(e)}
        
        return analysis
    
    def _generate_lcm_reasoning(self, conceptual_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un raisonnement LCM basé sur l'analyse conceptuelle"""
        
        detected_concepts = conceptual_analysis.get('concepts_detected', [])
        reasoning_paths = []
        
        if detected_concepts:
            for concept_name in detected_concepts[:3]:
                if concept_name in self.ontology.concepts:
                    try:
                        sequence = self.lcm_model.generate_sequence(
                            concept_name, length=4, temperature=0.8
                        )
                        if sequence:
                            reasoning_paths.append({
                                'start_concept': concept_name,
                                'reasoning_path': [c.name for c in sequence],
                                'path_probability': self.lcm_model.evaluate_sequence_probability(sequence)
                            })
                    except Exception as e:
                        logger.warning(f"Erreur génération séquence pour {concept_name}: {e}")
        
        return {
            'reasoning_paths': reasoning_paths,
            'total_paths': len(reasoning_paths),
            'reasoning_confidence': sum(p['path_probability'] for p in reasoning_paths) / max(len(reasoning_paths), 1)
        }
    
    
    def _generate_hybrid_response(self, question: str, conceptual_analysis: Dict[str, Any], 
                            context: Optional[str] = None) -> str:
        """Génération hybride optimisée sans timeout (non supporté par Ollama)"""
        
        enriched_prompt = self._build_conceptually_enriched_prompt(
            question, conceptual_analysis, context
        )
        
        constraints = self._build_conceptual_constraints(conceptual_analysis)
        
        # Génération optimisée sans timeout
        try:
            confidence_threshold = conceptual_analysis.get('enhanced_confidence', 
                                                         conceptual_analysis.get('confidence', 0))
            
            if constraints and confidence_threshold > self.learning_threshold:
                # Tentative avec contraintes (simplifiée)
                try:
                    generation_result = self.llm.generate_with_constraints(
                        enriched_prompt, constraints, max_attempts=1  # Réduit pour vitesse
                    )
                    response = generation_result['text']
                    
                    if not generation_result.get('constraints_satisfied', False):
                        logger.debug("Contraintes non respectées, fallback génération libre")
                        raise Exception("Constraints not satisfied")
                        
                except Exception as e:
                    logger.debug(f"Génération contrainte échouée: {e}, fallback libre")
                    response = self.llm.generate_text(
                        enriched_prompt, 
                        max_tokens=self._max_llm_tokens
                    )
            else:
                # Génération libre directe (plus rapide)
                response = self.llm.generate_text(
                    enriched_prompt, 
                    max_tokens=self._max_llm_tokens
                )
            
            return response
            
        except Exception as e:
            logger.warning(f"❌ Erreur génération LLaMA: {e}")
            
            # Fallback ultime - prompt simplifié
            fallback_prompt = f"Réponds brièvement en français à cette question philosophique: {question}"
            try:
                return self.llm.generate_text(fallback_prompt, max_tokens=300)
            except Exception as fallback_error:
                logger.error(f"❌ Fallback échoué: {fallback_error}")
                return f"Je rencontre des difficultés pour répondre à votre question sur '{question}'. Cela pourrait être lié à la complexité du sujet ou à un problème technique temporaire."
    
    def _build_conceptually_enriched_prompt(self, question: str, 
                                          conceptual_analysis: Dict[str, Any],
                                          context: Optional[str] = None) -> str:
        """Construit un prompt enrichi par l'analyse conceptuelle"""
        
        base_prompt = f"""Tu es SophIA, une IA philosophique qui combine raisonnement conceptuel et expression naturelle.

QUESTION: {question}"""
        
        if context:
            base_prompt += f"\nCONTEXTE: {context}"
        
        detected_concepts = conceptual_analysis.get('concepts_detected', [])
        conceptual_paths = conceptual_analysis.get('conceptual_paths', [])
        
        if detected_concepts:
            base_prompt += f"\n\nCONCEPTS IDENTIFIÉS: {', '.join(detected_concepts)}"
        
        if conceptual_paths:
            base_prompt += "\n\nCHEMINS DE RAISONNEMENT CONCEPTUEL:"
            for i, path in enumerate(conceptual_paths[:2], 1):
                path_str = " → ".join(path['reasoning_path'])
                base_prompt += f"\n{i}. {path_str}"
        
        relations = conceptual_analysis.get('relations_implied', [])
        if relations:
            base_prompt += "\n\nRELATIONS CONCEPTUELLES:"
            for relation in relations[:3]:
                base_prompt += f"\n- {relation['from']} {relation['relation']} {relation['to']}"
        
        base_prompt += "\n\nRéponds en intégrant ces éléments conceptuels de manière naturelle et philosophiquement rigoureuse."
        
        return base_prompt
    
    def _build_conceptual_constraints(self, conceptual_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les contraintes basées sur l'analyse conceptuelle"""
        
        constraints = {}
        
        detected_concepts = conceptual_analysis.get('concepts_detected', [])
        if detected_concepts:
            constraints['required_concepts'] = detected_concepts[:3]
        
        relations = conceptual_analysis.get('relations_implied', [])
        if relations:
            normalized_relations = []
            for relation in relations[:2]:
                normalized_relation = {
                    'from': relation.get('from', ''),
                    'to': relation.get('to', ''),
                    'relation': relation.get('relation', relation.get('type', 'IMPLIES'))
                }
                normalized_relations.append(normalized_relation)
            
            constraints['required_relations'] = normalized_relations
        
        constraints.update({
            'tone': 'philosophique et analytique',
            'max_tokens': 600
        })
        
        return constraints
    
    def _validate_and_improve_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et améliore la réponse selon les contraintes philosophiques"""
        
        validation_report = self.constraint_manager.validate_response(response, context)
        
        logger.info(f"📊 Score de validation: {validation_report['global_score']:.2f}")
        
        if not validation_report['is_valid']:
            logger.warning(f"⚠️ Violations: {len(validation_report['violations'])}")
            for violation in validation_report['violations']:
                logger.warning(f"  - {violation['constraint']}: {violation['score']:.2f}")
        
        return validation_report
    
    def _calculate_global_confidence(self, conceptual_analysis: Dict[str, Any], 
                                   validation_report: Dict[str, Any]) -> float:
        """Calcule la confiance globale de la réponse"""
        
        concept_confidence = conceptual_analysis.get('enhanced_confidence', 
                                                   conceptual_analysis.get('confidence', 0.5))
        validation_confidence = validation_report.get('global_score', 0.5)
        
        # Moyenne pondérée
        global_confidence = (concept_confidence * 0.6) + (validation_confidence * 0.4)
        
        return min(global_confidence, 1.0)
    
    def _should_learn_from_interaction(self, response: 'SophIAResponse') -> bool:
        """Détermine si l'interaction mérite un apprentissage"""
        
        if not self.autonomous_learner:
            return False
        
        # Critères d'apprentissage
        sufficient_confidence = response.confidence > 0.6
        has_concepts = len(response.conceptual_analysis.get('concepts_detected', [])) > 0
        reasonable_validation = response.validation_report.get('global_score', 0) > 0.4
        
        return sufficient_confidence and has_concepts and reasonable_validation

    def _learn_from_interaction(self, response: 'SophIAResponse'):
        """Effectue l'apprentissage autonome depuis une interaction"""
        
        try:
            if not self.autonomous_learner:
                return
            
            # Préparation des données d'apprentissage - CORRIGÉ
            response_data = {
                'conceptual_analysis': response.conceptual_analysis,
                'confidence': response.confidence,
                'validation_report': response.validation_report,
                'natural_response': response.natural_response,
                'lcm_reasoning': getattr(response, 'lcm_reasoning', {}),
                'performance_metrics': getattr(response, 'performance_metrics', {})
            }
            
            # Apprentissage autonome - MÉTHODE CORRIGÉE
            learning_result = self.autonomous_learner.learn_from_interaction(
                question=response.question,  # Paramètre explicite
                response_data=response_data,  # Paramètre explicite
                feedback_score=None  # Pas de feedback automatique
            )
            
            # Log des résultats d'apprentissage
            if learning_result.get('patterns_discovered', 0) > 0:
                logger.info(f"🧠 Apprentissage: {learning_result['patterns_discovered']} nouveaux patterns")
            
            if learning_result.get('adaptations_triggered'):
                logger.info(f"🔄 Adaptations autonomes déclenchées")
                
        except Exception as e:
            logger.error(f"Erreur apprentissage autonome: {e}")
            # Continue sans bloquer la réponse principale
    
    def explain_reasoning(self, question: str) -> Dict[str, Any]:
        """Explique le processus de raisonnement de SophIA pour une question"""
        
        conceptual_analysis = self._extract_concepts_from_question(question)
        lcm_reasoning = self._generate_lcm_reasoning(conceptual_analysis)
        
        explanation = {
            'question': question,
            'step1_concept_detection': {
                'method': 'Multi-niveau: LLM Extractor + Bridge Enhanced',
                'concepts_found': conceptual_analysis['concepts_detected'],
                'confidence': conceptual_analysis.get('enhanced_confidence', conceptual_analysis.get('confidence', 0))
            },
            'step2_conceptual_reasoning': {
                'method': 'LCM path generation',
                'reasoning_paths': lcm_reasoning['reasoning_paths'],
                'total_paths': lcm_reasoning['total_paths']
            },
            'step3_constraint_validation': {
                'constraints_available': len(self.constraint_manager.constraints),
                'philosophical_clusters': len(self.constraint_manager.philosophical_clusters)
            },
            'step4_synthesis': {
                'how_response_built': 'Enhanced multi-level conceptual analysis guides constrained LLaMA generation'
            },
            'advanced_modules': {
                'performance_monitor': self.perf_monitor is not None,
                'tokenizer': self.tokenizer is not None,
                'autonomous_learner': self.autonomous_learner is not None,
                'llm_extractor': LLM_EXTRACTOR_AVAILABLE
            }
        }
        
        return explanation
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la conversation en cours avec métriques avancées"""
        
        if not self.conversation_history:
            return {'status': 'no_conversation'}
        
        all_concepts = []
        validation_scores = []
        performance_data = []
        
        for response in self.conversation_history:
            all_concepts.extend(response.conceptual_analysis.get('concepts_detected', []))
            validation_scores.append(response.validation_report.get('global_score', 0))
            
            if hasattr(response, 'performance_metrics') and response.performance_metrics:
                duration = response.performance_metrics.get('duration', 0)
                if duration > 0:
                    performance_data.append(duration)
        
        concept_frequency = {}
        for concept in all_concepts:
            concept_frequency[concept] = concept_frequency.get(concept, 0) + 1
        
        top_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Calculs de performance
        avg_response_time = sum(performance_data) / len(performance_data) if performance_data else 0
        learning_events = sum(1 for r in self.conversation_history if hasattr(r, 'learning_triggered') and r.learning_triggered)
        
        return {
            'total_interactions': len(self.conversation_history),
            'most_discussed_concepts': top_concepts[:5],
            'average_confidence': sum(r.confidence for r in self.conversation_history) / len(self.conversation_history),
            'average_validation': sum(validation_scores) / len(validation_scores) if validation_scores else 0,
            'average_response_time': avg_response_time,
            'learning_events': learning_events,
            'system_performance': {
                'concept_bridge_active': True,
                'constraint_manager_active': True,
                'lcm_transitions': len(self.lcm_model.transitions),
                'performance_monitor_active': self.perf_monitor is not None,
                'tokenizer_active': self.tokenizer is not None,
                'autonomous_learner_active': self.autonomous_learner is not None
            },
            'advanced_modules_status': {
                'llm_extractor': LLM_EXTRACTOR_AVAILABLE,
                'tokenizer': TOKENIZER_AVAILABLE,
                'performance_monitor': PERFORMANCE_MONITOR_AVAILABLE,
                'autonomous_learner': AUTONOMOUS_LEARNER_AVAILABLE
            }
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport de performance détaillé"""
        
        if not self.perf_monitor:
            return {'error': 'Performance Monitor non disponible'}
        
        try:
            return {
                'overall_performance': self.perf_monitor.get_overall_stats(),
                'operation_breakdown': self.perf_monitor.get_operation_stats(),
                'memory_usage': self.perf_monitor.get_memory_usage(),
                'efficiency_metrics': self.perf_monitor.get_efficiency_metrics(),
                'recommendations': self.perf_monitor.get_optimization_recommendations()
            }
        except Exception as e:
            return {'error': f'Erreur génération rapport performance: {e}'}
    
    def save_session(self, final_notes: str = "") -> str:
        """Sauvegarde la session complète avec métriques avancées"""
        
        if not self.session:
            raise ValueError("Auto-save désactivé, impossible de sauvegarder")
        
        # Cache size avec le bon attribut _cache
        bridge_cache_size = len(self.concept_bridge._cache) if hasattr(self.concept_bridge, '_cache') else 0
        
        final_metrics = {
            'conversation_summary': self.get_conversation_summary(),
            'performance_report': self.get_performance_report(),
            'final_notes': final_notes,
            'system_status': {
                'ontology_concepts': len(self.ontology.concepts),
                'lcm_transitions': len(self.lcm_model.transitions),
                'llm_status': self.llm.get_model_info()['status'],
                'bridge_cache_size': bridge_cache_size,
                'constraint_violations': sum(
                    len(r.validation_report.get('violations', []))
                    for r in self.conversation_history
                ),
                'advanced_modules': {
                    'performance_monitor': self.perf_monitor is not None,
                    'tokenizer': self.tokenizer is not None,
                    'autonomous_learner': self.autonomous_learner is not None
                }
            }
        }
        
        return self.session.save_final_model(
            self.lcm_model, self.ontology, self.trainer, final_metrics
        )
    
    def load_session(self, session_name: str) -> bool:
        """Charge une session sauvegardée et réinitialise les modules avancés"""
        
        try:
            session = TrainingSession(session_name)
            
            try:
                model, ontology, trainer, metadata = session.load_final_model()
            except FileNotFoundError:
                latest = session.load_latest_checkpoint()
                if latest:
                    model, ontology, trainer, metadata = latest
                else:
                    return False
            
            self.lcm_model = model
            self.ontology = ontology
            self.trainer = trainer
            self.session = session
            
            # Réinitialisation des modules avancés avec la nouvelle ontologie
            self.concept_bridge = EnhancedConceptTextBridge(self.ontology, self.llm)
            self.constraint_manager = PhilosophicalConstraintManager(self.ontology, self.llm)
            
            # Réinitialisation des modules avancés optionnels
            self._initialize_advanced_modules()
            
            logger.info(f"Session '{session_name}' chargée avec succès")
            self._log_system_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur chargement session: {e}")
            return False
    
    def _configure_performance_settings(self):
        """Configure les paramètres de performance selon le mode"""
        
        if self.performance_mode == "speed":
            # Mode rapide - sacrifie un peu de qualité pour la vitesse
            self.response_temperature = 0.5
            self.conceptual_weight = 0.5
            self.learning_threshold = 0.5
            self._max_llm_tokens = 400
            self._llm_timeout = 15  # 15s max pour LLaMA
            logger.info("⚡ Mode performance: SPEED")
            
        elif self.performance_mode == "quality":
            # Mode qualité - prend plus de temps mais meilleure qualité
            self.response_temperature = 0.8
            self.conceptual_weight = 0.7
            self.learning_threshold = 0.2
            self._max_llm_tokens = 800
            self._llm_timeout = 30
            logger.info("🎯 Mode performance: QUALITY")
            
        else:  # balanced
            # Mode équilibré (défaut)
            self.response_temperature = 0.7
            self.conceptual_weight = 0.6
            self.learning_threshold = 0.3
            self._max_llm_tokens = 600
            self._llm_timeout = 20
            logger.info("⚖️ Mode performance: BALANCED")
        
        # Configure les seuils du performance monitor
        if self.perf_monitor:
            if self.performance_mode == "speed":
                self.perf_monitor.set_thresholds(slow_threshold=2.0, memory_threshold=30, cpu_threshold=60)
            elif self.performance_mode == "quality":
                self.perf_monitor.set_thresholds(slow_threshold=8.0, memory_threshold=100, cpu_threshold=90)
            else:  # balanced
                self.perf_monitor.set_thresholds(slow_threshold=4.0, memory_threshold=50, cpu_threshold=70)