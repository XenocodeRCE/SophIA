"""
Système d'entraînement pour les modèles LCM de SophIA
Entraînement avec conscience ontologique et validation de cohérence
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from sophia.core.ontology import SimpleOntology, Concept
from sophia.core.concept_types import ConceptType, RelationType
from sophia.models.lcm_core import SimpleLCM

logger = logging.getLogger(__name__)

@dataclass
class TrainingMetrics:
    """Métriques d'entraînement pour une époque"""
    epoch: int
    loss: float
    coherence_score: float
    ontological_violations: int
    transitions_learned: int
    sequence_coverage: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'epoch': self.epoch,
            'loss': self.loss,
            'coherence_score': self.coherence_score,
            'ontological_violations': self.ontological_violations,
            'transitions_learned': self.transitions_learned,
            'sequence_coverage': self.sequence_coverage,
            'timestamp': self.timestamp
        }

class SimpleLCMTrainer:
    """Entraîneur de base pour les modèles LCM"""
    
    def __init__(self, model: SimpleLCM, ontology: SimpleOntology):
        self.model = model
        self.ontology = ontology
        self.training_history: List[TrainingMetrics] = []
        
        # Paramètres d'entraînement
        self.learning_rate = 0.1
        self.batch_size = 32
        self.validation_split = 0.2
        
        logger.info("SimpleLCMTrainer initialisé")
    
    def train(self, training_sequences: List[List[Concept]], 
              epochs: int = 10, verbose: bool = True) -> List[TrainingMetrics]:
        """Entraîne le modèle sur des séquences de concepts"""
        
        if not training_sequences:
            logger.error("Aucune séquence d'entraînement fournie")
            return []
        
        # Division train/validation
        split_idx = int(len(training_sequences) * (1 - self.validation_split))
        train_sequences = training_sequences[:split_idx]
        val_sequences = training_sequences[split_idx:]
        
        logger.info(f"Début entraînement: {len(train_sequences)} séquences train, "
                   f"{len(val_sequences)} séquences validation")
        
        for epoch in range(epochs):
            logger.info(f"--- Début de l'époque {epoch+1}/{epochs} ---")
            logger.debug(f"Séquences d'entraînement pour cette époque: {len(train_sequences)}")
            # Entraînement sur le batch
            train_metrics = self._train_epoch(train_sequences, epoch)
            logger.debug(f"Résultats entraînement époque {epoch+1}: {train_metrics}")
            
            # Validation
            if val_sequences:
                logger.debug(f"Validation sur {len(val_sequences)} séquences")
            val_metrics = self._validate_epoch(val_sequences, epoch) if val_sequences else None
            if val_metrics:
                logger.debug(f"Résultats validation époque {epoch+1}: {val_metrics}")
            
            # Enregistrement des métriques
            final_metrics = self._combine_metrics(train_metrics, val_metrics, epoch)
            self.training_history.append(final_metrics)
            
            if verbose:
                self._log_epoch_results(final_metrics)
            logger.info(f"--- Fin de l'époque {epoch+1}/{epochs} ---")
        
        logger.info(f"Entraînement terminé après {epochs} époques")
        return self.training_history
    
    def _train_epoch(self, sequences: List[List[Concept]], epoch: int) -> Dict[str, Any]:
        """Entraîne une époque sur les séquences données"""
        
        total_loss = 0.0
        transitions_learned = 0
        ontological_violations = 0
        
        logger.debug(f"Mélange des séquences pour l'époque {epoch+1}")
        # Mélange des séquences pour cet époque
        np.random.shuffle(sequences)
        
        for idx, sequence in enumerate(sequences):
            if len(sequence) < 2:
                logger.debug(f"Séquence {idx} ignorée (trop courte)")
                continue
            
            logger.debug(f"Époque {epoch+1}, séquence {idx}: {', '.join([c.name for c in sequence])}")
            # Calcul de la loss avant mise à jour
            initial_prob = self.model.evaluate_sequence_probability(sequence)
            logger.debug(f"Probabilité initiale de la séquence: {initial_prob:.6f}")
            
            # Entraînement sur la séquence
            sequence_stats = self.model.train_on_sequences([sequence], epochs=1)
            logger.debug(f"Stats d'entraînement sur la séquence: {sequence_stats}")
            transitions_learned += sequence_stats['total_transitions_learned']
            
            # Calcul de la loss après mise à jour
            final_prob = self.model.evaluate_sequence_probability(sequence)
            logger.debug(f"Probabilité finale de la séquence: {final_prob:.6f}")
            
            # Loss = -log de l'amélioration de probabilité
            if final_prob > initial_prob:
                loss = -np.log(final_prob / max(initial_prob, 1e-10))
            else:
                loss = np.log(max(initial_prob, 1e-10) / max(final_prob, 1e-10))
            
            logger.debug(f"Loss calculée pour la séquence: {loss:.6f}")
            total_loss += loss
            
            # Vérification des violations ontologiques
            violations = self._check_ontological_violations(sequence)
            if violations > 0:
                logger.debug(f"{violations} violation(s) ontologique(s) détectée(s) dans la séquence")
            ontological_violations += violations
        
        avg_loss = total_loss / max(len(sequences), 1)
        logger.info(f"Époque {epoch+1}: loss moyenne={avg_loss:.6f}, transitions apprises={transitions_learned}, violations ontologiques={ontological_violations}")
        
        return {
            'loss': avg_loss,
            'transitions_learned': transitions_learned,
            'ontological_violations': ontological_violations,
            'sequences_processed': len(sequences)
        }
    
    def _validate_epoch(self, val_sequences: List[List[Concept]], epoch: int) -> Dict[str, Any]:
        """Validation sur un ensemble de séquences"""
        
        if not val_sequences:
            logger.warning("Aucune séquence de validation fournie")
            return {}
        
        total_prob = 0.0
        coherence_scores = []
        
        for idx, sequence in enumerate(val_sequences):
            if len(sequence) < 2:
                logger.debug(f"Séquence de validation {idx} ignorée (trop courte)")
                continue
            
            prob = self.model.evaluate_sequence_probability(sequence)
            logger.debug(f"Validation époque {epoch+1}, séquence {idx}: probabilité={prob:.6f}")
            total_prob += prob
            
            coherence = self._calculate_coherence_score(sequence)
            logger.debug(f"Score de cohérence pour la séquence {idx}: {coherence:.4f}")
            coherence_scores.append(coherence)
        
        avg_probability = total_prob / max(len(val_sequences), 1)
        avg_coherence = np.mean(coherence_scores) if coherence_scores else 0.0
        
        logger.info(f"Validation époque {epoch+1}: probabilité moyenne={avg_probability:.6f}, cohérence moyenne={avg_coherence:.4f}")
        
        return {
            'validation_probability': avg_probability,
            'coherence_score': avg_coherence,
            'sequences_validated': len(val_sequences)
        }
    
    def _check_ontological_violations(self, sequence: List[Concept]) -> int:
        """Vérifie les violations ontologiques dans une séquence"""
        
        violations = 0
        
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_concept = sequence[i + 1]
            
            # Vérification des contradictions explicites
            if RelationType.CONTRADICTS.value in current.relations:
                if next_concept.name in current.relations[RelationType.CONTRADICTS.value]:
                    violations += 1
                    logger.debug(f"Violation détectée: {current.name} contradicts {next_concept.name}")
        
        return violations
    
    def _calculate_coherence_score(self, sequence: List[Concept]) -> float:
        """Calcule un score de cohérence ontologique pour une séquence"""
        
        if len(sequence) < 2:
            return 1.0
        
        coherence_points = 0
        total_transitions = len(sequence) - 1
        
        for i in range(total_transitions):
            current = sequence[i]
            next_concept = sequence[i + 1]
            
            # Points pour relations ontologiques existantes
            for relation_type, related_concepts in current.relations.items():
                if next_concept.name in related_concepts:
                    # Poids différents selon le type de relation
                    weights = {
                        RelationType.IMPLIES.value: 1.0,
                        RelationType.IS_A.value: 0.8,
                        RelationType.ENABLES.value: 0.7,
                        RelationType.DEFINES.value: 0.6,
                        RelationType.CONTRADICTS.value: -1.0,  # Pénalité
                        RelationType.OPPOSES.value: -0.5
                    }
                    logger.debug(f"Relation {relation_type} trouvée entre {current.name} et {next_concept.name}, poids={weights.get(relation_type, 0.3)}")
                    coherence_points += weights.get(relation_type, 0.3)
            
            # Points pour types de concepts compatibles
            if self._are_concept_types_compatible(current.concept_type, next_concept.concept_type):
                logger.debug(f"Types compatibles: {current.concept_type} -> {next_concept.concept_type}")
                coherence_points += 0.2
        
        # Normalisation
        max_possible_score = total_transitions * 1.2  # Maximum théorique
        coherence_score = max(0, coherence_points) / max(max_possible_score, 1)
        
        logger.debug(f"Score de cohérence normalisé: {coherence_score:.4f}")
        return min(1.0, coherence_score)
    
    def _are_concept_types_compatible(self, type1: ConceptType, type2: ConceptType) -> bool:
        """Vérifie si deux types de concepts sont compatibles pour une transition"""
        
        # Définition de compatibilités basiques
        compatible_pairs = {
            (ConceptType.ENTITY, ConceptType.PROPERTY),
            (ConceptType.ENTITY, ConceptType.EPISTEMIC),
            (ConceptType.EPISTEMIC, ConceptType.LOGICAL),
            (ConceptType.LOGICAL, ConceptType.EPISTEMIC),
            (ConceptType.MORAL, ConceptType.VALUE),
            (ConceptType.VALUE, ConceptType.MORAL),
        }
        
        return (type1, type2) in compatible_pairs or (type2, type1) in compatible_pairs
    
    def _combine_metrics(self, train_metrics: Dict[str, Any], 
                        val_metrics: Optional[Dict[str, Any]], epoch: int) -> TrainingMetrics:
        """Combine les métriques d'entraînement et de validation"""
        
        coherence_score = val_metrics.get('coherence_score', 0.0) if val_metrics else 0.0
        
        return TrainingMetrics(
            epoch=epoch,
            loss=train_metrics['loss'],
            coherence_score=coherence_score,
            ontological_violations=train_metrics['ontological_violations'],
            transitions_learned=train_metrics['transitions_learned'],
            sequence_coverage=self._calculate_sequence_coverage(),
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_sequence_coverage(self) -> float:
        """Calcule le pourcentage de concepts couverts par les transitions"""
        
        model_stats = self.model.get_model_stats()
        return model_stats.get('coverage_ratio', 0.0)
    
    def _log_epoch_results(self, metrics: TrainingMetrics) -> None:
        """Affiche les résultats d'une époque"""
        
        logger.info(f"Époque {metrics.epoch + 1}: "
                   f"Loss={metrics.loss:.4f}, "
                   f"Cohérence={metrics.coherence_score:.3f}, "
                   f"Violations={metrics.ontological_violations}, "
                   f"Transitions={metrics.transitions_learned}")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'entraînement"""
        
        if not self.training_history:
            return {'status': 'no_training'}
        
        losses = [m.loss for m in self.training_history]
        coherence_scores = [m.coherence_score for m in self.training_history]
        
        return {
            'total_epochs': len(self.training_history),
            'final_loss': losses[-1],
            'best_loss': min(losses),
            'final_coherence': coherence_scores[-1],
            'best_coherence': max(coherence_scores),
            'total_violations': sum(m.ontological_violations for m in self.training_history),
            'total_transitions_learned': sum(m.transitions_learned for m in self.training_history),
            'improvement': {
                'loss_reduction': losses[0] - losses[-1] if len(losses) > 1 else 0,
                'coherence_improvement': coherence_scores[-1] - coherence_scores[0] if len(coherence_scores) > 1 else 0
            }
        }

class OntologyAwareLCMTrainer(SimpleLCMTrainer):
    """Entraîneur avancé avec conscience ontologique renforcée"""
    
    def __init__(self, model: SimpleLCM, ontology: SimpleOntology, 
                 consistency_weight: float = 0.3):
        super().__init__(model, ontology)
        self.consistency_weight = consistency_weight
        
        # Pré-calcul des relations ontologiques pour optimisation
        self.ontological_constraints = self._build_ontological_constraints()
        
        logger.info("OntologyAwareLCMTrainer initialisé avec poids de cohérence: "
                   f"{consistency_weight}")
    
    def _build_ontological_constraints(self) -> Dict[str, Dict[str, float]]:
        """Pré-calcule les contraintes ontologiques pour l'entraînement"""
        
        constraints = {}
        
        for concept_name, concept in self.ontology.concepts.items():
            concept_constraints = {}
            
            # Contraintes positives (relations encouragées)
            for relation_type, related_concepts in concept.relations.items():
                weight = self._get_relation_weight(relation_type)
                for related_concept in related_concepts:
                    concept_constraints[related_concept] = weight
            
            constraints[concept_name] = concept_constraints
        
        return constraints
    
    def _get_relation_weight(self, relation_type: str) -> float:
        """Détermine le poids d'encouragement pour un type de relation"""
        
        weights = {
            RelationType.IMPLIES.value: 1.0,
            RelationType.IS_A.value: 0.8,
            RelationType.ENABLES.value: 0.7,
            RelationType.DEFINES.value: 0.6,
            RelationType.EXPLAINS.value: 0.5,
            RelationType.HAS_PROPERTY.value: 0.4,
            RelationType.CONTRADICTS.value: -1.0,  # Fortement découragé
            RelationType.OPPOSES.value: -0.8
        }
        
        return weights.get(relation_type, 0.2)
    
    def _train_epoch(self, sequences: List[List[Concept]], epoch: int) -> Dict[str, Any]:
        """Entraînement avec prise en compte renforcée de l'ontologie"""
        
        # Entraînement de base
        base_metrics = super()._train_epoch(sequences, epoch)
        
        # Ajustement des transitions selon les contraintes ontologiques
        consistency_adjustments = self._apply_ontological_consistency()
        
        base_metrics.update({
            'consistency_adjustments': consistency_adjustments,
            'ontology_influence_applied': True
        })
        
        return base_metrics
    
    def _apply_ontological_consistency(self) -> int:
        """Applique les contraintes ontologiques aux transitions apprises"""
        
        adjustments = 0
        
        for (from_concept, to_concept), transition in self.model.transitions.items():
            
            # Vérifie les contraintes ontologiques
            if from_concept in self.ontological_constraints:
                constraints = self.ontological_constraints[from_concept]
                
                if to_concept in constraints:
                    ontological_weight = constraints[to_concept]
                    
                    # Ajustement du poids de transition
                    adjustment_factor = 1.0 + (self.consistency_weight * ontological_weight)
                    old_weight = transition.weight
                    transition.weight *= adjustment_factor
                    
                    if abs(old_weight - transition.weight) > 0.01:
                        adjustments += 1
        
        # Invalidation du cache du modèle
        self.model._cache_valid = False
        
        logger.debug(f"Ajustements ontologiques appliqués: {adjustments}")
        return adjustments