"""
Tokenizer Philosophique Ultra-Avancé pour SophIA
Analyse linguistique spécialisée en philosophie
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
import unicodedata

logger = logging.getLogger(__name__)

class PhilosophicalCategory(Enum):
    """Catégories de termes philosophiques"""
    EPISTEMOLOGICAL = "épistémologique"
    ETHICAL = "éthique"
    METAPHYSICAL = "métaphysique"
    AESTHETIC = "esthétique"
    LOGICAL = "logique"
    POLITICAL = "politique"
    EXISTENTIAL = "existentiel"
    PHENOMENOLOGICAL = "phénoménologique"

@dataclass
class PhilosophicalTerm:
    """Représente un terme philosophique identifié"""
    term: str
    category: PhilosophicalCategory
    weight: float
    position: int
    context: str
    confidence: float

@dataclass
class LinguisticPattern:
    """Pattern linguistique philosophique"""
    pattern: str
    category: PhilosophicalCategory
    weight: float
    description: str

class PhilosophicalTokenizer:
    """
    Tokenizer ultra-spécialisé pour l'analyse philosophique
    - Détection de termes techniques philosophiques
    - Analyse de complexité conceptuelle
    - Identification de structures argumentatives
    - Mesure de profondeur philosophique
    """
    
    def __init__(self):
        logger.info("📝 Initialisation du Tokenizer Philosophique Ultra-Avancé")
        
        # Dictionnaire des termes philosophiques par catégorie
        self.philosophical_lexicon = self._build_philosophical_lexicon()
        
        # Patterns linguistiques philosophiques
        self.linguistic_patterns = self._build_linguistic_patterns()
        
        # Connecteurs argumentatifs
        self.argumentative_connectors = self._build_argumentative_connectors()
        
        # Marqueurs de complexité
        self.complexity_markers = self._build_complexity_markers()
        
        # Cache pour optimisation
        self._analysis_cache = {}
        
        # Statistiques
        self.stats = {
            'texts_analyzed': 0,
            'terms_found': defaultdict(int),
            'categories_detected': defaultdict(int)
        }
        
        logger.info(f"📚 Lexique: {sum(len(terms) for terms in self.philosophical_lexicon.values())} termes")
        logger.info(f"🔍 Patterns: {len(self.linguistic_patterns)} patterns linguistiques")
    
    def _build_philosophical_lexicon(self) -> Dict[PhilosophicalCategory, Dict[str, float]]:
        """Construit le lexique philosophique spécialisé"""
        
        return {
            PhilosophicalCategory.EPISTEMOLOGICAL: {
                # Termes de base
                'connaissance': 1.0, 'savoir': 0.9, 'vérité': 1.0, 'croyance': 0.9,
                'justification': 0.9, 'preuve': 0.8, 'évidence': 0.8, 'certitude': 0.9,
                'doute': 0.8, 'scepticisme': 0.9, 'empirisme': 0.9, 'rationalisme': 0.9,
                
                # Termes avancés
                'épistémologie': 1.0, 'gnoséologie': 0.9, 'véracité': 0.8,
                'falsifiabilité': 0.9, 'corroboration': 0.8, 'induction': 0.8,
                'déduction': 0.8, 'abduction': 0.7, 'paradigme': 0.8,
                
                # Verbes épistémologiques
                'connaître': 0.7, 'savoir': 0.7, 'croire': 0.6, 'douter': 0.7,
                'vérifier': 0.7, 'prouver': 0.8, 'démontrer': 0.8, 'réfuter': 0.8
            },
            
            PhilosophicalCategory.ETHICAL: {
                # Termes fondamentaux
                'bien': 1.0, 'mal': 1.0, 'bon': 0.8, 'mauvais': 0.8,
                'justice': 1.0, 'injustice': 0.9, 'équité': 0.9, 'inéquité': 0.8,
                'vertu': 0.9, 'vice': 0.8, 'morale': 1.0, 'éthique': 1.0,
                
                # Concepts éthiques spécialisés
                'devoir': 0.9, 'obligation': 0.8, 'responsabilité': 0.9,
                'culpabilité': 0.8, 'innocence': 0.7, 'mérite': 0.7,
                'dignité': 0.8, 'respect': 0.7, 'altruisme': 0.8, 'égoïsme': 0.8,
                
                # Systèmes éthiques
                'utilitarisme': 0.9, 'déontologie': 0.9, 'conséquentialisme': 0.9,
                'contractualisme': 0.8, 'virtue ethics': 0.8, 'éthique appliquée': 0.8,
                
                # Valeurs morales
                'honnêteté': 0.7, 'courage': 0.7, 'compassion': 0.7, 'tolérance': 0.7,
                'fidélité': 0.6, 'loyauté': 0.6, 'générosité': 0.6, 'prudence': 0.7
            },
            
            PhilosophicalCategory.METAPHYSICAL: {
                # Concepts ontologiques
                'être': 1.0, 'existence': 1.0, 'essence': 1.0, 'substance': 0.9,
                'réalité': 1.0, 'apparence': 0.8, 'phénomène': 0.8, 'noumène': 0.9,
                'identité': 0.8, 'différence': 0.7, 'unité': 0.7, 'multiplicité': 0.7,
                
                # Concepts temporels et spatiaux
                'temps': 0.9, 'espace': 0.9, 'éternité': 0.8, 'temporalité': 0.8,
                'durée': 0.7, 'instant': 0.6, 'permanence': 0.7, 'changement': 0.8,
                'devenir': 0.8, 'mouvement': 0.7, 'immobilité': 0.6,
                
                # Causalité et nécessité
                'cause': 0.8, 'effet': 0.8, 'causalité': 0.9, 'déterminisme': 0.9,
                'hasard': 0.7, 'contingence': 0.8, 'nécessité': 0.9, 'possibilité': 0.8,
                'actualité': 0.8, 'potentialité': 0.8,
                
                # Métaphysique spécialisée
                'ontologie': 1.0, 'cosmologie': 0.8, 'théologie': 0.8,
                'monisme': 0.8, 'dualisme': 0.8, 'pluralisme': 0.8
            },
            
            PhilosophicalCategory.AESTHETIC: {
                # Concepts esthétiques fondamentaux
                'beauté': 1.0, 'laid': 0.8, 'beau': 0.9, 'esthétique': 1.0,
                'art': 0.9, 'artistique': 0.8, 'création': 0.8, 'créativité': 0.7,
                'œuvre': 0.8, 'style': 0.7, 'forme': 0.7, 'contenu': 0.6,
                
                # Qualités esthétiques
                'sublime': 0.9, 'gracieux': 0.7, 'élégant': 0.6, 'harmonieux': 0.8,
                'proportionné': 0.7, 'équilibré': 0.7, 'symétrique': 0.6,
                'expressif': 0.7, 'significatif': 0.6,
                
                # Jugement esthétique
                'goût': 0.8, 'jugement': 0.7, 'appréciation': 0.6, 'critique': 0.7,
                'interprétation': 0.7, 'réception': 0.6, 'contemplation': 0.8,
                
                # Genres artistiques
                'poésie': 0.6, 'musique': 0.6, 'peinture': 0.6, 'sculpture': 0.6,
                'architecture': 0.6, 'littérature': 0.6, 'théâtre': 0.6
            },
            
            PhilosophicalCategory.LOGICAL: {
                # Logique formelle
                'logique': 1.0, 'raisonnement': 0.9, 'argument': 0.9, 'preuve': 0.8,
                'démonstration': 0.8, 'inférence': 0.8, 'déduction': 0.8, 'induction': 0.8,
                'syllogisme': 0.9, 'premise': 0.8, 'conclusion': 0.8,
                
                # Validité et vérité
                'validité': 0.9, 'invalide': 0.8, 'cohérence': 0.8, 'contradiction': 0.9,
                'consistance': 0.8, 'inconsistance': 0.8, 'paradoxe': 0.9,
                
                # Fallacies et erreurs
                'sophisme': 0.8, 'paralogisme': 0.8, 'fallacie': 0.8,
                'pétition de principe': 0.7, 'ad hominem': 0.7, 'généralisation': 0.6,
                
                # Modalités logiques
                'nécessaire': 0.8, 'contingent': 0.8, 'impossible': 0.7, 'possible': 0.7,
                'probable': 0.6, 'certain': 0.7, 'incertain': 0.6
            },
            
            PhilosophicalCategory.EXISTENTIAL: {
                # Existence et condition humaine
                'existence': 1.0, 'existant': 0.8, 'inexistant': 0.7, 'néant': 0.9,
                'absurde': 0.9, 'absurdité': 0.9, 'angoisse': 0.8, 'anxiété': 0.7,
                'liberté': 1.0, 'déterminisme': 0.9, 'libre arbitre': 1.0,
                
                # Concepts existentialistes
                'authenticité': 0.9, 'mauvaise foi': 0.9, 'projet': 0.7, 'situation': 0.6,
                'factricité': 0.8, 'transcendance': 0.9, 'immanence': 0.8,
                'être-pour-soi': 0.9, 'être-en-soi': 0.9, 'être-pour-autrui': 0.8,
                
                # Temporalité existentielle
                'mortalité': 0.8, 'finitude': 0.8, 'immortalité': 0.7, 'éternité': 0.7,
                'présent': 0.6, 'passé': 0.6, 'futur': 0.6, 'devenir': 0.7,
                
                # Philosophes existentialistes
                'existentialisme': 1.0, 'phénoménologie': 0.9, 'herméneutique': 0.8
            }
        }
    
    def _build_linguistic_patterns(self) -> List[LinguisticPattern]:
        """Construit les patterns linguistiques philosophiques"""
        
        return [
            # Patterns épistémologiques - CORRIGÉS
            LinguisticPattern(
                r'\bqu[\'"]?est-ce que\b.*\?',  # CORRECTION: [\'"] au lieu de [\'']
                PhilosophicalCategory.EPISTEMOLOGICAL,
                0.8,
                "Question philosophique directe"
            ),
            LinguisticPattern(
                r'\b(comment|pourquoi|dans quelle mesure)\b.*\?',
                PhilosophicalCategory.EPISTEMOLOGICAL,
                0.7,
                "Question philosophique analytique"
            ),
            LinguisticPattern(
                r'\b(il est possible que|il se peut que|peut-être)\b',
                PhilosophicalCategory.EPISTEMOLOGICAL,
                0.6,
                "Expression d'incertitude épistémique"
            ),
            
            # Patterns éthiques
            LinguisticPattern(
                r'\b(doit|devrait|faut-il|est-il juste de)\b',
                PhilosophicalCategory.ETHICAL,
                0.8,
                "Obligation morale"
            ),
            LinguisticPattern(
                r'\b(bien|mal|juste|injuste|moral|immoral)\b',
                PhilosophicalCategory.ETHICAL,
                0.7,
                "Évaluation morale"
            ),
            
            # Patterns métaphysiques - CORRIGÉS
            LinguisticPattern(
                r'\b(essence|nature de|qu[\'"]?est-ce que l[\'"]?être)\b',  # CORRECTION
                PhilosophicalCategory.METAPHYSICAL,
                0.9,
                "Question ontologique"
            ),
            LinguisticPattern(
                r'\b(existe|inexistant|réel|irréel)\b',
                PhilosophicalCategory.METAPHYSICAL,
                0.7,
                "Question d'existence"
            ),
            
            # Patterns logiques
            LinguisticPattern(
                r'\b(donc|par conséquent|ainsi|en effet|cependant|néanmoins)\b',
                PhilosophicalCategory.LOGICAL,
                0.6,
                "Connecteur logique"
            ),
            LinguisticPattern(
                r'\b(si.*alors|soit.*soit|ou bien.*ou bien)\b',
                PhilosophicalCategory.LOGICAL,
                0.8,
                "Structure logique conditionnelle"
            ),
            
            # Patterns esthétiques
            LinguisticPattern(
                r'\b(beau|sublime|gracieux|harmonieux|élégant)\b',
                PhilosophicalCategory.AESTHETIC,
                0.7,
                "Qualification esthétique"
            ),
            
            # Patterns existentiels
            LinguisticPattern(
                r'\b(sens de|signification de|absurde|absurdité)\b',
                PhilosophicalCategory.EXISTENTIAL,
                0.8,
                "Question existentielle"
            )
        ]
    
    def _build_argumentative_connectors(self) -> Dict[str, Dict[str, float]]:
        """Construit la liste des connecteurs argumentatifs"""
        
        return {
            'introduction': {
                'tout d\'abord': 0.8, 'premièrement': 0.8, 'en premier lieu': 0.8,
                'pour commencer': 0.7, 'avant tout': 0.7, 'initialement': 0.6
            },
            'développement': { 
                'ensuite': 0.7, 'puis': 0.6, 'deuxièmement': 0.8, 'par ailleurs': 0.8,
                'de plus': 0.6, 'en outre': 0.7, 'également': 0.6, 'aussi': 0.5
            },
            'opposition': {
                'cependant': 0.8, 'néanmoins': 0.8, 'toutefois': 0.8, 'pourtant': 0.7,
                'mais': 0.6, 'or': 0.7, 'en revanche': 0.8, 'au contraire': 0.8
            },
            'concession': {
                'certes': 0.8, 'il est vrai que': 0.8, 'bien que': 0.7, 'quoique': 0.7,
                'malgré': 0.6, 'en dépit de': 0.7, 'même si': 0.6
            },
            'conséquence': {
                'donc': 0.8, 'par conséquent': 0.9, 'ainsi': 0.7, 'c\'est pourquoi': 0.8,
                'de ce fait': 0.7, 'dès lors': 0.7, 'en conséquence': 0.8
            },
            'conclusion': {
                'enfin': 0.7, 'finalement': 0.7, 'en conclusion': 0.9, 'pour conclure': 0.9,
                'en définitive': 0.8, 'au final': 0.6, 'en somme': 0.8
            }
        }
    
    def _build_complexity_markers(self) -> Dict[str, float]:
        """Construit les marqueurs de complexité philosophique"""
        
        return {
            # Marqueurs de questionnement profond
            'paradoxe': 1.0, 'dilemme': 0.9, 'aporie': 1.0, 'antinomie': 0.9,
            'contradiction': 0.8, 'tension': 0.7, 'ambiguïté': 0.7,
            
            # Marqueurs métaphysiques
            'transcendant': 0.9, 'immanent': 0.9, 'absolu': 0.8, 'relatif': 0.7,
            'infini': 0.8, 'éternel': 0.8, 'temporel': 0.7, 'spatial': 0.6,
            
            # Marqueurs épistémologiques complexes
            'dialectique': 0.9, 'herméneutique': 0.9, 'phénoménologique': 1.0,
            'analytique': 0.7, 'synthétique': 0.7, 'a priori': 0.8, 'a posteriori': 0.8,
            
            # Concepts techniques
            'ontologique': 0.9, 'épistémologique': 0.9, 'axiologique': 0.8,
            'téléologique': 0.8, 'déontologique': 0.8, 'conséquentialiste': 0.8,
            
            # Modalités philosophiques
            'nécessairement': 0.8, 'contingent': 0.8, 'possible': 0.6, 'impossible': 0.7,
            'vraisemblable': 0.7, 'plausible': 0.6, 'probable': 0.6
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenisation philosophique avancée"""
        
        # Normalisation du texte
        normalized_text = self._normalize_text(text)
        
        # Tokenisation de base
        basic_tokens = re.findall(r'\b\w+\b|[^\w\s]', normalized_text, re.UNICODE)
        
        # Détection de phrases philosophiques composées
        compound_terms = self._detect_compound_philosophical_terms(normalized_text)
        
        # Fusion des tokens
        final_tokens = self._merge_compound_tokens(basic_tokens, compound_terms)
        
        return final_tokens
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour l'analyse philosophique"""
        
        # Suppression des accents pour certaines analyses
        normalized = unicodedata.normalize('NFD', text)
        
        # Conversion en minuscules
        normalized = normalized.lower()
        
        # Nettoyage des caractères spéciaux
        normalized = re.sub(r'[''`]', "'", normalized)
        normalized = re.sub(r'[""«»]', '"', normalized)
        
        return normalized
    
    def _detect_compound_philosophical_terms(self, text: str) -> List[Tuple[str, int, int]]:
        """Détecte les termes philosophiques composés"""
        
        compound_terms = [
            'libre arbitre', 'a priori', 'a posteriori', 'être-pour-soi', 'être-en-soi',
            'mauvaise foi', 'bonne foi', 'sens commun', 'raison pure', 'raison pratique',
            'impératif catégorique', 'volonté générale', 'contrat social', 'état de nature',
            'chose en soi', 'pour soi', 'en soi', 'être au monde', 'être-là',
            'pétition de principe', 'ad hominem', 'post hoc', 'reductio ad absurdum'
        ]
        
        found_compounds = []
        for term in compound_terms:
            for match in re.finditer(re.escape(term), text, re.IGNORECASE):
                found_compounds.append((term, match.start(), match.end()))
        
        return found_compounds
    
    def _merge_compound_tokens(self, basic_tokens: List[str], 
                             compound_terms: List[Tuple[str, int, int]]) -> List[str]:
        """Fusionne les tokens en tenant compte des termes composés"""
        
        # Pour simplicité, retourne les tokens de base
        # Une implémentation complète gérerait la fusion
        return basic_tokens
    
    def extract_philosophical_terms(self, text: str) -> List[PhilosophicalTerm]:
        """Extrait les termes philosophiques avec catégorisation - VERSION CORRIGÉE"""
        
        # Cache check
        text_hash = hash(text.lower().strip())
        if text_hash in self._analysis_cache:
            return self._analysis_cache[text_hash]
        
        philosophical_terms = []
        text_lower = text.lower()
        
        # Extraction par catégorie avec gestion d'erreur
        for category, terms_dict in self.philosophical_lexicon.items():
            for term, weight in terms_dict.items():
                try:
                    # Recherche du terme dans le texte
                    pattern = r'\b' + re.escape(term) + r'\b'
                    for match in re.finditer(pattern, text_lower):
                        # Calcul de confiance basé sur contexte - CORRIGÉ
                        context = self._extract_context_safe(text, match.start(), match.end())
                        confidence = self._calculate_term_confidence(term, context, weight)
                        
                        philosophical_terms.append(PhilosophicalTerm(
                            term=term,
                            category=category,
                            weight=weight,
                            position=match.start(),
                            context=context,
                            confidence=confidence
                        ))
                        
                        # Statistiques
                        self.stats['terms_found'][term] += 1
                        self.stats['categories_detected'][category.value] += 1
                        
                except Exception as e:
                    # Continue en cas d'erreur sur un terme spécifique
                    logger.debug(f"Erreur extraction terme '{term}': {e}")
                    continue
        
        # Tri par confiance
        philosophical_terms.sort(key=lambda t: t.confidence, reverse=True)
        
        # Cache
        self._analysis_cache[text_hash] = philosophical_terms
        
        return philosophical_terms

    def _extract_context_safe(self, text: str, start: int, end: int, window: int = 30) -> str:
        """Extrait le contexte de manière sécurisée - VERSION CORRIGÉE"""
        
        try:
            # Sécurisation des indices
            text_length = len(text)
            
            context_start = max(0, start - window)
            context_end = min(text_length, end + window)
            
            # Vérification des limites
            if context_start >= text_length or context_end <= 0:
                return text[max(0, start):min(text_length, end)]
            
            context = text[context_start:context_end]
            
            # Validation du contexte
            if not context or len(context) == 0:
                return text[max(0, start):min(text_length, end)]
            
            return context
            
        except Exception as e:
            logger.debug(f"Erreur extraction contexte: {e}")
            # Fallback ultra-sécurisé
            try:
                return text[start:end] if start < len(text) and end <= len(text) else ""
            except:
                return ""
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """Extrait le contexte autour d'un terme"""
        
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        return text[context_start:context_end]
    
    def _calculate_term_confidence(self, term: str, context: str, base_weight: float) -> float:
        """Calcule la confiance d'un terme philosophique en contexte"""
        
        confidence = base_weight
        context_lower = context.lower()
        
        # Bonus pour contexte philosophique
        philosophical_indicators = [
            'philosophie', 'philosophique', 'pensée', 'réflexion', 'concept',
            'notion', 'idée', 'théorie', 'doctrine', 'système'
        ]
        
        for indicator in philosophical_indicators:
            if indicator in context_lower:
                confidence += 0.1
        
        # Bonus pour questions philosophiques
        if '?' in context or any(q in context_lower for q in ['pourquoi', 'comment', 'qu\'est-ce']):
            confidence += 0.1
        
        # Malus pour contexte non-philosophique
        mundane_indicators = [
            'aujourd\'hui', 'hier', 'demain', 'achat', 'vente', 'prix',
            'restaurant', 'magasin', 'voiture', 'téléphone'
        ]
        
        for indicator in mundane_indicators:
            if indicator in context_lower:
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def calculate_complexity(self, text: str) -> float:
        """Calcule le score de complexité philosophique"""
        
        if not text.strip():
            return 0.0
        
        complexity_score = 0.0
        text_lower = text.lower()
        word_count = len(text.split())
        
        # 1. Complexité lexicale (termes philosophiques)
        philosophical_terms = self.extract_philosophical_terms(text)
        if philosophical_terms:
            lexical_complexity = sum(term.weight * term.confidence for term in philosophical_terms)
            lexical_complexity = lexical_complexity / word_count  # Normalisation
            complexity_score += lexical_complexity * 0.4
        
        # 2. Complexité structurelle (connecteurs argumentatifs)
        structural_complexity = 0.0
        total_connectors = 0
        
        for category, connectors in self.argumentative_connectors.items():
            for connector, weight in connectors.items():
                if connector in text_lower:
                    structural_complexity += weight
                    total_connectors += 1
        
        if total_connectors > 0:
            structural_complexity = structural_complexity / word_count * 10  # Normalisation
            complexity_score += structural_complexity * 0.3
        
        # 3. Complexité conceptuelle (marqueurs spéciaux)
        conceptual_complexity = 0.0
        
        for marker, weight in self.complexity_markers.items():
            if marker in text_lower:
                conceptual_complexity += weight
        
        conceptual_complexity = conceptual_complexity / word_count * 10  # Normalisation
        complexity_score += conceptual_complexity * 0.3
        
        # 4. Longueur et structure des phrases
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_complexity = min(avg_sentence_length / 20, 1.0)  # Normalisation sur 20 mots
        complexity_score += length_complexity * 0.1
        
        # Score final
        final_score = min(complexity_score, 1.0)
        
        return final_score
    
    def analyze_argumentative_structure(self, text: str) -> Dict[str, Any]:
        """Analyse la structure argumentative du texte"""
        
        structure_analysis = {
            'has_introduction': False,
            'has_development': False,
            'has_opposition': False,
            'has_conclusion': False,
            'connector_count': 0,
            'argumentative_strength': 0.0,
            'connectors_found': []
        }
        
        text_lower = text.lower()
        
        for category, connectors in self.argumentative_connectors.items():
            category_found = False
            
            for connector, weight in connectors.items():
                if connector in text_lower:
                    structure_analysis['connectors_found'].append({
                        'connector': connector,
                        'category': category,
                        'weight': weight
                    })
                    structure_analysis['connector_count'] += 1
                    
                    if not category_found:
                        structure_analysis[f'has_{category}'] = True
                        category_found = True
        
        # Calcul de la force argumentative
        if structure_analysis['connector_count'] > 0:
            total_weight = sum(c['weight'] for c in structure_analysis['connectors_found'])
            structure_analysis['argumentative_strength'] = min(total_weight / 5, 1.0)
        
        return structure_analysis
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Génère des statistiques complètes sur le texte"""
        
        self.stats['texts_analyzed'] += 1
        
        tokens = self.tokenize(text)
        philosophical_terms = self.extract_philosophical_terms(text)
        complexity = self.calculate_complexity(text)
        argumentative_structure = self.analyze_argumentative_structure(text)
        
        # Répartition par catégorie
        category_distribution = defaultdict(int)
        for term in philosophical_terms:
            category_distribution[term.category.value] += 1
        
        # Termes les plus significatifs
        top_terms = sorted(philosophical_terms, key=lambda t: t.confidence, reverse=True)[:5]
        
        return {
            'basic_stats': {
                'character_count': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(text.split('.')),
                'token_count': len(tokens)
            },
            'philosophical_analysis': {
                'philosophical_terms_count': len(philosophical_terms),
                'complexity_score': complexity,
                'category_distribution': dict(category_distribution),
                'top_terms': [
                    {
                        'term': t.term,
                        'category': t.category.value,
                        'confidence': t.confidence
                    } for t in top_terms
                ]
            },
            'argumentative_analysis': argumentative_structure,
            'overall_assessment': self._generate_overall_assessment(
                complexity, len(philosophical_terms), argumentative_structure
            )
        }
    
    def _generate_overall_assessment(self, complexity: float, term_count: int, 
                                   structure: Dict[str, Any]) -> Dict[str, str]:
        """Génère une évaluation globale du texte"""
        
        # Évaluation de complexité
        if complexity >= 0.8:
            complexity_level = "Très élevée"
        elif complexity >= 0.6:
            complexity_level = "Élevée"
        elif complexity >= 0.4:
            complexity_level = "Modérée"
        elif complexity >= 0.2:
            complexity_level = "Faible"
        else:
            complexity_level = "Très faible"
        
        # Évaluation philosophique
        if term_count >= 10:
            philosophical_level = "Texte hautement philosophique"
        elif term_count >= 5:
            philosophical_level = "Texte philosophique"
        elif term_count >= 2:
            philosophical_level = "Texte avec éléments philosophiques"
        else:
            philosophical_level = "Texte peu philosophique"
        
        # Évaluation argumentative
        if structure['argumentative_strength'] >= 0.7:
            argumentative_level = "Structure argumentative forte"
        elif structure['argumentative_strength'] >= 0.4:
            argumentative_level = "Structure argumentative modérée"
        else:
            argumentative_level = "Structure argumentative faible"
        
        return {
            'complexity_assessment': complexity_level,
            'philosophical_assessment': philosophical_level,
            'argumentative_assessment': argumentative_level
        }
    
    def get_tokenizer_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du tokenizer"""
        
        return {
            'texts_analyzed': self.stats['texts_analyzed'],
            'most_frequent_terms': dict(sorted(
                self.stats['terms_found'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            'category_usage': dict(self.stats['categories_detected']),
            'lexicon_size': {
                category.value: len(terms) 
                for category, terms in self.philosophical_lexicon.items()
            },
            'cache_size': len(self._analysis_cache)
        }
    
    def clear_cache(self):
        """Vide le cache d'analyse"""
        self._analysis_cache.clear()
        logger.info("🗑️ Cache Tokenizer vidé")