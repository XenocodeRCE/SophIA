"""
Pont entre le texte et les concepts de SophIA
Gestion des synonymes et des relations textuelles
"""

import os
import json
import threading
from typing import List, Dict, Any

from sophia.core.concept_types import ConceptType
from sophia.core.ontology import SimpleOntology, Concept

class ConceptTextBridge:
    """Gère la conversion entre le texte et les concepts ontologiques"""
    
    def __init__(self, ontology: SimpleOntology, llm, *args, **kwargs):
        self.ontology = ontology
        self._standard_synonyms = {}  # Synonymes standards (à remplir selon l'ontologie)
        self._custom_synonyms = {}    # Synonymes personnalisés (utilisateur)
        self._custom_synonyms_path = os.path.join(os.path.dirname(__file__), "concept_synonyms.json")
        self._cache_path = os.path.join(os.path.dirname(__file__), "concept_bridge_cache.json")
        
        print("DEBUG: ConceptTextBridge: Chargement des synonymes personnalisés...")
        self._custom_synonyms = self._load_custom_synonyms()
        print(f"DEBUG: ConceptTextBridge: Synonymes personnalisés chargés: {bool(self._custom_synonyms)}")
        
        print("DEBUG: ConceptTextBridge: Chargement du cache...")
        self._cache = self._load_cache()
        print(f"DEBUG: ConceptTextBridge: Cache chargé: {bool(self._cache)}")
        
        self._cache_lock = threading.Lock()
        
        # Initialisation du cache en tâche de fond
        print("DEBUG: ConceptTextBridge: Initialisation du cache en tâche de fond...")
        self._init_cache_async(ontology, llm)
        print("DEBUG: ConceptTextBridge: __init__ terminé.")
    
    def _load_custom_synonyms(self):
        """Charge les synonymes personnalisés depuis un fichier JSON"""
        
        if os.path.exists(self._custom_synonyms_path):
            with open(self._custom_synonyms_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_custom_synonyms(self):
        """Sauvegarde les synonymes personnalisés dans un fichier JSON"""
        
        with open(self._custom_synonyms_path, "w", encoding="utf-8") as f:
            json.dump(self._custom_synonyms, f, ensure_ascii=False, indent=2)
    
    def _load_cache(self):
        """Charge le cache depuis un fichier JSON"""
        
        if os.path.exists(self._cache_path):
            with open(self._cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Sauvegarde le cache dans un fichier JSON"""
        
        with self._cache_lock:
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
    
    def _init_cache_async(self, ontology, llm):
        """Initialise le cache en tâche de fond si besoin."""
        def build_cache():
            updated = False
            for concept in ontology.concepts.values():
                cname = concept.name
                if cname not in self._cache.get("synonyms", {}):
                    # Calcul coûteux : synonymes
                    syns = self._get_standard_synonyms(cname)
                    self._cache.setdefault("synonyms", {})[cname] = syns
                    updated = True
                # Ajoutez ici d'autres calculs coûteux à mettre en cache si besoin
            if updated:
                self._save_cache()
        # Lancement en thread pour ne pas bloquer l'init
        threading.Thread(target=build_cache, daemon=True).start()
    
    def _get_standard_synonyms(self, concept_name: str) -> List[str]:
        """Retourne les synonymes standards d'un concept"""
        
        # Synonymes prédéfinis pour les concepts philosophiques courants
        standard_synonyms_db = {
            'VÉRITÉ': ['vrai', 'véracité', 'réalité', 'authenticité', 'exactitude'],
            'JUSTICE': ['équité', 'droit', 'justesse', 'impartialité', 'équitable'],
            'LIBERTÉ': ['libre arbitre', 'autonomie', 'indépendance', 'libre'],
            'BIEN': ['bon', 'bonté', 'vertu', 'moral', 'bienveillance'],
            'MAL': ['mauvais', 'méchanceté', 'vice', 'immoral', 'malveillance'],
            'ÊTRE': ['existence', 'ontologie', 'réalité', 'existant'],
            'DEVENIR': ['changement', 'évolution', 'transformation', 'mutation'],
            'CONNAISSANCE': ['savoir', 'science', 'épistémologie', 'comprendre'],
            'CROYANCE': ['foi', 'conviction', 'opinion', 'croire'],
            'CAUSE': ['causalité', 'origine', 'source', 'raison'],
            'EFFET': ['conséquence', 'résultat', 'impact', 'suite'],
            'TEMPS': ['temporel', 'durée', 'moment', 'époque'],
            'ESPACE': ['spatial', 'lieu', 'étendue', 'dimension'],
            'CONSCIENCE': ['conscient', 'awareness', 'lucidité', 'éveil'],
            'MORT': ['mortalité', 'décès', 'fin', 'trépas'],
            'VIE': ['vivant', 'existence', 'vital', 'biologique'],
            'AMOUR': ['affection', 'sentiment', 'passion', 'tendresse'],
            'HAINE': ['antipathie', 'aversion', 'hostilité', 'répulsion'],
            'BEAUTÉ': ['esthétique', 'beau', 'harmonie', 'élégance'],
            'LAIDEUR': ['laid', 'difformité', 'inesthétique', 'disgracieux']
        }
        
        return standard_synonyms_db.get(concept_name, [])
    
    def _get_concept_synonyms(self, concept_name: str) -> List[str]:
        """Retourne la liste des synonymes (standards et personnalisés) pour un concept"""
        
        # Synonymes standards (cache disque)
        synonyms = set(self._cache.get("synonyms", {}).get(concept_name, []))
        
        # Ajout des synonymes standards prédéfinis
        standard_syns = self._get_standard_synonyms(concept_name)
        synonyms.update(standard_syns)
        
        # Synonymes personnalisés
        custom = self._custom_synonyms.get(concept_name, [])
        synonyms.update(custom)
        
        return list(synonyms)
    
    def add_concept_synonym(self, concept_name: str, synonym: str):
        """Ajoute un synonyme personnalisé pour un concept et sauvegarde."""
        print(f"DEBUG: ConceptTextBridge.add_concept_synonym appelée pour {concept_name} -> {synonym}")
        if concept_name not in self._custom_synonyms:
            self._custom_synonyms[concept_name] = []
        if synonym not in self._custom_synonyms[concept_name]:
            self._custom_synonyms[concept_name].append(synonym)
            self._save_custom_synonyms()
            print(f"DEBUG: ConceptTextBridge: Synonyme '{synonym}' ajouté pour '{concept_name}' et sauvegardé.")
        else:
            print(f"DEBUG: ConceptTextBridge: Synonyme '{synonym}' existe déjà pour '{concept_name}'.")
    
    def get_concept(self, text: str) -> Concept:
        """Retourne le concept associé à un texte donné (avec gestion des synonymes)"""
        
        text_lower = text.lower().strip()
        
        # Recherche directe par nom de concept
        for concept_name, concept in self.ontology.concepts.items():
            if concept_name.lower() == text_lower:
                return concept
        
        # Recherche par synonymes
        for concept_name, concept in self.ontology.concepts.items():
            synonyms = self._get_concept_synonyms(concept_name)
            for synonym in synonyms:
                if synonym.lower() == text_lower:
                    return concept
        
        return None
    
    def are_concepts_related(self, concept_name1: str, concept_name2: str) -> bool:
        """Vérifie si deux concepts sont liés par une relation ontologique"""
        
        concept1 = self.ontology.get_concept(concept_name1)
        concept2 = self.ontology.get_concept(concept_name2)
        
        if not concept1 or not concept2:
            return False
        
        # Vérification des relations directes
        if concept2.name in concept1.relations.get('related_to', []):
            return True
        if concept1.name in concept2.relations.get('related_to', []):
            return True
        
        # Vérification des synonymes
        synonyms1 = self._get_concept_synonyms(concept_name1)
        synonyms2 = self._get_concept_synonyms(concept_name2)
        
        for syn1 in synonyms1:
            if syn1 in concept2.relations.get('related_to', []):
                return True
        for syn2 in synonyms2:
            if syn2 in concept1.relations.get('related_to', []):
                return True
        
        return False
    
    def get_related_concepts(self, concept_name: str) -> List[Concept]:
        """Retourne les concepts liés à un concept donné"""
        
        concept = self.ontology.get_concept(concept_name)
        
        if not concept:
            return []
        
        related_concepts = []
        
        # Relations directes
        for related_name in concept.relations.get('related_to', []):
            related_concept = self.ontology.get_concept(related_name)
            if related_concept:
                related_concepts.append(related_concept)
        
        # Synonymes
        synonyms = self._get_concept_synonyms(concept_name)
        for synonym in synonyms:
            synonym_concept = self.ontology.get_concept(synonym)
            if synonym_concept:
                for related_name in synonym_concept.relations.get('related_to', []):
                    related_concept = self.ontology.get_concept(related_name)
                    if related_concept and related_concept.name != concept_name:
                        related_concepts.append(related_concept)
        
        return list(set(related_concepts))  # Unique concepts only
    
    def update_standard_synonyms(self, new_synonyms: Dict[str, List[str]]):
        """Met à jour les synonymes standards (pour test ou autre usage)"""
        
        self._standard_synonyms.update(new_synonyms)
    
    def clear_custom_synonyms(self):
        """Efface tous les synonymes personnalisés"""
        
        self._custom_synonyms = {}
        self._save_custom_synonyms()

class EnhancedConceptTextBridge(ConceptTextBridge):
    """Version enrichie du ConceptTextBridge avec extraction conceptuelle avancée"""
    
    def __init__(self, ontology: SimpleOntology, llm, *args, **kwargs):
        print("DEBUG: EnhancedConceptTextBridge __init__ début.")
        super().__init__(ontology, llm, *args, **kwargs)
        print("DEBUG: EnhancedConceptTextBridge __init__ fin.")
        
        # Vérification de la présence de la méthode après l'initialisation
        if hasattr(self, 'add_concept_synonym'):
            print("DEBUG: EnhancedConceptTextBridge instance a bien 'add_concept_synonym'.")
        else:
            print("ERREUR DEBUG: EnhancedConceptTextBridge instance N'A PAS 'add_concept_synonym'.")
            print(f"DEBUG: MRO: {type(self).mro()}")

    def enhanced_concept_extraction(self, text: str, base_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraction conceptuelle améliorée avec analyse contextuelle
        Méthode principale utilisée par sophia_hybrid.py
        """
        print(f"DEBUG: enhanced_concept_extraction appelée avec texte: {text[:50]}...")
        
        # 1. Récupération des concepts de base
        base_concepts = base_extraction.get('concepts_detected', [])
        base_confidence = base_extraction.get('confidence', 0.5)
        
        print(f"DEBUG: Concepts de base: {base_concepts}")
        
        # 2. Recherche de concepts additionnels via synonymes
        additional_concepts = self._find_additional_concepts_via_synonyms(text, base_concepts)
        
        # 3. Recherche de concepts par mots-clés philosophiques
        keyword_concepts = self._find_concepts_by_keywords(text, base_concepts + additional_concepts)
        
        # 4. Analyse contextuelle simple
        context_analysis = self._analyze_text_context(text)
        
        # 5. Analyse des relations entre concepts
        concept_relations = self._analyze_concept_relations(base_concepts + additional_concepts + keyword_concepts)
        
        # 6. Calcul de confiance améliorée
        all_concepts = list(set(base_concepts + additional_concepts + keyword_concepts))
        enhanced_confidence = self._calculate_enhanced_confidence(
            all_concepts, base_confidence, context_analysis
        )
        
        # 7. Construction de la réponse enrichie
        enhanced_extraction = {
            **base_extraction,
            'concepts_detected': all_concepts,
            'enhanced_confidence': enhanced_confidence,
            'additional_concepts_found': additional_concepts,
            'keyword_concepts_found': keyword_concepts,
            'context_analysis': context_analysis,
            'concept_relations': concept_relations,
            'method': 'enhanced_bridge_with_synonyms_and_keywords',
            'bridge_version': 'v2.1',
            'extraction_details': {
                'base_concepts_count': len(base_concepts),
                'synonym_concepts_count': len(additional_concepts),
                'keyword_concepts_count': len(keyword_concepts),
                'total_concepts_count': len(all_concepts)
            }
        }
        
        print(f"DEBUG: Extraction enrichie terminée: {len(all_concepts)} concepts")
        return enhanced_extraction

    def _find_additional_concepts_via_synonyms(self, text: str, base_concepts: List[str]) -> List[str]:
        """Trouve des concepts additionnels en utilisant les synonymes"""
        text_lower = text.lower()
        additional_concepts = []
        
        # Parcours de tous les concepts de l'ontologie
        for concept_name in self.ontology.concepts.keys():
            if concept_name not in base_concepts:
                # Vérification des synonymes
                synonyms = self._get_concept_synonyms(concept_name)
                
                for synonym in synonyms:
                    if synonym.lower() in text_lower:
                        additional_concepts.append(concept_name)
                        print(f"DEBUG: Concept additionnel trouvé: {concept_name} via synonyme '{synonym}'")
                        break
        
        return additional_concepts

    def _find_concepts_by_keywords(self, text: str, existing_concepts: List[str]) -> List[str]:
        """Trouve des concepts via des mots-clés philosophiques spécifiques"""
        text_lower = text.lower()
        keyword_concepts = []
        
        # Mots-clés spécifiques pour concepts philosophiques
        concept_keywords = {
            'VÉRITÉ': ['vérité', 'véracité', 'authentique', 'réel', 'vrai'],
            'JUSTICE': ['justice', 'juste', 'équité', 'équitable', 'droit', 'injustice'],
            'LIBERTÉ': ['liberté', 'libre', 'autonomie', 'indépendance', 'libre arbitre'],
            'CONNAISSANCE': ['connaissance', 'savoir', 'connaître', 'comprendre', 'épistémologie'],
            'ÊTRE': ['être', 'existence', 'exister', 'ontologie', 'existant'],
            'DEVENIR': ['devenir', 'changement', 'évolution', 'transformation', 'mutation'],
            'BIEN': ['bien', 'bon', 'bonté', 'vertu', 'moral', 'éthique'],
            'MAL': ['mal', 'mauvais', 'vice', 'immoral', 'méchanceté'],
            'BEAUTÉ': ['beauté', 'beau', 'esthétique', 'harmonie', 'élégance'],
            'TEMPS': ['temps', 'temporel', 'durée', 'moment', 'époque', 'chronologie'],
            'ESPACE': ['espace', 'spatial', 'lieu', 'étendue', 'dimension'],
            'CONSCIENCE': ['conscience', 'conscient', 'awareness', 'lucidité', 'éveil'],
            'MORT': ['mort', 'mortalité', 'décès', 'fin', 'trépas'],
            'VIE': ['vie', 'vivant', 'vital', 'biologique', 'existence'],
            'AMOUR': ['amour', 'affection', 'sentiment', 'passion', 'tendresse'],
            'CAUSE': ['cause', 'causalité', 'origine', 'source', 'raison'],
            'EFFET': ['effet', 'conséquence', 'résultat', 'impact', 'suite']
        }
        
        for concept_name, keywords in concept_keywords.items():
            if concept_name not in existing_concepts:
                for keyword in keywords:
                    if keyword in text_lower:
                        keyword_concepts.append(concept_name)
                        print(f"DEBUG: Concept par mot-clé trouvé: {concept_name} via '{keyword}'")
                        break
        
        return keyword_concepts

    def _analyze_text_context(self, text: str) -> Dict[str, Any]:
        """Analyse contextuelle simple du texte"""
        text_lower = text.lower()
        
        # Indicateurs philosophiques
        philosophical_indicators = [
            'qu\'est-ce que', 'nature de', 'essence de', 'définition',
            'pourquoi', 'comment', 'peut-on', 'doit-on',
            'philosophie', 'pensée', 'réflexion', 'concept',
            'théorie', 'doctrine', 'principe'
        ]
        
        indicators_found = [ind for ind in philosophical_indicators if ind in text_lower]
        
        # Types de questions
        question_type = 'unknown'
        if any(word in text_lower for word in ['qu\'est-ce que', 'nature de', 'essence']):
            question_type = 'definition'
        elif any(word in text_lower for word in ['pourquoi', 'comment']):
            question_type = 'explanation'
        elif any(word in text_lower for word in ['peut-on', 'doit-on']):
            question_type = 'normative'
        elif any(word in text_lower for word in ['relation', 'lien', 'rapport']):
            question_type = 'relational'
        
        # Complexité linguistique
        complexity_indicators = {
            'long_sentences': len([s for s in text.split('.') if len(s.split()) > 10]),
            'philosophical_terms': len(indicators_found),
            'question_marks': text.count('?'),
            'conjunctions': len([w for w in ['et', 'ou', 'mais', 'donc', 'car'] if w in text_lower])
        }
        
        return {
            'text_length': len(text),
            'word_count': len(text.split()),
            'philosophical_indicators': indicators_found,
            'question_type': question_type,
            'complexity_score': min(len(text) / 100, 1.0),
            'complexity_indicators': complexity_indicators,
            'has_question_mark': '?' in text,
            'is_interrogative': question_type != 'unknown'
        }

    def _analyze_concept_relations(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """Analyse les relations entre les concepts détectés"""
        relations = []
        
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                if self.are_concepts_related(concept1, concept2):
                    relations.append({
                        'concept1': concept1,
                        'concept2': concept2,
                        'relation_type': 'related_to',
                        'strength': 0.8  # Simplified strength score
                    })
        
        return relations

    def _calculate_enhanced_confidence(self, concepts: List[str], base_confidence: float, 
                                     context_analysis: Dict[str, Any]) -> float:
        """Calcule une confiance améliorée basée sur plusieurs facteurs"""
        
        # Facteur de base
        enhanced_confidence = base_confidence
        
        # Bonus pour concepts multiples (diversité conceptuelle)
        concept_bonus = min(len(concepts) * 0.08, 0.25)
        enhanced_confidence += concept_bonus
        
        # Bonus pour indicateurs philosophiques
        philosophical_indicators = context_analysis.get('philosophical_indicators', [])
        philosophical_bonus = min(len(philosophical_indicators) * 0.05, 0.15)
        enhanced_confidence += philosophical_bonus
        
        # Bonus pour type de question identifié
        question_bonus = 0.1 if context_analysis.get('question_type') != 'unknown' else 0
        enhanced_confidence += question_bonus
        
        # Bonus pour complexité appropriée
        complexity_score = context_analysis.get('complexity_score', 0)
        if 0.3 <= complexity_score <= 0.8:  # Complexité optimale
            enhanced_confidence += 0.05
        
        # Bonus pour question interrogative
        if context_analysis.get('is_interrogative'):
            enhanced_confidence += 0.05
        
        # Normalisation finale
        enhanced_confidence = min(enhanced_confidence, 1.0)
        enhanced_confidence = max(enhanced_confidence, 0.0)
        
        return enhanced_confidence

    # Redéfinition explicite pour s'assurer qu'elle est disponible
    def add_concept_synonym(self, concept_name: str, synonym: str):
        """Ajoute un synonyme personnalisé pour un concept et sauvegarde."""
        print(f"DEBUG: EnhancedConceptTextBridge.add_concept_synonym (explicite) appelée pour {concept_name} -> {synonym}")
        # Appel à la méthode de la classe parente
        return super().add_concept_synonym(concept_name, synonym)

    # Version publique si nécessaire pour le test
    def get_public_concept_synonyms(self, concept_name: str) -> List[str]:
        print(f"DEBUG: EnhancedConceptTextBridge.get_public_concept_synonyms appelée pour {concept_name}")
        return self._get_concept_synonyms(concept_name)

    def extract_concepts(self, text: str, existing_extraction: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Méthode alternative d'extraction pour compatibilité
        """
        if existing_extraction is None:
            existing_extraction = {'concepts_detected': [], 'confidence': 0.5}
        
        return self.enhanced_concept_extraction(text, existing_extraction)