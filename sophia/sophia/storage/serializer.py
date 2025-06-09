"""
Système de sérialisation pour SophIA
Sauvegarde et chargement des modèles, ontologies et états d'entraînement
"""

import json
import pickle
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import logging
from pathlib import Path

from sophia.core.ontology import SimpleOntology, Concept
from sophia.models.lcm_core import SimpleLCM
from sophia.training.trainer import SimpleLCMTrainer, OntologyAwareLCMTrainer


logger = logging.getLogger(__name__)

class LCMSerializer:
    """Sérialiseur pour les modèles LCM et ontologies"""
    
    def __init__(self, base_path: str = "./models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.version = "1.0"
        
        logger.info(f"LCMSerializer initialisé avec base_path: {self.base_path}")
    
    def save_complete_model(self, model: SimpleLCM, ontology: SimpleOntology, 
                           trainer: Optional[SimpleLCMTrainer] = None,
                           model_name: str = "sophia_model", 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Sauvegarde complète : modèle + ontologie + trainer"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name}_{timestamp}"
        filepath = self.base_path / f"{filename}.sophia"
        
        # Construction des données complètes
        save_data = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'metadata': metadata or {},
            
            # Données principales
            'ontology': self._serialize_ontology(ontology),
            'model': self._serialize_lcm_model(model),
            'trainer': self._serialize_trainer(trainer) if trainer else None,
            
            # Statistiques de sauvegarde
            'save_stats': {
                'concepts_count': len(ontology.concepts),
                'transitions_count': len(model.transitions),
                'training_epochs': len(trainer.training_history) if trainer else 0
            }
        }
        
        # Sauvegarde du fichier principal (JSON)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Sauvegarde des données binaires si nécessaire (historique d'entraînement détaillé)
            if trainer and trainer.training_history:
                binary_filepath = filepath.with_suffix('.training_data')
                with open(binary_filepath, 'wb') as f:
                    pickle.dump({
                        'training_history': trainer.training_history,
                        'model_transitions_detailed': model.transitions
                    }, f)
            
            logger.info(f"Modèle sauvegardé: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise
    
    def load_complete_model(self, filepath: str) -> Tuple[SimpleLCM, SimpleOntology, Optional[SimpleLCMTrainer], Dict[str, Any]]:
        """Charge un modèle complet"""
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier modèle non trouvé: {filepath}")
        
        try:
            # Chargement du fichier principal
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Reconstruction de l'ontologie
            ontology = self._deserialize_ontology(save_data['ontology'])
            
            # Reconstruction du modèle LCM
            model = self._deserialize_lcm_model(save_data['model'], ontology)
            
            # Reconstruction du trainer
            trainer = None
            if save_data.get('trainer'):
                trainer = self._deserialize_trainer(save_data['trainer'], model, ontology)
                
                # Chargement des données binaires si disponibles
                binary_filepath = filepath.with_suffix('.training_data')
                if binary_filepath.exists():
                    with open(binary_filepath, 'rb') as f:
                        binary_data = pickle.load(f)
                        trainer.training_history = binary_data.get('training_history', [])
            
            metadata = save_data.get('metadata', {})
            
            logger.info(f"Modèle chargé: {filepath}")
            logger.info(f"Version: {save_data.get('version', 'unknown')}")
            logger.info(f"Concepts: {len(ontology.concepts)}, Transitions: {len(model.transitions)}")
            
            return model, ontology, trainer, metadata
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            raise
    
    def _serialize_ontology(self, ontology: SimpleOntology) -> Dict[str, Any]:
        """Sérialise une ontologie"""
        
        return {
            'metadata': ontology.metadata,
            'concepts': {
                name: concept.to_dict() 
                for name, concept in ontology.concepts.items()
            }
        }
    
    def _deserialize_ontology(self, data: Dict[str, Any]) -> SimpleOntology:
        """Désérialise une ontologie"""
        
        ontology = SimpleOntology(load_core_concepts=False)
        ontology.metadata = data.get('metadata', ontology.metadata)
        
        # Reconstruction des concepts
        concepts_data = data.get('concepts', {})
        for name, concept_data in concepts_data.items():
            concept = Concept.from_dict(concept_data)
            ontology.concepts[name] = concept
        
        return ontology
    
    def _serialize_lcm_model(self, model: SimpleLCM) -> Dict[str, Any]:
        """Sérialise un modèle LCM"""
        
        return {
            'model_type': 'SimpleLCM',
            'learning_rate': model.learning_rate,
            'model_state': model.save_model_state(),
            'model_stats': model.get_model_stats()
        }
    
    def _deserialize_lcm_model(self, data: Dict[str, Any], ontology: SimpleOntology) -> SimpleLCM:
        """Désérialise un modèle LCM"""
        
        learning_rate = data.get('learning_rate', 0.1)
        model = SimpleLCM(ontology, learning_rate=learning_rate)
        
        # Chargement de l'état du modèle
        model_state = data.get('model_state', {})
        if model_state:
            model.load_model_state(model_state)
        
        return model
    
    def _serialize_trainer(self, trainer: SimpleLCMTrainer) -> Dict[str, Any]:
        """Sérialise un trainer"""
        
        trainer_data = {
            'trainer_type': trainer.__class__.__name__,
            'learning_rate': trainer.learning_rate,
            'batch_size': trainer.batch_size,
            'validation_split': trainer.validation_split,
            'training_summary': trainer.get_training_summary()
        }
        
        # Données spécifiques au trainer ontologique
        if isinstance(trainer, OntologyAwareLCMTrainer):
            trainer_data['consistency_weight'] = trainer.consistency_weight
            trainer_data['ontological_constraints_count'] = len(trainer.ontological_constraints)
        
        return trainer_data
    
    def _deserialize_trainer(self, data: Dict[str, Any], model: SimpleLCM, 
                           ontology: SimpleOntology) -> SimpleLCMTrainer:
        """Désérialise un trainer"""
        
        trainer_type = data.get('trainer_type', 'SimpleLCMTrainer')
        
        if trainer_type == 'OntologyAwareLCMTrainer':
            consistency_weight = data.get('consistency_weight', 0.3)
            trainer = OntologyAwareLCMTrainer(model, ontology, consistency_weight)
        else:
            trainer = SimpleLCMTrainer(model, ontology)
        
        # Restauration des paramètres
        trainer.learning_rate = data.get('learning_rate', 0.1)
        trainer.batch_size = data.get('batch_size', 32)
        trainer.validation_split = data.get('validation_split', 0.2)
        
        return trainer
    
    def list_saved_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles sauvegardés"""
        
        models = []
        
        for filepath in self.base_path.glob("*.sophia"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                model_info = {
                    'filename': filepath.name,
                    'filepath': str(filepath),
                    'model_name': data.get('model_name', 'unknown'),
                    'timestamp': data.get('timestamp', 'unknown'),
                    'version': data.get('version', 'unknown'),
                    'stats': data.get('save_stats', {}),
                    'size_mb': filepath.stat().st_size / (1024 * 1024)
                }
                
                models.append(model_info)
                
            except Exception as e:
                logger.warning(f"Impossible de lire le modèle {filepath}: {e}")
        
        # Tri par date de création (plus récent en premier)
        models.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return models
    
    def delete_model(self, filepath: str) -> bool:
        """Supprime un modèle sauvegardé"""
        
        filepath = Path(filepath)
        
        try:
            # Suppression du fichier principal
            if filepath.exists():
                filepath.unlink()
            
            # Suppression du fichier de données binaires associé
            binary_filepath = filepath.with_suffix('.training_data')
            if binary_filepath.exists():
                binary_filepath.unlink()
            
            logger.info(f"Modèle supprimé: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False
    
    def export_model_summary(self, filepath: str) -> Dict[str, Any]:
        """Exporte un résumé détaillé d'un modèle"""
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier modèle non trouvé: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Construction du résumé
        summary = {
            'model_info': {
                'name': data.get('model_name', 'unknown'),
                'version': data.get('version', 'unknown'),
                'timestamp': data.get('timestamp', 'unknown'),
                'metadata': data.get('metadata', {})
            },
            'ontology_summary': {
                'total_concepts': len(data.get('ontology', {}).get('concepts', {})),
                'concept_types': self._analyze_concept_types(data.get('ontology', {})),
                'relations_count': self._count_ontology_relations(data.get('ontology', {}))
            },
            'model_summary': {
                'transitions_count': len(data.get('model', {}).get('model_state', {}).get('transitions', {})),
                'learning_rate': data.get('model', {}).get('learning_rate', 0),
                'coverage_stats': data.get('model', {}).get('model_stats', {})
            },
            'training_summary': data.get('trainer', {}).get('training_summary', {}) if data.get('trainer') else None
        }
        
        return summary
    
    def _analyze_concept_types(self, ontology_data: Dict[str, Any]) -> Dict[str, int]:
        """Analyse la répartition des types de concepts"""
        
        type_counts = {}
        concepts = ontology_data.get('concepts', {})
        
        for concept_data in concepts.values():
            concept_type = concept_data.get('concept_type', 'unknown')
            type_counts[concept_type] = type_counts.get(concept_type, 0) + 1
        
        return type_counts
    
    def _count_ontology_relations(self, ontology_data: Dict[str, Any]) -> int:
        """Compte le nombre total de relations dans l'ontologie"""
        
        total_relations = 0
        concepts = ontology_data.get('concepts', {})
        
        for concept_data in concepts.values():
            relations = concept_data.get('relations', {})
            for relation_list in relations.values():
                total_relations += len(relation_list)
        
        return total_relations