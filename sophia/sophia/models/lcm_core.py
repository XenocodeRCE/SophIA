"""
Modèle LCM (Logical Concept Model) de base pour SophIA
Gestion des transitions et génération de séquences conceptuelles
"""

import random
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from collections import defaultdict, Counter

from sophia.core.ontology import SimpleOntology, Concept
from sophia.core.concept_types import ConceptType, RelationType

logger = logging.getLogger(__name__)

@dataclass
class ConceptTransition:
    """Représente une transition entre deux concepts"""
    from_concept: str
    to_concept: str
    weight: float
    relation_type: Optional[str] = None
    context: Optional[str] = None
    frequency: int = 1
    
    def __post_init__(self):
        """Validation après création"""
        if self.weight < 0:
            raise ValueError("Le poids ne peut pas être négatif")
        if self.frequency < 1:
            raise ValueError("La fréquence doit être au moins 1")

class SimpleLCM:
    """
    Modèle LCM simple pour SophIA
    Apprend et génère des séquences de concepts basées sur des transitions probabilistes
    """
    
    def __init__(self, ontology: SimpleOntology, learning_rate: float = 0.1):
        self.ontology = ontology
        self.learning_rate = learning_rate
        
        # Matrice de transitions : {(concept_from, concept_to): ConceptTransition}
        self.transitions: Dict[Tuple[str, str], ConceptTransition] = {}
        
        # Statistiques d'apprentissage
        self.training_history: List[Dict[str, Any]] = []
        self.total_sequences_seen = 0
        
        # Cache pour optimisation
        self._transition_cache: Dict[str, List[Tuple[str, float]]] = {}
        self._cache_valid = False
        
        logger.info("SimpleLCM initialisé")
    
    def add_transition(self, from_concept: str, to_concept: str, 
                      weight: float = 1.0, relation_type: Optional[str] = None) -> None:
        """Ajoute ou met à jour une transition entre concepts"""
        
        from_name = from_concept.upper().strip()
        to_name = to_concept.upper().strip()
        
        # Vérification que les concepts existent dans l'ontologie
        if from_name not in self.ontology.concepts:
            logger.warning(f"Concept source {from_name} n'existe pas dans l'ontologie")
            return
        
        if to_name not in self.ontology.concepts:
            logger.warning(f"Concept cible {to_name} n'existe pas dans l'ontologie")
            return
        
        transition_key = (from_name, to_name)
        
        if transition_key in self.transitions:
            # Mise à jour d'une transition existante
            existing = self.transitions[transition_key]
            existing.weight = (existing.weight + weight * self.learning_rate)
            existing.frequency += 1
        else:
            # Nouvelle transition
            self.transitions[transition_key] = ConceptTransition(
                from_concept=from_name,
                to_concept=to_name,
                weight=weight,
                relation_type=relation_type
            )
        
        self._cache_valid = False  # Invalider le cache
        logger.debug(f"Transition ajoutée/mise à jour: {from_name} -> {to_name} (poids: {weight})")
    
    def get_next_concepts(self, current_concept: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Récupère les concepts suivants les plus probables"""
        
        current_name = current_concept.upper().strip()
        
        if not self._cache_valid:
            self._rebuild_cache()
        
        if current_name in self._transition_cache:
            transitions = self._transition_cache[current_name]
            return transitions[:top_k]
        
        return []
    
    def _rebuild_cache(self) -> None:
        """Reconstruit le cache des transitions pour optimisation"""
        self._transition_cache.clear()
        
        # Grouper par concept source
        concept_transitions = defaultdict(list)
        
        for (from_concept, to_concept), transition in self.transitions.items():
            # Normalisation du poids par fréquence
            normalized_weight = transition.weight * (transition.frequency ** 0.5)
            concept_transitions[from_concept].append((to_concept, normalized_weight))
        
        # Tri par poids décroissant et normalisation probabiliste
        for concept, transitions_list in concept_transitions.items():
            # Tri par poids
            sorted_transitions = sorted(transitions_list, key=lambda x: x[1], reverse=True)
            
            # Normalisation probabiliste
            total_weight = sum(weight for _, weight in sorted_transitions)
            if total_weight > 0:
                normalized_transitions = [
                    (concept_name, weight / total_weight) 
                    for concept_name, weight in sorted_transitions
                ]
                self._transition_cache[concept] = normalized_transitions
        
        self._cache_valid = True
        logger.debug(f"Cache reconstruit: {len(self._transition_cache)} concepts avec transitions")
    
    def generate_sequence(self, start_concept: str, length: int = 5, 
                         temperature: float = 1.0) -> List[Concept]:
        """Génère une séquence de concepts à partir d'un concept de départ"""
        
        start_name = start_concept.upper().strip()
        logger.info(f"Début de génération de séquence depuis {start_name} (longueur={length}, température={temperature})")
        
        if start_name not in self.ontology.concepts:
            logger.error(f"Concept de départ {start_name} n'existe pas")
            return []
        
        sequence = [self.ontology.concepts[start_name]]
        current_concept = start_name
        
        for step in range(length - 1):
            logger.debug(f"Étape {step+1}/{length-1} - concept courant: {current_concept}")
            next_candidates = self.get_next_concepts(current_concept, top_k=10)
            logger.debug(f"Transitions probabilistes trouvées: {next_candidates}")
            
            if not next_candidates:
                logger.info(f"Aucune transition probabiliste trouvée depuis {current_concept}, fallback sur ontologie")
                # Aucune transition disponible, utiliser les relations ontologiques
                next_candidates = self._get_ontological_next_concepts(current_concept)
                logger.debug(f"Transitions ontologiques candidates: {next_candidates}")
            
            if not next_candidates:
                logger.warning(f"Aucune transition disponible depuis {current_concept}, arrêt de la séquence")
                break
            
            # Sélection avec température
            next_concept = self._sample_with_temperature(next_candidates, temperature)
            logger.debug(f"Concept sélectionné: {next_concept}")
            
            if next_concept in [c.name for c in sequence]:
                logger.info(f"Cycle détecté avec {next_concept}, on saute ce concept")
                continue
            
            sequence.append(self.ontology.concepts[next_concept])
            logger.info(f"Ajout du concept {next_concept} à la séquence")
            current_concept = next_concept
        
        logger.info(f"Séquence générée: {[c.name for c in sequence]}")
        logger.debug(f"Séquence complète: {[c for c in sequence]}")
        return sequence
    
    def _get_ontological_next_concepts(self, concept_name: str) -> List[Tuple[str, float]]:
        """Utilise les relations ontologiques comme fallback pour les transitions"""
        
        logger.debug(f"Recherche des transitions ontologiques pour {concept_name}")
        concept = self.ontology.get_concept(concept_name)
        if not concept:
            logger.warning(f"Concept {concept_name} introuvable dans l'ontologie pour fallback")
            return []
        
        candidates = []
        
        # Utiliser les relations ontologiques avec des poids prédéfinis
        relation_weights = {
            RelationType.IMPLIES.value: 0.8,
            RelationType.IS_A.value: 0.7,
            RelationType.ENABLES.value: 0.6,
            RelationType.DEFINES.value: 0.5,
            RelationType.EXPLAINS.value: 0.4,
            RelationType.HAS_PROPERTY.value: 0.3
        }
        
        for relation_type, related_concepts in concept.relations.items():
            weight = relation_weights.get(relation_type, 0.2)
            for related_concept in related_concepts:
                if related_concept in self.ontology.concepts:
                    candidates.append((related_concept, weight))
        
        # Normalisation
        if candidates:
            total_weight = sum(weight for _, weight in candidates)
            candidates = [(concept, weight/total_weight) for concept, weight in candidates]
        
        return sorted(candidates, key=lambda x: x[1], reverse=True)
    
    def _sample_with_temperature(self, candidates: List[Tuple[str, float]], 
                                temperature: float) -> str:
        """Échantillonnage avec température pour contrôler la créativité"""
        
        if not candidates:
            return ""
        
        if temperature == 0:
            # Déterministe - prendre le plus probable
            return candidates[0][0]
        
        # Application de la température
        concepts, weights = zip(*candidates)
        weights = np.array(weights)
        
        # Température inverse (plus haute = plus créatif)
        weights = weights ** (1.0 / temperature)
        weights = weights / weights.sum()
        
        # Échantillonnage
        choice_idx = np.random.choice(len(concepts), p=weights)
        return concepts[choice_idx]
    
    def train_on_sequences(self, sequences: List[List[Concept]], epochs: int = 1) -> Dict[str, float]:
        """Entraîne le modèle sur une liste de séquences de concepts"""
        
        total_transitions = 0
        successful_transitions = 0
        
        for epoch in range(epochs):
            epoch_transitions = 0
            
            for sequence in sequences:
                if len(sequence) < 2:
                    continue
                
                # Apprendre des transitions séquentielles
                for i in range(len(sequence) - 1):
                    from_concept = sequence[i].name
                    to_concept = sequence[i + 1].name
                    
                    # Poids basé sur la proximité dans la séquence
                    weight = 1.0 / (1 + 0.1 * i)  # Décroissance légère
                    
                    self.add_transition(from_concept, to_concept, weight)
                    epoch_transitions += 1
                    total_transitions += 1
            
            logger.debug(f"Époque {epoch + 1}: {epoch_transitions} transitions apprises")
        
        # Statistiques d'entraînement
        self.total_sequences_seen += len(sequences)
        
        training_stats = {
            'total_transitions_learned': total_transitions,
            'unique_transitions': len(self.transitions),
            'sequences_processed': len(sequences),
            'epochs': epochs,
            'average_transitions_per_sequence': total_transitions / max(len(sequences), 1)
        }
        
        self.training_history.append(training_stats)
        
        logger.info(f"Entraînement terminé: {total_transitions} transitions, "
                   f"{len(self.transitions)} transitions uniques")
        
        return training_stats
    
    def evaluate_sequence_probability(self, sequence: List[Concept]) -> float:
        """Évalue la probabilité d'une séquence selon le modèle"""
        
        if len(sequence) < 2:
            return 1.0
        
        log_probability = 0.0
        
        for i in range(len(sequence) - 1):
            from_concept = sequence[i].name
            to_concept = sequence[i + 1].name
            
            # Récupère la probabilité de transition
            next_concepts = self.get_next_concepts(from_concept, top_k=100)
            
            probability = 0.0
            for concept, prob in next_concepts:
                if concept == to_concept:
                    probability = prob
                    break
            
            if probability == 0:
                # Utiliser une probabilité minimale pour éviter log(0)
                probability = 1e-10
            
            log_probability += np.log(probability)
        
        return np.exp(log_probability)
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le modèle"""
        
        if not self.transitions:
            return {'total_transitions': 0, 'concepts_with_transitions': 0}
        
        concepts_with_outgoing = set()
        concepts_with_incoming = set()
        
        for (from_concept, to_concept), transition in self.transitions.items():
            concepts_with_outgoing.add(from_concept)
            concepts_with_incoming.add(to_concept)
        
        return {
            'total_transitions': len(self.transitions),
            'concepts_with_outgoing_transitions': len(concepts_with_outgoing),
            'concepts_with_incoming_transitions': len(concepts_with_incoming),
            'coverage_ratio': len(concepts_with_outgoing) / max(len(self.ontology.concepts), 1),
            'total_sequences_seen': self.total_sequences_seen,
            'training_epochs': len(self.training_history)
        }
    
    def save_model_state(self) -> Dict[str, Any]:
        """Sauvegarde l'état du modèle pour sérialisation"""
        
        return {
            'transitions': {
                f"{from_c}->{to_c}": {
                    'from_concept': transition.from_concept,
                    'to_concept': transition.to_concept,
                    'weight': transition.weight,
                    'relation_type': transition.relation_type,
                    'context': transition.context,
                    'frequency': transition.frequency
                }
                for (from_c, to_c), transition in self.transitions.items()
            },
            'learning_rate': self.learning_rate,
            'total_sequences_seen': self.total_sequences_seen,
            'training_history': self.training_history
        }
    
    def load_model_state(self, state: Dict[str, Any]) -> None:
        """Charge l'état du modèle depuis une sérialisation"""
        
        self.transitions.clear()
        self.learning_rate = state.get('learning_rate', 0.1)
        self.total_sequences_seen = state.get('total_sequences_seen', 0)
        self.training_history = state.get('training_history', [])
        
        # Reconstruction des transitions
        for key, transition_data in state.get('transitions', {}).items():
            from_concept = transition_data['from_concept']
            to_concept = transition_data['to_concept']
            
            transition = ConceptTransition(
                from_concept=from_concept,
                to_concept=to_concept,
                weight=transition_data['weight'],
                relation_type=transition_data.get('relation_type'),
                context=transition_data.get('context'),
                frequency=transition_data.get('frequency', 1)
            )
            
            self.transitions[(from_concept, to_concept)] = transition
        
        self._cache_valid = False
        logger.info(f"Modèle chargé: {len(self.transitions)} transitions")