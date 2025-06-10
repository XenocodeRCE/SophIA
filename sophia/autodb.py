#!/usr/bin/env python3
"""
Script d'enrichissement automatique des concepts philosophiques via Ollama
Version avec structure JSON stricte
"""

import sys
import os
import requests
import json
import re
from typing import List, Dict, Tuple, Set
from enum import Enum
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Essayer différents chemins d'import
try:
    from concept_types import ConceptType, RelationType, CORE_PHILOSOPHICAL_CONCEPTS, CORE_RELATIONS
except ImportError:
    try:
        from sophia.concept_types import ConceptType, RelationType, CORE_PHILOSOPHICAL_CONCEPTS, CORE_RELATIONS
    except ImportError:
        try:
            from sophia.core.concept_types import ConceptType, RelationType, CORE_PHILOSOPHICAL_CONCEPTS, CORE_RELATIONS
        except ImportError:
            # Si aucun import ne fonctionne, définir les types localement
            from enum import Enum
            
            class ConceptType(Enum):
                ENTITY = "entity"
                PROPERTY = "property"
                RELATION = "relation"
                EPISTEMIC = "epistemic"
                LOGICAL = "logical"
                MORAL = "moral"
                VALUE = "value"
                AESTHETIC = "aesthetic"
                POLITICAL = "political"
                PHILOSOPHICAL_DOMAIN = "domain"
                LEARNED_CONCEPT = "learned"
                USER_CONCEPT = "user_defined"

            class RelationType(Enum):
                IMPLIES = "implies"
                CONTRADICTS = "contradicts"
                IS_EQUIVALENT = "is_equivalent"
                IS_A = "is_a"
                PART_OF = "part_of"
                HAS_PROPERTY = "has_property"
                CAUSES = "causes"
                ENABLES = "enables"
                PREVENTS = "prevents"
                DEFINES = "defines"
                EXPLAINS = "explains"
                PRECEDES = "precedes"
                FOLLOWS = "follows"
                OPPOSES = "opposes"
                COMPLEMENTS = "complements"
                CUSTOM = "custom"
            
            CORE_PHILOSOPHICAL_CONCEPTS = {}
            CORE_RELATIONS = []
            print("⚠️ Impossible d'importer concept_types, utilisation des définitions locales")

