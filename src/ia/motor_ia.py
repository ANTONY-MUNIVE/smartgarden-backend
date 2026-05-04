import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from .predicciones_ia import obtener_prediccion_completa, PrediccionesIA

router = APIRouter(prefix="/api/ia", tags=["IA"])

class DatosHuerto(BaseModel):
    humedad_suelo: float
    temperatura: float
    luz: float
    humedad_aire: float
    latitude: float = -12.0  # Default: Lima, Perú
    longitude: float = -77.0

def generar_recomendacion(datos: DatosHuerto):
    recomendaciones = []
    prioridad = "baja"

    if datos.humedad_suelo < 25:
        recomendaciones.append("Riego urgente: la humedad del suelo está por debajo del 25%.")
        prioridad = "alta"

    if datos.temperatura > 32:
        recomendaciones.append("Temperatura elevada: revisar sombra o ventilación del cultivo.")
        prioridad = "alta"

    if datos.luz < 200:
        recomendaciones.append("Luminosidad baja: el cultivo necesita más exposición a la luz.")
        if prioridad != "alta":
            prioridad = "media"

    if not recomendaciones:
        recomendaciones.append("El huerto se encuentra en condiciones normales.")

    return recomendaciones, prioridad

@router.post("/recomendar")
def recomendar(datos: DatosHuerto):
    """Recomendación básica (compatibilidad)."""
    recomendaciones, prioridad = generar_recomendacion(datos)

    return {
        "estado": "analizado",
        "prioridad": prioridad,
        "recomendaciones": recomendaciones
    }


# DEPRECATED: Endpoint /predecir removido
# - Reemplazado por /prediccion-completa (más completo)
# - El modelo_humedad.pkl ya no se usa
# - Usar obtenerPrediccionCompleta() en su lugar

@router.post("/prediccion-completa")
def prediccion_completa(datos: DatosHuerto) -> Dict:
    """
    🚀 NUEVA CARACTERÍSTICA: Análisis predictivo completo
    
    Incluye:
    - 📅 Calendario de riegos (7 días)
    - ☀️ Horarios de luz solar óptima
    - 🦠 Predicción de enfermedades (% riesgo)
    - 🌡️ Pronóstico climático
    - 💡 Recomendaciones personalizadas
    
    Usa API de clima gratuita (Open-Meteo, sin API key)
    """
    try:
        resultado = obtener_prediccion_completa(
            humedad_suelo=datos.humedad_suelo,
            temperatura=datos.temperatura,
            luz=datos.luz,
            humedad_aire=datos.humedad_aire,
            lat=datos.latitude,
            lon=datos.longitude
        )
        return resultado
    except Exception as e:
        return {
            "error": f"Error en análisis predictivo: {str(e)}",
            "recomendacion": "Verifica conexión a internet y que la ubicación sea válida"
        }

@router.post("/calendario-riegos")
def calendario_riegos(datos: DatosHuerto) -> Dict:
    """Obtiene calendario optimizado de riegos para 7 días."""
    try:
        predicciones = PrediccionesIA(datos.latitude, datos.longitude)
        clima = predicciones.clima_service.obtener_clima_actual(datos.latitude, datos.longitude)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos de clima"}
        
        calendario = predicciones._calcular_riegos(datos.humedad_suelo, clima["pronostico_7_dias"])
        
        return {
            "calendario_riegos": calendario,
            "resumen": f"{len([c for c in calendario if c['necesidad'] in ['URGENTE', 'ALTA']])} días con riego necesario",
            "total_agua_estimado": round(sum([c["cantidad_litros_m2"] for c in calendario]), 1)
        }
    except Exception as e:
        return {"error": f"Error al calcular calendario: {str(e)}"}

@router.post("/riesgo-enfermedades")
def riesgo_enfermedades(datos: DatosHuerto) -> Dict:
    """Predice riesgo de enfermedades basado en clima."""
    try:
        from .enfermedades_modelo import modelo_enfermedades
        
        predicciones = PrediccionesIA(datos.latitude, datos.longitude)
        clima = predicciones.clima_service.obtener_clima_actual(datos.latitude, datos.longitude)
        
        riesgo = modelo_enfermedades.predecir_riesgo_enfermedad(
            humedad_suelo=datos.humedad_suelo,
            humedad_aire=clima["actual"]["humedad"],
            temperatura=clima["actual"]["temperatura"],
            precipitacion_proxima=clima["pronostico_7_dias"][0]["precipitacion"]
        )
        
        return {
            **riesgo,
            "clima_actual": clima["actual"],
            "pronostico_proxima_lluvia": clima["pronostico_7_dias"][0]
        }
    except Exception as e:
        return {"error": f"Error en análisis de enfermedad: {str(e)}"}

@router.post("/horarios-sol")
def horarios_sol(datos: DatosHuerto) -> Dict:
    """Obtiene horarios de salida/puesta de sol y horas de luz útil."""
    try:
        predicciones = PrediccionesIA(datos.latitude, datos.longitude)
        clima = predicciones.clima_service.obtener_clima_actual(datos.latitude, datos.longitude)
        
        horarios = predicciones.clima_service.calcular_horas_luz(clima["horarios_sol"])
        
        return {
            "horarios_proximos_7_dias": horarios,
            "promedio_horas_luz": round(sum([h["horas_luz"] for h in horarios]) / len(horarios), 1),
            "mejor_dia": max(horarios, key=lambda x: x["horas_luz"]),
            "peor_dia": min(horarios, key=lambda x: x["horas_luz"])
        }
    except Exception as e:
        return {"error": f"Error al obtener horarios: {str(e)}"}

@router.get("/clima-actual")
def clima_actual(latitude: float = -12.0, longitude: float = -77.0) -> Dict:
    """Obtiene clima actual y alertas sin consumir datos del sensor."""
    try:
        predicciones = PrediccionesIA(latitude, longitude)
        clima = predicciones.clima_service.obtener_clima_actual(latitude, longitude)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos de clima"}
        
        return {
            "clima_actual": clima["actual"],
            "alertas": predicciones.clima_service.alertas_clima(
                clima["actual"],
                clima["pronostico_7_dias"]
            ),
            "proximos_3_dias": clima["pronostico_7_dias"][:3]
        }
    except Exception as e:
        return {"error": f"Error al obtener clima: {str(e)}"}
