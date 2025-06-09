"""
Tests autonomes des améliorations SophIA - VERSION AVEC TOUS LES LOGS
Version complète avec debug détaillé pour diagnostiquer le freeze
"""

import sys
import os
import time
import logging

# CONFIGURATION LOGGING COMPLÈTE EN PREMIER
print("🔧 Configuration du logging...")
logging.basicConfig(
    level=logging.DEBUG,
    format='🕒 %(asctime)s | 📦 %(name)20s | 🔍 %(levelname)8s | 💬 %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

# Activation de TOUS les logs SophIA
loggers_to_activate = [
    'sophia',
    'sophia.bridge', 
    'sophia.bridge.concept_text_bridge',
    'sophia.llm',
    'sophia.llm.llama_interface', 
    'sophia.constraints',
    'sophia.core',
    'sophia.core.ontology',
    'requests',
    'urllib3'
]

for logger_name in loggers_to_activate:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

print("✅ Logging configuré pour tous les modules SophIA")

# Configuration des imports
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
print(f"📁 ROOT_DIR configuré: {ROOT_DIR}")

# Utilitaires de test intégrés
def assert_valid_response(response, min_length=10):
    """Vérifie qu'une réponse SophIA est valide"""
    print(f"🔍 Validation réponse (min_length={min_length})")
    assert response is not None
    assert hasattr(response, 'natural_response')
    assert hasattr(response, 'conceptual_analysis')
    assert len(response.natural_response) >= min_length
    assert 'concepts_detected' in response.conceptual_analysis
    print("✅ Réponse valide")

def assert_concepts_detected(response, expected_concepts, min_match=1):
    """Vérifie que les concepts attendus sont détectés"""
    print(f"🔍 Vérification concepts (attendus: {expected_concepts}, min_match={min_match})")
    detected = response.conceptual_analysis.get('concepts_detected', [])
    matches = sum(1 for concept in expected_concepts if concept in detected)
    assert matches >= min_match, f"Expected at least {min_match} concepts from {expected_concepts}, got {detected}"
    print(f"✅ {matches} concepts trouvés sur {len(expected_concepts)} attendus")

def measure_response_time(func, *args, **kwargs):
    """Mesure le temps de réponse d'une fonction"""
    print(f"⏱️ Début mesure temps pour {func.__name__}")
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    duration = end - start
    print(f"⏱️ Fin mesure: {duration:.2f}s")
    return result, duration

def test_concept_bridge():
    """Teste le pont conceptuel amélioré"""
    print("\n" + "="*60)
    print("🔗 DÉBUT TEST CONCEPT BRIDGE")
    print("="*60)
    
    try:
        print("📥 Import des modules Concept Bridge...")
        print("  📦 Import EnhancedConceptTextBridge...")
        from sophia.bridge.concept_text_bridge import EnhancedConceptTextBridge
        print("  ✅ EnhancedConceptTextBridge importé")
        
        print("  📦 Import SimpleOntology...")
        from sophia.core.ontology import SimpleOntology
        print("  ✅ SimpleOntology importé")
        
        print("  📦 Import OllamaLLaMAInterface...")
        from sophia.llm.llama_interface import OllamaLLaMAInterface
        print("  ✅ OllamaLLaMAInterface importé")
        
        print("\n🏗️ Création des composants...")
        
        print("  🏗️ Création ontologie...")
        start_time = time.time()
        ontology = SimpleOntology()
        ontology_time = time.time() - start_time
        print(f"  ✅ Ontologie créée en {ontology_time:.3f}s avec {len(ontology.concepts)} concepts")
        
        print("  🦙 Création interface LLaMA...")
        start_time = time.time()
        llm = OllamaLLaMAInterface()
        llm_time = time.time() - start_time
        print(f"  ✅ LLaMA interface créée en {llm_time:.3f}s")
        
        # Vérification status LLaMA AVANT d'utiliser
        print("  🔍 Vérification status LLaMA...")
        try:
            llm_info = llm.get_model_info()
            print(f"  📊 LLaMA Info complète: {llm_info}")
            print(f"  📊 LLaMA disponible: {getattr(llm, 'available', 'N/A')}")
            print(f"  📊 LLaMA status: {llm_info.get('status', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️ Erreur récupération info LLaMA: {e}")
        
        print("\n🌉 CRÉATION DU CONCEPT BRIDGE...")
        print("⚠️  ATTENTION: Cette étape peut prendre du temps ou freezer!")
        print("⚠️  Appel à Ollama pour génération de synonymes...")
        
        start_time = time.time()
        print(f"⏰ Début création bridge: {time.strftime('%H:%M:%S')}")
        
        # Création avec suivi détaillé
        bridge = EnhancedConceptTextBridge(ontology, llm)
        
        bridge_time = time.time() - start_time
        print(f"✅ Bridge créé en {bridge_time:.2f}s")
        
        # Test d'initialisation
        print("\n🔍 Vérification initialisation bridge...")
        assert bridge.ontology is not None
        print("  ✅ Ontologie attachée")
        assert bridge.llm is not None
        print("  ✅ LLM attaché")
        assert len(bridge.concept_patterns) > 0
        print(f"  ✅ {len(bridge.concept_patterns)} patterns de concepts")
        assert hasattr(bridge, '_synonyms_cache')
        print(f"  ✅ Cache synonymes: {len(bridge._synonyms_cache)} entrées")
        assert hasattr(bridge, '_context_cache')
        print(f"  ✅ Cache contexte: {len(bridge._context_cache)} entrées")
        
        # Test des synonymes améliorés
        print("\n🔍 Test génération synonymes...")
        test_concepts = ['VÉRITÉ', 'JUSTICE', 'LIBERTÉ']
        
        for concept in test_concepts:
            print(f"  🔍 Test synonymes pour {concept}...")
            start_time = time.time()
            
            synonyms = bridge._get_concept_synonyms(concept)
            
            synonyms_time = time.time() - start_time
            print(f"  ✅ Synonymes {concept} générés en {synonyms_time:.2f}s: {synonyms[:3]}...")
        
        # Test de l'extraction améliorée
        print("\n🔍 Test extraction améliorée...")
        test_text = "La vérité philosophique est-elle relative à notre perception de la justice ?"
        base_extraction = {'concepts_detected': ['VÉRITÉ'], 'confidence': 0.8}
        
        print(f"  📝 Texte test: {test_text}")
        print(f"  📝 Extraction base: {base_extraction}")
        
        start_time = time.time()
        enhanced = bridge.enhanced_concept_extraction(test_text, base_extraction)
        extraction_time = time.time() - start_time
        
        print(f"  ✅ Extraction améliorée en {extraction_time:.2f}s")
        
        # Vérifications
        assert 'enhanced_confidence' in enhanced
        print(f"  ✅ Confiance améliorée: {enhanced['enhanced_confidence']:.3f}")
        
        assert 'concept_matches' in enhanced
        print(f"  ✅ Matches trouvés: {len(enhanced['concept_matches'])}")
        
        assert 'concepts_detailed' in enhanced
        print(f"  ✅ Concepts détaillés: {len(enhanced['concepts_detailed'])}")
        
        assert enhanced['enhanced_confidence'] >= 0.0
        assert enhanced['enhanced_confidence'] <= 1.0
        print("  ✅ Confiance dans les limites [0,1]")

        print(f"\n📊 RÉSULTATS BRIDGE:")
        print(f"  🎯 Concepts détectés: {enhanced['concepts_detected']}")
        print(f"  🎯 Confiance améliorée: {enhanced['enhanced_confidence']:.3f}")
        print(f"  🎯 Temps total: {bridge_time + extraction_time:.2f}s")
        
        print("✅ TEST CONCEPT BRIDGE RÉUSSI")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR CONCEPT BRIDGE: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constraint_manager():
    """Teste le gestionnaire de contraintes"""
    print("\n" + "="*60)
    print("⚖️ DÉBUT TEST CONSTRAINT MANAGER")
    print("="*60)
    
    try:
        print("📥 Import des modules Constraint Manager...")
        from sophia.constraints.constraint_manager import PhilosophicalConstraintManager
        from sophia.core.ontology import SimpleOntology
        from sophia.llm.llama_interface import OllamaLLaMAInterface
        print("✅ Imports réussis")
        
        print("\n🏗️ Création des composants...")
        ontology = SimpleOntology()
        llm = OllamaLLaMAInterface()
        print("✅ Composants créés")
        
        print("⚖️ Création Constraint Manager...")
        start_time = time.time()
        constraint_manager = PhilosophicalConstraintManager(ontology, llm)
        manager_time = time.time() - start_time
        print(f"✅ Manager créé en {manager_time:.2f}s")
        
        # Test d'initialisation
        print("\n🔍 Vérification initialisation...")
        assert constraint_manager.ontology is not None
        print("  ✅ Ontologie attachée")
        assert constraint_manager.llm is not None
        print("  ✅ LLM attaché")
        assert len(constraint_manager.constraints) > 0
        print(f"  ✅ {len(constraint_manager.constraints)} contraintes")
        assert len(constraint_manager.philosophical_clusters) > 0
        print(f"  ✅ {len(constraint_manager.philosophical_clusters)} clusters")
        
        # Test des clusters philosophiques
        print("\n🔍 Test des clusters philosophiques...")
        clusters = constraint_manager.philosophical_clusters
        cluster_names = [c['name'] for c in clusters]
        
        expected_clusters = ['Épistémologie', 'Éthique', 'Métaphysique']
        found_clusters = [name for name in expected_clusters if name in cluster_names]
        
        print(f"  📊 Clusters attendus: {expected_clusters}")
        print(f"  📊 Clusters trouvés: {found_clusters}")
        print(f"  📊 Total clusters: {len(clusters)}")
        
        for cluster in clusters:
            print(f"    🏷️ {cluster['name']}: {len(cluster['concepts'])} concepts, {len(cluster['themes'])} thèmes")
        
        # Test de validation
        print("\n🔍 Test validation réponse...")
        test_response = """La vérité est un concept philosophique fondamental. 
        Tout d'abord, elle peut être considérée comme absolue selon Platon. 
        Ensuite, elle peut être relative selon les sophistes. 
        Enfin, elle dépend de notre capacité à connaître la réalité."""
        
        test_context = {
            'concepts_detected': ['VÉRITÉ', 'CONNAISSANCE'],
            'question': 'Qu\'est-ce que la vérité ?'
        }
        
        print(f"  📝 Réponse test: {test_response[:50]}...")
        print(f"  📝 Contexte: {test_context}")
        
        start_time = time.time()
        validation = constraint_manager.validate_response(test_response, test_context)
        validation_time = time.time() - start_time
        print(f"  ✅ Validation en {validation_time:.2f}s")
        
        # Vérifications
        assert 'global_score' in validation
        assert 'constraint_results' in validation
        assert 'is_valid' in validation
        assert 0.0 <= validation['global_score'] <= 1.0
        
        print(f"\n📊 RÉSULTATS VALIDATION:")
        print(f"  🎯 Score global: {validation['global_score']:.3f}")
        print(f"  🎯 Contraintes actives: {len(constraint_manager.constraints)}")
        print(f"  🎯 Validation réussie: {validation['is_valid']}")
        print(f"  🎯 Violations: {len(validation.get('violations', []))}")
        
        if validation.get('recommendations'):
            print(f"  💡 Recommandations: {len(validation['recommendations'])}")
            for rec in validation['recommendations'][:2]:
                print(f"    💡 {rec}")
        
        print("✅ TEST CONSTRAINT MANAGER RÉUSSI")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR CONSTRAINT MANAGER: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_sophia():
    """Teste SophIA avec les améliorations"""
    print("\n" + "="*60)
    print("🧠 DÉBUT TEST SOPHIA ENHANCED")
    print("="*60)
    
    try:
        print("📥 Import SophIA Enhanced...")
        from sophia.core.sophia_hybrid import HybridSophIA
        print("✅ Import réussi")
        
        print("\n🚀 Initialisation SophIA Enhanced...")
        print("⚠️  Cette étape peut prendre du temps (création bridge + constraints)...")
        
        start_time = time.time()
        sophia = HybridSophIA(session_name="test_enhanced", auto_save=False)
        init_time = time.time() - start_time
        print(f"✅ SophIA Enhanced initialisée en {init_time:.2f}s")
        
        # Vérifications d'initialisation
        print("\n🔍 Vérification des composants...")
        assert hasattr(sophia, 'concept_bridge')
        print("  ✅ Concept bridge présent")
        assert hasattr(sophia, 'constraint_manager')
        print("  ✅ Constraint manager présent")
        assert sophia.concept_bridge is not None
        print("  ✅ Concept bridge initialisé")
        assert sophia.constraint_manager is not None
        print("  ✅ Constraint manager initialisé")
        
        print(f"\n📊 COMPOSANTS SOPHIA:")
        print(f"  📚 Ontologie: {len(sophia.ontology.concepts)} concepts")
        print(f"  🔗 Bridge cache: {len(getattr(sophia.concept_bridge, '_synonyms_cache', {}))}")
        print(f"  ⚖️ Contraintes: {len(sophia.constraint_manager.constraints)}")
        print(f"  🎯 Clusters: {len(sophia.constraint_manager.philosophical_clusters)}")
        
        # Test de conversation
        print("\n💬 Test de conversation...")
        questions = [
            "Qu'est-ce que la vérité ?",
            "La justice peut-elle être absolue ?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n📝 Question {i}: {question}")
            
            start_time = time.time()
            response = sophia.ask(question)
            response_time = time.time() - start_time
            
            print(f"⏱️ Réponse générée en {response_time:.2f}s")
            
            # Vérifications de base
            assert_valid_response(response, min_length=30)
            assert hasattr(response, 'validation_report')
            assert response.confidence > 0.0
            
            print(f"  🧠 Réponse: {response.natural_response[:100]}...")
            
            concepts = response.conceptual_analysis.get('concepts_detected', [])
            print(f"  💡 Concepts: {concepts}")
            print(f"  🎯 Confiance: {response.confidence:.3f}")
            
            if 'global_score' in response.validation_report:
                print(f"  📊 Score validation: {response.validation_report['global_score']:.3f}")
            
            # Détails supplémentaires
            if hasattr(response, 'lcm_reasoning'):
                lcm_paths = response.lcm_reasoning.get('reasoning_paths', [])
                print(f"  🧠 Chemins LCM: {len(lcm_paths)}")
        
        print("✅ TEST SOPHIA ENHANCED RÉUSSI")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR SOPHIA ENHANCED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Teste les performances"""
    print("\n" + "="*60)
    print("⚡ DÉBUT TEST PERFORMANCE")
    print("="*60)
    
    try:
        print("🚀 Initialisation pour test performance...")
        from sophia.core.sophia_hybrid import HybridSophIA
        
        start_time = time.time()
        sophia = HybridSophIA(session_name="test_perf", auto_save=False)
        init_time = time.time() - start_time
        print(f"✅ Initialisation en {init_time:.2f}s")
        
        question = "Qu'est-ce que la vérité ?"
        print(f"📝 Question test: {question}")
        
        response, duration = measure_response_time(sophia.ask, question)
        
        assert_valid_response(response)
        print(f"✅ Réponse valide générée")
        
        # Évaluation performance
        if duration < 10.0:
            perf_level = "🚀 EXCELLENTE"
        elif duration < 30.0:
            perf_level = "✅ ACCEPTABLE"
        elif duration < 60.0:
            perf_level = "⚠️ LENTE"
        else:
            perf_level = "❌ TRÈS LENTE"
        
        print(f"\n📊 RÉSULTATS PERFORMANCE:")
        print(f"  ⏱️ Temps de réponse: {duration:.2f}s")
        print(f"  📈 Niveau: {perf_level}")
        print(f"  🎯 Seuils: <10s=Excellent, <30s=Acceptable, <60s=Lent")
        
        print("✅ TEST PERFORMANCE TERMINÉ")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR PERFORMANCE: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal avec logs complets"""
    print("🧪 TESTS DES AMÉLIORATIONS SOPHIA - VERSION LOGS COMPLETS")
    print("=" * 80)
    print(f"🕒 Début des tests: {time.strftime('%H:%M:%S')}")
    print(f"📁 Répertoire racine: {ROOT_DIR}")
    print("=" * 80)
    
    tests = [
        ("Concept Bridge", test_concept_bridge),
        ("Constraint Manager", test_constraint_manager),
        ("SophIA Enhanced", test_enhanced_sophia),
        ("Performance", test_performance)
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n🚀 LANCEMENT: {test_name}")
        print("🕒 Début:", time.strftime('%H:%M:%S'))
        print("-" * 70)
        
        test_start_time = time.time()
        
        try:
            success = test_func()
            test_duration = time.time() - test_start_time
            results.append((test_name, success, test_duration))
            
            status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
            print(f"\n📊 {test_name}: {status} (⏱️ {test_duration:.2f}s)")
            
        except Exception as e:
            test_duration = time.time() - test_start_time
            print(f"\n💥 {test_name}: ERREUR FATALE - {e}")
            print(f"⏱️ Temps avant erreur: {test_duration:.2f}s")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, test_duration))
    
    # Résumé final
    total_duration = time.time() - total_start_time
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print("=" * 80)
    print(f"🕒 Temps total: {total_duration:.2f}s")
    print("-" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, success, duration in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:<20} {status} (⏱️ {duration:6.2f}s)")
        if success:
            passed += 1
    
    print("-" * 40)
    print(f"🎯 SCORE FINAL: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 TOUTES LES AMÉLIORATIONS FONCTIONNENT PARFAITEMENT !")
        print("\n🚀 Prochaines étapes:")
        print("1. Lance: python simple_interface.py")
        print("2. Lance: python launch_web.py") 
        print("3. Teste avec des questions complexes!")
        print("4. Observe les améliorations (synonymes, validation, etc.)")
    elif passed > 0:
        print(f"\n✅ {passed} améliorations fonctionnent, {total-passed} ont des problèmes.")
        print("Vérifiez les logs détaillés ci-dessus pour diagnostiquer.")
    else:
        print("\n❌ Aucune amélioration ne fonctionne.")
        print("Vérifiez que Ollama est lancé et que les modules sont bien créés.")
    
    print(f"\n🕒 Fin des tests: {time.strftime('%H:%M:%S')}")
    return passed == total

if __name__ == '__main__':
    success = main()
    print(f"\n{'🎉 SUCCÈS TOTAL' if success else '⚠️ ÉCHECS DÉTECTÉS'} - Tests terminés")
    sys.exit(0 if success else 1)