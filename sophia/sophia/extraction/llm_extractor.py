"""
LLM Concept Extractor - Extraction conceptuelle de niveau supérieur
Utilise l'IA pour identifier et analyser les concepts philosophiques complexes
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class ConceptMatch:
    """Représente une correspondance conceptuelle détectée"""
    concept: str
    confidence: float
    source: str  # 'direct', 'inference', 'context', 'semantic'
    evidence: List[str]
    position: int
    related_concepts: List[str]

@dataclass
class ConceptualRelation:
    """Représente une relation entre concepts"""
    from_concept: str
    to_concept: str
    relation_type: str  # 'implies', 'contradicts', 'defines', 'exemplifies'
    strength: float
    evidence: str

class SemanticAnalyzer:
    """Analyseur sémantique pour détecter les concepts implicites"""
    
    def __init__(self):
        # Patterns sémantiques pour concepts philosophiques
        self.semantic_patterns = {
            'VÉRITÉ': [
                r'\b(vrai|faux|véracité|authenticité|réalité|fait)\b',
                r'\b(correspond|exact|précis|correct|erroné)\b',
                r'\b(vérifier|prouver|démontrer|confirmer)\b'
            ],
            'JUSTICE': [
                r'\b(juste|injuste|équitable|équité|droit|droits)\b',
                r'\b(tribunal|juge|jugement|sentence|verdict)\b',
                r'\b(punition|sanction|réparation|compensation)\b'
            ],
            'LIBERTÉ': [
                r'\b(libre|libérer|liberté|affranchir|émanciper)\b',
                r'\b(contrainte|obligation|devoir|responsabilité)\b',
                r'\b(choix|choisir|décider|option|alternative)\b'
            ],
            'BEAUTÉ': [
                r'\b(beau|belle|laid|esthétique|artistique)\b',
                r'\b(harmonie|proportion|symétrie|élégance)\b',
                r'\b(art|œuvre|création|style|goût)\b'
            ],
            'BIEN': [
                r'\b(bien|bon|bonté|vertu|moral|éthique)\b',
                r'\b(valeur|principe|idéal|noble)\b',
                r'\b(devoir|obligation|responsabilité)\b'
            ],
            'MAL': [
                r'\b(mal|mauvais|méchant|vice|immoral)\b',
                r'\b(péché|faute|erreur|tort|dommage)\b',
                r'\b(souffrance|douleur|nuire|blesser)\b'
            ],
            'ÊTRE': [
                r'\b(être|existence|exister|réel|réalité)\b',
                r'\b(ontologie|métaphysique|essence|nature)\b',
                r'\b(substantiel|matériel|spirituel)\b'
            ],
            'CONNAISSANCE': [
                r'\b(savoir|connaître|connaissance|science)\b',
                r'\b(apprendre|étudier|découvrir|comprendre)\b',
                r'\b(ignorance|ignorer|méconnaître)\b'
            ],
            'CONSCIENCE': [
                r'\b(conscience|conscient|inconscient|éveil)\b',
                r'\b(esprit|mental|psychique|âme)\b',
                r'\b(perception|sensation|sentiment|émotion)\b'
            ],
            'TEMPS': [
                r'\b(temps|temporel|durée|instant|moment)\b',
                r'\b(passé|présent|futur|éternel|permanent)\b',
                r'\b(chronologie|histoire|évolution)\b'
            ]
        }
        
        # Patterns pour relations conceptuelles
        self.relation_patterns = {
            'implies': [
                r'implique', r'entraîne', r'suppose', r'nécessite',
                r'si.*alors', r'donc', r'par conséquent'
            ],
            'contradicts': [
                r'contradictoire', r'oppose', r'contraire', r'incompatible',
                r'mais', r'cependant', r'néanmoins', r'pourtant'
            ],
            'defines': [
                r'définit', r'signifie', r'est', r'consiste', r'caractérise',
                r'qu\'est-ce que', r'nature de', r'essence de'
            ],
            'exemplifies': [
                r'exemple', r'illustre', r'montre', r'démontre',
                r'comme', r'tel que', r'notamment'
            ]
        }
    
    def extract_semantic_concepts(self, text: str) -> List[ConceptMatch]:
        """Extrait les concepts via analyse sémantique"""
        matches = []
        text_lower = text.lower()
        
        for concept, patterns in self.semantic_patterns.items():
            concept_evidence = []
            total_confidence = 0
            
            for pattern in patterns:
                regex_matches = re.finditer(pattern, text_lower)
                for match in regex_matches:
                    evidence = match.group(0)
                    concept_evidence.append(evidence)
                    total_confidence += 0.3  # Base confidence per match
            
            if concept_evidence:
                # Calcul de confiance basé sur nombre et qualité des matches
                confidence = min(total_confidence / len(patterns), 1.0)
                
                matches.append(ConceptMatch(
                    concept=concept,
                    confidence=confidence,
                    source='semantic',
                    evidence=concept_evidence,
                    position=text_lower.find(concept_evidence[0]) if concept_evidence else 0,
                    related_concepts=[]
                ))
        
        return matches
    
    def detect_relations(self, text: str, concepts: List[str]) -> List[ConceptualRelation]:
        """Détection de relations conceptuelles plus précise"""
        relations = []
        text_lower = text.lower()
        
        # Patterns de relation améliorés avec contexte
        enhanced_relation_patterns = {
            'implies': {
                'patterns': [r'implique', r'entraîne', r'suppose', r'nécessite', r'conduit à'],
                'context_words': ['donc', 'par conséquent', 'ainsi', 'de ce fait']
            },
            'contradicts': {
                'patterns': [r'mais', r'cependant', r'néanmoins', r'pourtant', r'oppose', r'contraire'],
                'context_words': ['contradiction', 'paradoxe', 'incompatible', 'divergent']
            },
            'transcends': {  # NOUVEAU TYPE DE RELATION
                'patterns': [r'transcende', r'dépasse', r'au-delà', r'sublime'],
                'context_words': ['élève', 'supérieur', 'métaphysique']
            },
            'defines': {
                'patterns': [r'définit', r'signifie', r'est', r'consiste', r'caractérise'],
                'context_words': ['nature', 'essence', 'concept', 'notion']
            }
        }
        
        # Détection de relations directes dans la phrase
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts):
                if i >= j:
                    continue
                
                concept1_lower = concept1.lower()
                concept2_lower = concept2.lower()
                
                # Recherche de relations explicites
                for relation_type, relation_data in enhanced_relation_patterns.items():
                    
                    # Pattern principal : concept1 + relation + concept2
                    for pattern in relation_data['patterns']:
                        
                        # Recherche bidirectionnelle
                        forward_pattern = rf'{concept1_lower}.*{pattern}.*{concept2_lower}'
                        backward_pattern = rf'{concept2_lower}.*{pattern}.*{concept1_lower}'
                        
                        if re.search(forward_pattern, text_lower, re.IGNORECASE):
                            # Calcul de force basé sur proximité et contexte
                            strength = self._calculate_relation_strength(
                                text_lower, concept1_lower, concept2_lower, pattern, relation_data['context_words']
                            )
                            
                            if strength >= 0.5:  # Seuil de qualité
                                relations.append(ConceptualRelation(
                                    from_concept=concept1,
                                    to_concept=concept2,
                                    relation_type=relation_type,
                                    strength=strength,
                                    evidence=f"'{pattern}' entre {concept1} et {concept2}"
                                ))
                        
                        elif re.search(backward_pattern, text_lower, re.IGNORECASE):
                            strength = self._calculate_relation_strength(
                                text_lower, concept2_lower, concept1_lower, pattern, relation_data['context_words']
                            )
                            
                            if strength >= 0.5:
                                relations.append(ConceptualRelation(
                                    from_concept=concept2,
                                    to_concept=concept1,
                                    relation_type=relation_type,
                                    strength=strength,
                                    evidence=f"'{pattern}' entre {concept2} et {concept1}"
                                ))
        
        # Filtrage des relations redondantes
        filtered_relations = self._filter_redundant_relations(relations)
        
        return filtered_relations

    def _calculate_relation_strength(self, text: str, concept1: str, concept2: str, 
                                   pattern: str, context_words: List[str]) -> float:
        """Calcule la force d'une relation basée sur le contexte"""
        base_strength = 0.6
        
        # Bonus pour mots de contexte
        context_bonus = 0
        for word in context_words:
            if word in text:
                context_bonus += 0.1
        
        # Bonus pour proximité des concepts
        concept1_pos = text.find(concept1)
        concept2_pos = text.find(concept2)
        if concept1_pos != -1 and concept2_pos != -1:
            distance = abs(concept1_pos - concept2_pos)
            proximity_bonus = max(0, 0.2 - (distance / len(text)) * 0.2)
        else:
            proximity_bonus = 0
        
        # Pénalité pour relations multiples entre mêmes concepts
        pattern_count = len(re.findall(pattern, text))
        if pattern_count > 1:
            redundancy_penalty = 0.1 * (pattern_count - 1)
        else:
            redundancy_penalty = 0
        
        final_strength = min(base_strength + context_bonus + proximity_bonus - redundancy_penalty, 1.0)
        return max(final_strength, 0.0)

    def _filter_redundant_relations(self, relations: List[ConceptualRelation]) -> List[ConceptualRelation]:
        """Filtre les relations redondantes ou contradictoires"""
        
        # Groupe par paire de concepts
        relation_groups = defaultdict(list)
        for rel in relations:
            key = (rel.from_concept, rel.to_concept)
            relation_groups[key].append(rel)
        
        filtered = []
        for (concept1, concept2), group_relations in relation_groups.items():
            if len(group_relations) == 1:
                filtered.append(group_relations[0])
            else:
                # Garde seulement la relation la plus forte
                best_relation = max(group_relations, key=lambda r: r.strength)
                
                # Vérifie qu'il n'y a pas de contradiction majeure
                relation_types = [r.relation_type for r in group_relations]
                if 'implies' in relation_types and 'contradicts' in relation_types:
                    # Conflict détecté - garde seulement si force > 0.8
                    if best_relation.strength > 0.8:
                        filtered.append(best_relation)
                else:
                    filtered.append(best_relation)
        
        return filtered

