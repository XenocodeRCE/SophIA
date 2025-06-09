"""
Pont conceptuel entre extraction LLM et LCM avec amélioration Ollama
Améliore la correspondance concepts ↔ texte via intelligence artificielle
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ConceptMatch:
    """Correspondance concept-texte détaillée"""
    concept: str
    text_span: str
    position: Tuple[int, int]
    confidence: float
    context: str
    reasoning: str

class EnhancedConceptTextBridge:
    """
    Pont amélioré entre concepts ontologiques et texte naturel
    Utilise Ollama pour améliorer l'analyse contextuelle
    """
    
    def __init__(self, ontology, llm_interface):
        self.ontology = ontology
        self.llm = llm_interface
        self.context_window = 50
        
        # Cache pour éviter les requêtes répétées - INITIALISE EN PREMIER
        self._synonyms_cache = {}
        self._context_cache = {}
        
        # Maintenant on peut construire les patterns
        self.concept_patterns = self._build_concept_patterns()
        
    def _build_concept_patterns(self) -> Dict[str, List[str]]:
        """Construit des patterns de reconnaissance pour chaque concept"""
        patterns = {}
        
        for concept_name, concept in self.ontology.concepts.items():
            patterns[concept_name] = [
                concept_name.lower(),
                concept_name.replace('_', ' ').lower(),
                concept_name.replace('_', '-').lower(),
                *self._get_concept_synonyms(concept_name)
            ]
        
        return patterns
    
    def _get_concept_synonyms(self, concept_name: str) -> List[str]:
        """Génère des synonymes contextuels via Ollama"""
        
        # Cache pour éviter les requêtes répétées
        if concept_name in self._synonyms_cache:
            return self._synonyms_cache[concept_name]
        
        # Synonymes de base (fallback)
        base_synonyms = {
            'VÉRITÉ': ['vrai', 'véracité', 'réalité', 'authenticité'],
            'JUSTICE': ['équité', 'droit', 'justesse', 'impartialité'],
            'LIBERTÉ': ['libre arbitre', 'autonomie', 'indépendance'],
            'BIEN': ['bon', 'bonté', 'vertu', 'moral'],
            'MAL': ['mauvais', 'méchanceté', 'vice', 'immoral'],
            'ÊTRE': ['existence', 'ontologie', 'réalité'],
            'DEVENIR': ['changement', 'évolution', 'transformation'],
            'CONNAISSANCE': ['savoir', 'science', 'épistémologie'],
            'CROYANCE': ['foi', 'conviction', 'opinion'],
            'CAUSE': ['causalité', 'origine', 'source'],
            'EFFET': ['conséquence', 'résultat', 'impact']
        }
        
        base_list = base_synonyms.get(concept_name, [])
        
        # Enrichissement via Ollama
        try:
            if hasattr(self.llm, 'available') and self.llm.available:
                prompt = f"""Génère 3 synonymes philosophiques précis pour le concept "{concept_name}".
Format: mot1, mot2, mot3
Seulement les mots, pas d'explication.

