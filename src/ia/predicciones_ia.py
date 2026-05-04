"""
Sistema unificado de predicciones inteligentes para el huerto.
Combina: Clima (Open-Meteo), Predicción de riegos, Alertas de enfermedades, Horarios de sol.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from .clima_service import ClimaService
from .enfermedades_modelo import modelo_enfermedades

class PrediccionesIA:
    """
    Orquesta predicciones de la IA para proporcionar:
    1. Calendario de riegos (predicción)
    2. Horarios óptimos de sol
    3. Alertas de enfermedad
    4. Recomendaciones de cultivo
    """
    
    def __init__(self, latitude: float = -12.0, longitude: float = -77.0):
        self.lat = latitude
        self.lon = longitude
        self.clima_service = ClimaService()
    
    def analisis_completo(self, 
                          humedad_suelo_actual: float,
                          temperatura_actual: float,
                          luminosidad_actual: float,
                          humedad_aire_actual: float) -> Dict:
        """
        Análisis completo: clima + riegos + enfermedades + sol.
        
        Retorna:
            Dict con análisis integrado y recomendaciones
        """
        # 1. Obtener datos de clima
        clima = self.clima_service.obtener_clima_actual(self.lat, self.lon)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos de clima"}
        
        # 2. Calcular necesidad de riego
        calendario_riegos = self._calcular_riegos(
            humedad_suelo_actual,
            clima["pronostico_7_dias"]
        )
        
        # 3. Predecir riesgo de enfermedades
        riesgo_enfermedad = modelo_enfermedades.predecir_riesgo_enfermedad(
            humedad_suelo=humedad_suelo_actual,
            humedad_aire=clima["actual"]["humedad"],
            temperatura=clima["actual"]["temperatura"],
            precipitacion_proxima=clima["pronostico_7_dias"][0]["precipitacion"]
        )
        
        # 4. Calcular horarios de luz solar óptima
        horarios_sol = self.clima_service.calcular_horas_luz(clima["horarios_sol"])
        
        # 5. Generar alertas climáticas
        alertas_clima = self.clima_service.alertas_clima(
            clima["actual"],
            clima["pronostico_7_dias"]
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "ubicacion": {"lat": self.lat, "lon": self.lon},
            
            "clima_actual": clima["actual"],
            "pronostico_7_dias": clima["pronostico_7_dias"],
            
            "calendario_riegos": calendario_riegos,
            "horarios_sol_optimo": horarios_sol,
            "riesgo_enfermedad": riesgo_enfermedad,
            "alertas_clima": alertas_clima,
            
            "recomendaciones_generales": self._generar_recomendaciones_generales(
                calendario_riegos,
                riesgo_enfermedad,
                horarios_sol
            ),
        }
    
    def _calcular_riegos(self, humedad_suelo_actual: float, pronostico: List[Dict]) -> List[Dict]:
        """
        Calcula calendario de riegos prediciendo:
        - Necesidad de riego basada en precipitación
        - Cantidad de riego recomendada
        - Horario óptimo (antes del pico de calor)
        """
        calendario = []
        humedad_predicha = humedad_suelo_actual
        
        for i, dia in enumerate(pronostico):
            # Precipitación reduce necesidad de riego
            lluvia = dia["precipitacion"]
            humedad_predicha = humedad_predicha - (lluvia * 2) + 5  # Evapotranspiración
            humedad_predicha = max(0, min(100, humedad_predicha))
            
            # Determinar si se necesita riego
            if humedad_predicha < 35:
                necesidad = "URGENTE"
                cantidad_recomendada = 40 - humedad_predicha  # Litros/m²
                horario = "06:00 AM (antes del calor)"
            elif humedad_predicha < 50:
                necesidad = "ALTA"
                cantidad_recomendada = 35 - humedad_predicha
                horario = "06:00 - 08:00 AM"
            elif humedad_predicha < 65:
                necesidad = "MEDIA"
                cantidad_recomendada = max(5, 30 - humedad_predicha)
                horario = "05:00 - 07:00 AM o 18:00 - 20:00 (tarde)"
            else:
                necesidad = "BAJA" if lluvia < 5 else "NO REQUERIDO"
                cantidad_recomendada = 0 if lluvia > 5 else 5
                horario = "Opcional"
            
            calendario.append({
                "fecha": dia["fecha"],
                "necesidad": necesidad,
                "cantidad_litros_m2": round(max(0, cantidad_recomendada), 1),
                "horario_recomendado": horario,
                "lluvia_esperada": dia["precipitacion"],
                "temp_max": dia["temp_max"],
                "humedad_predicha": round(humedad_predicha, 1),
                "notas": f"Condiciones: {dia['descripcion']}"
            })
        
        return calendario
    
    def _generar_recomendaciones_generales(self, 
                                           calendario: List[Dict],
                                           riesgo_enfermedad: Dict,
                                           horarios_sol: List[Dict]) -> List[str]:
        """Genera recomendaciones consolidadas."""
        recomendaciones = []
        
        # Por riego
        riegos_urgentes = [d for d in calendario if d["necesidad"] == "URGENTE"]
        if riegos_urgentes:
            recomendaciones.append(f"🌊 RIEGO URGENTE en {len(riegos_urgentes)} día(s): {riegos_urgentes[0]['fecha']}")
        
        # Por enfermedad
        if riesgo_enfermedad["nivel_riesgo"] != "BAJO":
            recomendaciones.append(f"🦠 {riesgo_enfermedad['indicador']} RIESGO DE ENFERMEDAD ({riesgo_enfermedad['nivel_riesgo']})")
            recomendaciones.extend(riesgo_enfermedad["recomendaciones"][:2])
        
        # Por luz
        horas_luz_promedio = sum([h["horas_luz"] for h in horarios_sol]) / len(horarios_sol)
        if horas_luz_promedio < 8:
            recomendaciones.append(f"☀️ Luz insuficiente ({horas_luz_promedio:.1f}h/día). Ajustar sombra.")
        
        if not recomendaciones:
            recomendaciones.append("✅ Condiciones óptimas. Mantener monitoreo regular.")
        
        return recomendaciones
    
    def prediccion_corto_plazo(self, dias: int = 1) -> Dict:
        """Predicción resumida para los próximos N días."""
        clima = self.clima_service.obtener_clima_actual(self.lat, self.lon)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos"}
        
        pronostico = clima["pronostico_7_dias"][:dias]
        
        return {
            "dias": dias,
            "pronostico": [{
                "fecha": p["fecha"],
                "clima": p["descripcion"],
                "temp": f"{p['temp_min']:.0f}°-{p['temp_max']:.0f}°C",
                "lluvia": f"{p['precipitacion']}mm",
                "uv": p["uv_index"],
            } for p in pronostico],
            "recomendacion": "Monitorear cambios de clima en tiempo real"
        }


# Funciones helper para integración en motor_ia.py
def obtener_prediccion_completa(humedad_suelo: float,
                                temperatura: float,
                                luz: float,
                                humedad_aire: float,
                                lat: float = -12.0,
                                lon: float = -77.0) -> Dict:
    """
    Función simplificada para obtener análisis completo.
    Uso: resultado = obtener_prediccion_completa(20, 28, 600, 65)
    """
    predicciones = PrediccionesIA(lat, lon)
    return predicciones.analisis_completo(humedad_suelo, temperatura, luz, humedad_aire)


if __name__ == "__main__":
    # Ejemplo de uso
    resultado = obtener_prediccion_completa(
        humedad_suelo=50,
        temperatura=25,
        luz=800,
        humedad_aire=70
    )
    print(f"Análisis completo:")
    print(f"Calendario de riegos: {resultado['calendario_riegos']}")
    print(f"Riesgo de enfermedad: {resultado['riesgo_enfermedad']}")
    print(f"Recomendaciones: {resultado['recomendaciones_generales']}")
