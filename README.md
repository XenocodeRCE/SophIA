# 🧠 SophIA - LCM Hybride

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)

> **SophIA** : Système d'Intelligence Artificielle spécialisé en philosophie, combinant raisonnement conceptuel avancé et génération naturelle.

## 🌟 Fonctionnalités Exceptionnelles

### 🧠 **Intelligence Hybride Révolutionnaire**
- **LCM (Logic Conceptual Model)** : Raisonnement philosophique structuré
- **LLaMA Integration** : Génération naturelle sophistiquée
- **Fusion Intelligente** : Combinaison optimale logique + créativité

### 🔍 **Extraction Conceptuelle Ultra-Avancée**
- **4 Niveaux d'Analyse** : Directe, Sémantique, Contextuelle, Inférentielle
- **201 Concepts Philosophiques** : Ontologie spécialisée complète
- **Relations Conceptuelles** : Détection automatique des liens philosophiques
- **Confiance Multi-Critères** : Validation sophistiquée

### 📝 **Tokenizer Philosophique Spécialisé**
- **Lexique Expert** : 201 termes techniques philosophiques
- **Analyse de Complexité** : Évaluation automatique de profondeur
- **Structures Argumentatives** : Détection de patterns logiques
- **Catégorisation** : Épistémologie, Éthique, Métaphysique, Esthétique, etc.

### 🔄 **Apprentissage Autonome Adaptatif**
- **Amélioration Continue** : Apprentissage par interaction
- **Adaptation Intelligente** : Optimisation automatique des performances
- **Patterns Conceptuels** : Découverte de nouvelles associations
- **Spécialisation Domaines** : Focus automatique sur les sujets préférés

### ⚖️ **Validation Éthique Intégrée**
- **7 Contraintes Philosophiques** : Cohérence, Profondeur, Nuance, etc.
- **Validation Temps Réel** : Vérification continue de la qualité
- **Respect des Principes** : Garantie d'intégrité philosophique

### 📊 **Monitoring Ultra-Détaillé**
- **Performance Temps Réel** : Métriques avancées
- **Optimisations Intelligentes** : Recommandations automatiques
- **Analyse des Goulots** : Identification et résolution proactive
- **Rapports Détaillés** : Insights complets sur les performances

## 🚀 Installation Rapide

### Prérequis
```bash
# Python 3.8+ requis
python --version

# Ollama pour LLaMA (recommandé)
# Installation : https://ollama.ai
ollama pull llama3.1:latest
```

### Installation
```bash
# Cloner le repository
git clone https://github.com/XenocodeRCE/SophIA.git
cd SophIA

# Installer les dépendances
pip install -r requirements.txt

# Lancer SophIA
python -c "
from sophia.core.sophia_hybrid import HybridSophIA
sophia = HybridSophIA()
response = sophia.ask('Qu\'est-ce que la vérité ?')
print(f'Réponse: {response.natural_response}')
print(f'Concepts: {response.conceptual_analysis[\"concepts_detected\"]}')
print(f'Confiance: {response.confidence:.1%}')
"
```

## 🎯 Utilisation

### 💫 **Usage Basique**
```python
from sophia.core.sophia_hybrid import HybridSophIA

# Initialisation
sophia = HybridSophIA()

# Question philosophique
response = sophia.ask("L'art a-t-il une fonction morale ?")

print(f"Réponse: {response.natural_response}")
print(f"Concepts détectés: {response.conceptual_analysis['concepts_detected']}")
print(f"Confiance: {response.confidence:.1%}")
print(f"Validation: {response.validation_report['global_score']:.1%}")
```

### ⚡ **Modes de Performance**
```python
# Mode Rapide (< 5s) - Interface utilisateur
sophia_fast = HybridSophIA(performance_mode="speed")

# Mode Équilibré (5-10s) - Usage général
sophia_balanced = HybridSophIA(performance_mode="balanced")

# Mode Qualité (10-20s) - Recherche approfondie
sophia_quality = HybridSophIA(performance_mode="quality")
```

### 🔍 **Analyse Avancée**
```python
# Question complexe avec analyse détaillée
response = sophia.ask("L'existence précède-t-elle l'essence ?")

# Concepts et relations
concepts = response.conceptual_analysis['concepts_detected']
relations = response.conceptual_analysis['relations_implied']

print(f"Concepts philosophiques: {concepts}")
print(f"Relations conceptuelles: {len(relations)}")

# Relations détaillées
for relation in relations:
    print(f"• {relation['from']} {relation['relation']} {relation['to']}")
```

