"""
Système hybride SophIA : LCM + LLaMA
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

logger = logging.getLogger(__name__)

class ConceptualResponse:
    """Représente une réponse de SophIA avec trace de raisonnement"""
    
    def __init__(self, question: str, natural_response: str, 
                 conceptual_analysis: Dict[str, Any], metadata: Dict[str, Any]):
        self.question = question
        self.natural_response = natural_response
        self.conceptual_analysis = conceptual_analysis
        self.metadata = metadata
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'natural_response': self.natural_response,
            'conceptual_analysis': self.conceptual_analysis,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

class HybridSophIA:
    """
    Système hybride SophIA combinant :
    - Raisonnement conceptuel (LCM)
    - Génération naturelle (LLaMA)
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
        
        # Système de session pour persistance
        self.session = TrainingSession(session_name) if auto_save else None
        
        # Historique conversationnel
        self.conversation_history: List[ConceptualResponse] = []
        self.learning_buffer: List[Dict[str, Any]] = []
        
        # Paramètres de fonctionnement
        self.response_temperature = 0.7
        self.conceptual_weight = 0.6  # Poids du raisonnement conceptuel vs génération libre
        self.learning_threshold = 0.3  # Seuil pour apprentissage automatique
        
        logger.info(f"SophIA Hybride initialisée : session '{session_name}'")
        self._log_system_status()
    
    def _log_system_status(self):
        """Affiche le statut des composants"""
        llm_info = self.llm.get_model_info()
        logger.info(f"Ontologie: {len(self.ontology.concepts)} concepts")
        logger.info(f"LCM: {len(self.lcm_model.transitions)} transitions")
        logger.info(f"LLaMA: {llm_info['status']} ({llm_info['model_name']})")
    
    def ask(self, question: str, context: Optional[str] = None) -> ConceptualResponse:
        """Interface principale pour poser une question à SophIA"""
        
        logger.info(f"Question reçue: {question}")
        
        # Phase 1: Analyse conceptuelle
        conceptual_analysis = self._analyze_question_conceptually(question, context)
        
        # Phase 2: Génération hybride
        natural_response = self._generate_hybrid_response(question, conceptual_analysis, context)
        
        # Phase 3: Construction de la réponse complète
        metadata = {
            'reasoning_method': 'hybrid',
            'conceptual_confidence': conceptual_analysis.get('confidence', 0.5),
            'llm_status': self.llm.get_model_info()['status'],
            'concepts_involved': conceptual_analysis.get('concepts_detected', []),
            'learning_triggered': False
        }
        
        response = ConceptualResponse(question, natural_response, conceptual_analysis, metadata)
        
        # Phase 4: Apprentissage automatique
        if self._should_learn_from_interaction(response):
            self._learn_from_interaction(response)
            response.metadata['learning_triggered'] = True
        
        # Phase 5: Sauvegarde dans l'historique
        self.conversation_history.append(response)
        
        return response
    
    def _analyze_question_conceptually(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyse conceptuelle de la question via LCM et extraction LLaMA"""
        
        # Extraction des concepts via LLaMA
        available_concepts = list(self.ontology.concepts.keys())
        
        # Texte à analyser (question + contexte éventuel)
        analysis_text = question
        if context:
            analysis_text = f"{context} {question}"
        
        llm_extraction = self.llm.extract_concepts_from_text(analysis_text, available_concepts)
        
        # Analyse LCM des concepts détectés
        detected_concepts = llm_extraction['concepts_detected']
        conceptual_paths = []
        
        if detected_concepts:
            # Génération de chemins conceptuels pour chaque concept détecté
            for concept_name in detected_concepts[:3]:  # Limite à 3 concepts principaux
                if concept_name in self.ontology.concepts:
                    # Génération d'une séquence conceptuelle
                    sequence = self.lcm_model.generate_sequence(concept_name, length=4, temperature=0.8)
                    conceptual_paths.append({
                        'start_concept': concept_name,
                        'reasoning_path': [c.name for c in sequence],
                        'path_probability': self.lcm_model.evaluate_sequence_probability(sequence)
                    })
        
        return {
            'concepts_detected': detected_concepts,
            'relations_implied': llm_extraction['relations_implied'],
            'conceptual_paths': conceptual_paths,
            'confidence': llm_extraction['confidence'],
            'analysis_method': 'llm_extraction + lcm_reasoning'
        }
    
    def _generate_hybrid_response(self, question: str, conceptual_analysis: Dict[str, Any], 
                                context: Optional[str] = None) -> str:
        """Génère une réponse hybride combinant raisonnement LCM et génération LLaMA"""
        
        # Construction du prompt enrichi conceptuellement
        enriched_prompt = self._build_conceptually_enriched_prompt(
            question, conceptual_analysis, context
        )
        
        # Contraintes basées sur l'analyse conceptuelle
        constraints = self._build_conceptual_constraints(conceptual_analysis)
        
        # Génération contrainte via LLaMA
        if constraints and conceptual_analysis['confidence'] > self.learning_threshold:
            # Mode contraint si bonne confiance conceptuelle
            generation_result = self.llm.generate_with_constraints(
                enriched_prompt, constraints, max_attempts=2
            )
            response = generation_result['text']
            
            # Fallback si contraintes non respectées
            if not generation_result['constraints_satisfied']:
                logger.warning("Contraintes non respectées, génération libre")
                response = self.llm.generate_text(enriched_prompt, max_tokens=200)
        else:
            # Mode génération libre si faible confiance conceptuelle
            response = self.llm.generate_text(enriched_prompt, max_tokens=200)
        
        return response
    
    def _build_conceptually_enriched_prompt(self, question: str, 
                                          conceptual_analysis: Dict[str, Any],
                                          context: Optional[str] = None) -> str:
        """Construit un prompt enrichi par l'analyse conceptuelle"""
        
        base_prompt = f"""Tu es SophIA, une IA philosophique qui combine raisonnement conceptuel et expression naturelle.

QUESTION: {question}"""
        
        if context:
            base_prompt += f"\nCONTEXTE: {context}"
        
        # Enrichissement conceptuel
        detected_concepts = conceptual_analysis.get('concepts_detected', [])
        conceptual_paths = conceptual_analysis.get('conceptual_paths', [])
        
        if detected_concepts:
            base_prompt += f"\n\nCONCEPTS IDENTIFIÉS: {', '.join(detected_concepts)}"
        
        if conceptual_paths:
            base_prompt += "\n\nCHEMINS DE RAISONNEMENT CONCEPTUEL:"
            for i, path in enumerate(conceptual_paths[:2], 1):  # Limite à 2 chemins
                path_str = " → ".join(path['reasoning_path'])
                base_prompt += f"\n{i}. {path_str}"
        
        # Relations détectées
        relations = conceptual_analysis.get('relations_implied', [])
        if relations:
            base_prompt += "\n\nRELATIONS CONCEPTUELLES:"
            for relation in relations[:3]:  # Limite à 3 relations
                base_prompt += f"\n- {relation['from']} {relation['relation']} {relation['to']}"
        
        base_prompt += "\n\nRéponds en intégrant ces éléments conceptuels de manière naturelle et philosophiquement rigoureuse."
        
        return base_prompt
    
    def _build_conceptual_constraints(self, conceptual_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Construit les contraintes basées sur l'analyse conceptuelle"""
        
        constraints = {}
        
        detected_concepts = conceptual_analysis.get('concepts_detected', [])
        if detected_concepts:
            # Exigence d'utiliser les concepts principaux
            constraints['required_concepts'] = detected_concepts[:3]
        
        relations = conceptual_analysis.get('relations_implied', [])
        if relations:
            # Normalisation des relations pour éviter les erreurs de clé
            normalized_relations = []
            for relation in relations[:2]:  # Limite à 2 relations
                normalized_relation = {
                    'from': relation.get('from', ''),
                    'to': relation.get('to', ''),
                    'relation': relation.get('relation', relation.get('type', 'IMPLIES'))  # Support des deux formats
                }
                normalized_relations.append(normalized_relation)
            
            constraints['required_relations'] = normalized_relations
        
        # Contraintes de style
        constraints.update({
            'tone': 'philosophique et analytique',
            'max_tokens': 2048
        })
        
        return constraints
    
    def _should_learn_from_interaction(self, response: ConceptualResponse) -> bool:
        """Détermine si SophIA doit apprendre de cette interaction"""
        
        # Critères d'apprentissage
        criteria = {
            'new_concepts_detected': len(response.conceptual_analysis.get('concepts_detected', [])) > 0,
            'high_confidence': response.conceptual_analysis.get('confidence', 0) > self.learning_threshold,
            'sufficient_response_length': len(response.natural_response) > 50,
            'contains_relations': len(response.conceptual_analysis.get('relations_implied', [])) > 0
        }
        
        # Apprentissage si au moins 2 critères sont remplis
        return sum(criteria.values()) >= 2
    
    def _learn_from_interaction(self, response: ConceptualResponse):
        """Apprend de l'interaction pour améliorer le modèle"""
        
        # Extraction des séquences conceptuelles pour l'entraînement
        conceptual_paths = response.conceptual_analysis.get('conceptual_paths', [])
        
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
        
        # Entraînement incrémental
        if training_sequences:
            self.trainer.train(training_sequences, epochs=1, verbose=False)
            logger.debug(f"Apprentissage: {len(training_sequences)} séquences intégrées")
        
        # Intégration des nouvelles relations
        relations = response.conceptual_analysis.get('relations_implied', [])
        for relation in relations:
            from_concept = relation['from']
            to_concept = relation['to']
            relation_type = relation['relation']
            
            # Ajout à l'ontologie si concepts valides
            if (from_concept in self.ontology.concepts and 
                to_concept in self.ontology.concepts):
                
                from .concept_types import RelationType
                try:
                    rel_enum = RelationType(relation_type.lower())
                    self.ontology.add_relation(from_concept, rel_enum, to_concept)
                    logger.debug(f"Relation apprise: {from_concept} {relation_type} {to_concept}")
                except ValueError:
                    logger.warning(f"Type de relation inconnu: {relation_type}")
        
        # Sauvegarde automatique si activée
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
        
        # Analyse sans générer de réponse
        conceptual_analysis = self._analyze_question_conceptually(question)
        
        explanation = {
            'question': question,
            'step1_concept_detection': {
                'method': 'LLaMA extraction',
                'concepts_found': conceptual_analysis['concepts_detected'],
                'confidence': conceptual_analysis['confidence']
            },
            'step2_conceptual_reasoning': {
                'method': 'LCM path generation',
                'reasoning_paths': conceptual_analysis['conceptual_paths']
            },
            'step3_ontological_relations': {
                'detected_relations': conceptual_analysis['relations_implied']
            },
            'step4_synthesis': {
                'how_response_built': 'Conceptual analysis guides LLaMA generation with constraints'
            }
        }
        
        return explanation
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la conversation en cours"""
        
        if not self.conversation_history:
            return {'status': 'no_conversation'}
        
        # Analyse des concepts discutés
        all_concepts = []
        for response in self.conversation_history:
            all_concepts.extend(response.conceptual_analysis.get('concepts_detected', []))
        
        concept_frequency = {}
        for concept in all_concepts:
            concept_frequency[concept] = concept_frequency.get(concept, 0) + 1
        
        # Concepts les plus discutés
        top_concepts = sorted(concept_frequency.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_interactions': len(self.conversation_history),
            'most_discussed_concepts': top_concepts[:5],
            'average_confidence': sum(
                r.conceptual_analysis.get('confidence', 0) 
                for r in self.conversation_history
            ) / len(self.conversation_history),
            'learning_events': sum(
                1 for r in self.conversation_history 
                if r.metadata.get('learning_triggered', False)
            )
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
                'llm_status': self.llm.get_model_info()['status']
            }
        }
        
        return self.session.save_final_model(
            self.lcm_model, self.ontology, self.trainer, final_metrics
        )
    
    def load_session(self, session_name: str) -> bool:
        """Charge une session sauvegardée"""
        
        try:
            session = TrainingSession(session_name)
            
            # Chargement du modèle final ou du dernier checkpoint
            try:
                model, ontology, trainer, metadata = session.load_final_model()
            except FileNotFoundError:
                latest = session.load_latest_checkpoint()
                if latest:
                    model, ontology, trainer, metadata = latest
                else:
                    return False
            
            # Remplacement des composants
            self.lcm_model = model
            self.ontology = ontology
            self.trainer = trainer
            self.session = session
            
            logger.info(f"Session '{session_name}' chargée avec succès")
            self._log_system_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur chargement session: {e}")
            return False