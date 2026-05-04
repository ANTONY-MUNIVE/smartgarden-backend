"""
Modelo de predicción de enfermedades en plantas basado en:
- Humedad (condiciones para hongos)
- Temperatura (rangos óptimos para patógenos)
- Precipitación (factores de propagación)
- Historial de sensores

Usa Random Forest para predecir probabilidad de enfermedades.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from typing import Dict, List

class EnfermedadesModelo:
    """
    Predice la probabilidad de enfermedades en plantas.
    Entrenado con patrones de humedad, temperatura y precipitación.
    """
    
    # Definición de enfermedades comunes en cultivos
    ENFERMEDADES = {
        "oídio": {"humedad_min": 40, "humedad_max": 90, "temp_min": 15, "temp_max": 27, "lluvia": False},
        "roya": {"humedad_min": 60, "humedad_max": 95, "temp_min": 10, "temp_max": 24, "lluvia": True},
        "antracnosis": {"humedad_min": 85, "humedad_max": 100, "temp_min": 20, "temp_max": 28, "lluvia": True},
        "mildiu": {"humedad_min": 80, "humedad_max": 100, "temp_min": 10, "temp_max": 20, "lluvia": True},
        "fusarium": {"humedad_min": 70, "humedad_max": 90, "temp_min": 20, "temp_max": 30, "lluvia": False},
        "botrytis": {"humedad_min": 85, "humedad_max": 100, "temp_min": 15, "temp_max": 23, "lluvia": False},
    }
    
    def __init__(self):
        self.modelo = None
        self.entrenado = False
        self._entrenar_modelo()
    
    def _entrenar_modelo(self):
        """Entrena un modelo Random Forest para predicción de enfermedades."""
        # Datos sintéticos de entrenamiento
        X_entrenamiento = []
        y_entrenamiento = []
        
        # Generar datos de escenarios de alto riesgo
        for _ in range(20):
            # Escenarios de alto riesgo (enfermedad = 1)
            X_entrenamiento.append([85, 18, 15, 75])  # Humedad alta, temp baja, lluvia
            y_entrenamiento.append(1)
        
        # Generar datos de escenarios de bajo riesgo
        for _ in range(20):
            # Escenarios de bajo riesgo (enfermedad = 0)
            X_entrenamiento.append([40, 25, 5, 30])  # Humedad baja, temp alta, sin lluvia
            y_entrenamiento.append(0)
        
        # Escenarios intermedios
        for _ in range(20):
            X_entrenamiento.append([60, 22, 10, 50])  # Condiciones intermedias
            y_entrenamiento.append(0)
        
        X = np.array(X_entrenamiento)
        y = np.array(y_entrenamiento)
        
        self.modelo = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        self.modelo.fit(X, y)
        self.entrenado = True
    
    def predecir_riesgo_enfermedad(self, 
                                   humedad_suelo: float,
                                   humedad_aire: float,
                                   temperatura: float,
                                   precipitacion_proxima: float) -> Dict:
        """
        Predice el riesgo de enfermedad basado en condiciones.
        
        Parámetros:
            humedad_suelo: Humedad del suelo (0-100)
            humedad_aire: Humedad del aire (0-100)
            temperatura: Temperatura en °C
            precipitacion_proxima: Precipitación esperada (mm)
        
        Retorna:
            Dict con predicción de riesgo y recomendaciones
        """
        if not self.entrenado:
            return {"error": "Modelo no entrenado"}
        
        # Preparar características
        X = np.array([[humedad_aire, temperatura, precipitacion_proxima, humedad_suelo]])
        
        # Predicción
        probabilidad_enfermedad = self.modelo.predict_proba(X)[0][1]
        
        # Evaluar riesgo por enfermedad específica
        riesgos = self._evaluar_enfermedades_especificas(
            humedad_aire, temperatura, precipitacion_proxima
        )
        
        # Determinar nivel de riesgo
        if probabilidad_enfermedad > 0.7:
            nivel = "CRÍTICO"
            color = "🔴"
        elif probabilidad_enfermedad > 0.5:
            nivel = "ALTO"
            color = "🟠"
        elif probabilidad_enfermedad > 0.3:
            nivel = "MEDIO"
            color = "🟡"
        else:
            nivel = "BAJO"
            color = "🟢"
        
        return {
            "probabilidad_enfermedad": round(probabilidad_enfermedad * 100, 2),
            "nivel_riesgo": nivel,
            "indicador": color,
            "enfermedades_riesgo": riesgos,
            "recomendaciones": self._generar_recomendaciones(riesgos, nivel),
        }
    
    def _evaluar_enfermedades_especificas(self, 
                                          humedad_aire: float,
                                          temperatura: float,
                                          precipitacion: float) -> List[str]:
        """Evalúa qué enfermedades específicas están en riesgo."""
        enfermedades_en_riesgo = []
        lluvia_proxima = precipitacion > 5
        
        for enfermedad, condiciones in self.ENFERMEDADES.items():
            en_rango_humedad = (condiciones["humedad_min"] <= humedad_aire <= condiciones["humedad_max"])
            en_rango_temp = (condiciones["temp_min"] <= temperatura <= condiciones["temp_max"])
            lluvia_coincide = (lluvia_proxima == condiciones["lluvia"]) or not condiciones["lluvia"]
            
            if en_rango_humedad and en_rango_temp and lluvia_coincide:
                enfermedades_en_riesgo.append(f"• {enfermedad.capitalize()} (Riesgo: Alto)")
        
        if not enfermedades_en_riesgo:
            enfermedades_en_riesgo.append("Condiciones favorables para el cultivo")
        
        return enfermedades_en_riesgo
    
    def _generar_recomendaciones(self, enfermedades: List[str], nivel: str) -> List[str]:
        """Genera recomendaciones basadas en enfermedades detectadas."""
        recomendaciones = []
        
        if nivel == "CRÍTICO":
            recomendaciones.append("🚨 APLICAR FUNGICIDA PREVENTIVO INMEDIATAMENTE")
            recomendaciones.append("⛔ Aislar plantas afectadas")
            recomendaciones.append("💨 Mejorar ventilación y reducir humedad")
        elif nivel == "ALTO":
            recomendaciones.append("⚠️ Monitorear diariamente")
            recomendaciones.append("🌬️ Aumentar ventilación")
            recomendaciones.append("💧 Reducir riego foliar")
        elif nivel == "MEDIO":
            recomendaciones.append("📋 Vigilancia semanal")
            recomendaciones.append("🧹 Remover hojas caídas")
        else:
            recomendaciones.append("✅ Continuar cuidado normal")
        
        return recomendaciones


# Inicializar modelo global
modelo_enfermedades = EnfermedadesModelo()


if __name__ == "__main__":
    modelo = EnfermedadesModelo()
    resultado = modelo.predecir_riesgo_enfermedad(
        humedad_suelo=65,
        humedad_aire=85,
        temperatura=18,
        precipitacion_proxima=15
    )
    print(f"Riesgo de enfermedad: {resultado}")
