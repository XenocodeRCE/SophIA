#!/usr/bin/env python3
"""
Test basique pour vérifier que l'ontologie fonctionne
"""

import sys
import os

# Ajouter le dossier sophia au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sophia.models.lcm_core import SimpleLCM
from sophia.core.ontology import SimpleOntology, Concept
from sophia.core.concept_types import ConceptType, RelationType
from sophia.training.trainer import SimpleLCMTrainer, OntologyAwareLCMTrainer
# Ajoute ces imports
from sophia.storage.serializer import LCMSerializer
from sophia.storage.session import TrainingSession
from sophia.llm.llama_interface import LLaMAInterface


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

# Ajoute cette fonction de test
def test_lcm_basic():
    print("\n=== Test LCM de base ===")
    
    # Création ontologie et LCM
    ontology = SimpleOntology()
    lcm = SimpleLCM(ontology)
    
    print(f"1. LCM créé avec {len(ontology.concepts)} concepts")
    
    # Test ajout transitions manuelles
    lcm.add_transition("VÉRITÉ", "CONNAISSANCE", 0.8)
    lcm.add_transition("CONNAISSANCE", "ÊTRE", 0.7)
    lcm.add_transition("ÊTRE", "EXISTENCE", 0.9)
    
    print("2. Transitions ajoutées")
    print(f"   Total transitions: {len(lcm.transitions)}")
    
    # Test génération séquence
    sequence = lcm.generate_sequence("VÉRITÉ", length=4)
    print(f"3. Séquence générée: {[c.name for c in sequence]}")
    
    # Test statistiques
    stats = lcm.get_model_stats()
    print(f"4. Stats LCM: {stats}")
    
    return True

def test_training_system():
    print("\n=== Test Système d'entraînement ===")
    
    # Setup
    ontology = SimpleOntology()
    lcm = SimpleLCM(ontology)
    trainer = OntologyAwareLCMTrainer(lcm, ontology)
    
    # Création de séquences d'entraînement philosophiques
    training_sequences = [
        # Séquences épistémologiques
        [ontology.get_concept("DOUTE"), ontology.get_concept("VÉRITÉ"), ontology.get_concept("CONNAISSANCE")],
        [ontology.get_concept("VÉRITÉ"), ontology.get_concept("CONNAISSANCE"), ontology.get_concept("ÊTRE")],
        [ontology.get_concept("CONNAISSANCE"), ontology.get_concept("ÊTRE"), ontology.get_concept("EXISTENCE")],
        
        # Séquences éthiques
        [ontology.get_concept("BIEN"), ontology.get_concept("VERTU"), ontology.get_concept("JUSTICE")],
        [ontology.get_concept("JUSTICE"), ontology.get_concept("BIEN"), ontology.get_concept("VERTU")],
        [ontology.get_concept("LIBERTÉ"), ontology.get_concept("RESPONSABILITÉ"), ontology.get_concept("MORALE")],
        
        # Séquences logiques
        [ontology.get_concept("ARGUMENT"), ontology.get_concept("PRÉMISSE"), ontology.get_concept("CONCLUSION")],
        [ontology.get_concept("PRÉMISSE"), ontology.get_concept("VALIDITÉ"), ontology.get_concept("CONCLUSION")],
    ]
    
    # Filtrer les concepts None
    training_sequences = [[c for c in seq if c is not None] for seq in training_sequences]
    training_sequences = [seq for seq in training_sequences if len(seq) >= 2]
    
    print(f"1. Séquences d'entraînement préparées: {len(training_sequences)}")
    
    # Entraînement
    print("2. Début de l'entraînement...")
    training_history = trainer.train(training_sequences, epochs=5, verbose=True)
    
    print(f"3. Entraînement terminé: {len(training_history)} époques")
    
    # Test génération après entraînement
    print("4. Test génération après entraînement:")
    for start_concept in ["VÉRITÉ", "BIEN", "ARGUMENT"]:
        if ontology.get_concept(start_concept):
            sequence = lcm.generate_sequence(start_concept, length=4)
            print(f"   {start_concept}: {[c.name for c in sequence]}")
    
    # Résumé de l'entraînement
    summary = trainer.get_training_summary()
    print(f"5. Résumé: Loss finale={summary['final_loss']:.4f}, "
          f"Cohérence={summary['final_coherence']:.3f}")
    
    return True

