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
    
    # Concepts manquants
    "FAUSSETÉ": ConceptType.EPISTEMIC,
    "VALEUR": ConceptType.VALUE,
    "CONCEPT": ConceptType.ENTITY,  # Meta-concept
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
]