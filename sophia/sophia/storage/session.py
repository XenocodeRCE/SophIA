"""
Gestionnaire de sessions d'entraînement pour SophIA
Gestion des checkpoints et reprise d'entraînement
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from .serializer import LCMSerializer
from ..models.lcm_core import SimpleLCM
from ..core.ontology import SimpleOntology
from ..training.trainer import SimpleLCMTrainer

logger = logging.getLogger(__name__)

class TrainingSession:
    """Gestionnaire de session d'entraînement avec checkpoints automatiques"""
    
    def __init__(self, session_name: str, base_path: str = "./models/sessions"):
        self.session_name = session_name
        self.base_path = Path(base_path)
        self.session_path = self.base_path / session_name
        
        # Création des dossiers
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.checkpoints_path = self.session_path / "checkpoints"
        self.checkpoints_path.mkdir(exist_ok=True)
        
        # Sérialiseur
        self.serializer = LCMSerializer(str(self.session_path))
        
        # Historique des checkpoints
        self.checkpoints_history: List[Dict[str, Any]] = []
        self._load_session_metadata()
        
        logger.info(f"Session d'entraînement initialisée: {session_name}")
    
    def _load_session_metadata(self) -> None:
        """Charge les métadonnées de la session si elles existent"""
        
        metadata_file = self.session_path / "session_metadata.json"
        
        if metadata_file.exists():
            try:
                import json
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    self.checkpoints_history = session_data.get('checkpoints_history', [])
                logger.info(f"Métadonnées de session chargées: {len(self.checkpoints_history)} checkpoints")
            except Exception as e:
                logger.warning(f"Impossible de charger les métadonnées de session: {e}")
    
    def _save_session_metadata(self) -> None:
        """Sauvegarde les métadonnées de la session"""
        
        metadata_file = self.session_path / "session_metadata.json"
        
        session_data = {
            'session_name': self.session_name,
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'checkpoints_history': self.checkpoints_history
        }
        
        try:
            import json
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des métadonnées: {e}")
    
    def save_checkpoint(self, model: SimpleLCM, ontology: SimpleOntology, 
                       trainer: SimpleLCMTrainer, epoch: int, 
                       metrics: Optional[Dict[str, Any]] = None) -> str:
        """Sauvegarde un checkpoint d'entraînement"""
        
        checkpoint_name = f"checkpoint_epoch_{epoch:04d}"
        
        # Métadonnées du checkpoint
        checkpoint_metadata = {
            'session_name': self.session_name,
            'epoch': epoch,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics or {},
            'is_checkpoint': True
        }
        
        # Sauvegarde
        checkpoint_path = self.serializer.save_complete_model(
            model, ontology, trainer,
            model_name=checkpoint_name,
            metadata=checkpoint_metadata
        )
        
        # Enregistrement dans l'historique
        checkpoint_info = {
            'epoch': epoch,
            'filepath': checkpoint_path,
            'timestamp': checkpoint_metadata['timestamp'],
            'metrics': metrics or {}
        }
        
        self.checkpoints_history.append(checkpoint_info)
        self._save_session_metadata()
        
        logger.info(f"Checkpoint sauvegardé: époque {epoch}")
        return checkpoint_path
    
    def save_final_model(self, model: SimpleLCM, ontology: SimpleOntology, 
                        trainer: SimpleLCMTrainer, 
                        final_metrics: Optional[Dict[str, Any]] = None) -> str:
        """Sauvegarde le modèle final de la session"""
        
        final_metadata = {
            'session_name': self.session_name,
            'is_final_model': True,
            'total_checkpoints': len(self.checkpoints_history),
            'final_metrics': final_metrics or {},
            'training_completed': datetime.now().isoformat()
        }
        
        final_model_name = f"{self.session_name}_final"
        
        final_path = self.serializer.save_complete_model(
            model, ontology, trainer,
            model_name=final_model_name,
            metadata=final_metadata
        )
        
        logger.info(f"Modèle final sauvegardé: {final_path}")
        return final_path
    
    def load_checkpoint(self, epoch: int) -> Tuple[SimpleLCM, SimpleOntology, SimpleLCMTrainer, Dict[str, Any]]:
        """Charge un checkpoint spécifique"""
        
        # Recherche du checkpoint
        checkpoint_info = None
        for checkpoint in self.checkpoints_history:
            if checkpoint['epoch'] == epoch:
                checkpoint_info = checkpoint
                break
        
        if not checkpoint_info:
            raise ValueError(f"Checkpoint pour l'époque {epoch} non trouvé")
        
        filepath = checkpoint_info['filepath']
        
        try:
            model, ontology, trainer, metadata = self.serializer.load_complete_model(filepath)
            logger.info(f"Checkpoint chargé: époque {epoch}")
            return model, ontology, trainer, metadata
        except Exception as e:
            logger.error(f"Erreur lors du chargement du checkpoint {epoch}: {e}")
            raise
    
    def load_latest_checkpoint(self) -> Optional[Tuple[SimpleLCM, SimpleOntology, SimpleLCMTrainer, Dict[str, Any]]]:
        """Charge le checkpoint le plus récent"""
        
        if not self.checkpoints_history:
            logger.warning("Aucun checkpoint disponible")
            return None
        
        latest_checkpoint = max(self.checkpoints_history, key=lambda x: x['epoch'])
        return self.load_checkpoint(latest_checkpoint['epoch'])
    
    def load_final_model(self) -> Tuple[SimpleLCM, SimpleOntology, SimpleLCMTrainer, Dict[str, Any]]:
        """Charge le modèle final de la session"""
        
        final_model_path = self.session_path / f"{self.session_name}_final.sophia"
        
        if not final_model_path.exists():
            raise FileNotFoundError(f"Modèle final non trouvé: {final_model_path}")
        
        return self.serializer.load_complete_model(str(final_model_path))
    
    def resume_training_from_epoch(self, epoch: int) -> Tuple[SimpleLCM, SimpleOntology, SimpleLCMTrainer, int]:
        """Reprend l'entraînement depuis un checkpoint spécifique"""
        
        model, ontology, trainer, metadata = self.load_checkpoint(epoch)
        
        logger.info(f"Reprise de l'entraînement depuis l'époque {epoch}")
        return model, ontology, trainer, epoch
    
    def resume_training_from_latest(self) -> Optional[Tuple[SimpleLCM, SimpleOntology, SimpleLCMTrainer, int]]:
        """Reprend l'entraînement depuis le dernier checkpoint"""
        
        latest_data = self.load_latest_checkpoint()
        if not latest_data:
            return None
        
        model, ontology, trainer, metadata = latest_data
        epoch = metadata.get('epoch', 0)
        
        logger.info(f"Reprise de l'entraînement depuis le dernier checkpoint (époque {epoch})")
        return model, ontology, trainer, epoch
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Liste tous les checkpoints de la session"""
        
        return sorted(self.checkpoints_history, key=lambda x: x['epoch'])
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la session d'entraînement"""
        
        if not self.checkpoints_history:
            return {
                'session_name': self.session_name,
                'status': 'empty',
                'checkpoints_count': 0
            }
        
        epochs = [cp['epoch'] for cp in self.checkpoints_history]
        
        return {
            'session_name': self.session_name,
            'status': 'active',
            'checkpoints_count': len(self.checkpoints_history),
            'epochs_range': {'min': min(epochs), 'max': max(epochs)},
            'latest_checkpoint': max(self.checkpoints_history, key=lambda x: x['epoch']),
            'total_size_mb': self._calculate_session_size()
        }
    
    def _calculate_session_size(self) -> float:
        """Calcule la taille totale de la session en MB"""
        
        total_size = 0
        
        for filepath in self.session_path.rglob("*"):
            if filepath.is_file():
                total_size += filepath.stat().st_size
        
        return total_size / (1024 * 1024)
    
    def cleanup_old_checkpoints(self, keep_latest: int = 5) -> int:
        """Nettoie les anciens checkpoints en gardant seulement les N plus récents"""
        
        if len(self.checkpoints_history) <= keep_latest:
            return 0
        
        # Tri par époque (plus récent en premier)
        sorted_checkpoints = sorted(self.checkpoints_history, key=lambda x: x['epoch'], reverse=True)
        
        # Checkpoints à supprimer
        to_delete = sorted_checkpoints[keep_latest:]
        deleted_count = 0
        
        for checkpoint in to_delete:
            try:
                filepath = Path(checkpoint['filepath'])
                if self.serializer.delete_model(str(filepath)):
                    self.checkpoints_history.remove(checkpoint)
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Impossible de supprimer le checkpoint {checkpoint['epoch']}: {e}")
        
        if deleted_count > 0:
            self._save_session_metadata()
            logger.info(f"Nettoyage terminé: {deleted_count} checkpoints supprimés")
        
        return deleted_count