class ContextualAnalyzer:
    """Analyseur contextuel pour inférences philosophiques avancées"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        
        # Contextes philosophiques typiques
        self.philosophical_contexts = {
            'epistemological': {
                'keywords': ['connaissance', 'savoir', 'vérité', 'croyance', 'justification', 'preuve'],
                'implied_concepts': ['VÉRITÉ', 'CONNAISSANCE', 'CROYANCE', 'JUSTIFICATION']
            },
            'ethical': {
                'keywords': ['moral', 'éthique', 'bien', 'mal', 'devoir', 'responsabilité', 'valeur'],
                'implied_concepts': ['BIEN', 'MAL', 'JUSTICE', 'VERTU', 'DEVOIR']
            },
            'metaphysical': {
                'keywords': ['être', 'existence', 'réalité', 'essence', 'substance', 'monde'],
                'implied_concepts': ['ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ', 'SUBSTANCE']
            },
            'aesthetic': {
                'keywords': ['art', 'beauté', 'création', 'style', 'goût', 'harmonie'],
                'implied_concepts': ['BEAUTÉ', 'ART', 'CRÉATION', 'HARMONIE']
            },
            'logical': {
                'keywords': ['logique', 'raisonnement', 'argument', 'preuve', 'démonstration'],
                'implied_concepts': ['LOGIQUE', 'RAISONNEMENT', 'ARGUMENT', 'VALIDITÉ']
            }
        }
    
    def analyze_context(self, text: str) -> Dict[str, Any]:
        """Analyse le contexte philosophique du texte"""
        text_lower = text.lower()
        context_scores = {}
        
        for context_name, context_data in self.philosophical_contexts.items():
            score = 0
            found_keywords = []
            
            for keyword in context_data['keywords']:
                if keyword in text_lower:
                    score += 1
                    found_keywords.append(keyword)
            
            if score > 0:
                context_scores[context_name] = {
                    'score': score / len(context_data['keywords']),
                    'keywords_found': found_keywords,
                    'implied_concepts': context_data['implied_concepts']
                }
        
        return context_scores
    
    def infer_concepts_from_context(self, text: str) -> List[ConceptMatch]:
        """Infère des concepts basés sur le contexte philosophique"""
        context_analysis = self.analyze_context(text)
        inferred_matches = []
        
        for context_name, context_info in context_analysis.items():
            if context_info['score'] > 0.3:  # Seuil de confiance contextuelle
                for concept in context_info['implied_concepts']:
                    # Vérifie que le concept n'est pas déjà explicitement mentionné
                    if concept.lower() not in text.lower():
                        inferred_matches.append(ConceptMatch(
                            concept=concept,
                            confidence=context_info['score'] * 0.6,  # Confiance réduite pour inférence
                            source='context_inference',
                            evidence=[f"Contexte {context_name}: {context_info['keywords_found']}"],
                            position=-1,  # Position virtuelle pour inférence
                            related_concepts=context_info['implied_concepts']
                        ))
        
        return inferred_matches

class LLMConceptExtractor:
    """
    Extracteur de concepts ultra-avancé utilisant l'IA
    Combine analyse directe, sémantique, contextuelle et inférentielle
    """
    
    def __init__(self, ontology, llm_interface, enable_advanced_inference: bool = True):
        self.ontology = ontology
        self.llm = llm_interface
        self.enable_advanced_inference = enable_advanced_inference
        
        # Analyseurs spécialisés
        self.semantic_analyzer = SemanticAnalyzer()
        self.contextual_analyzer = ContextualAnalyzer(ontology)
        
        # Cache pour optimiser les performances
        self._analysis_cache = {}
        self._cache_lock = threading.Lock()
        
        # Statistiques d'usage
        self.stats = {
            'total_extractions': 0,
            'cache_hits': 0,
            'llm_calls': 0,
            'concepts_found': defaultdict(int)
        }
        
        logger.info("🔍 LLM Concept Extractor Ultra-Avancé initialisé")
    
    def extract_concepts(self, text: str, max_concepts: int = 10) -> Dict[str, Any]:
        """Extraction de concepts multi-niveaux ultra-avancée"""
        
        # Cache check
        text_hash = hash(text.lower().strip())
        with self._cache_lock:
            if text_hash in self._analysis_cache:
                self.stats['cache_hits'] += 1
                logger.debug("🚀 Extraction depuis cache LLM")
                return self._analysis_cache[text_hash]
        
        self.stats['total_extractions'] += 1
        
        start_time = time.time()
        logger.info(f"🔍 Extraction LLM avancée: {text[:50]}...")
        
        # Niveau 1: Extraction directe via LLaMA
        direct_concepts = self._extract_direct_concepts(text)
        
        # Niveau 2: Analyse sémantique
        semantic_matches = self.semantic_analyzer.extract_semantic_concepts(text)
        
        # Niveau 3: Inférence contextuelle
        contextual_matches = self.contextual_analyzer.infer_concepts_from_context(text)
        
        # Niveau 4: Analyse relationnelle
        all_concept_names = list(set([m.concept for m in direct_concepts + semantic_matches + contextual_matches]))
        relations = self.semantic_analyzer.detect_relations(text, all_concept_names)
        
        # Niveau 5: Validation et scoring avancé
        validated_concepts = self._validate_and_score_concepts(
            text, direct_concepts + semantic_matches + contextual_matches
        )
        
        # Niveau 6: Enrichissement via LLaMA (si activé)
        if self.enable_advanced_inference and len(validated_concepts) > 0:
            enriched_concepts = self._enrich_with_llm_inference(text, validated_concepts)
            validated_concepts.extend(enriched_concepts)
        
        # Consolidation finale
        final_concepts = self._consolidate_concepts(validated_concepts, max_concepts)
        
        # Construction du résultat
        result = self._build_extraction_result(text, final_concepts, relations)
        
        # Mise en cache
        with self._cache_lock:
            self._analysis_cache[text_hash] = result
            # Limite du cache
            if len(self._analysis_cache) > 100:
                oldest_key = next(iter(self._analysis_cache))
                del self._analysis_cache[oldest_key]
        
        duration = time.time() - start_time
        logger.info(f"🔍 Extraction LLM terminée: {len(final_concepts)} concepts ({duration:.2f}s)")
        
        return result
    
    def _extract_direct_concepts(self, text: str) -> List[ConceptMatch]:
        """Extraction directe via détection de mots-clés et synonymes"""
        matches = []
        text_lower = text.lower()
        
        for concept_name, concept_obj in self.ontology.concepts.items():
            # Recherche directe du nom du concept
            if concept_name.lower() in text_lower:
                position = text_lower.find(concept_name.lower())
                matches.append(ConceptMatch(
                    concept=concept_name,
                    confidence=0.9,
                    source='direct',
                    evidence=[concept_name.lower()],
                    position=position,
                    related_concepts=[]
                ))
                self.stats['concepts_found'][concept_name] += 1
            
            # Recherche via synonymes si disponibles
            if hasattr(concept_obj, 'synonyms'):
                for synonym in concept_obj.synonyms:
                    if synonym.lower() in text_lower:
                        position = text_lower.find(synonym.lower())
                        matches.append(ConceptMatch(
                            concept=concept_name,
                            confidence=0.8,
                            source='direct',
                            evidence=[synonym.lower()],
                            position=position,
                            related_concepts=[]
                        ))
                        self.stats['concepts_found'][concept_name] += 1
        
        return matches
    
    def _validate_and_score_concepts(self, text: str, concept_matches: List[ConceptMatch]) -> List[ConceptMatch]:
        """Validation et scoring avancé des concepts détectés"""
        validated = []
        text_words = set(text.lower().split())
        
        for match in concept_matches:
            # Score de base
            base_score = match.confidence
            
            # Facteurs d'amélioration du score
            
            # 1. Multiplicité des preuves
            evidence_bonus = min(len(match.evidence) * 0.1, 0.3)
            
            # 2. Position dans le texte (début = plus important)
            if match.position >= 0:
                position_bonus = max(0, 0.2 - (match.position / len(text)) * 0.2)
            else:
                position_bonus = 0
            
            # 3. Contexte philosophique
            context_bonus = 0
            philosophical_indicators = [
                'philosophie', 'philosophique', 'concept', 'notion', 'idée',
                'principe', 'théorie', 'doctrine', 'pensée', 'réflexion'
            ]
            for indicator in philosophical_indicators:
                if indicator in text.lower():
                    context_bonus += 0.05
            context_bonus = min(context_bonus, 0.2)
            
            # 4. Cohérence avec autres concepts détectés
            coherence_bonus = 0
            other_concepts = [m.concept for m in concept_matches if m != match]
            if self._concepts_are_coherent(match.concept, other_concepts):
                coherence_bonus = 0.15
            
            # Score final
            final_score = min(base_score + evidence_bonus + position_bonus + context_bonus + coherence_bonus, 1.0)
            
            # Filtrage par seuil de qualité
            if final_score >= 0.4:  # Seuil de validation
                match.confidence = final_score
                validated.append(match)
        
        return validated
    
    def _concepts_are_coherent(self, concept: str, other_concepts: List[str]) -> bool:
        """Vérifie la cohérence philosophique entre concepts"""
        if not other_concepts:
            return False
        
        # Clusters de concepts cohérents
        coherent_clusters = [
            {'VÉRITÉ', 'CONNAISSANCE', 'CROYANCE', 'JUSTIFICATION'},
            {'BIEN', 'MAL', 'JUSTICE', 'VERTU', 'MORALE'},
            {'ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ'},
            {'BEAUTÉ', 'ART', 'HARMONIE', 'CRÉATION'},
            {'LIBERTÉ', 'RESPONSABILITÉ', 'CHOIX', 'VOLONTÉ'}
        ]
        
        for cluster in coherent_clusters:
            if concept in cluster:
                return any(other_concept in cluster for other_concept in other_concepts)
        
        return False
    
    def _enrich_with_llm_inference(self, text: str, validated_concepts: List[ConceptMatch]) -> List[ConceptMatch]:
        """Enrichissement via inférence LLaMA avancée"""
        if not validated_concepts:
            return []
        
        try:
            self.stats['llm_calls'] += 1
            
            # Construction du prompt d'inférence
            detected_concepts = [m.concept for m in validated_concepts]
            prompt = f"""Analyse ce texte philosophique et identifie les concepts philosophiques implicites non mentionnés directement.

