"""
Système hybride SophIA : LCM + LLaMA avec modules avancés
Combinaison du raisonnement conceptuel et de la génération naturelle
"""

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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'natural_response': self.natural_response,
            'conceptual_analysis': self.conceptual_analysis,
            'lcm_reasoning': self.lcm_reasoning,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'validation_report': self.validation_report
        }

class HybridSophIA:
    """
    Système hybride SophIA combinant :
    - Raisonnement conceptuel (LCM)
    - Génération naturelle (LLaMA)
    - Pont conceptuel avancé
    - Validation par contraintes
    - Apprentissage continu
    """
    
    def __init__(self, session_name: str = "sophia_hybrid", 
                 llm_model: str = "llama3.1:latest",
                 auto_save: bool = True):
        
        self.session_name = session_name
        self.auto_save = auto_save
        
        # Composants principaux
        self.ontology = SimpleOntology()
        self.lcm_model = SimpleLCM(self.ontology)
        self.trainer = OntologyAwareLCMTrainer(self.lcm_model, self.ontology)
        self.llm = OllamaLLaMAInterface(model_name=llm_model)
        
        # Modules avancés
        self.concept_bridge = EnhancedConceptTextBridge(self.ontology, self.llm)
        self.constraint_manager = PhilosophicalConstraintManager(self.ontology, self.llm)
        
        # Système de session pour persistance
        self.session = TrainingSession(session_name) if auto_save else None
        
        # Historique conversationnel
        self.conversation_history: List[SophIAResponse] = []
        self.learning_buffer: List[Dict[str, Any]] = []
        
        # Paramètres de fonctionnement
        self.response_temperature = 0.7
        self.conceptual_weight = 0.6
        self.learning_threshold = 0.3
        
        logger.info(f"SophIA Hybride initialisée : session '{session_name}'")
        self._log_system_status()
    
    def _log_system_status(self):
        """Affiche le statut des composants"""
        llm_info = self.llm.get_model_info()
        logger.info(f"Ontologie: {len(self.ontology.concepts)} concepts")
        logger.info(f"LCM: {len(self.lcm_model.transitions)} transitions")
        logger.info(f"LLaMA: {llm_info['status']} ({llm_info['model_name']})")
    
    def ask(self, question: str, context: Optional[str] = None) -> SophIAResponse:
        """Interface principale pour poser une question à SophIA"""
        
        logger.info(f"Question reçue: {question}")
        
        # Phase 1: Analyse conceptuelle enrichie
        conceptual_analysis = self._extract_concepts_from_question(question)
        
        # Phase 2: Raisonnement LCM
        lcm_reasoning = self._generate_lcm_reasoning(conceptual_analysis)
        
        # Phase 3: Génération hybride
        natural_response = self._generate_hybrid_response(question, conceptual_analysis, context)
        
        # Phase 4: Validation par contraintes
        validation_context = {
            **conceptual_analysis,
            'question': question,
            'context': context
        }
        validation_report = self._validate_and_improve_response(natural_response, validation_context)
        
        # Phase 5: Calcul de confiance globale
        confidence = self._calculate_global_confidence(conceptual_analysis, validation_report)
        
        # Phase 6: Construction de la réponse complète
        response = SophIAResponse(
            question=question,
            natural_response=natural_response,
            conceptual_analysis=conceptual_analysis,
            lcm_reasoning=lcm_reasoning,
            confidence=confidence,
            timestamp=datetime.now(),
            validation_report=validation_report
        )
        
        # Phase 7: Apprentissage automatique
        if self._should_learn_from_interaction(response):
            self._learn_from_interaction(response)
        
        # Phase 8: Sauvegarde dans l'historique
        self.conversation_history.append(response)
        
        return response
    
    def _extract_concepts_from_question(self, question: str) -> Dict[str, Any]:
        """Extrait les concepts philosophiques avec analyse améliorée"""
        
        # Extraction de base
        base_extraction = self.llm.extract_concepts_from_text(
            question, list(self.ontology.concepts.keys())
        )
        
        # Amélioration avec le bridge
        enhanced_extraction = self.concept_bridge.enhanced_concept_extraction(
            question, base_extraction
        )
        
        # Log des améliorations
        base_concepts = set(base_extraction.get('concepts_detected', []))
        enhanced_concepts = set(enhanced_extraction.get('concepts_detected', []))
        new_concepts = enhanced_concepts - base_concepts
        
        if new_concepts:
            logger.info(f"🔍 Bridge a trouvé de nouveaux concepts: {new_concepts}")
        
        return enhanced_extraction
    
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
        """Génère une réponse hybride combinant raisonnement LCM et génération LLaMA"""
        
        enriched_prompt = self._build_conceptually_enriched_prompt(
            question, conceptual_analysis, context
        )
        
        constraints = self._build_conceptual_constraints(conceptual_analysis)
        
        if constraints and conceptual_analysis['confidence'] > self.learning_threshold:
            try:
                generation_result = self.llm.generate_with_constraints(
                    enriched_prompt, constraints, max_attempts=2
                )
                response = generation_result['text']
                
                if not generation_result['constraints_satisfied']:
                    logger.warning("Contraintes non respectées, génération libre")
                    response = self.llm.generate_text(enriched_prompt, max_tokens=600)
            except Exception as e:
                logger.warning(f"Erreur génération contrainte: {e}")
                response = self.llm.generate_text(enriched_prompt, max_tokens=600)
        else:
            response = self.llm.generate_text(enriched_prompt, max_tokens=600)
        
        return response
    
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
    
    def _should_learn_from_interaction(self, response: SophIAResponse) -> bool:
        """Détermine si SophIA doit apprendre de cette interaction"""
        
        criteria = {
            'new_concepts_detected': len(response.conceptual_analysis.get('concepts_detected', [])) > 0,
            'high_confidence': response.confidence > self.learning_threshold,
            'sufficient_response_length': len(response.natural_response) > 50,
            'good_validation': response.validation_report.get('global_score', 0) > 0.6
        }
        
        return sum(criteria.values()) >= 2
    
    def _learn_from_interaction(self, response: SophIAResponse):
        """Apprend de l'interaction pour améliorer le modèle"""
        
        conceptual_paths = response.lcm_reasoning.get('reasoning_paths', [])
        
        training_sequences = []
        for path in conceptual_paths:
            sequence_names = path['reasoning_path']
            sequence_concepts = []
            
            for concept_name in sequence_names:
                concept = self.ontology.get_concept(concept_name)
                if concept:
                    sequence_concepts.append(concept)
            
            if len(sequence_concepts) >= 2:
                training_sequences.append(sequence_concepts)
        
        if training_sequences:
            self.trainer.train(training_sequences, epochs=1, verbose=False)
            logger.debug(f"Apprentissage: {len(training_sequences)} séquences intégrées")
        
        # Sauvegarde automatique
        if self.auto_save and self.session:
            try:
                checkpoint_path = self.session.save_checkpoint(
                    self.lcm_model, self.ontology, self.trainer,
                    epoch=len(self.conversation_history),
                    metrics={'conversation_count': len(self.conversation_history)}
                )
                logger.debug(f"Checkpoint automatique: {checkpoint_path}")
            except Exception as e:
                logger.warning(f"Erreur sauvegarde automatique: {e}")
    
    def explain_reasoning(self, question: str) -> Dict[str, Any]:
        """Explique le processus de raisonnement de SophIA pour une question"""
        
        conceptual_analysis = self._extract_concepts_from_question(question)
        lcm_reasoning = self._generate_lcm_reasoning(conceptual_analysis)
        
        explanation = {
            'question': question,
            'step1_concept_detection': {
                'method': 'LLaMA + Concept Bridge',
                'concepts_found': conceptual_analysis['concepts_detected'],
                'confidence': conceptual_analysis['enhanced_confidence']
            },
            'step2_conceptual_reasoning': {
                'method': 'LCM path generation',
                'reasoning_paths': lcm_reasoning['reasoning_paths']
            },
            'step3_constraint_validation': {
                'constraints_available': len(self.constraint_manager.constraints),
                'philosophical_clusters': len(self.constraint_manager.philosophical_clusters)
            },
            'step4_synthesis': {
                'how_response_built': 'Enhanced conceptual analysis guides constrained LLaMA generation'
            }
        }
        
        return explanation
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la conversation en cours"""
        
        if not self.conversation_history:
            return {'status': 'no_conversation'}
        
        all_concepts = []
        validation_scores = []
        
        for response in self.conversation_history:
            all_concepts.extend(response.conceptual_analysis.get('concepts_detected', []))
            validation_scores.append(response.validation_report.get('global_score', 0))
        
        concept_frequency = {}
        for concept in all_concepts:
            concept_frequency[concept] = concept_frequency.get(concept, 0) + 1
        
        top_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_interactions': len(self.conversation_history),
            'most_discussed_concepts': top_concepts[:5],
            'average_confidence': sum(r.confidence for r in self.conversation_history) / len(self.conversation_history),
            'average_validation': sum(validation_scores) / len(validation_scores) if validation_scores else 0,
            'learning_events': sum(1 for r in self.conversation_history if hasattr(r, 'learning_triggered')),
            'system_performance': {
                'concept_bridge_active': True,
                'constraint_manager_active': True,
                'lcm_transitions': len(self.lcm_model.transitions)
            }
        }
    
    def save_session(self, final_notes: str = "") -> str:
        """Sauvegarde la session complète"""
        
        if not self.session:
            raise ValueError("Auto-save désactivé, impossible de sauvegarder")
        
        final_metrics = {
            'conversation_summary': self.get_conversation_summary(),
            'final_notes': final_notes,
            'system_status': {
                'ontology_concepts': len(self.ontology.concepts),
                'lcm_transitions': len(self.lcm_model.transitions),
                'llm_status': self.llm.get_model_info()['status'],
                'bridge_cache_size': len(self.concept_bridge._synonyms_cache),
                'constraint_violations': sum(
                    len(r.validation_report.get('violations', []))
                    for r in self.conversation_history
                )
            }
        }
        
        return self.session.save_final_model(
            self.lcm_model, self.ontology, self.trainer, final_metrics
        )
    
    def load_session(self, session_name: str) -> bool:
        """Charge une session sauvegardée"""
        
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
            
            logger.info(f"Session '{session_name}' chargée avec succès")
            self._log_system_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur chargement session: {e}")
            return False