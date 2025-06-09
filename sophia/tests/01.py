"""
Tests autonomes des améliorations SophIA
Version complète sans dépendances externes
"""

import sys
import os

# Configuration des imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Utilitaires de test intégrés (pas d'import externe)
def assert_valid_response(response, min_length=10):
    """Vérifie qu'une réponse SophIA est valide"""
    assert response is not None
    assert hasattr(response, 'natural_response')
    assert hasattr(response, 'conceptual_analysis')
    assert len(response.natural_response) >= min_length
    assert 'concepts_detected' in response.conceptual_analysis

def assert_concepts_detected(response, expected_concepts, min_match=1):
    """Vérifie que les concepts attendus sont détectés"""
    detected = response.conceptual_analysis.get('concepts_detected', [])
    matches = sum(1 for concept in expected_concepts if concept in detected)
    assert matches >= min_match, f"Expected at least {min_match} concepts from {expected_concepts}, got {detected}"

def measure_response_time(func, *args, **kwargs):
    """Mesure le temps de réponse d'une fonction"""
    import time
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def test_concept_bridge():
    """Teste le pont conceptuel amélioré"""
    print("🔗 Test du Concept Bridge...")
    
    try:
        from sophia.bridge.concept_text_bridge import EnhancedConceptTextBridge
        from sophia.core.ontology import SimpleOntology
        from sophia.llm.llama_interface import OllamaLLaMAInterface
        
        ontology = SimpleOntology()
        llm = OllamaLLaMAInterface()
        bridge = EnhancedConceptTextBridge(ontology, llm)
        
        # Test d'initialisation
        assert bridge.ontology is not None
        assert bridge.llm is not None
        assert len(bridge.concept_patterns) > 0
        print("  ✅ Initialisation réussie")
        
        # Test des synonymes améliorés
        print("  🔍 Test génération synonymes...")
        synonyms = bridge._get_concept_synonyms('VÉRITÉ')
        assert isinstance(synonyms, list)
        assert len(synonyms) > 0
        print(f"  ✅ Synonymes pour VÉRITÉ: {synonyms[:5]}...")
        
        # Test de l'extraction améliorée
        print("  🔍 Test extraction améliorée...")
        test_text = "La vérité philosophique est-elle relative à notre perception de la justice ?"
        base_extraction = {'concepts_detected': ['VÉRITÉ'], 'confidence': 0.8}
        
        enhanced = bridge.enhanced_concept_extraction(test_text, base_extraction)
        
        assert 'enhanced_confidence' in enhanced
        assert 'concept_matches' in enhanced
        assert 'concepts_detailed' in enhanced
        assert 0.0 <= enhanced['enhanced_confidence'] <= 1.0
        
        print(f"  ✅ Concepts détectés: {enhanced['concepts_detected']}")
        print(f"  ✅ Confiance améliorée: {enhanced['enhanced_confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur Bridge: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constraint_manager():
    """Teste le gestionnaire de contraintes"""
    print("\n⚖️ Test du Constraint Manager...")
    
    try:
        from sophia.constraints.constraint_manager import PhilosophicalConstraintManager
        from sophia.core.ontology import SimpleOntology
        from sophia.llm.llama_interface import OllamaLLaMAInterface
        
        ontology = SimpleOntology()
        llm = OllamaLLaMAInterface()
        constraint_manager = PhilosophicalConstraintManager(ontology, llm)
        
        # Test d'initialisation
        assert constraint_manager.ontology is not None
        assert constraint_manager.llm is not None
        assert len(constraint_manager.constraints) > 0
        assert len(constraint_manager.philosophical_clusters) > 0
        print("  ✅ Initialisation réussie")
        
        # Test des clusters philosophiques
        clusters = constraint_manager.philosophical_clusters
        cluster_names = [c['name'] for c in clusters]
        
        expected_clusters = ['Épistémologie', 'Éthique', 'Métaphysique']
        found_clusters = [name for name in expected_clusters if name in cluster_names]
        
        print(f"  ✅ Clusters trouvés: {found_clusters}")
        print(f"  ✅ Total clusters: {len(clusters)}")
        
        # Test de validation
        print("  🔍 Test validation réponse...")
        test_response = """La vérité est un concept philosophique fondamental. 
        Tout d'abord, elle peut être considérée comme absolue selon Platon. 
        Ensuite, elle peut être relative selon les sophistes. 
        Enfin, elle dépend de notre capacité à connaître la réalité."""
        
        test_context = {
            'concepts_detected': ['VÉRITÉ', 'CONNAISSANCE'],
            'question': 'Qu\'est-ce que la vérité ?'
        }
        
        validation = constraint_manager.validate_response(test_response, test_context)
        
        assert 'global_score' in validation
        assert 'constraint_results' in validation
        assert 'is_valid' in validation
        assert 0.0 <= validation['global_score'] <= 1.0
        
        print(f"  ✅ Score global: {validation['global_score']:.2f}")
        print(f"  ✅ Contraintes actives: {len(constraint_manager.constraints)}")
        print(f"  ✅ Validation réussie: {validation['is_valid']}")
        
        if validation.get('recommendations'):
            print(f"  💡 Recommandations: {len(validation['recommendations'])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur Constraints: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_sophia():
    """Teste SophIA avec les améliorations"""
    print("\n🧠 Test de SophIA Enhanced...")
    
    try:
        from sophia.core.sophia_hybrid import HybridSophIA
        
        print("  🚀 Initialisation...")
        sophia = HybridSophIA(session_name="test_enhanced", auto_save=False)
        
        # Vérifications d'initialisation
        assert hasattr(sophia, 'concept_bridge')
        assert hasattr(sophia, 'constraint_manager')
        assert sophia.concept_bridge is not None
        assert sophia.constraint_manager is not None
        
        print("  ✅ SophIA Enhanced initialisée !")
        print(f"  📚 Ontologie: {len(sophia.ontology.concepts)} concepts")
        print(f"  🔗 Bridge actif: True")
        print(f"  ⚖️ Constraint manager actif: True")
        
        # Test de conversation
        print("\n  💬 Test de conversation...")
        questions = [
            "Qu'est-ce que la vérité ?",
            "La justice peut-elle être absolue ?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n  📝 Question {i}: {question}")
            
            response = sophia.ask(question)
            
            # Vérifications de base
            assert_valid_response(response, min_length=30)
            assert hasattr(response, 'validation_report')
            assert response.confidence > 0.0
            
            print(f"    🧠 Réponse: {response.natural_response[:100]}...")
            
            concepts = response.conceptual_analysis.get('concepts_detected', [])
            print(f"    💡 Concepts: {concepts}")
            print(f"    🎯 Confiance: {response.confidence:.2f}")
            
            if 'global_score' in response.validation_report:
                print(f"    📊 Score validation: {response.validation_report['global_score']:.2f}")
        
        # Test du raisonnement détaillé
        print("\n  🔍 Test d'explication du raisonnement:")
        explanation = sophia.explain_reasoning("Qu'est-ce que la justice ?")
        
        required_steps = ['step1_concept_detection', 'step2_conceptual_reasoning', 
                         'step3_constraint_validation', 'step4_synthesis']
        
        for step in required_steps:
            assert step in explanation, f"Étape manquante: {step}"
        
        print(f"    ✅ Toutes les étapes présentes: {len(required_steps)}")
        print(f"    - Méthode: {explanation['step1_concept_detection']['method']}")
        
        if 'concepts_found' in explanation['step1_concept_detection']:
            concepts_found = explanation['step1_concept_detection']['concepts_found']
            print(f"    - Concepts trouvés: {concepts_found}")
        
        # Test du résumé amélioré
        print("\n  📊 Test du résumé de conversation:")
        summary = sophia.get_conversation_summary()
        
        assert 'total_interactions' in summary
        assert 'average_confidence' in summary
        
        print(f"    - Interactions: {summary['total_interactions']}")
        print(f"    - Confiance moyenne: {summary['average_confidence']:.2f}")
        
        if 'system_performance' in summary:
            perf = summary['system_performance']
            print(f"    - Bridge actif: {perf.get('concept_bridge_active', 'N/A')}")
            print(f"    - Constraints actifs: {perf.get('constraint_manager_active', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur SophIA Enhanced: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Teste les performances"""
    print("\n⚡ Test de Performance...")
    
    try:
        from sophia.core.sophia_hybrid import HybridSophIA
        
        sophia = HybridSophIA(session_name="test_perf", auto_save=False)
        
        question = "Qu'est-ce que la vérité ?"
        print(f"  🔍 Test avec question: {question}")
        
        response, duration = measure_response_time(sophia.ask, question)
        
        assert_valid_response(response)
        print(f"  ✅ Temps de réponse: {duration:.2f}s")
        
        # Évaluation performance
        if duration < 10.0:
            print(f"  🚀 Performance excellente (< 10s)")
        elif duration < 30.0:
            print(f"  ✅ Performance acceptable (< 30s)")
        else:
            print(f"  ⚠️ Performance lente (> 30s)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur Performance: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal"""
    print("🧪 TESTS DES AMÉLIORATIONS SOPHIA")
    print("=" * 60)
    
    tests = [
        ("Concept Bridge", test_concept_bridge),
        ("Constraint Manager", test_constraint_manager),
        ("SophIA Enhanced", test_enhanced_sophia),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🚀 Test: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
        except Exception as e:
            print(f"💥 {test_name}: ERREUR FATALE - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("-" * 30)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:<20} {status}")
    
    print(f"\n🎯 SCORE FINAL: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 TOUTES LES AMÉLIORATIONS FONCTIONNENT PARFAITEMENT !")
        print("\n🚀 Prochaines étapes:")
        print("1. Lance: python simple_interface.py")
        print("2. Lance: python launch_web.py") 
        print("3. Teste avec des questions complexes!")
        print("4. Observe les améliorations (synonymes, validation, etc.)")
    elif passed > 0:
        print(f"\n✅ {passed} améliorations fonctionnent, {total-passed} ont des problèmes.")
        print("Vérifiez les erreurs ci-dessus pour les corriger.")
    else:
        print("\n❌ Aucune amélioration ne fonctionne.")
        print("Vérifiez que les fichiers sont bien créés et les imports corrects.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    print(f"\n{'🎉 SUCCÈS' if success else '⚠️ ÉCHEC'} - Test terminé")