class ConceptEnricher:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.ollama_url = ollama_url
        self.model = model
        self.generated_concepts = set()
        self.generated_relations = []
        
    def query_ollama(self, prompt: str) -> str:
        """Envoie une requête à Ollama et retourne la réponse"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 2000
                    }
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"Erreur Ollama: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Erreur connexion Ollama: {e}")
            return ""

    def parse_json_response(self, response: str) -> Dict:
        """Parse la réponse JSON d'Ollama"""
        try:
            # Extraire le JSON de la réponse (peut contenir du texte avant/après)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                print("Aucun JSON valide trouvé dans la réponse")
                return {}
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON: {e}")
            print(f"Réponse brute: {response[:500]}...")
            return {}

    def generate_concepts_for_domain(self, domain: str, base_concepts: List[str]) -> Dict:
        """Génère des concepts pour un domaine philosophique donné"""
        
        # Exemple de structure JSON attendue
        example_json = {
            "domain": "epistemologie",
            "concepts": [
                {
                    "name": "RELATIVISME",
                    "type": "EPISTEMIC",
                    "definition": "Position selon laquelle la vérité est relative au contexte",
                    "synonyms": ["relativité", "contextualisme"],
                    "related_concepts": ["VÉRITÉ", "OBJECTIVITÉ"]
                },
                {
                    "name": "SCEPTICISME",
                    "type": "EPISTEMIC", 
                    "definition": "Doctrine qui met en doute la possibilité de la connaissance certaine",
                    "synonyms": ["doute", "pyrrhonisme"],
                    "related_concepts": ["DOUTE", "CERTITUDE", "CONNAISSANCE"]
                }
            ]
        }
        
        prompt = f"""
Tu es un expert en philosophie. Pour le domaine "{domain}", génère 15 nouveaux concepts philosophiques liés aux concepts de base suivants: {', '.join(base_concepts)}.

Tu DOIS répondre UNIQUEMENT avec un JSON valide suivant EXACTEMENT cette structure:

{json.dumps(example_json, indent=2, ensure_ascii=False)}

Types de concepts disponibles:
- ENTITY (entités, objets, êtres)
- PROPERTY (propriétés, qualités, attributs)  
- RELATION (relations ontologiques)
- EPISTEMIC (concepts épistémologiques)
- LOGICAL (concepts logiques)
- MORAL (concepts moraux)
- VALUE (valeurs)
- AESTHETIC (concepts esthétiques)
- POLITICAL (concepts politiques)

IMPORTANT: 
- Réponds UNIQUEMENT avec le JSON, aucun texte avant ou après
- Les noms de concepts doivent être en MAJUSCULES
- Utilise exactement les types listés ci-dessus
- Donne des définitions concises en français
- Liste 2-4 concepts liés existants pour chaque nouveau concept

JSON pour le domaine "{domain}":
"""

        response = self.query_ollama(prompt)
        parsed_data = self.parse_json_response(response)
        
        if parsed_data:
            print(f"✓ Domaine {domain}: {len(parsed_data.get('concepts', []))} concepts générés")
        else:
            print(f"❌ Échec génération pour domaine {domain}")
            
        return {
            "domain": domain,
            "parsed_data": parsed_data,
            "raw_response": response
        }

    def generate_relations_for_concepts(self, concepts: List[str]) -> Dict:
        """Génère des relations entre les concepts donnés"""
        
        concept_list = concepts[:12]  # Limiter pour éviter des prompts trop longs
        
        # Exemple de structure JSON pour les relations
        example_json = {
            "relations": [
                {
                    "concept1": "VÉRITÉ",
                    "relation_type": "OPPOSES", 
                    "concept2": "MENSONGE",
                    "strength": 0.9,
                    "justification": "La vérité et le mensonge sont par nature opposés"
                },
                {
                    "concept1": "CONNAISSANCE",
                    "relation_type": "IMPLIES",
                    "concept2": "VÉRITÉ", 
                    "strength": 0.8,
                    "justification": "La vraie connaissance implique la vérité"
                },
                {
                    "concept1": "JUSTICE",
                    "relation_type": "ENABLES",
                    "concept2": "LIBERTÉ",
                    "strength": 0.7, 
                    "justification": "La justice permet l'exercice de la liberté"
                }
            ]
        }
        
        prompt = f"""
Tu es un expert en philosophie. Génère 20 relations philosophiques pertinentes entre ces concepts: {', '.join(concept_list)}.

Tu DOIS répondre UNIQUEMENT avec un JSON valide suivant EXACTEMENT cette structure:

{json.dumps(example_json, indent=2, ensure_ascii=False)}

Types de relations disponibles:
- IMPLIES (A implique B)
- CONTRADICTS (A contredit B)
- IS_EQUIVALENT (A équivaut à B) 
- IS_A (A est un type de B)
- PART_OF (A fait partie de B)
- HAS_PROPERTY (A a la propriété B)
- CAUSES (A cause B)
- ENABLES (A permet B)
- PREVENTS (A empêche B)
- DEFINES (A définit B)
- EXPLAINS (A explique B)
- OPPOSES (A s'oppose à B)
- COMPLEMENTS (A complète B)

IMPORTANT:
- Réponds UNIQUEMENT avec le JSON, aucun texte avant ou après
- Les noms de concepts doivent être en MAJUSCULES
- Utilise exactement les types de relations listés ci-dessus
- La force (strength) doit être entre 0.1 et 1.0
- Justifie brièvement chaque relation

JSON des relations:
"""

        response = self.query_ollama(prompt)
        parsed_data = self.parse_json_response(response)
        
        if parsed_data:
            print(f"✓ {len(parsed_data.get('relations', []))} relations générées")
        else:
            print(f"❌ Échec génération des relations")
            
        return {
            "parsed_data": parsed_data,
            "raw_response": response
        }

    def enrich_concept_neighborhood(self, central_concept: str) -> Dict:
        """Enrichit le voisinage conceptuel autour d'un concept central"""
        
        # Exemple de structure JSON pour le voisinage conceptuel
        example_json = {
            "central_concept": "VÉRITÉ",
            "neighborhood": {
                "direct_concepts": [
                    {
                        "name": "OBJECTIVITÉ",
                        "type": "EPISTEMIC",
                        "relation_to_central": "HAS_PROPERTY",
                        "definition": "Caractère de ce qui est objectif, indépendant des opinions",
                        "distance": 1
                    },
                    {
                        "name": "MENSONGE", 
                        "type": "EPISTEMIC",
                        "relation_to_central": "OPPOSES",
                        "definition": "Assertion contraire à la vérité",
                        "distance": 1
                    }
                ],
                "indirect_concepts": [
                    {
                        "name": "RÉALISME",
                        "type": "EPISTEMIC", 
                        "relation_path": ["VÉRITÉ", "OBJECTIVITÉ", "RÉALISME"],
                        "definition": "Doctrine selon laquelle la réalité existe indépendamment de nos représentations",
                        "distance": 2
                    }
                ],
                "relations": [
                    {
                        "concept1": "VÉRITÉ",
                        "relation_type": "HAS_PROPERTY",
                        "concept2": "OBJECTIVITÉ",
                        "strength": 0.9
                    },
                    {
                        "concept1": "OBJECTIVITÉ", 
                        "relation_type": "ENABLES",
                        "concept2": "RÉALISME",
                        "strength": 0.7
                    }
                ]
            }
        }
        
        prompt = f"""
Tu es un expert en philosophie. Pour le concept central "{central_concept}", génère son voisinage conceptuel complet.

Tu DOIS répondre UNIQUEMENT avec un JSON valide suivant EXACTEMENT cette structure:

{json.dumps(example_json, indent=2, ensure_ascii=False)}

IMPORTANT:
- Réponds UNIQUEMENT avec le JSON, aucun texte avant ou après
- Génère 8 concepts directs (distance 1) et 6 concepts indirects (distance 2)
- Les noms de concepts doivent être en MAJUSCULES
- Utilise les types: ENTITY, PROPERTY, RELATION, EPISTEMIC, LOGICAL, MORAL, VALUE, AESTHETIC, POLITICAL
- Utilise les relations: IMPLIES, CONTRADICTS, IS_EQUIVALENT, IS_A, PART_OF, HAS_PROPERTY, CAUSES, ENABLES, PREVENTS, DEFINES, EXPLAINS, OPPOSES, COMPLEMENTS
- Pour les concepts indirects, indique le chemin conceptuel complet
- La force (strength) doit être entre 0.1 et 1.0

JSON pour le concept "{central_concept}":
"""

        response = self.query_ollama(prompt)
        parsed_data = self.parse_json_response(response)
        
        if parsed_data:
            neighborhood = parsed_data.get("neighborhood", {})
            direct_count = len(neighborhood.get("direct_concepts", []))
            indirect_count = len(neighborhood.get("indirect_concepts", []))
            relations_count = len(neighborhood.get("relations", []))
            print(f"✓ Concept {central_concept}: {direct_count} directs, {indirect_count} indirects, {relations_count} relations")
        else:
            print(f"❌ Échec enrichissement pour {central_concept}")
            
        return {
            "central_concept": central_concept,
            "parsed_data": parsed_data,
            "raw_response": response
        }

    def generate_comprehensive_enrichment(self) -> Dict:
        """Génère un enrichissement complet de la base de concepts"""
        
        print("🚀 Début de l'enrichissement automatique des concepts philosophiques...")
        
        results = {
            "metadata": {
                "generation_timestamp": time.time(),
                "ollama_model": self.model,
                "total_domains": 0,
                "total_neighborhoods": 0,
                "total_new_concepts": 0,
                "total_new_relations": 0
            },
            "domains": {},
            "concept_neighborhoods": {},
            "relations": {},
            "summary": {
                "all_concepts": [],
                "all_relations": []
            }
        }
        
        # 1. Enrichissement par domaines
        domains = {
            "métaphysique": ["ÊTRE", "EXISTENCE", "ESSENCE", "SUBSTANCE"],
            "épistémologie": ["VÉRITÉ", "CONNAISSANCE", "CROYANCE", "DOUTE"],
            "éthique": ["BIEN", "MAL", "JUSTICE", "VERTU"],
            "esthétique": ["BEAUTÉ", "ART", "GOÛT", "SUBLIME"],
            "politique": ["ÉTAT", "POUVOIR", "LIBERTÉ", "DÉMOCRATIE"],
            "logique": ["ARGUMENT", "VALIDITÉ", "CONTRADICTION", "COHÉRENCE"]
        }
        
        for domain, base_concepts in domains.items():
            print(f"\n📚 Traitement du domaine: {domain}")
            domain_result = self.generate_concepts_for_domain(domain, base_concepts)
            results["domains"][domain] = domain_result
            
            # Ajouter les concepts au résumé
            if domain_result["parsed_data"]:
                concepts = domain_result["parsed_data"].get("concepts", [])
                results["summary"]["all_concepts"].extend(concepts)
            
            time.sleep(2)  # Pause pour éviter de surcharger Ollama
        
        results["metadata"]["total_domains"] = len(domains)
        
        # 2. Enrichissement des voisinages conceptuels
        key_concepts = ["VÉRITÉ", "JUSTICE", "BEAUTÉ", "LIBERTÉ", "CONNAISSANCE", "ÊTRE"]
        
        for concept in key_concepts:
            print(f"\n🎯 Enrichissement du voisinage: {concept}")
            neighborhood_result = self.enrich_concept_neighborhood(concept)
            results["concept_neighborhoods"][concept] = neighborhood_result
            
            # Ajouter au résumé
            if neighborhood_result["parsed_data"]:
                neighborhood = neighborhood_result["parsed_data"].get("neighborhood", {})
                
                # Concepts directs et indirects
                direct_concepts = neighborhood.get("direct_concepts", [])
                indirect_concepts = neighborhood.get("indirect_concepts", [])
                results["summary"]["all_concepts"].extend(direct_concepts + indirect_concepts)
                
                # Relations
                relations = neighborhood.get("relations", [])
                results["summary"]["all_relations"].extend(relations)
            
            time.sleep(2)
        
        results["metadata"]["total_neighborhoods"] = len(key_concepts)
        
        # 3. Génération de relations supplémentaires
        print(f"\n🔗 Génération de relations supplémentaires...")
        all_concept_names = list(set([
            concept.get("name", "") for concept in results["summary"]["all_concepts"] 
            if concept.get("name")
        ]))
        
        if all_concept_names:
            relations_result = self.generate_relations_for_concepts(all_concept_names[:15])
            results["relations"] = relations_result
            
            if relations_result["parsed_data"]:
                additional_relations = relations_result["parsed_data"].get("relations", [])
                results["summary"]["all_relations"].extend(additional_relations)
        
        # Mise à jour des métadonnées finales
        results["metadata"]["total_new_concepts"] = len(results["summary"]["all_concepts"])
        results["metadata"]["total_new_relations"] = len(results["summary"]["all_relations"])
        
        print(f"\n✅ Enrichissement terminé!")
        print(f"   - {results['metadata']['total_new_concepts']} nouveaux concepts")
        print(f"   - {results['metadata']['total_new_relations']} nouvelles relations")
        print(f"   - {results['metadata']['total_domains']} domaines traités")
        print(f"   - {results['metadata']['total_neighborhoods']} voisinages enrichis")
        
        return results

    def export_to_python_code(self, results: Dict, output_file: str = "enriched_concepts.py"):
        """Exporte les résultats vers un fichier Python"""
        
        concepts_dict = {}
        relations_list = []
        
        # Traitement des concepts
        for concept_data in results["summary"]["all_concepts"]:
            if concept_data.get("name") and concept_data.get("type"):
                try:
                    concept_type = ConceptType(concept_data["type"].lower())
                    concepts_dict[concept_data["name"]] = concept_type
                except:
                    continue
        
        # Traitement des relations
        for relation_data in results["summary"]["all_relations"]:
            if all(key in relation_data for key in ["concept1", "relation_type", "concept2"]):
                try:
                    relation_type = RelationType(relation_data["relation_type"].lower())
                    relations_list.append((
                        relation_data["concept1"],
                        relation_type,
                        relation_data["concept2"]
                    ))
                except:
                    continue
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('"""\\nConcepts et relations générés automatiquement par Ollama\\n')
            f.write(f'Générés le: {time.ctime(results["metadata"]["generation_timestamp"])}\\n')
            f.write(f'Modèle utilisé: {results["metadata"]["ollama_model"]}\\n')
            f.write(f'Total concepts: {len(concepts_dict)}\\n')
            f.write(f'Total relations: {len(relations_list)}\\n')
            f.write('"""\\n\\n')
            
            f.write('from concept_types import ConceptType, RelationType\\n\\n')
            
            # Nouveaux concepts
            f.write('# Nouveaux concepts générés\\n')
            f.write('NEW_CONCEPTS = {\\n')
            for concept, concept_type in sorted(concepts_dict.items()):
                f.write(f'    "{concept}": ConceptType.{concept_type.name},\\n')
            f.write('}\\n\\n')
            
            # Nouvelles relations
            f.write('# Nouvelles relations générées\\n')
            f.write('NEW_RELATIONS = [\\n')
            for concept1, relation, concept2 in relations_list:
                f.write(f'    ("{concept1}", RelationType.{relation.name}, "{concept2}"),\\n')
            f.write(']\\n\\n')
            
            # Code pour intégrer
            f.write('# Code pour intégrer dans concept_types.py:\\n')
            f.write('# CORE_PHILOSOPHICAL_CONCEPTS.update(NEW_CONCEPTS)\\n')
            f.write('# CORE_RELATIONS.extend(NEW_RELATIONS)\\n')
        
        print(f"📝 Résultats exportés vers {output_file}")

def main():
    """Fonction principale"""
    enricher = ConceptEnricher()
    
    # Test de connexion à Ollama
    print("🔄 Test de connexion à Ollama...")
    test_response = enricher.query_ollama("Réponds uniquement par 'CONNEXION_OK' si tu me reçois.")
    if not test_response or "CONNEXION_OK" not in test_response:
        print("❌ Impossible de se connecter à Ollama. Vérifiez que le service est lancé.")
        print("   Commandes à exécuter:")
        print("   1. ollama serve")
        print("   2. ollama pull llama3.1")
        return
    
    print("✅ Connexion à Ollama réussie")
    
    # Génération complète
    results = enricher.generate_comprehensive_enrichment()
    
    # Export vers Python
    enricher.export_to_python_code(results)
    
    # Sauvegarde JSON structurée pour debug et réutilisation
    with open('enrichment_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("💾 Résultats complets sauvegardés dans enrichment_results.json")

if __name__ == "__main__":
    main()