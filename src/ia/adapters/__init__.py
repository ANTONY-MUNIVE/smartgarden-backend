"""
Adaptadores para el puerto de IA.

Los adaptadores implementan la interfaz IAPort y pueden usar diferentes
tecnologías, APIs o modelos de machine learning internamente.
"""

from .openmeteo_ia_adapter import OpenMeteoIAAdapter

__all__ = ["OpenMeteoIAAdapter"]
