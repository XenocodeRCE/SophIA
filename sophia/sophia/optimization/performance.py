"""
Performance Monitor ultra-avancé pour SophIA
Métriques détaillées, analyse en temps réel, optimisations
"""

import time
import psutil
import threading
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class OperationMetrics:
    """Métriques détaillées d'une opération"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.duration = 0.0
        self.memory_start = psutil.virtual_memory().used
        self.memory_end = None
        self.memory_delta = 0
        self.cpu_start = psutil.cpu_percent()
        self.cpu_end = None
        self.cpu_avg = 0.0
        self.error = None
        self.sub_operations = []
        self.metadata = {}
    
    def end(self, error: Optional[str] = None):
        """Termine l'opération et calcule les métriques"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.memory_end = psutil.virtual_memory().used
        self.memory_delta = self.memory_end - self.memory_start
        self.cpu_end = psutil.cpu_percent()
        self.cpu_avg = (self.cpu_start + self.cpu_end) / 2
        self.error = error
    
    def add_metadata(self, key: str, value: Any):
        """Ajoute des métadonnées à l'opération"""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'name': self.name,
            'duration': self.duration,
            'memory_delta_mb': self.memory_delta / (1024 * 1024),
            'cpu_avg': self.cpu_avg,
            'error': self.error,
            'metadata': self.metadata,
            'sub_operations': len(self.sub_operations)
        }

