"""
Types et énumérations pour les concepts philosophiques
"""

from enum import Enum
from typing import Set, Dict, Any

class ConceptType(Enum):
    """Types de concepts philosophiques"""
    
    # Métaphysique
    ENTITY = "entity"                    # Être, Existence, Substance
    PROPERTY = "property"                # Qualités, Attributs
    RELATION = "relation"                # Relations ontologiques
    
    # Épistémologie  
    EPISTEMIC = "epistemic"              # Vérité, Connaissance, Croyance
    LOGICAL = "logical"                  # Arguments, Propositions
    
    # Éthique
    MORAL = "moral"                      # Bien, Mal, Justice
    VALUE = "value"                      # Valeurs morales
    
    # Esthétique
    AESTHETIC = "aesthetic"              # Beauté, Art, Goût
    
    # Domaines spécialisés
    POLITICAL = "political"              # Justice sociale, État
    PHILOSOPHICAL_DOMAIN = "domain"      # Métaphysique, Éthique comme domaines
    
    # Meta-concepts
    LEARNED_CONCEPT = "learned"          # Concepts appris dynamiquement
    USER_CONCEPT = "user_defined"        # Concepts définis par l'utilisateur

class RelationType(Enum):
    """Types de relations entre concepts"""
    
    # Relations logiques
    IMPLIES = "implies"                  # A implique B
    CONTRADICTS = "contradicts"          # A contredit B
    IS_EQUIVALENT = "is_equivalent"      # A équivaut à B
    
    # Relations ontologiques
    IS_A = "is_a"                       # A est un type de B
    PART_OF = "part_of"                 # A fait partie de B
    HAS_PROPERTY = "has_property"       # A a la propriété B
    
    # Relations causales
    CAUSES = "causes"                   # A cause B
    ENABLES = "enables"                 # A permet B
    PREVENTS = "prevents"               # A empêche B
    
    # Relations épistémiques
    DEFINES = "defines"                 # A définit B
    EXPLAINS = "explains"               # A explique B
    EVIDENCES = "evidences"             # A est une évidence pour B
    
    # Relations temporelles
    PRECEDES = "precedes"               # A précède B
    FOLLOWS = "follows"                 # A suit B
    
    # Relations d'opposition
    OPPOSES = "opposes"                 # A s'oppose à B
    COMPLEMENTS = "complements"         # A complète B
    
    # Relations personnalisées
    CUSTOM = "custom"                   # Relation définie par l'utilisateur

class PhilosophicalDomain(Enum):
    """Domaines philosophiques principaux"""
    
    METAPHYSICS = "metaphysics"
    EPISTEMOLOGY = "epistemology"
    ETHICS = "ethics"
    AESTHETICS = "aesthetics"
    LOGIC = "logic"
    POLITICAL_PHILOSOPHY = "political_philosophy"
    PHILOSOPHY_OF_MIND = "philosophy_of_mind"
    PHILOSOPHY_OF_LANGUAGE = "philosophy_of_language"
    PHILOSOPHY_OF_SCIENCE = "philosophy_of_science"

