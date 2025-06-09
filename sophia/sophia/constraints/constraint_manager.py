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
        logger.info("Initialisation du PhilosophicalConstraintManager")
        self.ontology = ontology
        self.llm = llm_interface
        self.constraints = self._build_default_constraints()
        logger.debug(f"Contraintes par défaut chargées: {[c.name for c in self.constraints]}")
        
        # Clusters philosophiques enrichis
        self.philosophical_clusters = self._build_enhanced_philosophical_clusters()
        logger.debug(f"Clusters philosophiques enrichis: {[c['name'] for c in self.philosophical_clusters]}")
        
        # Cache pour éviter les requêtes répétées
        self._evaluation_cache = {}
        logger.info("Cache d'évaluation initialisé")
        
    def _build_enhanced_philosophical_clusters(self) -> List[Dict[str, Any]]:
        logger.info("Construction des clusters philosophiques enrichis")
        """Construit des clusters philosophiques enrichis"""
        return [
            {
                'name': 'Épistémologie',
                'concepts': {
                    'VÉRITÉ', 'CONNAISSANCE', 'CROYANCE', 'DOUTE', 'CERTITUDE', 'JUSTIFICATION',
                    'SAVOIR', 'PERCEPTION', 'RATIONALITÉ', 'SCEPTICISME', 'EPISTÉMOLOGIE', 'ERREUR',
                    'EVIDENCE', 'EXPLICATION', 'INTERPRÉTATION', 'OBJECTIVITÉ', 'SUBJECTIVITÉ'
                },
                'themes': [
                    'connaissance', 'savoir', 'vérité', 'science', 'épistémologie', 'croyance',
                    'justification', 'perception', 'rationalité', 'scepticisme', 'objectivité', 'subjectivité'
                ],
                'weight': 0.95
            },
            {
                'name': 'Éthique',
                'concepts': {
                    'BIEN', 'MAL', 'JUSTICE', 'VERTU', 'DEVOIR', 'RESPONSABILITÉ', 'VALEUR', 'MORALE',
                    'CONSCIENCE', 'LIBERTÉ', 'OBLIGATION', 'CONSÉQUENTIALISME', 'UTILITARISME', 'DROIT',
                    'ÉQUITÉ', 'ALTRUISME', 'ÉGOÏSME', 'RESPECT', 'HONNÊTETÉ', 'INTÉGRITÉ'
                },
                'themes': [
                    'morale', 'éthique', 'bien', 'mal', 'justice', 'vertu', 'devoir', 'responsabilité',
                    'valeur', 'obligation', 'utilitarisme', 'conséquentialisme', 'droits', 'respect', 'intégrité'
                ],
                'weight': 0.95
            },
            {
                'name': 'Métaphysique',
                'concepts': {
                    'ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ', 'TEMPS', 'ESPACE', 'SUBSTANCE', 'IDENTITÉ',
                    'CHANGEMENT', 'CAUSALITÉ', 'CONTINGENCE', 'NÉCESSITÉ', 'UNIVERS', 'MONDE', 'ÂME',
                    'CORPS', 'DUALISME', 'MONISME', 'PLURALISME', 'INFINI', 'FINITUDE'
                },
                'themes': [
                    'être', 'existence', 'réalité', 'métaphysique', 'ontologie', 'essence', 'temps', 'espace',
                    'substance', 'identité', 'changement', 'causalité', 'nécessité', 'contingence', 'univers'
                ],
                'weight': 0.9
            },
            {
                'name': 'Philosophie politique',
                'concepts': {
                    'LIBERTÉ', 'AUTORITÉ', 'POUVOIR', 'ÉGALITÉ', 'SOCIÉTÉ', 'ÉTAT', 'LOI', 'DROIT', 'JUSTICE',
                    'CITOYEN', 'DÉMOCRATIE', 'RÉPUBLIQUE', 'SOUVERAINETÉ', 'CONTRAT SOCIAL', 'GOUVERNEMENT',
                    'LÉGITIMITÉ', 'RÉVOLUTION', 'OPPRESSION', 'PARTICIPATION', 'CIVISME'
                },
                'themes': [
                    'politique', 'société', 'liberté', 'autorité', 'démocratie', 'loi', 'droit', 'citoyen',
                    'état', 'justice', 'gouvernement', 'contrat social', 'égalité', 'souveraineté'
                ],
                'weight': 0.9
            },
            {
                'name': 'Logique',
                'concepts': {
                    'CAUSE', 'EFFET', 'NÉCESSITÉ', 'POSSIBILITÉ', 'CONTRADICTION', 'RAISONNEMENT', 'ARGUMENT',
                    'VALIDITÉ', 'PREMISE', 'CONCLUSION', 'SYLLOGISME', 'PARADOXE', 'DÉDUCTION', 'INDUCTION',
                    'INFERENCE', 'ANALOGIE', 'FALLACIE', 'CONSISTANCE', 'COHÉRENCE'
                },
                'themes': [
                    'logique', 'raisonnement', 'argument', 'preuve', 'démonstration', 'contradiction',
                    'validité', 'paradoxe', 'syllogisme', 'déduction', 'induction', 'inférence'
                ],
                'weight': 0.85
            },
            {
                'name': 'Esthétique',
                'concepts': {
                    'BEAUTÉ', 'ART', 'CRÉATION', 'HARMONIE', 'SENSIBILITÉ', 'JUGEMENT', 'SUBLIME', 'GOÛT',
                    'IMAGINATION', 'SYMBOLISME', 'STYLE', 'ŒUVRE', 'EXPRESSION', 'INTERPRÉTATION', 'ÉMOTION'
                },
                'themes': [
                    'beauté', 'art', 'esthétique', 'création', 'goût', 'sublime', 'imagination', 'émotion',
                    'jugement', 'style', 'expression', 'interprétation'
                ],
                'weight': 0.8
            },
            {
                'name': 'Philosophie de la science',
                'concepts': {
                    'SCIENCE', 'EXPLICATION', 'THÉORIE', 'MODÈLE', 'OBSERVATION', 'EXPERIENCE', 'LOI',
                    'HYPOTHÈSE', 'RÉFUTATION', 'VÉRIFICATION', 'PARADIGME', 'OBJECTIVITÉ', 'MÉTHODE',
                    'RÉDUCTIONNISME', 'EMERGENTISME', 'CAUSALITÉ', 'DÉTERMINISME', 'INDÉTERMINISME'
                },
                'themes': [
                    'science', 'expérience', 'théorie', 'modèle', 'observation', 'loi', 'hypothèse',
                    'méthode scientifique', 'réfutation', 'paradigme', 'objectivité', 'réductionnisme'
                ],
                'weight': 0.85
            },
            {
                'name': 'Philosophie de l’esprit',
                'concepts': {
                    'CONSCIENCE', 'PENSÉE', 'ESPRIT', 'MENTAL', 'SUBJECTIVITÉ', 'QUALIA', 'INTENTIONNALITÉ',
                    'PERCEPTION', 'SENSATION', 'VOLONTÉ', 'LIBRE ARBITRE', 'DUALISME', 'PHYSICALISME',
                    'IDENTITÉ PERSONNELLE', 'INCONSCIENT', 'ÉMOTION', 'RAISON', 'IMAGINATION'
                },
                'themes': [
                    'conscience', 'esprit', 'pensée', 'mental', 'subjectivité', 'perception', 'volonté',
                    'libre arbitre', 'identité', 'inconscient', 'émotion', 'raison'
                ],
                'weight': 0.85
            },
            {
                'name': 'Philosophie du langage',
                'concepts': {
                    'LANGAGE', 'SIGNIFICATION', 'SENS', 'RÉFÉRENCE', 'COMMUNICATION', 'INTERPRÉTATION',
                    'SYMBOLISME', 'PRAGMATIQUE', 'SÉMANTIQUE', 'SYNTAQUE', 'ÉNONCÉ', 'DISCOURS', 'VÉRITÉ',
                    'AMBIGUÏTÉ', 'CONVENTION', 'JEU DE LANGAGE', 'PERFORMATIF'
                },
                'themes': [
                    'langage', 'signification', 'communication', 'interprétation', 'pragmatique', 'sémantique',
                    'syntaxe', 'discours', 'vérité', 'ambiguïté', 'convention', 'jeu de langage'
                ],
                'weight': 0.8
            },
            {
                'name': 'Philosophie de la religion',
                'concepts': {
                    'DIEU', 'FOI', 'RELIGION', 'SPIRITUALITÉ', 'SACRÉ', 'PROFANE', 'MYSTICISME', 'RÉVÉLATION',
                    'MIRACLE', 'EXISTENCE DE DIEU', 'THÉISME', 'ATHÉISME', 'AGNOSTICISME', 'CULTE',
                    'TRANSCENDANCE', 'IMMANENCE', 'SALUT', 'PÉCHÉ', 'GRÂCE', 'RITUEL'
                },
                'themes': [
                    'religion', 'dieu', 'foi', 'spiritualité', 'sacré', 'profané', 'mysticisme', 'révélation',
                    'miracle', 'théisme', 'athéisme', 'agnosticisme', 'culte', 'transcendance', 'salut'
                ],
                'weight': 0.8
            },
            {
                'name': 'Philosophie morale appliquée',
                'concepts': {
                    'BIOÉTHIQUE', 'JUSTICE SOCIALE', 'ENVIRONNEMENT', 'DROITS DE L’HOMME', 'ANIMALITÉ',
                    'TECHNOLOGIE', 'INTELLIGENCE ARTIFICIELLE', 'ÉCOLOGIE', 'SANTÉ', 'MÉDECINE', 'GENRE',
                    'SEXUALITÉ', 'FÉMINISME', 'RACISME', 'DISCRIMINATION', 'PAUVRETÉ', 'GUERRE', 'PAIX'
                },
                'themes': [
                    'bioéthique', 'justice sociale', 'environnement', 'droits de l’homme', 'animalité',
                    'technologie', 'écologie', 'santé', 'médecine', 'genre', 'sexualité', 'féminisme',
                    'racisme', 'discrimination', 'paix', 'guerre'
                ],
                'weight': 0.8
            },
            {
                'name': 'Philosophie antique',
                'concepts': {
                    'PLATON', 'ARISTOTE', 'SOCRATE', 'PYTHAGORE', 'HÉRACLITE', 'PARMÉNIDE', 'ÉPICURE',
                    'STOÏCISME', 'SCEPTICISME', 'CYNISME', 'SOPHISTE', 'DÉMOCRITE', 'ZÉNON', 'PYRRHON'
                },
                'themes': [
                    'philosophie antique', 'platonisme', 'aristotélisme', 'stoïcisme', 'épicurisme',
                    'scepticisme', 'cynisme', 'sophistes'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie moderne',
                'concepts': {
                    'DESCARTES', 'SPINOZA', 'LOCKE', 'HUME', 'KANT', 'HEGEL', 'ROUSSEAU', 'VOLTAIRE',
                    'LEIBNIZ', 'HOBBES', 'MONTESQUIEU', 'DIDEROT', 'CONDORCET', 'BERKELEY'
                },
                'themes': [
                    'philosophie moderne', 'cartésianisme', 'empirisme', 'rationalisme', 'idéalisme',
                    'matérialisme', 'lumières', 'criticisme'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie contemporaine',
                'concepts': {
                    'NIETZSCHE', 'HEIDEGGER', 'SARTRE', 'CAMUS', 'MERLEAU-PONTY', 'FREUD', 'WITTGENSTEIN',
                    'DELEUZE', 'DERRIDA', 'FOUCAULT', 'LEVINAS', 'ARENDT', 'SIMONE DE BEAUVOIR', 'BACHELARD'
                },
                'themes': [
                    'philosophie contemporaine', 'existentialisme', 'phénoménologie', 'herméneutique',
                    'structuralisme', 'déconstruction', 'psychanalyse', 'postmodernisme'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie orientale',
                'concepts': {
                    'BOUDDHA', 'CONFUCIUS', 'LAOZI', 'ZEN', 'TAO', 'DHARMA', 'KARMA', 'NIRVANA', 'YIN', 'YANG',
                    'VEDANTA', 'MAHAYANA', 'BODHISATTVA', 'SAMADHI', 'QI', 'WU WEI'
                },
                'themes': [
                    'philosophie orientale', 'bouddhisme', 'taoïsme', 'confucianisme', 'hindouisme',
                    'zen', 'karma', 'nirvana', 'yin', 'yang', 'dharma'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie analytique',
                'concepts': {
                    'ANALYSE', 'LANGAGE ORDINAIRE', 'LOGIQUE FORMELLE', 'POSITIVISME LOGIQUE', 'FALSIFIABILITÉ',
                    'SCIENCE', 'SIGNIFICATION', 'VÉRIFICATION', 'RÉDUCTION', 'FONCTION', 'PROPOSITION'
                },
                'themes': [
                    'philosophie analytique', 'analyse', 'langage ordinaire', 'logique formelle',
                    'positivisme logique', 'falsifiabilité', 'réduction', 'proposition'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie continentale',
                'concepts': {
                    'PHÉNOMÉNOLOGIE', 'HERMÉNEUTIQUE', 'STRUCTURALISME', 'DÉCONSTRUCTION', 'EXISTENTIALISME',
                    'DIALECTIQUE', 'TOTALITÉ', 'ALTÉRITÉ', 'DIFFÉRANCE', 'POUVOIR', 'DISCOURS'
                },
                'themes': [
                    'philosophie continentale', 'phénoménologie', 'herméneutique', 'structuralisme',
                    'déconstruction', 'existentialisme', 'dialectique', 'altérité'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie de l’histoire',
                'concepts': {
                    'HISTOIRE', 'PROGRÈS', 'DÉTERMINISME HISTORIQUE', 'RÉPÉTITION', 'ÉVÉNEMENT', 'NARRATION',
                    'SENS DE L’HISTOIRE', 'TÉLÉOLOGIE', 'CONTINGENCE', 'STRUCTURE', 'AGENT', 'COLLECTIF'
                },
                'themes': [
                    'philosophie de l’histoire', 'progrès', 'déterminisme', 'événement', 'narration',
                    'téléologie', 'structure', 'collectif'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie de l’éducation',
                'concepts': {
                    'ÉDUCATION', 'APPRENTISSAGE', 'ENSEIGNEMENT', 'TRANSMISSION', 'SAVOIR', 'AUTONOMIE',
                    'DISCIPLINE', 'ÉMANCIPATION', 'FORMATION', 'PÉDAGOGIE', 'VALEUR', 'CITOYENNETÉ'
                },
                'themes': [
                    'philosophie de l’éducation', 'apprentissage', 'enseignement', 'transmission',
                    'autonomie', 'discipline', 'émancipation', 'pédagogie', 'citoyenneté'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie de la technique',
                'concepts': {
                    'TECHNIQUE', 'TECHNOLOGIE', 'INNOVATION', 'PROGRÈS', 'MACHINE', 'AUTOMATISATION',
                    'CYBERNÉTIQUE', 'VIRTUALITÉ', 'ARTIFICIALITÉ', 'HUMAIN', 'POSTHUMANISME', 'ROBOTIQUE'
                },
                'themes': [
                    'philosophie de la technique', 'technologie', 'innovation', 'progrès', 'machine',
                    'cybernétique', 'virtualité', 'artificialité', 'posthumanisme', 'robotique'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie du droit',
                'concepts': {
                    'DROIT', 'LOI', 'JUSTICE', 'LÉGALITÉ', 'LÉGITIMITÉ', 'SANCTION', 'NORME', 'RESPONSABILITÉ',
                    'PUNITION', 'RÉPARATION', 'CONTRAT', 'JUGE', 'PROCÈS', 'ÉQUITÉ', 'DROITS NATURELS'
                },
                'themes': [
                    'philosophie du droit', 'loi', 'justice', 'légalité', 'légitimité', 'sanction',
                    'norme', 'responsabilité', 'contrat', 'équité', 'droits naturels'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie de l’économie',
                'concepts': {
                    'ÉCONOMIE', 'VALEUR', 'TRAVAIL', 'CAPITAL', 'MARCHÉ', 'ÉCHANGE', 'PROPRIÉTÉ',
                    'PRODUCTION', 'CONSOMMATION', 'INÉGALITÉ', 'JUSTICE SOCIALE', 'LIBÉRALISME',
                    'MARXISME', 'RICHESSE', 'PAUVRETÉ'
                },
                'themes': [
                    'philosophie de l’économie', 'valeur', 'travail', 'capital', 'marché', 'échange',
                    'propriété', 'production', 'consommation', 'inégalité', 'justice sociale', 'libéralisme', 'marxisme'
                ],
                'weight': 0.7
            },
            {
                'name': 'Philosophie de l’environnement',
                'concepts': {
                    'ENVIRONNEMENT', 'NATURE', 'ÉCOLOGIE', 'DÉVELOPPEMENT DURABLE', 'ANTHROPOCÈNE',
                    'BIODIVERSITÉ', 'RESPONSABILITÉ', 'PRÉSERVATION', 'RÉCHAUFFEMENT', 'ÉTHIQUE ENVIRONNEMENTALE'
                },
                'themes': [
                    'philosophie de l’environnement', 'écologie', 'nature', 'développement durable',
                    'biodiversité', 'responsabilité', 'préservation', 'réchauffement', 'éthique environnementale'
                ],
                'weight': 0.7
            }
        ]
    
    def _build_default_constraints(self) -> List[Constraint]:
        logger.info("Construction des contraintes philosophiques par défaut")
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
        logger.info("Début de la validation de la réponse")
        logger.debug(f"Réponse à valider: {response[:100]}...")
        logger.debug(f"Contexte: {context}")
        validation_results = {}
        total_score = 0.0
        total_weight = 0.0
        violations = []
        
        for constraint in self.constraints:
            logger.info(f"Validation de la contrainte: {constraint.name}")
            try:
                score = constraint.validator(response, context)
                logger.debug(f"Score obtenu pour {constraint.name}: {score}")
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
                    logger.warning(f"Violation de contrainte obligatoire: {constraint.name} (score: {score})")
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
        logger.info(f"Score global obtenu: {global_score}")
        logger.info(f"Contraintes violées: {violations}")
        
        result = {
            'global_score': global_score,
            'constraint_results': validation_results,
            'violations': violations,
            'is_valid': len(violations) == 0 and global_score >= 0.6,
            'recommendations': self._generate_recommendations(validation_results)
        }
        logger.debug(f"Résultat de validation: {result}")
        return result
    
    def _validate_philosophical_depth(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la profondeur philosophique")
        # Cache pour éviter les requêtes répétées
        cache_key = f"depth:{response[:50]}"
        if cache_key in self._evaluation_cache:
            logger.debug(f"Score profondeur récupéré du cache pour clé {cache_key}")
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
        logger.debug(f"Score de base profondeur: {base_score}")
        
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
            logger.debug(f"Réponse Ollama profondeur: {ollama_response}")
            
            if ollama_response:
                # Extraction du score
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', ollama_response)
                if score_match:
                    ollama_score = float(score_match.group(1)) / 10.0
                    logger.debug(f"Score Ollama extrait: {ollama_score}")
                    final_score = (base_score * 0.4) + (ollama_score * 0.6)
                else:
                    logger.warning("Aucun score détecté dans la réponse Ollama pour la profondeur")
                    final_score = base_score
            else:
                logger.warning("Réponse Ollama vide pour la profondeur")
                final_score = base_score
            
            # Cache du résultat
            self._evaluation_cache[cache_key] = final_score
            logger.info(f"Score final profondeur: {final_score}")
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation profondeur Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
    def _validate_academic_tone(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation du ton académique")
        cache_key = f"tone:{response[:50]}"
        if cache_key in self._evaluation_cache:
            logger.debug(f"Score ton académique récupéré du cache pour clé {cache_key}")
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
        logger.debug(f"Indicateurs académiques trouvés: {academic_count}, informels: {informal_count}")
        base_score = min(academic_count / 3, 1.0) - (informal_count * 0.2)
        base_score = max(base_score, 0.0)
        logger.debug(f"Score de base ton académique: {base_score}")
        
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
            logger.debug(f"Réponse Ollama ton académique: {ollama_response}")
            
            if ollama_response:
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', ollama_response)
                if score_match:
                    ollama_score = float(score_match.group(1)) / 10.0
                    logger.debug(f"Score Ollama extrait: {ollama_score}")
                    final_score = (base_score * 0.4) + (ollama_score * 0.6)
                else:
                    logger.warning("Aucun score détecté dans la réponse Ollama pour le ton académique")
                    final_score = base_score
            else:
                logger.warning("Réponse Ollama vide pour le ton académique")
                final_score = base_score
            
            self._evaluation_cache[cache_key] = final_score
            logger.info(f"Score final ton académique: {final_score}")
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation ton académique Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
    def _validate_conceptual_coherence(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la cohérence conceptuelle")
        concepts_detected = context.get('concepts_detected', [])
        logger.debug(f"Concepts détectés: {concepts_detected}")
        if len(concepts_detected) < 2:
            logger.info("Moins de deux concepts détectés, score par défaut 0.7")
            return 0.7
        
        # Vérification via clusters philosophiques
        coherence_score = 0.0
        total_pairs = 0
        for i, concept1 in enumerate(concepts_detected):
            for concept2 in concepts_detected[i+1:]:
                related = self._concepts_are_related_enhanced(concept1, concept2)
                logger.debug(f"Relation {concept1}-{concept2}: {related}")
                if related:
                    coherence_score += 1.0
                total_pairs += 1
        score = coherence_score / total_pairs if total_pairs > 0 else 0.5
        logger.info(f"Score cohérence conceptuelle: {score}")
        return score
    
    def _concepts_are_related_enhanced(self, concept1: str, concept2: str) -> bool:
        logger.debug(f"Vérification de la relation entre {concept1} et {concept2}")
        # Vérification dans les clusters philosophiques
        for cluster in self.philosophical_clusters:
            if concept1 in cluster['concepts'] and concept2 in cluster['concepts']:
                logger.debug(f"Concepts {concept1} et {concept2} liés dans le cluster {cluster['name']}")
                return True
        
        # Relations ontologiques directes
        if concept1 in self.ontology.concepts and concept2 in self.ontology.concepts:
            concept1_obj = self.ontology.concepts[concept1]
            if hasattr(concept1_obj, 'related_concepts'):
                related = concept2 in concept1_obj.related_concepts
                logger.debug(f"Relation ontologique directe entre {concept1} et {concept2}: {related}")
                return related
        logger.debug(f"Aucune relation trouvée entre {concept1} et {concept2}")
        return False
    
    def _validate_concept_relevance(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la pertinence des concepts")
        question = context.get('question', '')
        concepts_detected = context.get('concepts_detected', [])
        logger.debug(f"Question: {question}")
        logger.debug(f"Concepts détectés: {concepts_detected}")
        if not concepts_detected:
            logger.info("Aucun concept détecté, score 0.3")
            return 0.3
        question_words = set(question.lower().split())
        relevance_scores = []
        for concept in concepts_detected:
            concept_words = set(concept.lower().split('_'))
            intersection = question_words & concept_words
            relevance = len(intersection) / len(concept_words) if concept_words else 0
            logger.debug(f"Concept: {concept}, intersection: {intersection}, score: {relevance}")
            if concept.lower() in response.lower():
                relevance += 0.3
                logger.debug(f"Concept {concept} présent dans la réponse, bonus ajouté")
            relevance_scores.append(min(relevance, 1.0))
        score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        logger.info(f"Score pertinence des concepts: {score}")
        return score
    
    def _validate_argumentative_structure(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la structure argumentative")
        structure_indicators = [
            'tout d\'abord', 'premièrement', 'en premier lieu',
            'ensuite', 'deuxièmement', 'par ailleurs',
            'enfin', 'finalement', 'en conclusion',
            'cependant', 'néanmoins', 'toutefois',
            'donc', 'ainsi', 'par conséquent'
        ]
        
        response_lower = response.lower()
        found_indicators = sum(1 for indicator in structure_indicators if indicator in response_lower)
        logger.debug(f"Indicateurs de structure trouvés: {found_indicators}")
        structure_score = min(found_indicators / 3, 1.0)
        word_count = len(response.split())
        logger.debug(f"Nombre de mots: {word_count}")
        if word_count > 100:
            structure_score += 0.2
            logger.debug("Bonus structure pour longueur > 100 mots")
        score = min(structure_score, 1.0)
        logger.info(f"Score structure argumentative: {score}")
        return score
    
    def _validate_clarity(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la clarté du discours")
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        logger.debug(f"Longueur moyenne des phrases: {avg_sentence_length}")
        clarity_score = 1.0
        if avg_sentence_length > 25:
            clarity_score -= 0.3
            logger.debug("Pénalité pour phrases longues (>25 mots)")
        elif avg_sentence_length > 35:
            clarity_score -= 0.5
            logger.debug("Pénalité supplémentaire pour phrases très longues (>35 mots)")
        logical_connectors = [
            'car', 'parce que', 'puisque', 'étant donné',
            'donc', 'ainsi', 'par conséquent', 'c\'est pourquoi'
        ]
        response_lower = response.lower()
        found_connectors = sum(1 for connector in logical_connectors if connector in response_lower)
        logger.debug(f"Connecteurs logiques trouvés: {found_connectors}")
        clarity_score += min(found_connectors * 0.1, 0.3)
        score = min(max(clarity_score, 0.0), 1.0)
        logger.info(f"Score clarté: {score}")
        return score
    
    def _validate_length(self, response: str, context: Dict[str, Any]) -> float:
        logger.info("Validation de la longueur appropriée")
        word_count = len(response.split())
        concepts_count = len(context.get('concepts_detected', []))
        logger.debug(f"Nombre de mots: {word_count}, concepts détectés: {concepts_count}")
        expected_min = max(50, concepts_count * 30)
        expected_max = min(500, concepts_count * 100)
        logger.debug(f"Longueur attendue: min {expected_min}, max {expected_max}")
        if expected_min <= word_count <= expected_max:
            logger.info("Longueur appropriée, score 1.0")
            return 1.0
        elif word_count < expected_min:
            score = word_count / expected_min
            logger.info(f"Longueur trop courte, score: {score}")
            return score
        else:
            score = max(0.5, expected_max / word_count)
            logger.info(f"Longueur trop longue, score: {score}")
            return score
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        logger.info("Génération des recommandations d'amélioration")
        recommendations = []
        for constraint_name, result in validation_results.items():
            if result.get('score', 0) < 0.6:
                logger.debug(f"Recommandation pour {constraint_name}")
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
        logger.info(f"Recommandations générées: {recommendations}")
        return recommendations
    
    def add_constraint(self, constraint: Constraint):
        logger.info(f"Ajout d'une nouvelle contrainte: {constraint.name}")
        self.constraints.append(constraint)
        logger.debug(f"Contraintes actuelles: {[c.name for c in self.constraints]}")
    
    def remove_constraint(self, constraint_name: str):
        logger.info(f"Suppression de la contrainte: {constraint_name}")
        self.constraints = [c for c in self.constraints if c.name != constraint_name]
        logger.debug(f"Contraintes restantes: {[c.name for c in self.constraints]}")
    
    def get_constraint_report(self) -> Dict[str, Any]:
        logger.info("Génération du rapport sur les contraintes configurées")
        report = {
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
        logger.debug(f"Rapport généré: {report}")
        return report