class PerformanceMonitor:
    """
    Monitor de performance ultra-avancé pour SophIA
    - Métriques en temps réel
    - Analyse des goulots d'étranglement
    - Recommandations d'optimisation
    - Historique des performances
    """
    
    def __init__(self, history_size: int = 1000, enable_auto_save: bool = True):
        self.history_size = history_size
        self.enable_auto_save = enable_auto_save
        
        # Métriques actuelles
        self.active_operations: Dict[str, OperationMetrics] = {}
        self.completed_operations: deque = deque(maxlen=history_size)
        
        # Statistiques globales
        self.session_start = time.time()
        self.total_operations = 0
        self.total_errors = 0
        
        # Métriques par type d'opération
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        self.error_stats: Dict[str, int] = defaultdict(int)
        
        # Seuils d'alerte
        self.slow_operation_threshold = 5.0  # secondes
        self.high_memory_threshold = 100  # MB
        self.high_cpu_threshold = 80  # %
        
        # Thread monitoring
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Cache des recommandations
        self._recommendations_cache = []
        self._last_analysis = None
        
        logger.info("📊 Performance Monitor Ultra-Avancé initialisé")
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._background_monitor,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.debug("🔍 Monitoring en arrière-plan démarré")
    
    def _background_monitor(self):
        """Monitoring continu en arrière-plan"""
        while self.monitoring_active:
            try:
                # Vérification des opérations longues
                current_time = time.time()
                for op_name, op_metrics in self.active_operations.items():
                    duration = current_time - op_metrics.start_time
                    if duration > self.slow_operation_threshold:
                        logger.warning(f"⚠️ Opération lente détectée: {op_name} ({duration:.2f}s)")
                
                # Vérification mémoire/CPU
                memory_percent = psutil.virtual_memory().percent
                cpu_percent = psutil.cpu_percent(interval=1)
                
                if memory_percent > 90:
                    logger.warning(f"⚠️ Mémoire élevée: {memory_percent:.1f}%")
                
                if cpu_percent > self.high_cpu_threshold:
                    logger.warning(f"⚠️ CPU élevé: {cpu_percent:.1f}%")
                
                time.sleep(2)  # Vérification toutes les 2 secondes
                
            except Exception as e:
                logger.error(f"Erreur monitoring arrière-plan: {e}")
                time.sleep(5)
    
    def start_operation(self, operation_name: str, metadata: Optional[Dict] = None) -> str:
        """Démarre le tracking d'une opération"""
        # Identifiant unique pour les opérations imbriquées
        operation_id = f"{operation_name}_{int(time.time() * 1000000) % 1000000}"
        
        metrics = OperationMetrics(operation_name)
        if metadata:
            metrics.metadata.update(metadata)
        
        self.active_operations[operation_id] = metrics
        
        logger.debug(f"📊 Début opération: {operation_name} (ID: {operation_id})")
        return operation_id
    
    def end_operation(self, operation_id: str, error: Optional[str] = None, 
                     metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Termine une opération et retourne les métriques"""
        
        if operation_id not in self.active_operations:
            # Fallback pour compatibilité avec l'ancienne API
            operation_name = operation_id
            matching_ops = [
                (oid, op) for oid, op in self.active_operations.items() 
                if op.name == operation_name
            ]
            
            if matching_ops:
                operation_id, _ = matching_ops[-1]  # Prend la plus récente
            else:
                logger.warning(f"Opération inconnue: {operation_id}")
                return {}
        
        metrics = self.active_operations.pop(operation_id)
        metrics.end(error)
        
        if metadata:
            metrics.metadata.update(metadata)
        
        # Statistiques
        self.total_operations += 1
        if error:
            self.total_errors += 1
            self.error_stats[metrics.name] += 1
        
        self.operation_stats[metrics.name].append(metrics.duration)
        self.completed_operations.append(metrics)
        
        # Alertes
        if metrics.duration > self.slow_operation_threshold:
            logger.warning(f"🐌 Opération lente: {metrics.name} ({metrics.duration:.2f}s)")
        
        if abs(metrics.memory_delta) > self.high_memory_threshold * 1024 * 1024:
            memory_mb = metrics.memory_delta / (1024 * 1024)
            logger.warning(f"💾 Usage mémoire élevé: {metrics.name} ({memory_mb:+.1f}MB)")
        
        result = metrics.to_dict()
        logger.debug(f"📊 Fin opération: {metrics.name} ({metrics.duration:.3f}s)")
        
        return result
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """Statistiques détaillées par type d'opération"""
        stats = {}
        
        for op_name, durations in self.operation_stats.items():
            if durations:
                stats[op_name] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'total_duration': sum(durations),
                    'error_count': self.error_stats.get(op_name, 0),
                    'error_rate': self.error_stats.get(op_name, 0) / len(durations) * 100,
                    'recent_trend': self._calculate_trend(durations[-10:]) if len(durations) >= 5 else 'stable'
                }
        
        return stats
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance des performances"""
        if len(values) < 3:
            return 'stable'
        
        # Régression linéaire simple
        n = len(values)
        x_avg = sum(range(n)) / n
        y_avg = sum(values) / n
        
        numerator = sum((i - x_avg) * (y - y_avg) for i, y in enumerate(values))
        denominator = sum((i - x_avg) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'deteriorating'
        elif slope < -0.1:
            return 'improving'
        else:
            return 'stable'
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Informations détaillées sur l'usage mémoire"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        return {
            'system_total_gb': memory.total / (1024**3),
            'system_available_gb': memory.available / (1024**3),
            'system_used_percent': memory.percent,
            'process_memory_mb': process.memory_info().rss / (1024**2),
            'process_memory_percent': process.memory_percent(),
            'memory_status': self._get_memory_status(memory.percent)
        }
    
    def _get_memory_status(self, percent: float) -> str:
        """Détermine le statut de la mémoire"""
        if percent < 50:
            return 'optimal'
        elif percent < 70:
            return 'good'
        elif percent < 85:
            return 'warning'
        else:
            return 'critical'
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Informations détaillées sur l'usage CPU"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_count_logical': cpu_count,
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_status': self._get_cpu_status(cpu_percent),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def _get_cpu_status(self, percent: float) -> str:
        """Détermine le statut du CPU"""
        if percent < 30:
            return 'optimal'
        elif percent < 60:
            return 'good'
        elif percent < 80:
            return 'warning'
        else:
            return 'critical'
    
    def calculate_efficiency(self) -> float:
        """Calcule un score d'efficacité global"""
        if not self.operation_stats:
            return 1.0
        
        # Facteurs d'efficacité
        error_rate = self.total_errors / max(self.total_operations, 1)
        
        # Performance moyenne
        all_durations = []
        for durations in self.operation_stats.values():
            all_durations.extend(durations)
        
        avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0
        
        # Score basé sur vitesse et fiabilité
        speed_score = max(0, 1 - (avg_duration / 10))  # Normalise sur 10s max
        reliability_score = 1 - error_rate
        
        return (speed_score * 0.6 + reliability_score * 0.4)
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Génère des recommandations d'optimisation intelligentes"""
        recommendations = []
        
        # Analyse des opérations lentes
        slow_operations = []
        for op_name, durations in self.operation_stats.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > self.slow_operation_threshold:
                    slow_operations.append((op_name, avg_duration))
        
        if slow_operations:
            slow_operations.sort(key=lambda x: x[1], reverse=True)
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'Optimiser les opérations lentes',
                'description': f"Opérations à optimiser: {', '.join([op[0] for op in slow_operations[:3]])}",
                'impact': 'Amélioration significative du temps de réponse',
                'actions': [
                    'Analyser les goulots d\'étranglement',
                    'Implémenter du cache',
                    'Paralléliser les opérations'
                ]
            })
        
        # Analyse de la mémoire
        memory = self.get_memory_usage()
        if memory['system_used_percent'] > 80:
            recommendations.append({
                'type': 'memory',
                'priority': 'medium',
                'title': 'Optimiser l\'usage mémoire',
                'description': f"Usage mémoire élevé: {memory['system_used_percent']:.1f}%",
                'impact': 'Prévention des ralentissements système',
                'actions': [
                    'Implémenter un garbage collection',
                    'Optimiser les caches',
                    'Réduire les données en mémoire'
                ]
            })
        
        # Analyse des erreurs
        high_error_ops = [
            (op, rate) for op, stats in self.get_operation_stats().items()
            if stats['error_rate'] > 10
        ]
        
        if high_error_ops:
            recommendations.append({
                'type': 'reliability',
                'priority': 'high',
                'title': 'Améliorer la fiabilité',
                'description': f"Opérations avec taux d'erreur élevé: {len(high_error_ops)}",
                'impact': 'Amélioration de la stabilité système',
                'actions': [
                    'Renforcer la gestion d\'erreurs',
                    'Ajouter des retry mechanisms',
                    'Implémenter des fallbacks'
                ]
            })
        
        # Recommandations générales
        efficiency = self.calculate_efficiency()
        if efficiency < 0.7:
            recommendations.append({
                'type': 'general',
                'priority': 'medium',
                'title': 'Optimisation générale',
                'description': f"Score d'efficacité: {efficiency:.1%}",
                'impact': 'Amélioration globale des performances',
                'actions': [
                    'Profiling détaillé du code',
                    'Optimisation des algorithmes',
                    'Mise à jour des dépendances'
                ]
            })
        
        return recommendations
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Statistiques globales du système"""
        session_duration = time.time() - self.session_start
        
        return {
            'session_duration_minutes': session_duration / 60,
            'total_operations': self.total_operations,
            'total_errors': self.total_errors,
            'error_rate_percent': (self.total_errors / max(self.total_operations, 1)) * 100,
            'operations_per_minute': self.total_operations / max(session_duration / 60, 1),
            'efficiency_score': self.calculate_efficiency(),
            'active_operations': len(self.active_operations),
            'memory_status': self.get_memory_usage()['memory_status'],
            'cpu_status': self.get_cpu_usage()['cpu_status']
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Rapport de performance complet"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': self.get_overall_stats(),
            'operation_stats': self.get_operation_stats(),
            'system_resources': {
                'memory': self.get_memory_usage(),
                'cpu': self.get_cpu_usage()
            },
            'recommendations': self.get_optimization_recommendations(),
            'recent_operations': [
                op.to_dict() for op in list(self.completed_operations)[-10:]
            ]
        }
    
    def save_report(self, filepath: Optional[str] = None) -> str:
        """Sauvegarde le rapport de performance"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"performance_report_{timestamp}.json"
        
        report = self.get_detailed_report()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Rapport de performance sauvegardé: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport: {e}")
            return ""
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        logger.info("📊 Performance Monitor arrêté")
    
    def __del__(self):
        """Cleanup lors de la destruction"""
        self.stop_monitoring()
        
    def set_thresholds(self, slow_threshold: float = 3.0, memory_threshold: int = 50, cpu_threshold: int = 70):
        """Configure des seuils plus adaptés pour SophIA"""
        self.slow_operation_threshold = slow_threshold
        self.high_memory_threshold = memory_threshold  
        self.high_cpu_threshold = cpu_threshold
        logger.info(f"📊 Seuils mis à jour: slow={slow_threshold}s, memory={memory_threshold}MB, cpu={cpu_threshold}%")