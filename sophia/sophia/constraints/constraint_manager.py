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
                    'EVIDENCE', 'EXPLICATION', 'INTERPRÉTATION', 'OBJECTIVITÉ', 'SUBJECTIVITÉ',
                    'RÉFLEXIVITÉ', 'PRAGMATISME', 'EMPIRISME', 'RATIONALISME', 'FALSIFIABILITÉ',
                    'COHÉRENCE', 'CORRESPONDANCE', 'CONVENTIONNALISME', 'CONSTRUCTIVISME',
                    'RÉALISME', 'ANTIRÉALISME', 'INSTRUMENTALISME', 'POSITIVISME', 'POSTMODERNISME',
                    'VÉRIFICATION', 'SIGNIFICATION', 'LANGAGE', 'SÉMANTIQUE', 'PRÉSUPPOSITION',
                    'INFERENCE', 'DÉDUCTION', 'INDUCTION', 'ABDUCTION', 'HYPOTHÈSE', 'THÉORIE',
                    'MODÈLE', 'PARADIGME', 'ANOMALIE', 'RÉVOLUTION SCIENTIFIQUE', 'OBJECTIVITÉ',
                    'SUBJECTIVITÉ', 'CERTITUDE', 'DOUTE', 'CROYANCE', 'JUSTIFICATION', 'SAVOIR',
                    'IGNORANCE', 'ERREUR', 'EVIDENCE', 'EXPLICATION', 'INTERPRÉTATION',
                    'SENS', 'SIGNIFIANT', 'SIGNIFIÉ', 'PRAGMATIQUE', 'SYNTAQUE', 'RÉFÉRENCE',
                    'CONNAISSANCE TACITE', 'CONNAISSANCE EXPLICITE', 'SAVOIR-FAIRE', 'SAVOIR-ÊTRE',
                    'SAVOIR-THÉORIQUE', 'SAVOIR-PRATIQUE', 'CERTITUDE ABSOLUE', 'CERTITUDE RELATIVE',
                    'DOUTE MÉTHODIQUE', 'DOUTE RADICAL', 'DOUTE SCEPTIQUE', 'DOUTE CARTÉSIEN',
                    'EPISTÉMOLOGIE HISTORIQUE', 'EPISTÉMOLOGIE GÉNÉTIQUE', 'EPISTÉMOLOGIE CRITIQUE',
                    'EPISTÉMOLOGIE ANALYTIQUE', 'EPISTÉMOLOGIE CONTEMPORAINE', 'EPISTÉMOLOGIE CLASSIQUE',
                    'THÉORIE DE LA CONNAISSANCE', 'THÉORIE DE LA VÉRITÉ', 'THÉORIE DE LA JUSTIFICATION',
                    'THÉORIE DE L’ERREUR', 'THÉORIE DE L’EXPLICATION', 'THÉORIE DE L’INTERPRÉTATION',
                    'THÉORIE DE L’EVIDENCE', 'THÉORIE DE LA PERCEPTION', 'THÉORIE DE LA RATIONALITÉ',
                    'THÉORIE DE LA SCIENCE', 'THÉORIE DE LA CROYANCE', 'THÉORIE DE L’OBJECTIVITÉ',
                    'THÉORIE DE LA SUBJECTIVITÉ', 'THÉORIE DE LA COHÉRENCE', 'THÉORIE DE LA CORRESPONDANCE',
                    'THÉORIE DE LA CONVENTION', 'THÉORIE DE LA CONSTRUCTION', 'THÉORIE DU RÉALISME',
                    'THÉORIE DE L’ANTIRÉALISME', 'THÉORIE DE L’INSTRUMENTALISME', 'THÉORIE DU POSITIVISME',
                    'THÉORIE DU POSTMODERNISME', 'THÉORIE DE LA VÉRIFICATION', 'THÉORIE DE LA SIGNIFICATION',
                    'THÉORIE DU LANGAGE', 'THÉORIE DE LA SÉMANTIQUE', 'THÉORIE DE LA PRÉSUPPOSITION',
                    'THÉORIE DE L’INFERENCE', 'THÉORIE DE LA DÉDUCTION', 'THÉORIE DE L’INDUCTION',
                    'THÉORIE DE L’ABDUCTION', 'THÉORIE DE L’HYPOTHÈSE', 'THÉORIE DU MODÈLE',
                    'THÉORIE DU PARADIGME', 'THÉORIE DE L’ANOMALIE', 'THÉORIE DE LA RÉVOLUTION SCIENTIFIQUE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'connaissance', 'savoir', 'vérité', 'science', 'épistémologie', 'croyance',
                    'justification', 'perception', 'rationalité', 'scepticisme', 'objectivité', 'subjectivité',
                    'réflexivité', 'pragmatisme', 'empirisme', 'rationalisme', 'falsifiabilité',
                    'cohérence', 'correspondance', 'conventionnalisme', 'constructivisme',
                    'réalisme', 'antiréalisme', 'instrumentalisme', 'positivisme', 'postmodernisme',
                    'vérification', 'signification', 'langage', 'sémantique', 'présupposition',
                    'inférence', 'déduction', 'induction', 'abduction', 'hypothèse', 'théorie',
                    'modèle', 'paradigme', 'anomalie', 'révolution scientifique',
                    'analyse', 'expérience', 'observation', 'preuve', 'explication', 'interprétation',
                    'argumentation', 'démonstration', 'raison', 'logique', 'méthode', 'critique',
                    'réfutation', 'confirmation', 'probabilité', 'incertitude', 'subjectivisme',
                    'objectivisme', 'relativisme', 'absolutisme', 'dogmatisme', 'antidogmatisme',
                    'pluralisme', 'monisme', 'dualisme', 'holisme', 'réductionnisme', 'contextualisme',
                    'universalité', 'particularité', 'singularité', 'généralité', 'spécificité',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.95
            },
            {
                'name': 'Éthique',
                'concepts': {
                    'BIEN', 'MAL', 'JUSTICE', 'VERTU', 'DEVOIR', 'RESPONSABILITÉ', 'VALEUR', 'MORALE',
                    'CONSCIENCE', 'LIBERTÉ', 'OBLIGATION', 'CONSÉQUENTIALISME', 'UTILITARISME', 'DROIT',
                    'ÉQUITÉ', 'ALTRUISME', 'ÉGOÏSME', 'RESPECT', 'HONNÊTETÉ', 'INTÉGRITÉ',
                    'NIHILISME', 'RELATIVISME MORAL', 'ABSOLUTISME MORAL', 'ÉTHIQUE DE LA VERTU',
                    'ÉTHIQUE DE LA RESPONSABILITÉ', 'ÉTHIQUE DE LA CONVICTION', 'ÉTHIQUE APPLIQUÉE',
                    'ÉTHIQUE NORMATIVE', 'ÉTHIQUE DÉONTOLOGIQUE', 'ÉTHIQUE TÉLÉOLOGIQUE',
                    'ÉTHIQUE DES CARES', 'ÉTHIQUE ENVIRONNEMENTALE', 'ÉTHIQUE MÉDICALE',
                    'ÉTHIQUE PROFESSIONNELLE', 'ÉTHIQUE SOCIALE', 'ÉTHIQUE POLITIQUE',
                    'ÉTHIQUE ANIMALE', 'ÉTHIQUE DE LA RECHERCHE', 'ÉTHIQUE DE L’INTELLIGENCE ARTIFICIELLE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'morale', 'éthique', 'bien', 'mal', 'justice', 'vertu', 'devoir', 'responsabilité',
                    'valeur', 'obligation', 'utilitarisme', 'conséquentialisme', 'droits', 'respect', 'intégrité',
                    'solidarité', 'tolérance', 'bienveillance', 'compassion', 'empathie', 'honnêteté',
                    'loyauté', 'fidélité', 'courage', 'prudence', 'tempérance', 'générosité', 'humilité',
                    'dignité', 'égalité', 'fraternité', 'liberté', 'autonomie', 'justice distributive',
                    'justice réparatrice', 'justice procédurale', 'justice sociale', 'justice pénale',
                    'justice transitionnelle', 'justice environnementale', 'justice intergénérationnelle',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.95
            },
            {
                'name': 'Métaphysique',
                'concepts': {
                    'ÊTRE', 'EXISTENCE', 'ESSENCE', 'RÉALITÉ', 'TEMPS', 'ESPACE', 'SUBSTANCE', 'IDENTITÉ',
                    'CHANGEMENT', 'CAUSALITÉ', 'CONTINGENCE', 'NÉCESSITÉ', 'UNIVERS', 'MONDE', 'ÂME',
                    'CORPS', 'DUALISME', 'MONISME', 'PLURALISME', 'INFINI', 'FINITUDE',
                    'ACTUALITÉ', 'POTENTIALITÉ', 'MOUVEMENT', 'IMMOBILITÉ', 'MATIÈRE', 'SPIRITUALITÉ',
                    'IMMORTALITÉ', 'MORTALITÉ', 'SUBSISTANCE', 'ACCIDENT', 'SUBSTRAT', 'MODALITÉ',
                    'UN', 'MULTIPLE', 'ABSOLU', 'RELATIF', 'UNIVERSALITÉ', 'PARTICULARITÉ',
                    'NATURE', 'PHYSIS', 'COSMOS', 'CHAOS', 'ORDRE', 'DÉSORDRE', 'DÉTERMINISME',
                    'INDÉTERMINISME', 'LIBERTÉ', 'DESTIN', 'HASARD', 'NÉANT', 'TRANSCENDANCE',
                    'IMMANENCE', 'TRANSCENDANTAL', 'IMMANENT', 'ONTOLOGIE', 'ONTOLOGIQUE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'être', 'existence', 'réalité', 'métaphysique', 'ontologie', 'essence', 'temps', 'espace',
                    'substance', 'identité', 'changement', 'causalité', 'nécessité', 'contingence', 'univers',
                    'monde', 'âme', 'corps', 'dualisme', 'monisme', 'pluralisme', 'infini', 'finitude',
                    'nature', 'cosmos', 'ordre', 'désordre', 'déterminisme', 'indéterminisme', 'liberté',
                    'destin', 'hasard', 'néant', 'transcendance', 'immanence', 'absolu', 'relatif',
                    'universalité', 'particularité', 'singularité', 'généralité', 'spécificité',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.9
            },
            {
                'name': 'Philosophie politique',
                'concepts': {
                    'LIBERTÉ', 'AUTORITÉ', 'POUVOIR', 'ÉGALITÉ', 'SOCIÉTÉ', 'ÉTAT', 'LOI', 'DROIT', 'JUSTICE',
                    'CITOYEN', 'DÉMOCRATIE', 'RÉPUBLIQUE', 'SOUVERAINETÉ', 'CONTRAT SOCIAL', 'GOUVERNEMENT',
                    'LÉGITIMITÉ', 'RÉVOLUTION', 'OPPRESSION', 'PARTICIPATION', 'CIVISME',
                    'ANARCHIE', 'MONARCHIE', 'OLIGARCHIE', 'PLUTOCRATIE', 'THÉOCRATIE', 'DICTATURE',
                    'TOTALITARISME', 'AUTORITARISME', 'FÉDÉRALISME', 'CENTRALISATION', 'DÉCENTRALISATION',
                    'SÉPARATION DES POUVOIRS', 'SOUVERAIN', 'PEUPLE', 'MAJORITÉ', 'MINORITÉ',
                    'DROITS DE L’HOMME', 'DROITS CIVIQUES', 'DROITS POLITIQUES', 'DROITS SOCIAUX',
                    'DROITS ÉCONOMIQUES', 'DROITS CULTURELS', 'DROITS COLLECTIFS', 'DROITS INDIVIDUELS',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'politique', 'société', 'liberté', 'autorité', 'démocratie', 'loi', 'droit', 'citoyen',
                    'état', 'justice', 'gouvernement', 'contrat social', 'égalité', 'souveraineté',
                    'république', 'révolution', 'oppression', 'participation', 'civisme', 'anarchie',
                    'monarchie', 'oligarchie', 'ploutocratie', 'théocratie', 'dictature', 'totalitarisme',
                    'autoritarisme', 'fédéralisme', 'centralisation', 'décentralisation',
                    'séparation des pouvoirs', 'souverain', 'peuple', 'majorité', 'minorité',
                    'droits de l’homme', 'droits civiques', 'droits politiques', 'droits sociaux',
                    'droits économiques', 'droits culturels', 'droits collectifs', 'droits individuels',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.9
            },
            {
                'name': 'Logique',
                'concepts': {
                    'CAUSE', 'EFFET', 'NÉCESSITÉ', 'POSSIBILITÉ', 'CONTRADICTION', 'RAISONNEMENT', 'ARGUMENT',
                    'VALIDITÉ', 'PREMISE', 'CONCLUSION', 'SYLLOGISME', 'PARADOXE', 'DÉDUCTION', 'INDUCTION',
                    'INFERENCE', 'ANALOGIE', 'FALLACIE', 'CONSISTANCE', 'COHÉRENCE',
                    'ANTÉCÉDENT', 'CONSÉQUENT', 'MODUS PONENS', 'MODUS TOLLENS', 'RAISON SUFFISANTE',
                    'RAISON NÉCESSAIRE', 'RAISON FORMELLE', 'RAISON MATÉRIELLE', 'RAISON FINALE',
                    'RAISON EFFICIENTE', 'RAISON CAUSALE', 'RAISON LOGIQUE', 'RAISON PRATIQUE',
                    'RAISON THÉORIQUE', 'RAISON D’ÊTRE', 'RAISON DE FAIRE', 'RAISON DE CROIRE',
                    'RAISON DE SAVOIR', 'RAISON DE JUGER', 'RAISON DE DOUTER', 'RAISON DE JUSTIFIER',
                    'RAISON DE CONCLURE', 'RAISON DE DÉMONTRER', 'RAISON DE PROUVER', 'RAISON DE RÉFUTER',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'logique', 'raisonnement', 'argument', 'preuve', 'démonstration', 'contradiction',
                    'validité', 'paradoxe', 'syllogisme', 'déduction', 'induction', 'inférence',
                    'analogie', 'fallacie', 'consistance', 'cohérence', 'antécédent', 'conséquent',
                    'modus ponens', 'modus tollens', 'raison suffisante', 'raison nécessaire',
                    'raison formelle', 'raison matérielle', 'raison finale', 'raison efficiente',
                    'raison causale', 'raison logique', 'raison pratique', 'raison théorique',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.85
            },
            {
                'name': 'Esthétique',
                'concepts': {
                    'BEAUTÉ', 'ART', 'CRÉATION', 'HARMONIE', 'SENSIBILITÉ', 'JUGEMENT', 'SUBLIME', 'GOÛT',
                    'IMAGINATION', 'SYMBOLISME', 'STYLE', 'ŒUVRE', 'EXPRESSION', 'INTERPRÉTATION', 'ÉMOTION',
                    'MIMÉSIS', 'CATHARSIS', 'PLAISIR', 'DÉSIR', 'SENTIMENT', 'PERCEPTION ESTHÉTIQUE',
                    'CRITIQUE', 'GENRE', 'MOUVEMENT ARTISTIQUE', 'MODERNISME', 'POSTMODERNISME',
                    'AVANT-GARDE', 'TRADITION', 'INNOVATION', 'ORIGINALITÉ', 'IMITATION', 'RÉALISME',
                    'ABSTRACTION', 'FIGURATION', 'NON-FIGURATION', 'SYMBOLIQUE', 'ALLÉGORIE', 'MÉTAPHORE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'beauté', 'art', 'esthétique', 'création', 'goût', 'sublime', 'imagination', 'émotion',
                    'jugement', 'style', 'expression', 'interprétation', 'mimésis', 'catharsis', 'plaisir',
                    'désir', 'sentiment', 'perception esthétique', 'critique', 'genre', 'mouvement artistique',
                    'modernisme', 'postmodernisme', 'avant-garde', 'tradition', 'innovation', 'originalité',
                    'imitation', 'réalisme', 'abstraction', 'figuration', 'non-figuration', 'symbolique',
                    'allégorie', 'métaphore',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.8
            },
            # Ajout de nouveaux clusters massifs
            {
                'name': 'Philosophie de la religion',
                'concepts': {
                    'DIEU', 'DIVINITÉ', 'FOI', 'RAISON', 'RÉVÉLATION', 'MIRACLE', 'THÉISME', 'ATHÉISME',
                    'AGNOSTICISME', 'SPIRITUALITÉ', 'SACRÉ', 'PROFANE', 'MYSTICISME', 'RELIGION',
                    'CULTE', 'RITUEL', 'TRANSCENDANCE', 'IMMANENCE', 'SALUT', 'PÉCHÉ', 'GRÂCE',
                    'PROVIDENCE', 'DESTIN', 'PRÉDESTINATION', 'LIBRE ARBITRE', 'ÂME', 'IMMORTALITÉ',
                    'RÉSURRECTION', 'PARADIS', 'ENFER', 'PURGATOIRE', 'RÉDEMPTION', 'SACRIFICE',
                    'PRIÈRE', 'MÉDITATION', 'CONTEMPLATION', 'ÉVEIL', 'ILLUMINATION', 'DOGME',
                    'ORTHODOXIE', 'HÉRÉSIE', 'SCHISME', 'ÉGLISE', 'SECTE', 'PROPHÉTIE', 'APOCALYPSE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'religion', 'foi', 'raison', 'révélation', 'miracle', 'théisme', 'athéisme',
                    'agnosticisme', 'spiritualité', 'sacré', 'profane', 'mysticisme', 'culte',
                    'rituel', 'transcendance', 'immanence', 'salut', 'péché', 'grâce', 'providence',
                    'destin', 'prédestination', 'libre arbitre', 'âme', 'immortalité', 'résurrection',
                    'paradis', 'enfer', 'purgatoire', 'rédemption', 'sacrifice', 'prière', 'méditation',
                    'contemplation', 'éveil', 'illumination', 'dogme', 'orthodoxie', 'hérésie', 'schisme',
                    'église', 'secte', 'prophétie', 'apocalypse',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.85
            },
            {
                'name': 'Philosophie de l\'esprit',
                'concepts': {
                    'CONSCIENCE', 'INCONSCIENT', 'SUBJECTIVITÉ', 'QUALIA', 'INTENTIONNALITÉ',
                    'DUALISME', 'PHYSICALISME', 'FONCTIONNALISME', 'IDENTITÉ', 'PENSÉE',
                    'PERCEPTION', 'SENSATION', 'ÉMOTION', 'VOLONTÉ', 'LIBRE ARBITRE',
                    'MÉMOIRE', 'IMAGINATION', 'RÊVE', 'SOMMEIL', 'RÉFLEXION', 'RÉMINISCENCE',
                    'APPRENTISSAGE', 'INTELLIGENCE', 'RAISON', 'SENTIMENT', 'AFFECT', 'MOTIVATION',
                    'DÉSIR', 'PEUR', 'JOIE', 'TRISTESSE', 'COLÈRE', 'SURMOI', 'ÇA', 'MOI',
                    'PERSONNALITÉ', 'INDIVIDU', 'MOI SOCIAL', 'MOI PROFOND', 'MOI IDÉAL',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'esprit', 'conscience', 'inconscient', 'subjectivité', 'qualia', 'intentionnalité',
                    'dualisme', 'physicalisme', 'fonctionnalisme', 'identité', 'pensée',
                    'perception', 'sensation', 'émotion', 'volonté', 'libre arbitre', 'mémoire',
                    'imagination', 'rêve', 'sommeil', 'réflexion', 'réminiscence', 'apprentissage',
                    'intelligence', 'raison', 'sentiment', 'affect', 'motivation', 'désir', 'peur',
                    'joie', 'tristesse', 'colère', 'surmoi', 'ça', 'moi', 'personnalité', 'individu',
                    'moi social', 'moi profond', 'moi idéal',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.9
            },
            {
                'name': 'Philosophie des sciences',
                'concepts': {
                    'SCIENCE', 'EXPLICATION', 'LOI', 'THÉORIE', 'MODÈLE', 'PARADIGME', 'EXPERIENCE',
                    'OBSERVATION', 'HYPOTHÈSE', 'VÉRIFICATION', 'FALSIFICATION', 'RÉFUTATION',
                    'OBJECTIVITÉ', 'SUBJECTIVITÉ', 'RÉDUCTIONNISME', 'HOLISME', 'CAUSALITÉ',
                    'MÉTHODE SCIENTIFIQUE', 'EXPERIMENTATION', 'RÉPÉTABILITÉ', 'REPRODUCTIBILITÉ',
                    'PREDICTIBILITÉ', 'EXACTITUDE', 'PRÉCISION', 'MESURE', 'INSTRUMENTATION',
                    'MODÉLISATION', 'SIMULATION', 'CALCUL', 'STATISTIQUE', 'PROBABILITÉ',
                    'INCERTITUDE', 'ERREUR EXPÉRIMENTALE', 'BIAIS', 'OBJECTIVATION', 'CONSTRUCTION',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'science', 'explication', 'loi', 'théorie', 'modèle', 'paradigme', 'expérience',
                    'observation', 'hypothèse', 'vérification', 'falsification', 'réfutation',
                    'objectivité', 'subjectivité', 'réductionnisme', 'holisme', 'causalité',
                    'méthode scientifique', 'expérimentation', 'répétabilité', 'reproductibilité',
                    'prédictibilité', 'exactitude', 'précision', 'mesure', 'instrumentation',
                    'modélisation', 'simulation', 'calcul', 'statistique', 'probabilité',
                    'incertitude', 'erreur expérimentale', 'biais', 'objectivation', 'construction',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.9
            },
            {
                'name': 'Philosophie du langage',
                'concepts': {
                    'LANGAGE', 'SIGNIFIANT', 'SIGNIFIÉ', 'SÉMANTIQUE', 'PRAGMATIQUE', 'SYNTAQUE',
                    'RÉFÉRENCE', 'SIGNIFICATION', 'COMMUNICATION', 'INTERPRÉTATION', 'DISCOURS',
                    'ÉNONCÉ', 'PAROLE', 'LANGUE', 'CONVENTION', 'JEU DE LANGAGE',
                    'ACTE DE PAROLE', 'PERFORMATIF', 'LOCUTOIRE', 'ILLOCUTOIRE', 'PERLOCUTOIRE',
                    'AMBIGUÏTÉ', 'POLYSÉMIE', 'MONOSÉMIE', 'MÉTAPHORE', 'SYNECDOQUE', 'MÉTONYMIE',
                    'ANAPHORE', 'CATAPHORE', 'DÉIXIS', 'PRONOM', 'SYNONYME', 'ANTONYME', 'HOMONYME',
                    'PARADIGME LINGUISTIQUE', 'SYSTÈME', 'STRUCTURE', 'CODE', 'MESSAGE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'langage', 'signifiant', 'signifié', 'sémantique', 'pragmatique', 'syntaxe',
                    'référence', 'signification', 'communication', 'interprétation', 'discours',
                    'énoncé', 'parole', 'langue', 'convention', 'jeu de langage', 'acte de parole',
                    'performatif', 'locutoire', 'illocutoire', 'perlocutoire', 'ambiguïté',
                    'polysémie', 'monosémie', 'métaphore', 'synecdoque', 'métonymie', 'anaphore',
                    'cataphore', 'déixis', 'pronom', 'synonyme', 'antonyme', 'homonyme',
                    'paradigme linguistique', 'système', 'structure', 'code', 'message',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.85
            },
            {
                'name': 'Philosophie de la technique',
                'concepts': {
                    'TECHNIQUE', 'TECHNOLOGIE', 'INNOVATION', 'PROGRÈS', 'MACHINE', 'AUTOMATISATION',
                    'CYBERNÉTIQUE', 'ARTIFICIALITÉ', 'NATURE', 'OUTIL', 'INSTRUMENT', 'VIRTUALITÉ',
                    'ROBOTIQUE', 'INTELLIGENCE ARTIFICIELLE', 'TRANSHUMANISME', 'POSTHUMANISME',
                    'CYBORG', 'AUGMENTATION', 'NUMÉRISATION', 'INFORMATION', 'ALGORITHME',
                    'BIG DATA', 'INTERNET', 'RÉSEAU', 'CONNECTIVITÉ', 'SMART', 'OBJET CONNECTÉ',
                    'RÉALITÉ VIRTUELLE', 'RÉALITÉ AUGMENTÉE', 'SIMULATION', 'AUTONOMIE', 'AUTOMATE',
                    'SYSTÈME', 'PROCESSUS', 'PRODUCTION', 'FABRICATION', 'INDUSTRIALISATION',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'technique', 'technologie', 'innovation', 'progrès', 'machine', 'automatisation',
                    'cybernétique', 'artificialité', 'nature', 'outil', 'instrument', 'virtualité',
                    'robotique', 'intelligence artificielle', 'transhumanisme', 'posthumanisme',
                    'cyborg', 'augmentation', 'numérisation', 'information', 'algorithme',
                    'big data', 'internet', 'réseau', 'connectivité', 'smart', 'objet connecté',
                    'réalité virtuelle', 'réalité augmentée', 'simulation', 'autonomie', 'automate',
                    'système', 'processus', 'production', 'fabrication', 'industrialisation',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.8
            },
            {
                'name': 'Philosophie de l\'art',
                'concepts': {
                    'ART', 'BEAUTÉ', 'ESTHÉTIQUE', 'CRÉATION', 'IMAGINATION', 'SYMBOLISME', 'STYLE',
                    'ŒUVRE', 'EXPRESSION', 'INTERPRÉTATION', 'ÉMOTION', 'JUGEMENT', 'SUBLIME', 'GOÛT',
                    'MIMÉSIS', 'CATHARSIS', 'PLAISIR', 'DÉSIR', 'SENTIMENT', 'PERCEPTION ESTHÉTIQUE',
                    'CRITIQUE', 'GENRE', 'MOUVEMENT ARTISTIQUE', 'MODERNISME', 'POSTMODERNISME',
                    'AVANT-GARDE', 'TRADITION', 'INNOVATION', 'ORIGINALITÉ', 'IMITATION', 'RÉALISME',
                    'ABSTRACTION', 'FIGURATION', 'NON-FIGURATION', 'SYMBOLIQUE', 'ALLÉGORIE', 'MÉTAPHORE',
                    # ...continuez à ajouter des concepts pour atteindre plusieurs centaines...
                },
                'themes': [
                    'art', 'beauté', 'esthétique', 'création', 'imagination', 'symbolisme', 'style',
                    'œuvre', 'expression', 'interprétation', 'émotion', 'jugement', 'sublime', 'goût',
                    'mimésis', 'catharsis', 'plaisir', 'désir', 'sentiment', 'perception esthétique',
                    'critique', 'genre', 'mouvement artistique', 'modernisme', 'postmodernisme',
                    'avant-garde', 'tradition', 'innovation', 'originalité', 'imitation', 'réalisme',
                    'abstraction', 'figuration', 'non-figuration', 'symbolique', 'allégorie', 'métaphore',
                    # ...continuez à ajouter des thèmes pour atteindre plusieurs centaines...
                ],
                'weight': 0.8
            },
            # Ajoutez ici d'autres clusters spécialisés si besoin, en suivant la même logique.
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
    
    def _validate_conceptual_coherence(self, response: str, context: Dict[str, Any]) -> float:
        """Validation de la cohérence conceptuelle - VERSION ULTRA CORRIGÉE"""
        logger.info("Validation de la cohérence conceptuelle")
        concepts_detected = context.get('concepts_detected', [])
        logger.debug(f"Concepts détectés: {concepts_detected}")
        
        if len(concepts_detected) < 2:
            logger.info("Moins de deux concepts détectés, score par défaut 0.7")
            return 0.7
        
        # Relations philosophiques enrichies avec nouveaux concepts
        known_relations = {
            # Relations épistémologiques
            ('VÉRITÉ', 'CONNAISSANCE'): True, ('CONNAISSANCE', 'VÉRITÉ'): True,
            ('VÉRITÉ', 'CROYANCE'): True, ('CROYANCE', 'VÉRITÉ'): True,
            ('VÉRITÉ', 'VALIDITÉ'): True, ('VALIDITÉ', 'VÉRITÉ'): True,  # NOUVEAU
            ('CONNAISSANCE', 'VALIDITÉ'): True, ('VALIDITÉ', 'CONNAISSANCE'): True,  # NOUVEAU
            
            # Relations éthiques enrichies
            ('JUSTICE', 'BIEN'): True, ('BIEN', 'JUSTICE'): True,
            ('JUSTICE', 'MAL'): True, ('MAL', 'JUSTICE'): True,
            ('BIEN', 'MAL'): True, ('MAL', 'BIEN'): True,
            ('JUSTICE', 'VÉRITÉ'): True, ('VÉRITÉ', 'JUSTICE'): True,  # CLEF !
            
            # Relations esthétiques enrichies
            ('BEAUTÉ', 'ART'): True, ('ART', 'BEAUTÉ'): True,
            ('BEAUTÉ', 'BIEN'): True, ('BIEN', 'BEAUTÉ'): True,  # Transcendantaux
            ('BEAUTÉ', 'HARMONIE'): True, ('HARMONIE', 'BEAUTÉ'): True,
            
            # Relations métaphysiques enrichies
            ('ÊTRE', 'EXISTENCE'): True, ('EXISTENCE', 'ÊTRE'): True,
            ('ÊTRE', 'ESSENCE'): True, ('ESSENCE', 'ÊTRE'): True,
            ('EXISTENCE', 'ESSENCE'): True, ('ESSENCE', 'EXISTENCE'): True,
            ('ESSENCE', 'ACTUALITÉ'): True, ('ACTUALITÉ', 'ESSENCE'): True,  # NOUVEAU
            ('ÊTRE', 'ACTUALITÉ'): True, ('ACTUALITÉ', 'ÊTRE'): True,  # NOUVEAU
            
            # Relations spéciales multi-domaines
            ('VÉRITÉ', 'ESSENCE'): True, ('ESSENCE', 'VÉRITÉ'): True,  # NOUVEAU
            ('JUSTICE', 'ESSENCE'): True, ('ESSENCE', 'JUSTICE'): True,  # NOUVEAU
            ('BEAUTÉ', 'ESSENCE'): True, ('ESSENCE', 'BEAUTÉ'): True,  # NOUVEAU
            ('ACTUALITÉ', 'VÉRITÉ'): True, ('VÉRITÉ', 'ACTUALITÉ'): True,  # NOUVEAU
            ('VALIDITÉ', 'JUSTICE'): True, ('JUSTICE', 'VALIDITÉ'): True,  # NOUVEAU
            
            # Relations conceptuelles générales
            ('CONNAISSANCE', 'SCIENCE'): True, ('SCIENCE', 'CONNAISSANCE'): True,
            ('LOGIQUE', 'VALIDITÉ'): True, ('VALIDITÉ', 'LOGIQUE'): True,  # NOUVEAU
            ('RAISONNEMENT', 'VALIDITÉ'): True, ('VALIDITÉ', 'RAISONNEMENT'): True  # NOUVEAU
        }
        
        # Calcul de cohérence
        coherent_pairs = 0
        total_pairs = 0
        
        for i, concept1 in enumerate(concepts_detected):
            for concept2 in concepts_detected[i+1:]:
                total_pairs += 1
                pair = (concept1, concept2)
                
                if known_relations.get(pair, False):
                    coherent_pairs += 1
                    logger.debug(f"✅ Relation cohérente: {concept1} ↔ {concept2}")
                else:
                    logger.debug(f"❓ Relation inconnue: {concept1} ↔ {concept2}")
        
        # Score de base
        if total_pairs == 0:
            base_score = 0.7
        else:
            base_score = coherent_pairs / total_pairs
        
        # Bonus pour nombre de concepts (diversité philosophique)
        concept_count_bonus = min(len(concepts_detected) * 0.05, 0.2)
        
        # Bonus pour concepts mentionnés dans la réponse
        response_lower = response.lower()
        mentioned = 0
        for concept in concepts_detected:
            variants = [concept.lower(), concept.replace('_', ' ').lower()]
            if any(v in response_lower for v in variants):
                mentioned += 1
        
        mention_bonus = (mentioned / len(concepts_detected)) * 0.2
        
        # Score final optimisé
        final_score = base_score + concept_count_bonus + mention_bonus
        final_score = min(final_score, 1.0)
        final_score = max(final_score, 0.5)  # Score minimum plus élevé
        
        logger.info(f"Score cohérence: {final_score:.3f} (base: {base_score:.3f}, bonus_concepts: {concept_count_bonus:.3f}, bonus_mention: {mention_bonus:.3f})")
        return final_score
    
    def _concepts_are_related_enhanced(self, concept1: str, concept2: str) -> bool:
        """OBSOLÈTE - remplacée par la logique dans _validate_conceptual_coherence"""
        logger.debug(f"Vérification de la relation entre {concept1} et {concept2}")
        # Cette méthode n'est plus utilisée, mais gardée pour compatibilité
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
        
        # Amélioration via Ollama si disponible
        try:
            if hasattr(self.llm, 'available') and self.llm.available:
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
            else:
                final_score = base_score
            
            # Cache du résultat
            self._evaluation_cache[cache_key] = final_score
            logger.info(f"Score final profondeur: {final_score}")
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation profondeur Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
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
        
        # Amélioration via Ollama si disponible
        try:
            if hasattr(self.llm, 'available') and self.llm.available:
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
            else:
                final_score = base_score
            
            self._evaluation_cache[cache_key] = final_score
            logger.info(f"Score final ton académique: {final_score}")
            return final_score
            
        except Exception as e:
            logger.warning(f"Erreur évaluation ton académique Ollama: {e}")
            self._evaluation_cache[cache_key] = base_score
            return base_score
    
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