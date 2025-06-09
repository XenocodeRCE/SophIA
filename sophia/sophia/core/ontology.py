"""
Système d'ontologie pour SophIA
Gestion des concepts et relations philosophiques
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from .concept_types import ConceptType, RelationType, CORE_PHILOSOPHICAL_CONCEPTS, CORE_RELATIONS

logger = logging.getLogger(__name__)

@dataclass
class Concept:
    """Représente un concept philosophique"""
    
    name: str
    concept_type: ConceptType
    domain: Optional[str] = None
    relations: Dict[str, List[str]] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    definitions: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    # Métadonnées d'apprentissage
    learning_weight: float = 1.0
    last_updated: Optional[str] = None
    source: str = "core"  # core, learned, user_defined
    
    def __post_init__(self):
        """Validation et initialisation après création"""
        self.name = self.name.upper().strip()
        if not self.name:
            raise ValueError("Le nom du concept ne peut pas être vide")
    
    def add_relation(self, relation_type: RelationType, target_concept: str) -> None:
        """Ajoute une relation vers un autre concept"""
        relation_str = relation_type.value
        if relation_str not in self.relations:
            self.relations[relation_str] = []
        
        if target_concept not in self.relations[relation_str]:
            self.relations[relation_str].append(target_concept)
            logger.debug(f"Relation ajoutée: {self.name} {relation_type.value} {target_concept}")
    
    def remove_relation(self, relation_type: RelationType, target_concept: str) -> bool:
        """Supprime une relation vers un autre concept"""
        relation_str = relation_type.value
        if relation_str in self.relations and target_concept in self.relations[relation_str]:
            self.relations[relation_str].remove(target_concept)
            if not self.relations[relation_str]:  # Supprime la clé si liste vide
                del self.relations[relation_str]
            logger.debug(f"Relation supprimée: {self.name} {relation_type.value} {target_concept}")
            return True
        return False
    
    def get_related_concepts(self, relation_type: Optional[RelationType] = None) -> List[str]:
        """Récupère tous les concepts reliés, optionnellement filtrés par type de relation"""
        if relation_type:
            return self.relations.get(relation_type.value, [])
        
        # Tous les concepts reliés
        all_related = []
        for concepts_list in self.relations.values():
            all_related.extend(concepts_list)
        return list(set(all_related))  # Dédoublonnage
    
    def add_definition(self, definition: str, source: str = "unknown") -> None:
        """Ajoute une définition du concept"""
        full_definition = f"{definition} (source: {source})"
        if full_definition not in self.definitions:
            self.definitions.append(full_definition)
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise le concept en dictionnaire"""
        return {
            'name': self.name,
            'concept_type': self.concept_type.value,
            'domain': self.domain,
            'relations': self.relations,
            'properties': self.properties,
            'definitions': self.definitions,
            'examples': self.examples,
            'learning_weight': self.learning_weight,
            'last_updated': self.last_updated,
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Concept':
        """Désérialise un concept depuis un dictionnaire"""
        concept_type = ConceptType(data['concept_type'])
        return cls(
            name=data['name'],
            concept_type=concept_type,
            domain=data.get('domain'),
            relations=data.get('relations', {}),
            properties=data.get('properties', {}),
            definitions=data.get('definitions', []),
            examples=data.get('examples', []),
            learning_weight=data.get('learning_weight', 1.0),
            last_updated=data.get('last_updated'),
            source=data.get('source', 'unknown')
        )

class SimpleOntology:
    """Ontologie philosophique pour SophIA"""
    
    def __init__(self, load_core_concepts: bool = True):
        self.concepts: Dict[str, Concept] = {}
        self.metadata = {
            'version': '1.0',
            'creation_date': None,
            'last_modified': None,
            'total_concepts': 0,
            'total_relations': 0
        }
        
        if load_core_concepts:
            self._load_core_philosophical_concepts()
    
    def _load_core_philosophical_concepts(self) -> None:
        """Charge les concepts philosophiques fondamentaux"""
        logger.info("Chargement des concepts philosophiques de base...")
        
        # Ajout des concepts de base
        for concept_name, concept_type in CORE_PHILOSOPHICAL_CONCEPTS.items():
            self.add_concept(concept_name, concept_type, source="core")
        
        # Ajout des relations de base
        for from_concept, relation_type, to_concept in CORE_RELATIONS:
            self.add_relation(from_concept, relation_type, to_concept)
        
        self._update_metadata()
        logger.info(f"Chargement terminé: {len(self.concepts)} concepts, {self._count_relations()} relations")
    
    def add_concept(self, name: str, concept_type: ConceptType, **kwargs) -> Concept:
        """Ajoute un nouveau concept à l'ontologie"""
        name = name.upper().strip()
        
        if name in self.concepts:
            logger.warning(f"Concept {name} existe déjà, mise à jour...")
            existing = self.concepts[name]
            # Mise à jour des propriétés si nécessaire
            for key, value in kwargs.items():
                setattr(existing, key, value)
            return existing
        
        concept = Concept(name=name, concept_type=concept_type, **kwargs)
        self.concepts[name] = concept
        
        logger.debug(f"Concept ajouté: {name} ({concept_type.value})")
        self._update_metadata()
        return concept
    
    def get_concept(self, name: str) -> Optional[Concept]:
        """Récupère un concept par son nom"""
        return self.concepts.get(name.upper().strip())
    
    def add_relation(self, from_concept: str, relation_type: RelationType, to_concept: str) -> bool:
        """Ajoute une relation entre deux concepts"""
        from_name = from_concept.upper().strip()
        to_name = to_concept.upper().strip()
        
        # Vérification que les concepts existent
        if from_name not in self.concepts:
            logger.warning(f"Concept source {from_name} n'existe pas")
            return False
        
        if to_name not in self.concepts:
            logger.warning(f"Concept cible {to_name} n'existe pas")
            return False
        
        # Vérification de cohérence (éviter les auto-contradictions)
        if not self._is_relation_consistent(from_name, relation_type, to_name):
            logger.warning(f"Relation incohérente: {from_name} {relation_type.value} {to_name}")
            return False
        
        # Ajout de la relation
        self.concepts[from_name].add_relation(relation_type, to_name)
        
        # Ajout de la relation inverse si applicable
        inverse_relation = self._get_inverse_relation(relation_type)
        if inverse_relation:
            self.concepts[to_name].add_relation(inverse_relation, from_name)
        
        self._update_metadata()
        return True
    
    def _is_relation_consistent(self, from_concept: str, relation_type: RelationType, to_concept: str) -> bool:
        """Vérifie la cohérence d'une relation avant ajout"""
        
        # Éviter l'auto-référence pour certaines relations
        if from_concept == to_concept and relation_type in [RelationType.CONTRADICTS, RelationType.OPPOSES]:
            return False
        
        # Vérifier les contradictions existantes
        existing_relations = self.concepts[from_concept].relations
        
        if relation_type == RelationType.CONTRADICTS:
            # Si A contradicts B, alors A ne peut pas impliquer B
            if RelationType.IMPLIES.value in existing_relations:
                if to_concept in existing_relations[RelationType.IMPLIES.value]:
                    return False
        
        if relation_type == RelationType.IMPLIES:
            # Si A implique B, alors A ne peut pas contredire B
            if RelationType.CONTRADICTS.value in existing_relations:
                if to_concept in existing_relations[RelationType.CONTRADICTS.value]:
                    return False
        
        return True
    
    def _get_inverse_relation(self, relation_type: RelationType) -> Optional[RelationType]:
        """Retourne la relation inverse si elle existe"""
        inverse_map = {
            RelationType.IS_A: RelationType.HAS_PROPERTY,  # Approximation
            RelationType.PART_OF: None,  # Pas d'inverse automatique
            RelationType.PRECEDES: RelationType.FOLLOWS,
            RelationType.FOLLOWS: RelationType.PRECEDES,
            RelationType.CONTRADICTS: RelationType.CONTRADICTS,  # Symétrique
            RelationType.IS_EQUIVALENT: RelationType.IS_EQUIVALENT,  # Symétrique
        }
        return inverse_map.get(relation_type)
    
    def find_path(self, start_concept: str, end_concept: str, max_depth: int = 3) -> List[List[str]]:
        """Trouve les chemins conceptuels entre deux concepts"""
        start_name = start_concept.upper().strip()
        end_name = end_concept.upper().strip()
        
        if start_name not in self.concepts or end_name not in self.concepts:
            return []
        
        paths = []
        
        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current == target and len(path) > 1:
                paths.append(path[:])
                return
            
            if current in self.concepts:
                related = self.concepts[current].get_related_concepts()
                for next_concept in related:
                    if next_concept not in path:  # Éviter les cycles
                        path.append(next_concept)
                        dfs(next_concept, target, path, depth + 1)
                        path.pop()
        
        dfs(start_name, end_name, [start_name], 0)
        return paths
    
    def get_related_concepts(self, concept_name: str, relation_types: Optional[List[RelationType]] = None) -> Dict[str, List[str]]:
        """Récupère tous les concepts reliés avec leurs types de relations"""
        concept = self.get_concept(concept_name)
        if not concept:
            return {}
        
        if relation_types:
            filtered_relations = {}
            for rel_type in relation_types:
                if rel_type.value in concept.relations:
                    filtered_relations[rel_type.value] = concept.relations[rel_type.value]
            return filtered_relations
        
        return concept.relations
    
    def _count_relations(self) -> int:
        """Compte le nombre total de relations dans l'ontologie"""
        total = 0
        for concept in self.concepts.values():
            for relation_list in concept.relations.values():
                total += len(relation_list)
        return total
    
    def _update_metadata(self) -> None:
        """Met à jour les métadonnées de l'ontologie"""
        from datetime import datetime
        
        self.metadata['total_concepts'] = len(self.concepts)
        self.metadata['total_relations'] = self._count_relations()
        self.metadata['last_modified'] = datetime.now().isoformat()
        
        if not self.metadata['creation_date']:
            self.metadata['creation_date'] = datetime.now().isoformat()
    
    def get_concepts_by_type(self, concept_type: ConceptType) -> List[Concept]:
        """Récupère tous les concepts d'un type donné"""
        return [concept for concept in self.concepts.values() 
                if concept.concept_type == concept_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur l'ontologie"""
        stats = {
            'total_concepts': len(self.concepts),
            'total_relations': self._count_relations(),
            'concepts_by_type': {},
            'most_connected': None,
            'least_connected': None
        }
        
        # Répartition par type
        for concept in self.concepts.values():
            type_name = concept.concept_type.value
            if type_name not in stats['concepts_by_type']:
                stats['concepts_by_type'][type_name] = 0
            stats['concepts_by_type'][type_name] += 1
        
        # Concepts les plus/moins connectés
        if self.concepts:
            concept_connections = {
                name: len(concept.get_related_concepts())
                for name, concept in self.concepts.items()
            }
            
            stats['most_connected'] = max(concept_connections.items(), key=lambda x: x[1])
            stats['least_connected'] = min(concept_connections.items(), key=lambda x: x[1])
        
        return stats
    
    def validate_consistency(self) -> Dict[str, List[str]]:
        """Valide la cohérence logique de l'ontologie"""
        issues = {
            'contradictions': [],
            'circular_references': [],
            'missing_concepts': [],
            'orphaned_concepts': []
        }
        
        for concept_name, concept in self.concepts.items():
            # Vérification des références vers des concepts inexistants
            for relation_type, targets in concept.relations.items():
                for target in targets:
                    if target not in self.concepts:
                        issues['missing_concepts'].append(f"{concept_name} -> {target}")
            
            # Vérification des contradictions logiques
            relations = concept.relations
            if (RelationType.IMPLIES.value in relations and 
                RelationType.CONTRADICTS.value in relations):
                
                implies_set = set(relations[RelationType.IMPLIES.value])
                contradicts_set = set(relations[RelationType.CONTRADICTS.value])
                overlaps = implies_set.intersection(contradicts_set)
                
                for overlap in overlaps:
                    issues['contradictions'].append(
                        f"{concept_name} both implies and contradicts {overlap}"
                    )
            
            # Concepts orphelins (sans relations)
            if not concept.get_related_concepts():
                issues['orphaned_concepts'].append(concept_name)
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'ontologie complète"""
        return {
            'metadata': self.metadata,
            'concepts': {name: concept.to_dict() for name, concept in self.concepts.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleOntology':
        """Désérialise une ontologie depuis un dictionnaire"""
        ontology = cls(load_core_concepts=False)
        ontology.metadata = data.get('metadata', ontology.metadata)
        
        concepts_data = data.get('concepts', {})
        for name, concept_data in concepts_data.items():
            concept = Concept.from_dict(concept_data)
            ontology.concepts[name] = concept
        
        return ontology