"""
SophIA - Système d'IA Philosophique Hybride
LCM (Logical Concept Models) + LLaMA
"""

__version__ = "0.1.0"
__author__ = "Roux"

# Import seulement ce qui existe pour l'instant
from .core.ontology import SimpleOntology, Concept
# from .core.sophia_hybrid import HybridSophIA  # À décommenter plus tard
# from .models.lcm_core import SimpleLCM        # À décommenter plus tard

__all__ = [
    "SimpleOntology", 
    "Concept",
    # "HybridSophIA",  # À décommenter plus tard
    # "SimpleLCM"      # À décommenter plus tard
]