TEXTE: "{text}"

CONCEPTS DÉJÀ DÉTECTÉS: {', '.join(detected_concepts)}

CONCEPTS PHILOSOPHIQUES POSSIBLES: {', '.join(self.ontology.concepts.keys())}

Identifie jusqu'à 3 concepts philosophiques implicites présents dans ce texte mais non listés dans les concepts déjà détectés.

Réponds au format JSON:
{{"concepts_implicites": ["CONCEPT1", "CONCEPT2"], "justifications": ["raison1", "raison2"]}}"""
            
            response = self.llm.generate_text(prompt, max_tokens=200, temperature=0.3)
            
            # Parsing de la réponse
            inferred_matches = self._parse_llm_inference_response(response, detected_concepts)
            
            logger.debug(f"🧠 LLaMA inférence: {[m.concept for m in inferred_matches]}")
            return inferred_matches
            
        except Exception as e:
            logger.warning(f"Erreur enrichissement LLaMA: {e}")
            return []
    
    def _parse_llm_inference_response(self, response: str, existing_concepts: List[str]) -> List[ConceptMatch]:
        """Parse la réponse d'inférence de LLaMA"""
        matches = []
        
        try:
            # Tentative de parsing JSON
            if '{' in response and '}' in response:
                json_part = response[response.find('{'):response.rfind('}')+1]
                data = json.loads(json_part)
                
                concepts = data.get('concepts_implicites', [])
                justifications = data.get('justifications', [])
                
                for i, concept in enumerate(concepts):
                    if concept in self.ontology.concepts and concept not in existing_concepts:
                        justification = justifications[i] if i < len(justifications) else "Inférence LLaMA"
                        
                        matches.append(ConceptMatch(
                            concept=concept,
                            confidence=0.6,  # Confiance modérée pour inférence
                            source='llm_inference',
                            evidence=[justification],
                            position=-1,
                            related_concepts=existing_concepts
                        ))
            
            # Fallback: recherche de concepts dans la réponse brute
            if not matches:
                for concept_name in self.ontology.concepts.keys():
                    if concept_name in response and concept_name not in existing_concepts:
                        matches.append(ConceptMatch(
                            concept=concept_name,
                            confidence=0.5,
                            source='llm_inference',
                            evidence=[f"Mentionné dans réponse LLaMA"],
                            position=-1,
                            related_concepts=existing_concepts
                        ))
                        if len(matches) >= 3:  # Limite
                            break
            
        except Exception as e:
            logger.debug(f"Erreur parsing LLaMA response: {e}")
        
        return matches
    
    def _consolidate_concepts(self, concept_matches: List[ConceptMatch], max_concepts: int) -> List[ConceptMatch]:
        """Consolidation et déduplication des concepts"""
        
        # Regroupement par concept
        concept_groups = defaultdict(list)
        for match in concept_matches:
            concept_groups[match.concept].append(match)
        
        # Consolidation par concept
        consolidated = []
        for concept_name, matches in concept_groups.items():
            if len(matches) == 1:
                consolidated.append(matches[0])
            else:
                # Fusion des matches multiples
                best_match = max(matches, key=lambda m: m.confidence)
                
                # Combinaison des preuves
                all_evidence = []
                for match in matches:
                    all_evidence.extend(match.evidence)
                
                # Confiance consolidée (moyenne pondérée)
                total_confidence = sum(m.confidence for m in matches) / len(matches)
                # Bonus pour multiplicité
                total_confidence = min(total_confidence + 0.1, 1.0)
                
                consolidated_match = ConceptMatch(
                    concept=concept_name,
                    confidence=total_confidence,
                    source=f"consolidated({len(matches)})",
                    evidence=list(set(all_evidence)),
                    position=best_match.position,
                    related_concepts=best_match.related_concepts
                )
                consolidated.append(consolidated_match)
        
        # Tri par confiance et limitation
        consolidated.sort(key=lambda m: m.confidence, reverse=True)
        return consolidated[:max_concepts]
    
    def _build_extraction_result(self, text: str, final_concepts: List[ConceptMatch], 
                               relations: List[ConceptualRelation]) -> Dict[str, Any]:
        """Construction du résultat final d'extraction"""
        
        # Concepts détectés
        concepts_detected = [match.concept for match in final_concepts]
        
        # Confiance globale (moyenne pondérée)
        if final_concepts:
            total_weighted_confidence = sum(m.confidence for m in final_concepts)
            global_confidence = total_weighted_confidence / len(final_concepts)
        else:
            global_confidence = 0.0
        
        # Relations détectées
        relations_dict = []
        for relation in relations:
            if relation.from_concept in concepts_detected and relation.to_concept in concepts_detected:
                relations_dict.append({
                    'from': relation.from_concept,
                    'to': relation.to_concept,
                    'relation': relation.relation_type,
                    'strength': relation.strength,
                    'evidence': relation.evidence
                })
        
        # Analyse des sources
        source_analysis = defaultdict(int)
        for match in final_concepts:
            source_analysis[match.source] += 1
        
        # Métadonnées d'extraction
        extraction_metadata = {
            'extraction_method': 'llm_ultra_advanced',
            'total_candidates': len(final_concepts),
            'sources_used': dict(source_analysis),
            'relations_found': len(relations_dict),
            'processing_stats': {
                'cache_hit': self.stats['cache_hits'] > 0,
                'llm_inference_used': any(m.source == 'llm_inference' for m in final_concepts)
            }
        }
        
        result = {
            'concepts_detected': concepts_detected,
            'enhanced_confidence': global_confidence,
            'confidence': global_confidence,  # Rétrocompatibilité
            'relations_implied': relations_dict,
            'conceptual_paths': self._generate_conceptual_paths(final_concepts),
            'extraction_details': {
                'concept_matches': [match.__dict__ for match in final_concepts],
                'metadata': extraction_metadata
            }
        }
        
        return result
    
    def _generate_conceptual_paths(self, concept_matches: List[ConceptMatch]) -> List[Dict[str, Any]]:
        """Génère des chemins conceptuels pour le raisonnement LCM"""
        paths = []
        
        # Groupe les concepts par confiance
        high_confidence = [m for m in concept_matches if m.confidence > 0.7]
        
        if len(high_confidence) >= 2:
            # Crée des chemins basés sur les concepts haute confiance
            for i, match in enumerate(high_confidence[:3]):  # Max 3 chemins
                path = {
                    'start_concept': match.concept,
                    'reasoning_path': [match.concept] + match.related_concepts[:2],
                    'confidence': match.confidence,
                    'source': match.source
                }
                paths.append(path)
        
        return paths
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation"""
        return {
            'total_extractions': self.stats['total_extractions'],
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['total_extractions'], 1),
            'llm_calls': self.stats['llm_calls'],
            'most_found_concepts': dict(sorted(
                self.stats['concepts_found'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            'cache_size': len(self._analysis_cache)
        }
    
    def clear_cache(self):
        """Vide le cache d'analyse"""
        with self._cache_lock:
            self._analysis_cache.clear()
        logger.info("🗑️ Cache LLM Extractor vidé")
        
    def extract_concepts_fast(self, text: str, max_concepts: int = 4) -> Dict[str, Any]:
        """Version ultra-rapide de l'extraction (pour mode speed)"""
        
        # Cache check rapide
        text_hash = hash(text.lower().strip())
        with self._cache_lock:
            if text_hash in self._analysis_cache:
                return self._analysis_cache[text_hash]
        
        logger.debug(f"🚀 Extraction LLM TURBO: {text[:30]}...")
        
        start_time = time.time()
        
        # Extraction directe uniquement (pas d'inférence LLaMA)
        direct_concepts = self._extract_direct_concepts(text)
        
        # Validation rapide (seuil plus élevé)
        validated = [m for m in direct_concepts if m.confidence >= 0.6]
        
        # Consolidation rapide (prend les meilleurs)
        final_concepts = self._consolidate_concepts(validated, max_concepts)
        
        # Résultat simplifié
        result = {
            'concepts_detected': [m.concept for m in final_concepts],
            'enhanced_confidence': sum(m.confidence for m in final_concepts) / max(len(final_concepts), 1),
            'confidence': sum(m.confidence for m in final_concepts) / max(len(final_concepts), 1),
            'relations_implied': [],  # Pas de relations en mode rapide
            'conceptual_paths': [],
            'extraction_details': {
                'metadata': {'extraction_method': 'llm_turbo'}
            }
        }
        
        # Cache
        with self._cache_lock:
            self._analysis_cache[text_hash] = result
        
        duration = time.time() - start_time
        logger.debug(f"🚀 Extraction turbo terminée: {len(final_concepts)} concepts ({duration:.2f}s)")
        
        return result