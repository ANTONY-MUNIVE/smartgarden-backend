"""
Adaptador OpenMeteo que implementa el puerto IAPort.

Usa ClimaService (Open-Meteo) + PrediccionesIA internamente.
Expone métodos públicos para que motor_ia.py no acceda
directamente a PrediccionesIA.

NOTA: PrediccionesIA NO se modifica (backward compatibility con tests).
Este adaptador wrappea sus métodos y los expone públicamente.
"""

from typing import Dict, List
from src.domain.ports.ia_port import IAPort
from src.ia.predicciones_ia import obtener_prediccion_completa, PrediccionesIA
from src.ia.enfermedades_modelo import modelo_enfermedades


class OpenMeteoIAAdapter(IAPort):
    """
    Adaptador que implementa IAPort usando:
    - ClimaService (Open-Meteo para datos climáticos)
    - PrediccionesIA (orquestación de predicciones)
    - Modelo de enfermedades (predicción de riesgos)
    
    Puede ser reemplazado por otro adaptador (ej: modelo ML más avanzado)
    sin afectar el resto del backend.
    """
    
    def __init__(self):
        """Inicializa el adaptador."""
        pass
    
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
        Análisis predictivo completo usando obtener_prediccion_completa.
        """
        try:
            resultado = obtener_prediccion_completa(
                humedad_suelo=humedad_suelo,
                temperatura=temperatura,
                luz=luz,
                humedad_aire=humedad_aire,
                lat=latitude,
                lon=longitude
            )
            return resultado
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error en análisis predictivo: {str(e)}",
                "recomendacion": "Verifica conexión a internet y que la ubicación sea válida"
            }
    
    def calcular_riegos(
        self,
        humedad_suelo: float,
        pronostico_7_dias: List[Dict]
    ) -> List[Dict]:
        """
        Calcula calendario optimizado de riegos.
        Wrappea PrediccionesIA._calcular_riegos() (método privado).
        """
        try:
            predicciones = PrediccionesIA()
            calendario = predicciones._calcular_riegos(humedad_suelo, pronostico_7_dias)
            return calendario
        except Exception as e:
            return [{"error": f"Error al calcular calendario: {str(e)}"}]
    
    def generar_recomendaciones(
        self,
        calendario: List[Dict],
        riesgo_enfermedad: Dict,
        horarios_sol: List[Dict]
    ) -> List[str]:
        """
        Genera recomendaciones consolidadas.
        Wrappea PrediccionesIA._generar_recomendaciones_generales().
        """
        try:
            predicciones = PrediccionesIA()
            recomendaciones = predicciones._generar_recomendaciones_generales(
                calendario, riesgo_enfermedad, horarios_sol
            )
            return recomendaciones
        except Exception as e:
            return [f"⚠️ Error generando recomendaciones: {str(e)}"]
    
    def obtener_clima_actual(
        self,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Obtiene clima actual y pronóstico.
        Accede a PrediccionesIA.clima_service (atributo).
        """
        try:
            predicciones = PrediccionesIA(latitude, longitude)
            clima = predicciones.clima_service.obtener_clima_actual(latitude, longitude)
            return clima
        except Exception as e:
            return {
                "status": "error",
                "error": f"No se pudo obtener datos de clima: {str(e)}"
            }
    
    def calcular_horas_luz(
        self,
        horarios_sol: List[Dict]
    ) -> List[Dict]:
        """
        Calcula horas de luz a partir de horarios.
        Accede a PrediccionesIA.clima_service.calcular_horas_luz().
        """
        try:
            predicciones = PrediccionesIA()
            horarios = predicciones.clima_service.calcular_horas_luz(horarios_sol)
            return horarios if horarios else []
        except Exception as e:
            return []
    
    def obtener_alertas_clima(
        self,
        clima_actual: Dict,
        pronostico_7_dias: List[Dict]
    ) -> List[str]:
        """
        Genera alertas climáticas.
        Accede a PrediccionesIA.clima_service.alertas_clima().
        """
        try:
            predicciones = PrediccionesIA()
            alertas = predicciones.clima_service.alertas_clima(clima_actual, pronostico_7_dias)
            return alertas
        except Exception as e:
            return []
    
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
        Predice riesgo de enfermedades usando modelo_enfermedades.
        """
        try:
            predicciones = PrediccionesIA(latitude, longitude)
            clima = predicciones.clima_service.obtener_clima_actual(latitude, longitude)
            
            riesgo = modelo_enfermedades.predecir_riesgo_enfermedad(
                humedad_suelo=humedad_suelo,
                humedad_aire=humedad_aire,
                temperatura=temperatura,
                precipitacion_proxima=precipitacion
            )
            
            return {
                **riesgo,
                "clima_actual": clima.get("actual", {}),
                "pronostico_proxima_lluvia": clima.get("pronostico_7_dias", [{}])[0]
            }
        except Exception as e:
            return {
                "probabilidad_enfermedad": 0.0,
                "nivel_riesgo": "ERROR",
                "indicador": "❌ Error",
                "enfermedades_riesgo": [],
                "recomendaciones": [f"Error: {str(e)}"]
            }
