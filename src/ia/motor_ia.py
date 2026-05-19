import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from .predicciones_ia import obtener_prediccion_completa, PrediccionesIA
from fastapi import Depends
from src.domain.ports.ia_port import IAPort
from src.ia.adapters.openmeteo_ia_adapter import OpenMeteoIAAdapter
router = APIRouter(prefix="/api/ia", tags=["IA"])

class DatosHuerto(BaseModel):
    humedad_suelo: float
    temperatura: float
    luz: float
    humedad_aire: float
    latitude: float = -12.0  # Default: Lima, Perú
    longitude: float = -77.0

# ─── Inyección de dependencia para el adaptador IA ────────────────────────────

def get_ia_adapter() -> IAPort:
    """Provee la implementación del puerto IAPort.
    
    Actualmente usa OpenMeteoIAAdapter.
    Puede ser reemplazado por otro adaptador sin cambiar las rutas.
    """
    return OpenMeteoIAAdapter()

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


@router.post("/predecir")
def predecir(datos: DatosHuerto, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
    """Compatibilidad con el frontend antiguo que esperaba una predicción simple."""
    try:
        resultado = ia.predecir_completo(
            humedad_suelo=datos.humedad_suelo,
            temperatura=datos.temperatura,
            luz=datos.luz,
            humedad_aire=datos.humedad_aire,
            latitude=datos.latitude,
            longitude=datos.longitude,
        )

        calendario = resultado.get("calendario_riegos", [])
        primer_dia = calendario[0] if calendario else {}
        necesidad = primer_dia.get("necesidad", "MEDIA")

        ajuste_por_necesidad = {
            "URGENTE": -12,
            "ALTA": -8,
            "MEDIA": -4,
            "BAJA": 2,
        }

        humedad_predicha = max(
            0,
            min(
                100,
                round(
                    datos.humedad_suelo + ajuste_por_necesidad.get(necesidad, -2)
                ),
            ),
        )

        return {
            "humedad_futura_predicha": humedad_predicha,
            "mensaje": "Predicción generada por compatibilidad con el frontend.",
            **resultado,
        }
    except Exception as e:
        return {"error": f"Error en predicción: {str(e)}"}


# DEPRECATED: Endpoint /predecir removido
# - Reemplazado por /prediccion-completa (más completo)
# - El modelo_humedad.pkl ya no se usa
# - Usar obtenerPrediccionCompleta() en su lugar

@router.post("/prediccion-completa")
def prediccion_completa(datos: DatosHuerto, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
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
    return ia.predecir_completo(
        humedad_suelo=datos.humedad_suelo,
        temperatura=datos.temperatura,
        luz=datos.luz,
        humedad_aire=datos.humedad_aire,
        latitude=datos.latitude,
        longitude=datos.longitude
    )

@router.post("/calendario-riegos")
def calendario_riegos(datos: DatosHuerto, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
    """Obtiene calendario optimizado de riegos para 7 días."""
    try:
        clima = ia.obtener_clima_actual(datos.latitude, datos.longitude)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos de clima"}
        
        calendario = ia.calcular_riegos(datos.humedad_suelo, clima["pronostico_7_dias"])
        
        return {
            "calendario_riegos": calendario,
            "resumen": f"{len([c for c in calendario if c['necesidad'] in ['URGENTE', 'ALTA']])} días con riego necesario",
            "total_agua_estimado": round(sum([c["cantidad_litros_m2"] for c in calendario]), 1)
        }
    except Exception as e:
        return {"error": f"Error al calcular calendario: {str(e)}"}

@router.post("/riesgo-enfermedades")
def riesgo_enfermedades(datos: DatosHuerto, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
    """Predice riesgo de enfermedades basado en clima."""
    return ia.predecir_enfermedades(
        humedad_suelo=datos.humedad_suelo,
        humedad_aire=0.0,  # Se obtendrá del clima
        temperatura=datos.temperatura,
        precipitacion=0.0,  # Se obtendrá del pronóstico
        latitude=datos.latitude,
        longitude=datos.longitude
    )

@router.post("/horarios-sol")
def horarios_sol(datos: DatosHuerto, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
    """Obtiene horarios de salida/puesta de sol y horas de luz útil."""
    try:
        clima = ia.obtener_clima_actual(datos.latitude, datos.longitude)
        
        horarios = ia.calcular_horas_luz(clima.get("horarios_sol", []))
        
        if horarios and len(horarios) > 0:
            promedio = round(sum([h.get("horas_luz", 0) for h in horarios]) / len(horarios), 1)
            mejor = max(horarios, key=lambda x: x.get("horas_luz", 0))
            peor = min(horarios, key=lambda x: x.get("horas_luz", 0))
        else:
            promedio = 0
            mejor = None
            peor = None

        return {
            "horarios_proximos_7_dias": horarios,
            "promedio_horas_luz": promedio,
            "mejor_dia": mejor,
            "peor_dia": peor
        }
    except Exception as e:
        return {"error": f"Error al obtener horarios: {str(e)}"}

@router.get("/clima-actual")
def clima_actual(latitude: float = -12.0, longitude: float = -77.0, ia: IAPort = Depends(get_ia_adapter)) -> Dict:
    """Obtiene clima actual y alertas sin consumir datos del sensor."""
    try:
        clima = ia.obtener_clima_actual(latitude, longitude)
        
        if clima["status"] != "ok":
            return {"error": "No se pudo obtener datos de clima"}
        
        return {
            "clima_actual": clima["actual"],
            "alertas": ia.obtener_alertas_clima(
                clima["actual"],
                clima["pronostico_7_dias"]
            ),
            "proximos_3_dias": clima["pronostico_7_dias"][:3]
        }
    except Exception as e:
        return {"error": f"Error al obtener clima: {str(e)}"}