Concept: {concept_name}
Synonymes:"""
                
                ollama_response = self.llm.generate_text(prompt, max_tokens=30, temperature=0.3)
                
                # Extraction des synonymes
                ollama_synonyms = []
                if ollama_response:
                    # Nettoyage et extraction
                    cleaned = ollama_response.strip().lower()
                    # Suppression des numéros et caractères indésirables
                    cleaned = re.sub(r'\d+\.?\s*', '', cleaned)
                    
                    synonyms = [s.strip() for s in cleaned.split(',')]
                    ollama_synonyms = [s for s in synonyms if s and len(s) > 2 and len(s) < 20]
                
                # Combinaison base + Ollama
                all_synonyms = base_list + ollama_synonyms[:3]  # Limite à 3 synonymes Ollama
                
            else:
                all_synonyms = base_list
            
            # Cache du résultat
            self._synonyms_cache[concept_name] = all_synonyms
            
            logger.debug(f"Synonymes pour {concept_name}: {all_synonyms}")
            return all_synonyms
            
        except Exception as e:
            logger.warning(f"Erreur génération synonymes Ollama pour {concept_name}: {e}")
            self._synonyms_cache[concept_name] = base_list
            return base_list
    
    def _analyze_concept_context(self, match: ConceptMatch) -> Dict[str, Any]:
        """Analyse le contexte d'un concept via Ollama"""
        
        # Cache pour éviter les requêtes répétées
        cache_key = f"{match.concept}:{match.context[:30]}"
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]
        
        # Analyse de base (fallback)
        context_lower = match.context.lower()
        
        base_analysis = {
            'sentiment': 'neutre',
            'context_length': len(match.context),
            'philosophical_context': any(word in context_lower for word in [
                'philosophie', 'pensée', 'réflexion', 'théorie'
            ]),
            'complexity': 'medium'
        }
        
        # Enrichissement via Ollama
        try:
            if hasattr(self.llm, 'available') and self.llm.available:
                prompt = f"""Analyse ce contexte philosophique pour le concept "{match.concept}":

CONTEXTE: "{match.context[:100]}..."
CONCEPT: {match.concept}

Réponds avec ce format exact:
sentiment: [positif/négatif/neutre]
complexité: [simple/medium/complexe]
thème: [éthique/métaphysique/épistémologie/logique/politique/autre]

Analyse:"""
                
                ollama_response = self.llm.generate_text(prompt, max_tokens=60, temperature=0.2)
                
                if ollama_response:
                    # Extraction des informations
                    lines = ollama_response.lower().split('\n')
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if 'sentiment' in key:
                                base_analysis['sentiment'] = value
                            elif 'complexité' in key or 'complexity' in key:
                                base_analysis['complexity'] = value
                            elif 'thème' in key or 'theme' in key:
                                base_analysis['philosophical_theme'] = value
            
            # Cache du résultat
            self._context_cache[cache_key] = base_analysis
            
        except Exception as e:
            logger.warning(f"Erreur analyse contexte Ollama: {e}")
            self._context_cache[cache_key] = base_analysis
        
        return base_analysis
    
    def enhanced_concept_extraction(self, text: str, 
                                  base_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraction conceptuelle améliorée avec analyse contextuelle Ollama
        """
        matches = []
        text_lower = text.lower()
        
        # 1. Analyse des concepts de base détectés
        base_concepts = base_extraction.get('concepts_detected', [])
        
        for concept in base_concepts:
            concept_matches = self._find_concept_in_text(concept, text, text_lower)
            matches.extend(concept_matches)
        
        # 2. Recherche de concepts additionnels par patterns
        additional_concepts = self._find_additional_concepts(text, text_lower, base_concepts)
        matches.extend(additional_concepts)
        
        # 3. Analyse contextuelle et validation
        validated_matches = self._validate_concept_matches(matches, text)
        
        # 4. Construction de la réponse enrichie
        enhanced_extraction = {
            **base_extraction,
            'concept_matches': [self._match_to_dict(m) for m in validated_matches],
            'concepts_detailed': self._build_detailed_concepts(validated_matches),
            'contextual_analysis': self._analyze_context(validated_matches, text),
            'enhanced_confidence': self._calculate_enhanced_confidence(validated_matches),
            'concepts_detected': list(set(base_concepts + [m.concept for m in validated_matches]))
        }
        
        return enhanced_extraction
    
    def _find_concept_in_text(self, concept: str, text: str, text_lower: str) -> List[ConceptMatch]:
        """Trouve toutes les occurrences d'un concept dans le texte"""
        matches = []
        patterns = self.concept_patterns.get(concept, [concept.lower()])
        
        for pattern in patterns:
            regex = r'\b' + re.escape(pattern) + r'\b'
            
            for match in re.finditer(regex, text_lower):
                start, end = match.span()
                
                context_start = max(0, start - self.context_window)
                context_end = min(len(text), end + self.context_window)
                context = text[context_start:context_end]
                
                confidence = self._calculate_pattern_confidence(pattern, concept, context)
                
                matches.append(ConceptMatch(
                    concept=concept,
                    text_span=text[start:end],
                    position=(start, end),
                    confidence=confidence,
                    context=context,
                    reasoning=f"Pattern '{pattern}' matched for concept {concept}"
                ))
        
        return matches
    
    def _find_additional_concepts(self, text: str, text_lower: str, 
                                base_concepts: List[str]) -> List[ConceptMatch]:
        """Recherche de concepts additionnels non détectés initialement"""
        additional_matches = []
        found_concepts = set(base_concepts)
        
        for concept_name in self.ontology.concepts.keys():
            if concept_name not in found_concepts:
                matches = self._find_concept_in_text(concept_name, text, text_lower)
                strong_matches = [m for m in matches if m.confidence > 0.6]
                additional_matches.extend(strong_matches)
        
        return additional_matches
    
    def _validate_concept_matches(self, matches: List[ConceptMatch], 
                                text: str) -> List[ConceptMatch]:
        """Valide et filtre les correspondances conceptuelles"""
        concept_groups = defaultdict(list)
        for match in matches:
            concept_groups[match.concept].append(match)
        
        validated = []
        
        for concept, concept_matches in concept_groups.items():
            best_match = max(concept_matches, key=lambda m: m.confidence)
            
            if self._is_contextually_valid(best_match, text):
                validated.append(best_match)
        
        return validated
    
    def _is_contextually_valid(self, match: ConceptMatch, text: str) -> bool:
        """Valide un match dans son contexte"""
        negative_words = ['ne pas', 'non', 'absence de', 'manque de', 'sans']
        context_words = match.context.lower()
        match_position = context_words.find(match.text_span.lower())
        
        for neg_word in negative_words:
            if neg_word in context_words:
                neg_pos = context_words.find(neg_word)
                if abs(neg_pos - match_position) < 30:
                    return False
        
        return True
    
    def _calculate_pattern_confidence(self, pattern: str, concept: str, context: str) -> float:
        """Calcule la confiance d'un pattern dans son contexte"""
        base_confidence = 0.7
        
        if pattern == concept.lower():
            base_confidence += 0.2
        
        philosophical_words = [
            'philosophie', 'pensée', 'réflexion', 'concept', 'idée',
            'théorie', 'doctrine', 'principe', 'essence', 'nature'
        ]
        
        context_lower = context.lower()
        for word in philosophical_words:
            if word in context_lower:
                base_confidence += 0.1
                break
        
        return min(base_confidence, 1.0)
    
    def _calculate_enhanced_confidence(self, matches: List[ConceptMatch]) -> float:
        """Calcule la confiance globale améliorée"""
        if not matches:
            return 0.0
        
        total_confidence = sum(match.confidence for match in matches)
        avg_confidence = total_confidence / len(matches)
        
        unique_concepts = len(set(match.concept for match in matches))
        diversity_bonus = min(unique_concepts * 0.05, 0.2)
        
        return min(avg_confidence + diversity_bonus, 1.0)
    
    def _build_detailed_concepts(self, matches: List[ConceptMatch]) -> Dict[str, Dict]:
        """Construit une analyse détaillée des concepts"""
        detailed = {}
        
        for match in matches:
            if match.concept not in detailed:
                detailed[match.concept] = {
                    'confidence': match.confidence,
                    'occurrences': [],
                    'context_analysis': self._analyze_concept_context(match)
                }
            
            detailed[match.concept]['occurrences'].append({
                'text': match.text_span,
                'position': match.position,
                'context': match.context
            })
        
        return detailed
    
    def _analyze_context(self, matches: List[ConceptMatch], text: str) -> Dict[str, Any]:
        """Analyse contextuelle globale"""
        return {
            'total_concepts_found': len(matches),
            'text_length': len(text),
            'concept_density': len(matches) / max(len(text.split()), 1),
            'philosophical_indicators': self._count_philosophical_indicators(text),
            'complexity_score': self._calculate_complexity_score(matches, text)
        }
    
    def _count_philosophical_indicators(self, text: str) -> int:
        """Compte les indicateurs philosophiques dans le texte"""
        indicators = [
            'pourquoi', 'comment', 'qu\'est-ce que', 'nature de',
            'essence de', 'signification', 'sens de', 'définition',
            'concept de', 'idée de', 'théorie de', 'principe de'
        ]
        
        text_lower = text.lower()
        count = sum(1 for indicator in indicators if indicator in text_lower)
        return count
    
    def _calculate_complexity_score(self, matches: List[ConceptMatch], text: str) -> float:
        """Calcule un score de complexité philosophique"""
        if not matches:
            return 0.0
        
        concept_count = len(matches)
        unique_concepts = len(set(match.concept for match in matches))
        avg_confidence = sum(match.confidence for match in matches) / len(matches)
        text_length = len(text.split())
        
        complexity = (
            (concept_count * 0.3) +
            (unique_concepts * 0.4) +
            (avg_confidence * 0.2) +
            (min(text_length / 100, 1.0) * 0.1)
        )
        
        return min(complexity, 1.0)
    
    def _match_to_dict(self, match: ConceptMatch) -> Dict[str, Any]:
        """Convertit un ConceptMatch en dictionnaire"""
        return {
            'concept': match.concept,
            'text_span': match.text_span,
            'position': match.position,
            'confidence': match.confidence,
            'context': match.context,
            'reasoning': match.reasoning
        }