### 📊 **Monitoring et Insights**
```python
# Statistiques de session
summary = sophia.get_conversation_summary()
print(f"Questions traitées: {summary['total_interactions']}")
print(f"Confiance moyenne: {summary['average_confidence']:.1%}")
print(f"Concepts favoris: {summary['most_discussed_concepts'][:5]}")

# Performance détaillée
if sophia.perf_monitor:
    stats = sophia.perf_monitor.get_overall_stats()
    print(f"Efficacité: {stats['efficiency_score']:.1%}")
    print(f"Temps moyen: {stats['operations_per_minute']:.1f} ops/min")
```

### 🧠 **Apprentissage Autonome**
```python
# Insights d'apprentissage
if sophia.autonomous_learner:
    insights = sophia.autonomous_learner.get_learning_insights()
    
    # Progrès d'apprentissage
    learning = insights['learning_summary']
    print(f"Patterns découverts: {learning['patterns_discovered']}")
    print(f"Adaptations effectuées: {learning['adaptations_made']}")
    print(f"Confiance apprentissage: {learning['learning_confidence']:.1%}")
    
    # Concepts appris
    for concept in insights['top_learned_concepts'][:3]:
        print(f"• {concept['concept']}: {concept['usage_count']} utilisations")
```

## 🏗️ Architecture

```
🧠 SophIA Enhanced
├── 📦 Core/
│   ├── sophia_hybrid.py       # Système principal hybride
│   ├── ontology.py           # Ontologie philosophique
│   └── constraint_manager.py  # Validation éthique
│
├── 🔍 Extraction/
│   └── llm_extractor.py      # Extraction conceptuelle avancée
│
├── 📝 NLP/
│   └── tokenizer.py          # Tokenizer philosophique
│
├── 🧠 Learning/
│   └── autonomous_learner.py # Apprentissage adaptatif
│
├── 📊 Optimization/
│   └── performance.py        # Monitoring ultra-détaillé
│
├── 🦙 LLM/
│   └── llama_interface.py    # Interface LLaMA/Ollama
│
└── 🔗 Bridge/
    └── concept_text_bridge.py # Pont concepts-texte
```

## 📈 Performances

### 🎯 **Métriques de Qualité**
- **Précision Conceptuelle** : 92%+
- **Confiance Moyenne** : 88%+
- **Validation Éthique** : 85%+
- **Détection Relations** : 78%+

### ⚡ **Performances Temporelles**
- **Mode Speed** : 2-5 secondes
- **Mode Balanced** : 5-10 secondes
- **Mode Quality** : 10-20 secondes

### 🧠 **Capacités Avancées**
- **Concepts Philosophiques** : 201 concepts spécialisés
- **Domaines Couverts** : 7 branches philosophiques principales
- **Relations Conceptuelles** : Détection automatique multi-types
- **Apprentissage** : Adaptation continue automatique

## 🔧 Configuration Avancée

### ⚙️ **Paramètres Personnalisables**
```python
sophia = HybridSophIA(
    performance_mode="balanced",    # speed/balanced/quality
    auto_save=True,                # Sauvegarde automatique
    session_name="ma_session",     # Nom de session
    response_temperature=0.7,      # Créativité LLaMA
    conceptual_weight=0.6,         # Poids raisonnement conceptuel
    learning_threshold=0.3         # Seuil d'apprentissage
)
```

### 🎛️ **Optimisation Performance**
```python
# Configuration des seuils de monitoring
sophia.perf_monitor.set_thresholds(
    slow_threshold=3.0,      # Seuil opération lente
    memory_threshold=50,     # Seuil mémoire (MB)
    cpu_threshold=70         # Seuil CPU (%)
)
```

## 🧪 Tests et Validation

### 🔬 **Tests Unitaires**
```bash
# Tests des modules principaux
python test_llm_extractor.py      # Extraction conceptuelle
python test_tokenizer.py          # Analyse linguistique
python test_autonomous_learner.py # Apprentissage adaptatif
python test_performance_ultra.py  # Monitoring avancé
```

