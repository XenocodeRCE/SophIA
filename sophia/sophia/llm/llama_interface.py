"""
Interface Ollama pour l'intégration de LLaMA avec SophIA
Utilise Ollama local pour la génération et extraction conceptuelle
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
import re
import time

logger = logging.getLogger(__name__)

class OllamaLLaMAInterface:
    """Interface pour LLaMA via Ollama local"""
    
    def __init__(self, model_name: str = "llama3.1:latest", 
                 ollama_host: str = "http://localhost:11434"):
        
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.api_url = f"{ollama_host}/api"
        
        # Vérification qu'Ollama est disponible
        self.available = self._check_ollama_availability()
        
        if self.available:
            # Vérification que le modèle est installé
            self.model_available = self._check_model_availability()
            
            if self.model_available:
                logger.info(f"Interface Ollama initialisée avec {model_name}")
            else:
                logger.warning(f"Modèle {model_name} non trouvé dans Ollama")
        else:
            logger.warning("Ollama non disponible, mode fallback activé")
    
    def _check_ollama_availability(self) -> bool:
        """Vérifie qu'Ollama est disponible"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama non accessible: {e}")
            return False
    
    def _check_model_availability(self) -> bool:
        """Vérifie que le modèle LLaMA est installé"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                # Vérification exacte ou partielle du nom
                for name in model_names:
                    if self.model_name in name or name in self.model_name:
                        self.model_name = name  # Utilise le nom exact trouvé
                        logger.info(f"Modèle trouvé: {name}")
                        return True
                
                logger.warning(f"Modèles disponibles: {model_names}")
                return False
            return False
        except Exception as e:
            logger.error(f"Erreur vérification modèle: {e}")
            return False
    
    def generate_text(self, prompt: str, max_tokens: int = 256, 
                     temperature: float = 0.7, stream: bool = False) -> str:
        """Génère du texte à partir d'un prompt via Ollama"""
        
        if not self.available or not self.model_available:
            return self._fallback_generation(prompt, max_tokens)
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                if stream:
                    # Gestion du streaming
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                    return full_response.strip()
                else:
                    # Réponse complète
                    result = response.json()
                    return result.get('response', '').strip()
            else:
                logger.error(f"Erreur Ollama: {response.status_code} - {response.text}")
                return self._fallback_generation(prompt, max_tokens)
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            return self._fallback_generation(prompt, max_tokens)
    
    def _fallback_generation(self, prompt: str, max_tokens: int) -> str:
        """Génération de fallback si Ollama n'est pas disponible"""
        
        # Réponses simulées intelligentes basées sur le prompt
        prompt_lower = prompt.lower()
        
        if "concept" in prompt_lower and "philosophique" in prompt_lower:
            return "Les concepts philosophiques s'interconnectent dans un réseau de relations logiques et sémantiques."
        elif "vérité" in prompt_lower:
            return "La vérité, selon la tradition philosophique, entretient des relations complexes avec la connaissance et l'être."
        elif "être" in prompt_lower and "existence" in prompt_lower:
            return "L'être et l'existence constituent les fondements de l'interrogation métaphysique."
        elif "bien" in prompt_lower or "mal" in prompt_lower:
            return "Les concepts moraux du bien et du mal structurent notre compréhension éthique du monde."
        elif "justice" in prompt_lower:
            return "La justice, en tant que vertu cardinale, relie l'éthique individuelle et l'organisation sociale."
        else:
            return "Cette question mérite une réflexion approfondie sur les relations conceptuelles en jeu."
    
    def extract_concepts_from_text(self, text: str, available_concepts: List[str]) -> Dict[str, Any]:
        """Extrait les concepts philosophiques d'un texte via LLaMA 3.1"""
        
        # Limitation à 30 concepts pour éviter des prompts trop longs
        concepts_sample = available_concepts[:30] if len(available_concepts) > 30 else available_concepts
        
        extraction_prompt = f"""Tu es un expert en philosophie. Analyse ce texte et identifie quels concepts philosophiques y sont présents.

TEXTE À ANALYSER:
"{text}"

CONCEPTS DISPONIBLES:
{', '.join(concepts_sample)}

INSTRUCTIONS:
1. Identifie SEULEMENT les concepts de la liste qui sont réellement présents dans le texte
2. Détermine les relations logiques entre ces concepts
3. Réponds EXACTEMENT en format JSON comme ceci:

{{
    "concepts_detected": ["CONCEPT1", "CONCEPT2"],
    "relations_implied": [
        {{"from": "CONCEPT1", "relation": "IMPLIES", "to": "CONCEPT2"}}
    ],
    "confidence": 0.85
}}

Types de relations possibles: IMPLIES, CONTRADICTS, IS_A, DEFINES, EXPLAINS, OPPOSES

Réponds uniquement avec le JSON, sans autre texte."""
        
        response = self.generate_text(extraction_prompt, max_tokens=300, temperature=0.3)
        
        try:
            # Extraction du JSON de la réponse
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                extracted_data = json.loads(json_str)
                return self._validate_extraction(extracted_data, available_concepts)
            else:
                logger.warning("Pas de JSON trouvé dans la réponse LLaMA")
                return self._fallback_extraction(text, available_concepts)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Erreur parsing JSON: {e}")
            logger.debug(f"Réponse LLaMA: {response}")
            return self._fallback_extraction(text, available_concepts)
    
    def _validate_extraction(self, extracted_data: Dict[str, Any], 
                           available_concepts: List[str]) -> Dict[str, Any]:
        """Valide et nettoie les données extraites par LLaMA"""
        
        available_upper = [c.upper() for c in available_concepts]
        
        # Validation des concepts détectés
        detected_concepts = extracted_data.get('concepts_detected', [])
        valid_concepts = []
        
        for concept in detected_concepts:
            concept_upper = concept.upper().strip()
            if concept_upper in available_upper:
                valid_concepts.append(concept_upper)
        
        # Validation des relations
        relations = extracted_data.get('relations_implied', [])
        valid_relations = []
        
        valid_relation_types = ['IMPLIES', 'CONTRADICTS', 'IS_A', 'DEFINES', 'EXPLAINS', 'OPPOSES']
        
        for relation in relations:
            if (isinstance(relation, dict) and 
                'from' in relation and 'to' in relation and 'relation' in relation):
                
                from_concept = relation['from'].upper().strip()
                to_concept = relation['to'].upper().strip()
                relation_type = relation['relation'].upper().strip()
                
                if (from_concept in available_upper and 
                    to_concept in available_upper and
                    relation_type in valid_relation_types):
                    
                    valid_relations.append({
                        'from': from_concept,
                        'to': to_concept,
                        'relation': relation_type
                    })
        
        return {
            'concepts_detected': valid_concepts,
            'relations_implied': valid_relations,
            'confidence': max(0.1, min(1.0, extracted_data.get('confidence', 0.5)))
        }
    
    def _fallback_extraction(self, text: str, available_concepts: List[str]) -> Dict[str, Any]:
        """Extraction de fallback basée sur la correspondance de mots-clés"""
        
        text_lower = text.lower()
        detected_concepts = []
        
        # Correspondance directe et par mots-clés
        concept_patterns = {
            'VÉRITÉ': ['vérité', 'vrai', 'véridique', 'authentique', 'véracité'],
            'ÊTRE': ['être', 'étant', 'existence', 'existant', 'ontologie'],
            'CONNAISSANCE': ['connaissance', 'savoir', 'connaître', 'epistémologie', 'cognition'],
            'BIEN': ['bien', 'bon', 'bonne', 'bonté', 'bienfait'],
            'MAL': ['mal', 'mauvais', 'mauvaise', 'méchanceté', 'vice'],
            'JUSTICE': ['justice', 'juste', 'équitable', 'équité', 'justesse'],
            'LIBERTÉ': ['liberté', 'libre', 'libération', 'autonomie'],
            'CONSCIENCE': ['conscience', 'conscient', 'awareness', 'conscience de soi'],
            'ARGUMENT': ['argument', 'argumentation', 'raisonnement', 'preuve'],
            'LOGIQUE': ['logique', 'logiquement', 'raisonnement', 'rationnel']
        }
        
        for concept in available_concepts:
            concept_upper = concept.upper()
            
            # Vérification directe
            if concept.lower() in text_lower:
                detected_concepts.append(concept_upper)
                continue
            
            # Vérification par patterns
            if concept_upper in concept_patterns:
                for pattern in concept_patterns[concept_upper]:
                    if pattern in text_lower:
                        detected_concepts.append(concept_upper)
                        break
        
        return {
            'concepts_detected': list(set(detected_concepts)),
            'relations_implied': [],
            'confidence': 0.7 if detected_concepts else 0.3
        }
    
    def generate_with_constraints(self, prompt: str, constraints: Dict[str, Any], 
                                max_attempts: int = 3) -> Dict[str, Any]:
        """Génère du texte en respectant des contraintes conceptuelles"""
        
        constraint_instructions = self._build_constraint_instructions(constraints)
        
        constrained_prompt = f"""Tu es SophIA, une IA philosophique. Réponds à cette question en respectant ABSOLUMENT les contraintes données.

QUESTION:
{prompt}

CONTRAINTES OBLIGATOIRES:
{constraint_instructions}

Réponds de manière naturelle et philosophiquement cohérente en respectant toutes ces contraintes.
"""
        
        for attempt in range(max_attempts):
            # Température décroissante pour forcer la conformité
            temperature = max(0.3, 0.8 - (attempt * 0.2))
            
            response = self.generate_text(
                constrained_prompt, 
                max_tokens=constraints.get('max_tokens', 256),
                temperature=temperature
            )
            
            # Vérification des contraintes
            satisfaction = self._check_constraints_satisfaction(response, constraints)
            
            if satisfaction['satisfied']:
                return {
                    'text': response,
                    'attempt': attempt + 1,
                    'constraints_satisfied': True,
                    'satisfaction_details': satisfaction
                }
            
            # Ajustement pour la prochaine tentative
            failed_constraints = satisfaction['failed_constraints']
            constrained_prompt += f"\n\nATTENTION (Tentative {attempt + 2}): Tu as échoué sur ces contraintes: {failed_constraints}. Corrige-toi !"
        
        return {
            'text': response,
            'attempt': max_attempts,
            'constraints_satisfied': False,
            'satisfaction_details': satisfaction
        }
    
    def _build_constraint_instructions(self, constraints: Dict[str, Any]) -> str:
        """Construit les instructions de contraintes pour le prompt"""
        
        instructions = []
        
        if 'required_concepts' in constraints:
            concepts_str = ', '.join(constraints['required_concepts'])
            instructions.append(f"• Tu DOIS mentionner ces concepts: {concepts_str}")
        
        if 'forbidden_concepts' in constraints:
            forbidden_str = ', '.join(constraints['forbidden_concepts'])
            instructions.append(f"• Tu NE DOIS PAS mentionner: {forbidden_str}")
        
        if 'required_relations' in constraints:
            for relation in constraints['required_relations']:
                instructions.append(
                    f"• Établis cette relation: {relation['from']} {relation['type']} {relation['to']}"
                )
        
        if 'forbidden_relations' in constraints:
            for relation in constraints['forbidden_relations']:
                instructions.append(
                    f"• N'établis JAMAIS: {relation['from']} {relation['type']} {relation['to']}"
                )
        
        if 'tone' in constraints:
            instructions.append(f"• Ton: {constraints['tone']}")
        
        return '\n'.join(instructions) if instructions else "• Réponds de manière cohérente et philosophique"
    
    def _check_constraints_satisfaction(self, text: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie si un texte satisfait les contraintes données"""
        
        text_upper = text.upper()
        failed_constraints = []
        satisfied = True
        
        # Vérification des concepts requis
        if 'required_concepts' in constraints:
            missing_concepts = []
            for concept in constraints['required_concepts']:
                if concept.upper() not in text_upper:
                    missing_concepts.append(concept)
                    satisfied = False
            
            if missing_concepts:
                failed_constraints.append(f"Concepts manquants: {missing_concepts}")
        
        # Vérification des concepts interdits
        if 'forbidden_concepts' in constraints:
            found_forbidden = []
            for concept in constraints['forbidden_concepts']:
                if concept.upper() in text_upper:
                    found_forbidden.append(concept)
                    satisfied = False
            
            if found_forbidden:
                failed_constraints.append(f"Concepts interdits trouvés: {found_forbidden}")
        
        return {
            'satisfied': satisfied,
            'failed_constraints': failed_constraints,
            'text_length': len(text),
            'concepts_found': self._extract_concepts_from_response(text_upper, constraints)
        }
    
    def _extract_concepts_from_response(self, text_upper: str, constraints: Dict[str, Any]) -> List[str]:
        """Extrait rapidement les concepts trouvés dans une réponse"""
        found_concepts = []
        
        all_concepts = []
        all_concepts.extend(constraints.get('required_concepts', []))
        all_concepts.extend(constraints.get('forbidden_concepts', []))
        
        for concept in all_concepts:
            if concept.upper() in text_upper:
                found_concepts.append(concept)
        
        return found_concepts
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne des informations sur le modèle Ollama"""
        
        if not self.available:
            return {
                'status': 'ollama_unavailable',
                'model_name': 'fallback',
                'host': self.ollama_host
            }
        
        if not self.model_available:
            return {
                'status': 'model_unavailable',
                'model_name': self.model_name,
                'host': self.ollama_host
            }
        
        try:
            # Informations détaillées sur le modèle
            response = requests.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_info = None
                
                for model in models:
                    if model['name'] == self.model_name:
                        model_info = model
                        break
                
                return {
                    'status': 'ready',
                    'model_name': self.model_name,
                    'host': self.ollama_host,
                    'model_info': model_info,
                    'size_gb': model_info.get('size', 0) / (1024**3) if model_info else 'unknown'
                }
        except:
            pass
        
        return {
            'status': 'ready',
            'model_name': self.model_name,
            'host': self.ollama_host
        }

# Alias pour compatibilité
LLaMAInterface = OllamaLLaMAInterface