# Concepts philosophiques de base pré-définis
CORE_PHILOSOPHICAL_CONCEPTS = {
    # Métaphysique
    "ÊTRE": ConceptType.ENTITY,
    "EXISTENCE": ConceptType.ENTITY,
    "ESSENCE": ConceptType.PROPERTY,
    "SUBSTANCE": ConceptType.ENTITY,
    "ACCIDENT": ConceptType.PROPERTY,
    "NÉCESSITÉ": ConceptType.PROPERTY,
    "POSSIBILITÉ": ConceptType.PROPERTY,
    "ACTUALITÉ": ConceptType.PROPERTY,
    
    # Épistémologie
    "VÉRITÉ": ConceptType.EPISTEMIC,
    "CONNAISSANCE": ConceptType.EPISTEMIC,
    "CROYANCE": ConceptType.EPISTEMIC,
    "OPINION": ConceptType.EPISTEMIC,
    "DOUTE": ConceptType.EPISTEMIC,
    "CERTITUDE": ConceptType.EPISTEMIC,
    "ÉVIDENCE": ConceptType.EPISTEMIC,
    
    # Logique
    "ARGUMENT": ConceptType.LOGICAL,
    "PRÉMISSE": ConceptType.LOGICAL,
    "CONCLUSION": ConceptType.LOGICAL,
    "VALIDITÉ": ConceptType.LOGICAL,
    "SOLIDITÉ": ConceptType.LOGICAL,
    "CONTRADICTION": ConceptType.LOGICAL,
    "COHÉRENCE": ConceptType.LOGICAL,
    
    # Éthique
    "BIEN": ConceptType.MORAL,
    "MAL": ConceptType.MORAL,
    "JUSTICE": ConceptType.MORAL,
    "INJUSTICE": ConceptType.MORAL,
    "VERTU": ConceptType.VALUE,
    "VICE": ConceptType.VALUE,
    "DEVOIR": ConceptType.MORAL,
    "DROIT": ConceptType.MORAL,
    "RESPONSABILITÉ": ConceptType.MORAL,
    "LIBERTÉ": ConceptType.VALUE,
    
    # Esthétique
    "BEAUTÉ": ConceptType.AESTHETIC,
    "LAIDEUR": ConceptType.AESTHETIC,
    "ART": ConceptType.AESTHETIC,
    "GOÛT": ConceptType.AESTHETIC,
    "SUBLIME": ConceptType.AESTHETIC,
    
    "FAUSSETÉ": ConceptType.EPISTEMIC,
    "VALEUR": ConceptType.VALUE,
    "CONCEPT": ConceptType.ENTITY,  # Meta-concept

    # Métaphysique supplémentaires
    "IDENTITÉ": ConceptType.ENTITY,
    "DIFFÉRENCE": ConceptType.RELATION,
    "CAUSALITÉ": ConceptType.RELATION,
    "TEMPS": ConceptType.ENTITY,
    "ESPACE": ConceptType.ENTITY,
    "INFINI": ConceptType.PROPERTY,
    "CONTINGENCE": ConceptType.PROPERTY,
    "UNIVERSALITÉ": ConceptType.PROPERTY,
    "PARTICULARITÉ": ConceptType.PROPERTY,
    "MONDE": ConceptType.ENTITY,
    "OBJET": ConceptType.ENTITY,
    "SUJET": ConceptType.ENTITY,
    "PROCESSUS": ConceptType.ENTITY,
    "CHANGEMENT": ConceptType.RELATION,
    "CAUSE": ConceptType.RELATION,
    "EFFET": ConceptType.RELATION,

    # Épistémologie supplémentaires
    "RAISON": ConceptType.EPISTEMIC,
    "SENSATION": ConceptType.EPISTEMIC,
    "PERCEPTION": ConceptType.EPISTEMIC,
    "INTUITION": ConceptType.EPISTEMIC,
    "EXPLICATION": ConceptType.EPISTEMIC,
    "JUSTIFICATION": ConceptType.EPISTEMIC,
    "SCIENCE": ConceptType.EPISTEMIC,
    "THÉORIE": ConceptType.EPISTEMIC,
    "HYPOTHÈSE": ConceptType.EPISTEMIC,
    "EXPERIENCE": ConceptType.EPISTEMIC,
    "OBSERVATION": ConceptType.EPISTEMIC,
    "LANGAGE": ConceptType.EPISTEMIC,
    "SIGNIFICATION": ConceptType.EPISTEMIC,
    "RÉFÉRENCE": ConceptType.EPISTEMIC,

    # Logique supplémentaires
    "SYLLOGISME": ConceptType.LOGICAL,
    "PARADOXE": ConceptType.LOGICAL,
    "TAUTOLOGIE": ConceptType.LOGICAL,
    "ANTINOMIE": ConceptType.LOGICAL,
    "NÉGATION": ConceptType.LOGICAL,
    "IMPLICATION": ConceptType.LOGICAL,
    "CONJONCTION": ConceptType.LOGICAL,
    "DISJONCTION": ConceptType.LOGICAL,
    "INFERENCE": ConceptType.LOGICAL,
    "DÉDUCTION": ConceptType.LOGICAL,
    "INDUCTION": ConceptType.LOGICAL,
    "ABDUCTION": ConceptType.LOGICAL,

    # Éthique supplémentaires
    "BONHEUR": ConceptType.VALUE,
    "UTILITÉ": ConceptType.VALUE,
    "CONSÉQUENCE": ConceptType.VALUE,
    "INTENTION": ConceptType.VALUE,
    "AUTONOMIE": ConceptType.VALUE,
    "RESPECT": ConceptType.VALUE,
    "ÉGALITÉ": ConceptType.VALUE,
    "SOLIDARITÉ": ConceptType.VALUE,
    "ALTRUISME": ConceptType.VALUE,
    "ÉGOÏSME": ConceptType.VALUE,
    "LOI": ConceptType.MORAL,
    "SANCTION": ConceptType.MORAL,
    "PUNITION": ConceptType.MORAL,
    "RÉCOMPENSE": ConceptType.MORAL,

    # Esthétique supplémentaires
    "HARMONIE": ConceptType.AESTHETIC,
    "STYLE": ConceptType.AESTHETIC,
    "SYMBOLISME": ConceptType.AESTHETIC,
    "IMITATION": ConceptType.AESTHETIC,
    "CRÉATIVITÉ": ConceptType.AESTHETIC,
    "INTERPRÉTATION": ConceptType.AESTHETIC,

    # Philosophie politique
    "ÉTAT": ConceptType.POLITICAL,
    "SOCIÉTÉ": ConceptType.POLITICAL,
    "POUVOIR": ConceptType.POLITICAL,
    "AUTORITÉ": ConceptType.POLITICAL,
    "LÉGITIMITÉ": ConceptType.POLITICAL,
    "DÉMOCRATIE": ConceptType.POLITICAL,
    "LIBERTÉ_POLITIQUE": ConceptType.POLITICAL,
    "DROIT_NATUREL": ConceptType.POLITICAL,
    "CONTRAT_SOCIAL": ConceptType.POLITICAL,
    "CITOYENNETÉ": ConceptType.POLITICAL,

    # Philosophie de l'esprit
    "CONSCIENCE": ConceptType.ENTITY,
    "PENSÉE": ConceptType.ENTITY,
    "ESPRIT": ConceptType.ENTITY,
    "CORPS": ConceptType.ENTITY,
    "DUALISME": ConceptType.RELATION,
    "MONISME": ConceptType.RELATION,
    "INTENTIONNALITÉ": ConceptType.PROPERTY,
    "QUALIA": ConceptType.PROPERTY,

    # Philosophie du langage
    "SIGNIFIANT": ConceptType.ENTITY,
    "SIGNIFIÉ": ConceptType.ENTITY,
    "PRAGMATIQUE": ConceptType.PROPERTY,
    "SÉMANTIQUE": ConceptType.PROPERTY,
    "SYNTAQUE": ConceptType.PROPERTY,
    "ÉNONCÉ": ConceptType.ENTITY,
    "DISCOURS": ConceptType.ENTITY,

    # Philosophie des sciences
    "EXPLICATION_SCIENTIFIQUE": ConceptType.EPISTEMIC,
    "LOI_SCIENTIFIQUE": ConceptType.EPISTEMIC,
    "MODÈLE": ConceptType.EPISTEMIC,
    "RÉDUCTION": ConceptType.RELATION,
    "EMERGÉNCE": ConceptType.RELATION,
    "OBJECTIVITÉ": ConceptType.EPISTEMIC,
    "SUBJECTIVITÉ": ConceptType.EPISTEMIC,
    "RÉALISME": ConceptType.EPISTEMIC,
    "ANTIRÉALISME": ConceptType.EPISTEMIC,

    # Concepts ajoutés 
    "ETAT": ConceptType.POLITICAL,
    "LIMITÉ": ConceptType.PROPERTY,
    "OBÉISSANCE": ConceptType.POLITICAL,
    "CONTRE-POUVOIR": ConceptType.POLITICAL,
    "SAVOIR": ConceptType.EPISTEMIC,
    "JUGEMENT": ConceptType.AESTHETIC,
    "COMMUNICATION": ConceptType.EPISTEMIC,
    "EXPRESSION": ConceptType.EPISTEMIC,
    "PROGRÈS": ConceptType.EPISTEMIC,
    "PRÉDICTION": ConceptType.EPISTEMIC,
    "VÉRIFICATION": ConceptType.EPISTEMIC,
    "TRANSGRESSION": ConceptType.MORAL,
    "FINI": ConceptType.PROPERTY,
    "AFFIRMATION": ConceptType.LOGICAL,
    "ACTION": ConceptType.MORAL,
    "IGNORANCE": ConceptType.EPISTEMIC,
    "COMPRÉHENSION": ConceptType.EPISTEMIC,
    "ANARCHIE": ConceptType.POLITICAL,
    "RÉFLEXION": ConceptType.EPISTEMIC,
    "PROBABILITÉ": ConceptType.EPISTEMIC,
    "EXPLICATION": ConceptType.EPISTEMIC,
}

