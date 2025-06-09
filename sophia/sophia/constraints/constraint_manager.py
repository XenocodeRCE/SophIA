"""
Gestionnaire de contraintes pour génération philosophique avec Ollama
Assure la cohérence et la qualité des réponses via IA
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """Types de contraintes"""
    CONCEPTUAL = "conceptual"
    LINGUISTIC = "linguistic"
    PHILOSOPHICAL = "philosophical"
    LENGTH = "length"
    TONE = "tone"

@dataclass
class Constraint:
    """Définition d'une contrainte"""
    name: str
    constraint_type: ConstraintType
    validator: Callable[[str, Dict[str, Any]], float]
    weight: float = 1.0
    mandatory: bool = False
    description: str = ""

class PhilosophicalConstraintManager:
    """
    Gestionnaire de contraintes pour génération philosophique
    Utilise Ollama pour améliorer l'évaluation
    """
    
    def __init__(self, ontology, llm_interface):
        self.ontology = ontology
        self.llm = llm_interface
        self.constraints = self._build_default_constraints()
        
        # Clusters philosophiques enrichis
        self.philosophical_clusters = self._build_enhanced_philosophical_clusters()
        
        # Cache pour éviter les requêtes répétées
        self._evaluation_cache = {}
        
    def _build_enhanced_philosophical_clusters(self) -> List[Dict[str, Any]]:
        """Construit des clusters philosophiques enrichis"""
        return [
            {
                'name': 'Épistémologie',
                'concepts': {'VÉRITÉ', 'CONNAISSANCE', 'CROYANCE', 'DOUTE', 'CERTITUDE'},
                'themes': ['connaissance', 'savoir', 'vérité', 'science', 'épistémologie'],
                'weight': 0.9
            },
            {
                'name': 'Éthique',
                'concepts': {'BIEN', 'MAL', 'JUSTICE', 'VERTU', 'DEVOIR', 'RESPONSABILITÉ'},
                'themes': ['morale', 'éthique', 'bien', 'mal', 'justice', 'vertu'],
                'weight': 0.9
            },
            {
                'name': 'Métaphysique',
                'concepts': {'ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ', 'TEMPS', 'ESPACE'},
                'themes': ['être', 'existence', 'réalité', 'métaphysique', 'ontologie'],
                'weight': 0.8
            },
            {
                'name': 'Philosophie politique',
                'concepts': {'LIBERTÉ', 'AUTORITÉ', 'POUVOIR', 'ÉGALITÉ', 'SOCIÉTÉ'},
                'themes': ['politique', 'société', 'liberté', 'autorité', 'démocratie'],
                'weight': 0.8
            },
            {
                'name': 'Logique',
                'concepts': {'CAUSE', 'EFFET', 'NÉCESSITÉ', 'POSSIBILITÉ', 'CONTRADICTION'},
                'themes': ['logique', 'raisonnement', 'argument', 'preuve', 'démonstration'],
                'weight': 0.7
            },
            {
                'name': 'Esthétique',
                'concepts': {'BEAUTÉ', 'ART', 'CRÉATION', 'HARMONIE'},
                'themes': ['beauté', 'art', 'esthétique', 'création', 'goût'],
                'weight': 0.6
            }
        ]
    
    def _build_default_constraints(self) -> List[Constraint]:
        """Construit les contraintes philosophiques par défaut"""
        return [
            Constraint(
                name="conceptual_coherence",
                constraint_type=ConstraintType.CONCEPTUAL,
                validator=self._validate_conceptual_coherence,
                weight=0.8,
                mandatory=True,
                description="Cohérence entre concepts utilisés"
            ),
            
            Constraint(
                name="concept_relevance",
                constraint_type=ConstraintType.CONCEPTUAL,
                validator=self._validate_concept_relevance,
                weight=0.7,
                description="Pertinence des concepts par rapport à la question"
            ),
            
            Constraint(
                name="argumentative_structure",
                constraint_type=ConstraintType.PHILOSOPHICAL,
                validator=self._validate_argumentative_structure,
                weight=0.6,
                description="Structure argumentative claire"
            ),
            
            Constraint(
                name="philosophical_depth",
                constraint_type=ConstraintType.PHILOSOPHICAL,
                validator=self._validate_philosophical_depth,
                weight=0.5,
                description="Profondeur de l'analyse philosophique"
            ),
            
            Constraint(
                name="clarity",
                constraint_type=ConstraintType.LINGUISTIC,
                validator=self._validate_clarity,
                weight=0.4,
                description="Clarté et compréhensibilité"
            ),
            
            Constraint(
                name="academic_tone",
                constraint_type=ConstraintType.TONE,
                validator=self._validate_academic_tone,
                weight=0.3,
                description="Ton académique approprié"
            ),
            
            Constraint(
                name="appropriate_length",
                constraint_type=ConstraintType.LENGTH,
                validator=self._validate_length,
                weight=0.2,
                description="Longueur appropriée à la complexité"
            )
        ]
    
    def validate_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Valide une réponse selon toutes les contraintes"""
        validation_results = {}
        total_score = 0.0
        total_weight = 0.0
        violations = []
        
        for constraint in self.constraints:
            try:
                score = constraint.validator(response, context)
                validation_results[constraint.name] = {
                    'score': score,
                    'weight': constraint.weight,
                    'type': constraint.constraint_type.value,
                    'description': constraint.description,
                    'passed': score >= 0.6
                }
                
                total_score += score * constraint.weight
                total_weight += constraint.weight
                
                if constraint.mandatory and score < 0.6:
                    violations.append({
                        'constraint': constraint.name,
                        'score': score,
                        'description': constraint.description
                    })
                    
            except Exception as e:
                logger.error(f"Erreur validation contrainte {constraint.name}: {e}")
                validation_results[constraint.name] = {
                    'score': 0.0,
                    'error': str(e)
                }
        
        global_score = total_score / total_weight if total_weight > 0 else 0.0
        
        return {
            'global_score': global_score,
            'constraint_results': validation_results,
            'violations': violations,
            'is_valid': len(violations) == 0 and global_score >= 0.6,
            'recommendations': self._generate_recommendations(validation_results)
        }
    
    def _validate_philosophical_depth(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la profondeur philosophique via Ollama"""
        
        # Cache pour éviter les requêtes répétées
        cache_key = f"depth:{response[:50]}"
        if cache_key in self._evaluation_cache:
            return self._evaluation_cache[cache_key]
        
        # Analyse de base (fallback)
        depth_indicators = [
            'essence', 'nature', 'fondement', 'principe',
            'définition', 'concept', 'signification',
            'pourquoi', 'comment', 'dans quelle mesure',
            'dialectique', 'paradoxe', 'contradiction',
            'absolu', 'relatif', 'universel', 'particulier'
        ]
        
        response_lower = response.lower()
        found_depth = sum(1 for indicator in depth_indicators if indicator in response_lower)
        base_score = min(found_depth / 5, 1.0)
        
        # Amélioration via Ollama
        try:
            prompt = f"""Évalue la profondeur philosophique de ce texte sur une échelle de 0 à 10:

TEXTE: "{response[:300]}..."

Critères d'évaluation:
- Présence de questionnements fondamentaux
- Analyse conceptuelle approfondie
- Références aux problématiques philosophiques classiques
- Complexité de l'argumentation
- Originalité de la réflexion

Score (0-10):"""
            
            ollama_response = self.llm.generate_text(prompt, max_tokens=50, temperature=0.2)
            
            if ollama_response:
                # Extraction du score
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', ollama_response)
                if score_match:
                    ollama_score = float(score_match.group(1)) / 10.0
                    # Moyenne pondérée entre base et Ollama
                    final_score = (base_score * 0.4) + (ollama_score * 0.6)
                else:
                    final_score = base_score
            else:
                final_score = base_score
            
            # Cache du résultat
            self._evaluation_cache[cache_key] = final_score
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation profondeur Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
    def _validate_academic_tone(self, response: str, context: Dict[str, Any]) -> float:
        """Valide le ton académique via Ollama"""
        
        cache_key = f"tone:{response[:50]}"
        if cache_key in self._evaluation_cache:
            return self._evaluation_cache[cache_key]
        
        # Analyse de base (fallback)
        academic_indicators = [
            'selon', 'd\'après', 'conformément à',
            'il convient de', 'il est important de',
            'nous pouvons observer', 'il apparaît que',
            'en effet', 'néanmoins', 'toutefois'
        ]
        
        informal_indicators = [
            'bon', 'eh bien', 'voilà', 'quoi',
            'franchement', 'carrément', 'super'
        ]
        
        response_lower = response.lower()
        
        academic_count = sum(1 for indicator in academic_indicators if indicator in response_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in response_lower)
        
        base_score = min(academic_count / 3, 1.0) - (informal_count * 0.2)
        base_score = max(base_score, 0.0)
        
        # Amélioration via Ollama
        try:
            prompt = f"""Évalue le niveau académique de ce texte philosophique sur une échelle de 0 à 10:

TEXTE: "{response[:300]}..."

Critères:
- Vocabulaire précis et technique
- Formulations rigoureuses
- Absence de familiarités
- Style soutenu
- Respect des conventions académiques

Score académique (0-10):"""
            
            ollama_response = self.llm.generate_text(prompt, max_tokens=50, temperature=0.2)
            
            if ollama_response:
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', ollama_response)
                if score_match:
                    ollama_score = float(score_match.group(1)) / 10.0
                    final_score = (base_score * 0.4) + (ollama_score * 0.6)
                else:
                    final_score = base_score
            else:
                final_score = base_score
            
            self._evaluation_cache[cache_key] = final_score
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation ton académique Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
    def _validate_conceptual_coherence(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la cohérence conceptuelle améliorée"""
        concepts_detected = context.get('concepts_detected', [])
        
        if len(concepts_detected) < 2:
            return 0.7
        
        # Vérification via clusters philosophiques
        coherence_score = 0.0
        total_pairs = 0
        
        for i, concept1 in enumerate(concepts_detected):
            for concept2 in concepts_detected[i+1:]:
                if self._concepts_are_related_enhanced(concept1, concept2):
                    coherence_score += 1.0
                total_pairs += 1
        
        return coherence_score / total_pairs if total_pairs > 0 else 0.5
    
    def _concepts_are_related_enhanced(self, concept1: str, concept2: str) -> bool:
        """Vérifie si deux concepts sont liés via clusters enrichis"""
        # Vérification dans les clusters philosophiques
        for cluster in self.philosophical_clusters:
            if concept1 in cluster['concepts'] and concept2 in cluster['concepts']:
                return True
        
        # Relations ontologiques directes
        if concept1 in self.ontology.concepts and concept2 in self.ontology.concepts:
            concept1_obj = self.ontology.concepts[concept1]
            if hasattr(concept1_obj, 'related_concepts'):
                return concept2 in concept1_obj.related_concepts
        
        return False
    
    def _validate_concept_relevance(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la pertinence des concepts"""
        question = context.get('question', '')
        concepts_detected = context.get('concepts_detected', [])
        
        if not concepts_detected:
            return 0.3
        
        question_words = set(question.lower().split())
        relevance_scores = []
        
        for concept in concepts_detected:
            concept_words = set(concept.lower().split('_'))
            intersection = question_words & concept_words
            relevance = len(intersection) / len(concept_words) if concept_words else 0
            
            if concept.lower() in response.lower():
                relevance += 0.3
                
            relevance_scores.append(min(relevance, 1.0))
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _validate_argumentative_structure(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la structure argumentative"""
        structure_indicators = [
            'tout d\'abord', 'premièrement', 'en premier lieu',
            'ensuite', 'deuxièmement', 'par ailleurs',
            'enfin', 'finalement', 'en conclusion',
            'cependant', 'néanmoins', 'toutefois',
            'donc', 'ainsi', 'par conséquent'
        ]
        
        response_lower = response.lower()
        found_indicators = sum(1 for indicator in structure_indicators if indicator in response_lower)
        
        structure_score = min(found_indicators / 3, 1.0)
        
        word_count = len(response.split())
        if word_count > 100:
            structure_score += 0.2
        
        return min(structure_score, 1.0)
    
    def _validate_clarity(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la clarté du discours"""
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        clarity_score = 1.0
        if avg_sentence_length > 25:
            clarity_score -= 0.3
        elif avg_sentence_length > 35:
            clarity_score -= 0.5
        
        logical_connectors = [
            'car', 'parce que', 'puisque', 'étant donné',
            'donc', 'ainsi', 'par conséquent', 'c\'est pourquoi'
        ]
        
        response_lower = response.lower()
        found_connectors = sum(1 for connector in logical_connectors if connector in response_lower)
        
        clarity_score += min(found_connectors * 0.1, 0.3)
        
        return min(max(clarity_score, 0.0), 1.0)
    
    def _validate_length(self, response: str, context: Dict[str, Any]) -> float:
        """Valide la longueur appropriée"""
        word_count = len(response.split())
        concepts_count = len(context.get('concepts_detected', []))
        
        expected_min = max(50, concepts_count * 30)
        expected_max = min(500, concepts_count * 100)
        
        if expected_min <= word_count <= expected_max:
            return 1.0
        elif word_count < expected_min:
            return word_count / expected_min
        else:
            return max(0.5, expected_max / word_count)
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        for constraint_name, result in validation_results.items():
            if result.get('score', 0) < 0.6:
                if constraint_name == 'conceptual_coherence':
                    recommendations.append("Améliorer la cohérence entre les concepts utilisés")
                elif constraint_name == 'argumentative_structure':
                    recommendations.append("Structurer davantage l'argumentation avec des connecteurs logiques")
                elif constraint_name == 'philosophical_depth':
                    recommendations.append("Approfondir l'analyse philosophique")
                elif constraint_name == 'clarity':
                    recommendations.append("Améliorer la clarté en raccourcissant les phrases")
                elif constraint_name == 'academic_tone':
                    recommendations.append("Adopter un ton plus académique")
        
        return recommendations
    
    def add_constraint(self, constraint: Constraint):
        """Ajoute une nouvelle contrainte"""
        self.constraints.append(constraint)
        logger.info(f"Contrainte ajoutée: {constraint.name}")
    
    def remove_constraint(self, constraint_name: str):
        """Supprime une contrainte"""
        self.constraints = [c for c in self.constraints if c.name != constraint_name]
        logger.info(f"Contrainte supprimée: {constraint_name}")
    
    def get_constraint_report(self) -> Dict[str, Any]:
        """Rapport sur les contraintes configurées"""
        return {
            'total_constraints': len(self.constraints),
            'by_type': {
                ctype.value: len([c for c in self.constraints if c.constraint_type == ctype])
                for ctype in ConstraintType
            },
            'mandatory_constraints': len([c for c in self.constraints if c.mandatory]),
            'philosophical_clusters': len(self.philosophical_clusters),
            'constraints': [
                {
                    'name': c.name,
                    'type': c.constraint_type.value,
                    'weight': c.weight,
                    'mandatory': c.mandatory,
                    'description': c.description
                }
                for c in self.constraints
            ]
        }