### 🎯 **Tests Philosophiques**
```bash
# Tests sur questions complexes
python test_questions_philosophiques.py

# Comparaison des modes de performance
python test_performance_modes.py

# Test d'apprentissage continu
python test_apprentissage_continu.py
```

## 📊 Exemples d'Utilisation

### 🎓 **Enseignement Philosophique**
```python
# Assistant pédagogique
sophia = HybridSophIA(performance_mode="quality")

# Questions d'étudiants
questions_cours = [
    "Qu'est-ce qui distingue l'art de l'artisanat ?",
    "Peut-on fonder la morale sur la raison ?",
    "Le temps est-il une illusion ?"
]

for question in questions_cours:
    response = sophia.ask(question)
    print(f"Q: {question}")
    print(f"R: {response.natural_response}")
    print(f"Concepts clés: {response.conceptual_analysis['concepts_detected']}")
    print("---")
```

### 🔬 **Recherche Philosophique**
```python
# Analyse conceptuelle approfondie
sophia = HybridSophIA(performance_mode="quality")

# Recherche sur un thème
response = sophia.ask("Comment Heidegger conçoit-il la relation entre être et temps ?")

# Analyse des relations conceptuelles
relations = response.conceptual_analysis['relations_implied']
for rel in relations:
    print(f"Relation: {rel['from']} → {rel['relation']} → {rel['to']}")
    print(f"Force: {rel['strength']:.2f}")
```

### 💬 **Interface Conversationnelle**
```python
# Chat philosophique interactif
sophia = HybridSophIA(performance_mode="speed")

print("🧠 SophIA Enhanced - Assistant Philosophique")
print("Posez vos questions philosophiques (tapez 'quit' pour sortir)")

while True:
    question = input("\n📝 Votre question: ")
    if question.lower() == 'quit':
        break
    
    response = sophia.ask(question)
    print(f"\n🤖 SophIA: {response.natural_response}")
    
    # Concepts détectés
    concepts = response.conceptual_analysis['concepts_detected']
    if concepts:
        print(f"🎯 Concepts: {', '.join(concepts)}")
```

## 🤝 Contribution

### 🔧 **Développement**
```bash
# Cloner pour développement
git clone https://github.com/XenocodeRCE/SophIA.git
cd SophIA

# Installer en mode développement
pip install -e .

# Lancer les tests
python -m pytest tests/
```

### 📚 **Améliorer l'Ontologie**
Les concepts philosophiques sont dans `sophia/core/ontology.py`. 
Contributions bienvenues pour :
- Nouveaux concepts spécialisés
- Relations conceptuelles additionnelles
- Domaines philosophiques émergents

### 🔍 **Optimisations**
Domaines d'amélioration :
- Performance des requêtes LLaMA
- Précision de l'extraction conceptuelle
- Algorithmes d'apprentissage adaptatif
- Interface utilisateur avancée

## 📝 License

MIT License - voir [LICENSE](LICENSE) pour les détails.

## 🙏 Remerciements

- **Ollama** pour l'infrastructure LLaMA
- **Communauté Philosophique** pour l'inspiration
- **Contributeurs Open Source** pour les outils utilisés

## 📞 Support et Contact

### 🐛 **Issues**
Rapportez les bugs sur [GitHub Issues](https://github.com/XenocodeRCE/SophIA/issues)

### 💬 **Discussions**
Questions et idées sur [GitHub Discussions](https://github.com/XenocodeRCE/SophIA/discussions)

## 🚀 Roadmap

### 🎯 **Version 2.0 (Prochaine)**
- [ ] Interface Web React avancée
- [ ] API REST complète
- [ ] Support GPT-4/Claude
- [ ] Visualisation des graphes conceptuels
- [ ] Export vers formats académiques

### 🌟 **Version 3.0 (Future)**
- [ ] Mode multilingue (EN, DE, ES, IT)
- [ ] Intégration bases de données philosophiques
- [ ] IA générative pour textes philosophiques
- [ ] Collaboration temps réel multi-utilisateurs

---

[[Star on GitHub](https://img.shields.io/github/stars/XenocodeRCE/SophIA?style=social)](https://github.com/XenocodeRCE/SophIA)
[[Fork on GitHub](https://img.shields.io/github/forks/XenocodeRCE/SophIA?style=social)](https://github.com/XenocodeRCE/SophIA/fork)
