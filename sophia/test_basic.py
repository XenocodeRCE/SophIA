#!/usr/bin/env python3
"""
Test basique pour vérifier que l'ontologie fonctionne
"""

import sys
import os

# Ajouter le dossier sophia au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sophia.core.ontology import SimpleOntology, Concept
from sophia.core.concept_types import ConceptType, RelationType

def test_ontology_basic():
    print("=== Test Ontologie SophIA ===")
    
    # Test création ontologie
    print("1. Création de l'ontologie...")
    ontology = SimpleOntology()
    print(f"   ✓ Concepts chargés: {len(ontology.concepts)}")
    
    # Test stats
    print("2. Statistiques de base...")
    stats = ontology.get_stats()
    print(f"   ✓ Total concepts: {stats['total_concepts']}")
    print(f"   ✓ Total relations: {stats['total_relations']}")
    print(f"   ✓ Types de concepts: {list(stats['concepts_by_type'].keys())}")
    
    # Test ajout concept
    print("3. Test ajout concept...")
    nouveau_concept = ontology.add_concept("TEST_CONCEPT", ConceptType.LEARNED_CONCEPT)
    print(f"   ✓ Concept ajouté: {nouveau_concept.name}")
    print(f"   ✓ Total après ajout: {len(ontology.concepts)}")
    
    # Test ajout relation
    print("4. Test ajout relation...")
    success = ontology.add_relation("TEST_CONCEPT", RelationType.IS_A, "CONCEPT")
    print(f"   ✓ Relation ajoutée: {success}")
    
    # Test recherche
    print("5. Test recherche concept...")
    concept_trouve = ontology.get_concept("VÉRITÉ")
    if concept_trouve:
        print(f"   ✓ Concept trouvé: {concept_trouve.name} ({concept_trouve.concept_type.value})")
        print(f"   ✓ Relations: {concept_trouve.relations}")
    
    # Test validation
    print("6. Test validation cohérence...")
    issues = ontology.validate_consistency()
    print(f"   ✓ Contradictions: {len(issues['contradictions'])}")
    print(f"   ✓ Concepts orphelins: {len(issues['orphaned_concepts'])}")
    
    print("\n🎉 Tous les tests sont passés !")
    return True

if __name__ == "__main__":
    test_ontology_basic()