# Relations fondamentales pré-définies
CORE_RELATIONS = [
    ("EXISTENCE", RelationType.IMPLIES, "ÊTRE"),
    ("ESSENCE", RelationType.DEFINES, "ÊTRE"),
    ("CONNAISSANCE", RelationType.IMPLIES, "VÉRITÉ"),
    ("VÉRITÉ", RelationType.OPPOSES, "FAUSSETÉ"),
    ("BIEN", RelationType.OPPOSES, "MAL"),
    ("JUSTICE", RelationType.IS_A, "BIEN"),
    ("VERTU", RelationType.ENABLES, "BIEN"),
    ("ARGUMENT", RelationType.HAS_PROPERTY, "VALIDITÉ"),
    ("PRÉMISSE", RelationType.ENABLES, "CONCLUSION"),
    ("BEAUTÉ", RelationType.IS_A, "VALEUR"),
    ("LIBERTÉ", RelationType.ENABLES, "RESPONSABILITÉ"),

    # Métaphysique
    ("IDENTITÉ", RelationType.IS_EQUIVALENT, "ÊTRE"),
    ("DIFFÉRENCE", RelationType.CONTRADICTS, "IDENTITÉ"),
    ("CAUSALITÉ", RelationType.DEFINES, "CAUSE"),
    ("CAUSE", RelationType.CAUSES, "EFFET"),
    ("CHANGEMENT", RelationType.ENABLES, "PROCESSUS"),
    ("TEMPS", RelationType.PART_OF, "MONDE"),
    ("ESPACE", RelationType.PART_OF, "MONDE"),
    ("INFINI", RelationType.COMPLEMENTS, "FINI"),
    ("CONTINGENCE", RelationType.OPPOSES, "NÉCESSITÉ"),
    ("UNIVERSALITÉ", RelationType.OPPOSES, "PARTICULARITÉ"),
    ("OBJET", RelationType.OPPOSES, "SUJET"),

    # Épistémologie
    ("RAISON", RelationType.ENABLES, "CONNAISSANCE"),
    ("SENSATION", RelationType.ENABLES, "PERCEPTION"),
    ("PERCEPTION", RelationType.ENABLES, "CONNAISSANCE"),
    ("INTUITION", RelationType.ENABLES, "CONNAISSANCE"),
    ("JUSTIFICATION", RelationType.HAS_PROPERTY, "VÉRITÉ"),
    ("SCIENCE", RelationType.DEFINES, "THÉORIE"),
    ("THÉORIE", RelationType.ENABLES, "EXPLICATION"),
    ("HYPOTHÈSE", RelationType.PRECEDES, "THÉORIE"),
    ("OBSERVATION", RelationType.ENABLES, "EXPERIENCE"),
    ("LANGAGE", RelationType.ENABLES, "SIGNIFICATION"),
    ("SIGNIFICATION", RelationType.HAS_PROPERTY, "RÉFÉRENCE"),

    # Logique
    ("SYLLOGISME", RelationType.IS_A, "ARGUMENT"),
    ("PARADOXE", RelationType.CONTRADICTS, "TAUTOLOGIE"),
    ("NÉGATION", RelationType.OPPOSES, "AFFIRMATION"),
    ("IMPLICATION", RelationType.IMPLIES, "CONCLUSION"),
    ("CONJONCTION", RelationType.COMPLEMENTS, "DISJONCTION"),
    ("INFERENCE", RelationType.ENABLES, "CONCLUSION"),
    ("DÉDUCTION", RelationType.IS_A, "INFERENCE"),
    ("INDUCTION", RelationType.IS_A, "INFERENCE"),
    ("ABDUCTION", RelationType.IS_A, "INFERENCE"),

    # Éthique
    ("BONHEUR", RelationType.ENABLES, "BIEN"),
    ("UTILITÉ", RelationType.ENABLES, "BONHEUR"),
    ("CONSÉQUENCE", RelationType.FOLLOWS, "ACTION"),
    ("INTENTION", RelationType.PRECEDES, "ACTION"),
    ("AUTONOMIE", RelationType.ENABLES, "RESPONSABILITÉ"),
    ("RESPECT", RelationType.ENABLES, "JUSTICE"),
    ("ÉGALITÉ", RelationType.ENABLES, "JUSTICE"),
    ("SOLIDARITÉ", RelationType.ENABLES, "JUSTICE"),
    ("ALTRUISME", RelationType.OPPOSES, "ÉGOÏSME"),
    ("LOI", RelationType.ENABLES, "JUSTICE"),
    ("SANCTION", RelationType.FOLLOWS, "TRANSGRESSION"),
    ("PUNITION", RelationType.IS_A, "SANCTION"),
    ("RÉCOMPENSE", RelationType.OPPOSES, "PUNITION"),

    # Esthétique
    ("HARMONIE", RelationType.HAS_PROPERTY, "BEAUTÉ"),
    ("STYLE", RelationType.HAS_PROPERTY, "ART"),
    ("SYMBOLISME", RelationType.ENABLES, "INTERPRÉTATION"),
    ("IMITATION", RelationType.ENABLES, "ART"),
    ("CRÉATIVITÉ", RelationType.ENABLES, "ART"),

    # Philosophie politique
    ("ÉTAT", RelationType.PART_OF, "SOCIÉTÉ"),
    ("POUVOIR", RelationType.ENABLES, "AUTORITÉ"),
    ("AUTORITÉ", RelationType.ENABLES, "LÉGITIMITÉ"),
    ("DÉMOCRATIE", RelationType.IS_A, "ÉTAT"),
    ("LIBERTÉ_POLITIQUE", RelationType.ENABLES, "CITOYENNETÉ"),
    ("DROIT_NATUREL", RelationType.DEFINES, "CONTRAT_SOCIAL"),

    # Philosophie de l'esprit
    ("CONSCIENCE", RelationType.PART_OF, "ESPRIT"),
    ("PENSÉE", RelationType.PART_OF, "ESPRIT"),
    ("ESPRIT", RelationType.OPPOSES, "CORPS"),
    ("DUALISME", RelationType.OPPOSES, "MONISME"),
    ("INTENTIONNALITÉ", RelationType.HAS_PROPERTY, "CONSCIENCE"),
    ("QUALIA", RelationType.HAS_PROPERTY, "CONSCIENCE"),

    # Philosophie du langage
    ("SIGNIFIANT", RelationType.DEFINES, "SIGNIFIÉ"),
    ("PRAGMATIQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("SÉMANTIQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("SYNTAQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("ÉNONCÉ", RelationType.PART_OF, "DISCOURS"),

    # Philosophie des sciences
    ("EXPLICATION_SCIENTIFIQUE", RelationType.IS_A, "EXPLICATION"),
    ("LOI_SCIENTIFIQUE", RelationType.IS_A, "LOI"),
    ("MODÈLE", RelationType.ENABLES, "EXPLICATION_SCIENTIFIQUE"),
    ("RÉDUCTION", RelationType.OPPOSES, "EMERGÉNCE"),
    ("OBJECTIVITÉ", RelationType.OPPOSES, "SUBJECTIVITÉ"),
    ("RÉALISME", RelationType.OPPOSES, "ANTIRÉALISME"),

    # Métaphysique supplémentaires
    ("SUBSTANCE", RelationType.HAS_PROPERTY, "ESSENCE"),
    ("SUBSTANCE", RelationType.HAS_PROPERTY, "ACCIDENT"),
    ("ACTUALITÉ", RelationType.OPPOSES, "POSSIBILITÉ"),
    ("MONDE", RelationType.HAS_PROPERTY, "CONTINGENCE"),
    ("MONDE", RelationType.HAS_PROPERTY, "NÉCESSITÉ"),
    ("OBJET", RelationType.PART_OF, "MONDE"),
    ("SUJET", RelationType.PART_OF, "MONDE"),
    ("PROCESSUS", RelationType.ENABLES, "CHANGEMENT"),
    ("CHANGEMENT", RelationType.PRECEDES, "ETAT"),
    ("INFINI", RelationType.OPPOSES, "LIMITÉ"),
    ("ESPACE", RelationType.COMPLEMENTS, "TEMPS"),
    ("CAUSE", RelationType.PRECEDES, "EFFET"),
    ("EFFET", RelationType.FOLLOWS, "CAUSE"),
    ("ESSENCE", RelationType.DEFINES, "SUBSTANCE"),
    ("ACCIDENT", RelationType.PART_OF, "SUBSTANCE"),

    # Épistémologie supplémentaires
    ("CONNAISSANCE", RelationType.PREVENTS, "IGNORANCE"),
    ("CROYANCE", RelationType.PRECEDES, "CONNAISSANCE"),
    ("OPINION", RelationType.OPPOSES, "SAVOIR"),
    ("DOUTE", RelationType.OPPOSES, "CERTITUDE"),
    ("CERTITUDE", RelationType.ENABLES, "CONNAISSANCE"),
    ("ÉVIDENCE", RelationType.ENABLES, "CERTITUDE"),
    ("JUSTIFICATION", RelationType.ENABLES, "CROYANCE"),
    ("SCIENCE", RelationType.ENABLES, "CONNAISSANCE"),
    ("THÉORIE", RelationType.ENABLES, "HYPOTHÈSE"),
    ("EXPERIENCE", RelationType.ENABLES, "CONNAISSANCE"),
    ("OBSERVATION", RelationType.ENABLES, "THÉORIE"),
    ("LANGAGE", RelationType.ENABLES, "COMMUNICATION"),
    ("SIGNIFICATION", RelationType.ENABLES, "COMPRÉHENSION"),
    ("RÉFÉRENCE", RelationType.ENABLES, "SIGNIFICATION"),

    # Logique supplémentaires
    ("ARGUMENT", RelationType.HAS_PROPERTY, "SOLIDITÉ"),
    ("CONTRADICTION", RelationType.OPPOSES, "COHÉRENCE"),
    ("CONTRADICTION", RelationType.PREVENTS, "VALIDITÉ"),
    ("COHÉRENCE", RelationType.ENABLES, "VALIDITÉ"),
    ("PRÉMISSE", RelationType.PART_OF, "ARGUMENT"),
    ("CONCLUSION", RelationType.FOLLOWS, "PRÉMISSE"),
    ("SYLLOGISME", RelationType.ENABLES, "DÉDUCTION"),
    ("PARADOXE", RelationType.PREVENTS, "CONCLUSION"),
    ("NÉGATION", RelationType.CONTRADICTS, "AFFIRMATION"),
    ("IMPLICATION", RelationType.ENABLES, "DÉDUCTION"),
    ("CONJONCTION", RelationType.COMPLEMENTS, "DISJONCTION"),
    ("INFERENCE", RelationType.ENABLES, "ARGUMENT"),
    ("DÉDUCTION", RelationType.ENABLES, "CERTITUDE"),
    ("INDUCTION", RelationType.ENABLES, "PROBABILITÉ"),
    ("ABDUCTION", RelationType.ENABLES, "HYPOTHÈSE"),

    # Éthique supplémentaires
    ("BIEN", RelationType.COMPLEMENTS, "VERTU"),
    ("MAL", RelationType.COMPLEMENTS, "VICE"),
    ("JUSTICE", RelationType.OPPOSES, "INJUSTICE"),
    ("DEVOIR", RelationType.ENABLES, "JUSTICE"),
    ("DROIT", RelationType.ENABLES, "JUSTICE"),
    ("RESPONSABILITÉ", RelationType.ENABLES, "JUSTICE"),
    ("LIBERTÉ", RelationType.ENABLES, "AUTONOMIE"),
    ("BONHEUR", RelationType.ENABLES, "VERTU"),
    ("UTILITÉ", RelationType.ENABLES, "BONHEUR"),
    ("CONSÉQUENCE", RelationType.FOLLOWS, "ACTION"),
    ("INTENTION", RelationType.PRECEDES, "ACTION"),
    ("AUTONOMIE", RelationType.ENABLES, "RESPONSABILITÉ"),
    ("RESPECT", RelationType.ENABLES, "JUSTICE"),
    ("ÉGALITÉ", RelationType.ENABLES, "JUSTICE"),
    ("SOLIDARITÉ", RelationType.ENABLES, "JUSTICE"),
    ("ALTRUISME", RelationType.OPPOSES, "ÉGOÏSME"),
    ("LOI", RelationType.ENABLES, "JUSTICE"),
    ("SANCTION", RelationType.FOLLOWS, "TRANSGRESSION"),
    ("PUNITION", RelationType.IS_A, "SANCTION"),
    ("RÉCOMPENSE", RelationType.OPPOSES, "PUNITION"),
    ("VERTU", RelationType.ENABLES, "BIEN"),
    ("VICE", RelationType.ENABLES, "MAL"),
    ("DROIT", RelationType.ENABLES, "LIBERTÉ"),
    ("DEVOIR", RelationType.OPPOSES, "DROIT"),

    # Esthétique supplémentaires
    ("BEAUTÉ", RelationType.OPPOSES, "LAIDEUR"),
    ("ART", RelationType.ENABLES, "BEAUTÉ"),
    ("GOÛT", RelationType.ENABLES, "JUGEMENT"),
    ("SUBLIME", RelationType.COMPLEMENTS, "BEAUTÉ"),
    ("HARMONIE", RelationType.ENABLES, "BEAUTÉ"),
    ("STYLE", RelationType.HAS_PROPERTY, "ART"),
    ("SYMBOLISME", RelationType.ENABLES, "INTERPRÉTATION"),
    ("IMITATION", RelationType.ENABLES, "ART"),
    ("CRÉATIVITÉ", RelationType.ENABLES, "ART"),
    ("INTERPRÉTATION", RelationType.ENABLES, "JUGEMENT"),

    # Philosophie politique supplémentaires
    ("ÉTAT", RelationType.HAS_PROPERTY, "AUTORITÉ"),
    ("SOCIÉTÉ", RelationType.PART_OF, "MONDE"),
    ("POUVOIR", RelationType.ENABLES, "AUTORITÉ"),
    ("AUTORITÉ", RelationType.ENABLES, "LÉGITIMITÉ"),
    ("LÉGITIMITÉ", RelationType.ENABLES, "OBÉISSANCE"),
    ("DÉMOCRATIE", RelationType.IS_A, "ÉTAT"),
    ("LIBERTÉ_POLITIQUE", RelationType.ENABLES, "CITOYENNETÉ"),
    ("DROIT_NATUREL", RelationType.DEFINES, "CONTRAT_SOCIAL"),
    ("CONTRAT_SOCIAL", RelationType.ENABLES, "ÉTAT"),
    ("CITOYENNETÉ", RelationType.PART_OF, "SOCIÉTÉ"),
    ("ÉTAT", RelationType.OPPOSES, "ANARCHIE"),
    ("POUVOIR", RelationType.OPPOSES, "CONTRE-POUVOIR"),

    # Philosophie de l'esprit supplémentaires
    ("CONSCIENCE", RelationType.PART_OF, "ESPRIT"),
    ("PENSÉE", RelationType.PART_OF, "ESPRIT"),
    ("ESPRIT", RelationType.OPPOSES, "CORPS"),
    ("DUALISME", RelationType.OPPOSES, "MONISME"),
    ("INTENTIONNALITÉ", RelationType.HAS_PROPERTY, "CONSCIENCE"),
    ("QUALIA", RelationType.HAS_PROPERTY, "CONSCIENCE"),
    ("ESPRIT", RelationType.ENABLES, "PENSÉE"),
    ("CORPS", RelationType.ENABLES, "SENSATION"),
    ("CONSCIENCE", RelationType.ENABLES, "RÉFLEXION"),
    ("PENSÉE", RelationType.ENABLES, "ACTION"),

    # Philosophie du langage supplémentaires
    ("SIGNIFIANT", RelationType.DEFINES, "SIGNIFIÉ"),
    ("PRAGMATIQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("SÉMANTIQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("SYNTAQUE", RelationType.HAS_PROPERTY, "LANGAGE"),
    ("ÉNONCÉ", RelationType.PART_OF, "DISCOURS"),
    ("DISCOURS", RelationType.ENABLES, "COMMUNICATION"),
    ("LANGAGE", RelationType.ENABLES, "PENSÉE"),
    ("SIGNIFIÉ", RelationType.ENABLES, "COMPRÉHENSION"),
    ("SIGNIFIANT", RelationType.ENABLES, "EXPRESSION"),

    # Philosophie des sciences supplémentaires
    ("EXPLICATION_SCIENTIFIQUE", RelationType.IS_A, "EXPLICATION"),
    ("LOI_SCIENTIFIQUE", RelationType.IS_A, "LOI"),
    ("MODÈLE", RelationType.ENABLES, "EXPLICATION_SCIENTIFIQUE"),
    ("RÉDUCTION", RelationType.OPPOSES, "EMERGÉNCE"),
    ("OBJECTIVITÉ", RelationType.OPPOSES, "SUBJECTIVITÉ"),
    ("RÉALISME", RelationType.OPPOSES, "ANTIRÉALISME"),
    ("SCIENCE", RelationType.ENABLES, "PROGRÈS"),
    ("PROGRÈS", RelationType.FOLLOWS, "SCIENCE"),
    ("THÉORIE", RelationType.ENABLES, "PRÉDICTION"),
    ("PRÉDICTION", RelationType.ENABLES, "EXPLICATION"),
    ("EXPERIENCE", RelationType.ENABLES, "VÉRIFICATION"),
    ("VÉRIFICATION", RelationType.ENABLES, "CONNAISSANCE"),
]