def test_save_load_system():
    print("\n=== Test Système de sauvegarde ===")
    
    # Setup modèle entraîné
    ontology = SimpleOntology()
    lcm = SimpleLCM(ontology)
    trainer = OntologyAwareLCMTrainer(lcm, ontology)
    
    # Entraînement rapide
    training_sequences = [
        [ontology.get_concept("VÉRITÉ"), ontology.get_concept("CONNAISSANCE"), ontology.get_concept("ÊTRE")],
        [ontology.get_concept("BIEN"), ontology.get_concept("VERTU"), ontology.get_concept("JUSTICE")],
    ]
    training_sequences = [[c for c in seq if c is not None] for seq in training_sequences]
    
    trainer.train(training_sequences, epochs=3, verbose=False)
    
    print("1. Modèle entraîné préparé")
    
    # Test session d'entraînement
    session = TrainingSession("test_session")
    
    # Sauvegarde checkpoints
    checkpoint1 = session.save_checkpoint(lcm, ontology, trainer, epoch=1, 
                                         metrics={'loss': 0.5, 'coherence': 0.8})
    checkpoint2 = session.save_checkpoint(lcm, ontology, trainer, epoch=2, 
                                         metrics={'loss': 0.3, 'coherence': 0.9})
    
    print(f"2. Checkpoints sauvegardés: {len(session.list_checkpoints())}")
    
    # Sauvegarde modèle final
    final_path = session.save_final_model(lcm, ontology, trainer, 
                                         final_metrics={'final_loss': 0.1})
    
    print("3. Modèle final sauvegardé")
    
    # Test chargement
    loaded_model, loaded_ontology, loaded_trainer, metadata = session.load_checkpoint(1)
    
    print(f"4. Checkpoint chargé - Concepts: {len(loaded_ontology.concepts)}, "
          f"Transitions: {len(loaded_model.transitions)}")
    
    # Test génération avec modèle chargé
    if loaded_ontology.get_concept("VÉRITÉ"):
        sequence = loaded_model.generate_sequence("VÉRITÉ", length=3)
        print(f"5. Génération avec modèle chargé: {[c.name for c in sequence]}")
    
    # Résumé session
    summary = session.get_session_summary()
    print(f"6. Résumé session: {summary['checkpoints_count']} checkpoints, "
          f"{summary['total_size_mb']:.2f} MB")
    
    return True

def test_llama_interface():
    print("\n=== Test Interface LLaMA ===")
    
    # Initialisation de l'interface (peut prendre du temps au premier chargement)
    print("1. Initialisation LLaMA (peut prendre quelques minutes)...")
    llama = LLaMAInterface()
    
    # Info sur le modèle
    model_info = llama.get_model_info()
    print(f"2. Modèle chargé: {model_info['status']}")
    print(f"   Nom: {model_info['model_name']}")
    print(f"   Paramètres: {model_info.get('parameters', 0):,}")
    
    # Test génération simple
    print("3. Test génération de texte...")
    prompt = "Qu'est-ce que la vérité en philosophie ?"
    response = llama.generate_text(prompt, max_tokens=100)
    print(f"   Prompt: {prompt}")
    print(f"   Réponse: {response[:200]}...")
    
    # Test extraction de concepts
    print("4. Test extraction de concepts...")
    ontology = SimpleOntology()
    available_concepts = list(ontology.concepts.keys())
    
    text = "La vérité est liée à la connaissance et à l'être"
    extraction = llama.extract_concepts_from_text(text, available_concepts)
    print(f"   Texte: {text}")
    print(f"   Concepts extraits: {extraction['concepts_detected']}")
    print(f"   Confiance: {extraction['confidence']}")
    
    # Test génération avec contraintes
    print("5. Test génération contrainte...")
    constraints = {
        'required_concepts': ['VÉRITÉ', 'CONNAISSANCE'],
        'max_tokens': 80
    }
    
    constrained_response = llama.generate_with_constraints(
        "Explique la relation entre vérité et connaissance", 
        constraints
    )
    
    print(f"   Contraintes satisfaites: {constrained_response['constraints_satisfied']}")
    print(f"   Réponse: {constrained_response['text'][:150]}...")
    
    return True

if __name__ == "__main__":
    test_ontology_basic()
    test_lcm_basic()
    test_training_system()
    test_save_load_system()
    test_llama_interface()