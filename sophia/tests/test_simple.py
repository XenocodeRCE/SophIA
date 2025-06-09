"""
Test simple pour identifier où ça freeze
"""

import sys
import os
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

print("🧪 TEST SIMPLE - IDENTIFICATION DU FREEZE")
print("=" * 50)

# Test 1: Imports de base
start = time.perf_counter()
print("📦 Test 1: Imports de base...")
try:
    from sophia.core.ontology import SimpleOntology
    from sophia.models.lcm_core import SimpleLCM
    print("✅ Imports de base OK")
except Exception as e:
    print(f"❌ Erreur imports de base: {e}")
    sys.exit(1)
print(f"⏱️ Temps écoulé Test 1: {time.perf_counter() - start:.3f} sec")

# Test 2: LLaMA Interface (probable cause du freeze)
start = time.perf_counter()
print("\n🦙 Test 2: LLaMA Interface...")
try:
    from sophia.llm.llama_interface import OllamaLLaMAInterface
    print("✅ Import LLaMA OK")
    
    print("🔍 Création interface (peut freezer ici)...")
    llm = OllamaLLaMAInterface()
    print("✅ Interface créée")
    
    print("🔍 Vérification disponibilité...")
    info = llm.get_model_info()
    print(f"📊 Info LLaMA: {info}")
    
except Exception as e:
    print(f"❌ Erreur LLaMA: {e}")
    print("💡 Ollama est-il lancé? (ollama serve)")
print(f"⏱️ Temps écoulé Test 2: {time.perf_counter() - start:.3f} sec")

# Test 3: Bridge (si LLaMA OK)
start = time.perf_counter()
print("\n🔗 Test 3: Concept Bridge...")
try:
    from sophia.bridge.concept_text_bridge import EnhancedConceptTextBridge
    print("✅ Import Bridge OK")
    
    ontology = SimpleOntology()
    print("✅ Ontologie créée")
    
    # Skip création si LLaMA pas dispo
    if 'llm' in locals():
        print("🔍 Création bridge (peut prendre du temps)...")
        bridge = EnhancedConceptTextBridge(ontology, llm)
        print("✅ Bridge créé")
        
    else:
        print("⚠️ Skip bridge (LLaMA non dispo)")
        
except Exception as e:
    print(f"❌ Erreur Bridge: {e}")
print(f"⏱️ Temps écoulé Test 3: {time.perf_counter() - start:.3f} sec")

# Test 4: Constraints
start = time.perf_counter()
print("\n⚖️ Test 4: Constraint Manager...")
try:
    from sophia.constraints.constraint_manager import PhilosophicalConstraintManager
    print("✅ Import Constraints OK")
    
    if 'llm' in locals() and 'ontology' in locals():
        constraints = PhilosophicalConstraintManager(ontology, llm)
        print("✅ Constraints créé")
    else:
        print("⚠️ Skip constraints (dépendances manquantes)")
        
except Exception as e:
    print(f"❌ Erreur Constraints: {e}")
print(f"⏱️ Temps écoulé Test 4: {time.perf_counter() - start:.3f} sec")

print("\n📊 DIAGNOSTIC TERMINÉ")
print("Si le freeze arrive, tu sauras maintenant où exactement!")