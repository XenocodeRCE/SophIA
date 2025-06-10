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
        print(f"Contenu du cache: [{self._cache}]")
        # Verrou pour la gestion du cache
        
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
                    # Calcul coûteux : synonymes
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
        
        # À implémenter : extraction des synonymes depuis l'ontologie ou une autre source
        return self._standard_synonyms.get(concept_name, [])
    
    def _get_concept_synonyms(self, concept_name: str) -> List[str]:
        """Retourne la liste des synonymes (standards et personnalisés) pour un concept"""
        
        # Synonymes standards (cache disque)
        synonyms = set(self._cache.get("synonyms", {}).get(concept_name, []))
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
        
        # À implémenter : logique pour trouver le concept à partir du texte
        # en utilisant les synonymes et l'ontologie
        pass
    
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
    """Version enrichie du ConceptTextBridge (hérite de toutes les méthodes publiques)"""
    
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

    # Redéfinition explicite pour s'assurer qu'elle est disponible
    def add_concept_synonym(self, concept_name: str, synonym: str):
        """Ajoute un synonyme personnalisé pour un concept et sauvegarde."""
        print(f"DEBUG: EnhancedConceptTextBridge.add_concept_synonym (explicite) appelée pour {concept_name} -> {synonym}")
        # Appel à la méthode de la classe parente
        return super().add_concept_synonym(concept_name, synonym)

    # Si _get_concept_synonyms est aussi utilisé directement par le test et pose problème :
    # def _get_concept_synonyms(self, concept_name: str) -> List[str]:
    #     print(f"DEBUG: EnhancedConceptTextBridge._get_concept_synonyms (explicite) appelée pour {concept_name}")
    #     return super()._get_concept_synonyms(concept_name)

    # Version publique si nécessaire pour le test
    def get_public_concept_synonyms(self, concept_name: str) -> List[str]:
        print(f"DEBUG: EnhancedConceptTextBridge.get_public_concept_synonyms appelée pour {concept_name}")
        return self._get_concept_synonyms(concept_name)