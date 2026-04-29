import os
import joblib
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/ia", tags=["IA"])

class DatosHuerto(BaseModel):
    humedad_suelo: float
    temperatura: float
    luz: float
    humedad_aire: float

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
    recomendaciones, prioridad = generar_recomendacion(datos)

    return {
        "estado": "analizado",
        "prioridad": prioridad,
        "recomendaciones": recomendaciones
    }

@router.post("/predecir")
def predecir(datos: DatosHuerto):
    ruta_modelo = "src/ia/modelo_humedad.pkl"

    if not os.path.exists(ruta_modelo):
        return {
            "error": "Modelo no entrenado. Ejecuta primero: python -m src.ia.entrenar_modelo"
        }

    modelo = joblib.load(ruta_modelo)

    entrada = [[
        datos.humedad_suelo,
        datos.temperatura,
        datos.luz,
        datos.humedad_aire
    ]]

    humedad_futura = modelo.predict(entrada)[0]

    return {
        "humedad_futura_predicha": round(float(humedad_futura), 2),
        "mensaje": "Predicción generada correctamente"
    }