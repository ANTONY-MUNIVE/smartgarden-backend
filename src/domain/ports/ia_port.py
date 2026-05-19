"""
Puerto (Interfaz) para servicios de IA.

Define el contrato que cualquier adaptador IA debe cumplir.
Desacopla la lógica de negocio de la implementación específica.
Siguiendo el principio de arquitectura hexagonal.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class IAPort(ABC):
    """Puerto para servicios de Inteligencia Artificial.
    
    Expone métodos públicos para:
    - Predicciones completas (clima + riegos + enfermedades + sol)
    - Cálculos individuales de riegos, enfermedades, horarios
    - Obtención de datos de clima
    - Generación de alertas y recomendaciones
    
    Cualquier adaptador (OpenMeteo, modelo ML avanzado, etc) debe
    implementar esta interfaz.
    """
    
    @abstractmethod
    def predecir_completo(
        self,
        humedad_suelo: float,
        temperatura: float,
        luz: float,
        humedad_aire: float,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Análisis predictivo completo incluyendo:
        - Pronóstico climático 7 días
        - Calendario de riegos optimizado
        - Horarios de luz solar óptima
        - Riesgo de enfermedades (% y tipo)
        - Recomendaciones generales consolidadas
        
        Args:
            humedad_suelo: Humedad actual del suelo (0-100)
            temperatura: Temperatura actual (°C)
            luz: Luminosidad actual (lux)
            humedad_aire: Humedad del aire (0-100)
            latitude: Latitud de ubicación (-90 a 90)
            longitude: Longitud de ubicación (-180 a 180)
        
        Returns:
            Dict con estructura: {
                'timestamp': ISO timestamp,
                'ubicacion': {'lat': float, 'lon': float},
                'clima_actual': {...},
                'pronostico_7_dias': [...],
                'calendario_riegos': [...],
                'horarios_sol_optimo': [...],
                'riesgo_enfermedad': {...},
                'alertas_clima': [...],
                'recomendaciones_generales': [...]
            }
        
        Raises:
            Exception: Si hay error en análisis (retorna con 'error' key)
        """
        pass
    
    @abstractmethod
    def calcular_riegos(
        self,
        humedad_suelo: float,
        pronostico_7_dias: List[Dict]
    ) -> List[Dict]:
        """
        Calcula calendario optimizado de riegos basado en predicción.
        
        Args:
            humedad_suelo: Humedad actual del suelo (0-100)
            pronostico_7_dias: Lista de dicts con pronóstico diario
        
        Returns:
            Lista de dicts con calendario de riegos para 7 días:
            [{
                'fecha': YYYY-MM-DD,
                'necesidad': 'URGENTE' | 'ALTA' | 'MEDIA' | 'BAJA',
                'cantidad_litros_m2': float,
                'horario_recomendado': str,
                'lluvia_esperada': float,
                'temp_max': float,
                'humedad_predicha': float,
                'notas': str
            }, ...]
        """
        pass
    
    @abstractmethod
    def generar_recomendaciones(
        self,
        calendario: List[Dict],
        riesgo_enfermedad: Dict,
        horarios_sol: List[Dict]
    ) -> List[str]:
        """
        Genera recomendaciones consolidadas basadas en todos los análisis.
        
        Args:
            calendario: Calendario de riegos calculado
            riesgo_enfermedad: Análisis de riesgo de enfermedades
            horarios_sol: Horarios de luz solar
        
        Returns:
            Lista de strings con recomendaciones para el usuario
        """
        pass
    
    @abstractmethod
    def obtener_clima_actual(
        self,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Obtiene clima actual y pronóstico de 7 días.
        
        Args:
            latitude: Latitud (-90 a 90)
            longitude: Longitud (-180 a 180)
        
        Returns:
            Dict con clima actual, pronóstico, horarios sol, etc.
            Si hay error: {'status': 'error', 'error': mensaje}
        """
        pass
    
    @abstractmethod
    def calcular_horas_luz(
        self,
        horarios_sol: List[Dict]
    ) -> List[Dict]:
        """
        Calcula horas de luz solar útil a partir de horarios.
        
        Args:
            horarios_sol: Lista con horarios de salida/puesta de sol
        
        Returns:
            Lista de dicts con horas de luz por día:
            [{
                'fecha': YYYY-MM-DD,
                'salida': HH:MM,
                'puesta': HH:MM,
                'horas_luz': float
            }, ...]
        """
        pass
    
    @abstractmethod
    def obtener_alertas_clima(
        self,
        clima_actual: Dict,
        pronostico_7_dias: List[Dict]
    ) -> List[str]:
        """
        Genera alertas climáticas basadas en condiciones actuales y futuras.
        
        Args:
            clima_actual: Dict con condiciones actuales
            pronostico_7_dias: Lista de pronósticos diarios
        
        Returns:
            Lista de strings con alertas (ej: "Sequía prevista", "Lluvia torrencial")
        """
        pass
    
    @abstractmethod
    def predecir_enfermedades(
        self,
        humedad_suelo: float,
        humedad_aire: float,
        temperatura: float,
        precipitacion: float,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Predice riesgo de enfermedades del cultivo basado en clima.
        
        Args:
            humedad_suelo: Humedad del suelo (0-100)
            humedad_aire: Humedad del aire (0-100)
            temperatura: Temperatura actual (°C)
            precipitacion: Precipitación esperada (mm)
            latitude: Latitud
            longitude: Longitud
        
        Returns:
            Dict con análisis de riesgo:
            {
                'probabilidad_enfermedad': float (0-100),
                'nivel_riesgo': 'BAJO' | 'MODERADO' | 'ALTO',
                'indicador': str (emoji + nombre),
                'enfermedades_riesgo': [str],
                'recomendaciones': [str]
            }
        """
        pass
