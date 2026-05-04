"""
Servicio de clima usando Open-Meteo (completamente gratis, sin API key).
Proporciona predicciones de clima, horarios de sol y alertas de clima.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ClimaService:
    """
    Consume Open-Meteo API (https://open-meteo.com)
    - ✅ Completamente gratis
    - ✅ Sin API key requerida
    - ✅ Sin limitación de llamadas
    - ✅ Datos precisos
    """
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    @staticmethod
    def obtener_clima_actual(latitude: float = -12.0, longitude: float = -77.0) -> Dict:
        """
        Obtiene clima actual y predicción de 7 días.
        Default: Lima, Perú (-12.0, -77.0)
        
        Parámetros:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
        
        Retorna:
            Dict con clima actual, predicción de 7 días, horarios de sol, etc.
        """
        try:
            # Forecast de 7 días con datos horarios y diarios
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,sunrise,sunset,uv_index_max",
                "timezone": "America/Lima",
                "forecast_days": 7
            }
            
            response = requests.get(f"{ClimaService.BASE_URL}/forecast", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "ok",
                    "actual": {
                        "temperatura": data["current"]["temperature_2m"],
                        "humedad": data["current"]["relative_humidity_2m"],
                        "codigo_clima": data["current"]["weather_code"],
                        "velocidad_viento": data["current"]["wind_speed_10m"],
                        "descripcion": ClimaService._describir_clima(data["current"]["weather_code"]),
                    },
                    "pronostico_7_dias": ClimaService._procesar_pronostico(data["daily"]),
                    "horarios_sol": ClimaService._extraer_horarios_sol(data["daily"]),
                    "lat": latitude,
                    "lon": longitude,
                }
            else:
                return {"status": "error", "mensaje": "No se pudo obtener el clima"}
                
        except requests.exceptions.Timeout:
            return {"status": "error", "mensaje": "Timeout al conectar con Open-Meteo"}
        except Exception as e:
            return {"status": "error", "mensaje": str(e)}
    
    @staticmethod
    def _describir_clima(codigo: int) -> str:
        """Convierte código WMO de clima a descripción."""
        descripciones = {
            0: "Cielo despejado",
            1: "Mayormente despejado",
            2: "Parcialmente nublado",
            3: "Nublado",
            45: "Niebla",
            48: "Niebla con escarcha",
            51: "Llovizna ligera",
            53: "Llovizna moderada",
            55: "Llovizna densa",
            61: "Lluvia ligera",
            63: "Lluvia moderada",
            65: "Lluvia pesada",
            71: "Nieve ligera",
            73: "Nieve moderada",
            75: "Nieve pesada",
            77: "Granos de nieve",
            80: "Chaparrones ligeros",
            81: "Chaparrones moderados",
            82: "Chaparrones violentos",
            85: "Chaparrón de nieve ligero",
            86: "Chaparrón de nieve denso",
            95: "Tormenta",
            96: "Tormenta con granizo",
            99: "Tormenta con granizo grande",
        }
        return descripciones.get(codigo, "Desconocido")
    
    @staticmethod
    def _procesar_pronostico(datos_diarios: Dict) -> List[Dict]:
        """Procesa pronóstico de 7 días."""
        pronostico = []
        for i in range(len(datos_diarios["time"])):
            pronostico.append({
                "fecha": datos_diarios["time"][i],
                "temp_max": datos_diarios["temperature_2m_max"][i],
                "temp_min": datos_diarios["temperature_2m_min"][i],
                "precipitacion": datos_diarios["precipitation_sum"][i],
                "codigo_clima": datos_diarios["weather_code"][i],
                "descripcion": ClimaService._describir_clima(datos_diarios["weather_code"][i]),
                "uv_index": datos_diarios["uv_index_max"][i],
            })
        return pronostico
    
    @staticmethod
    def _extraer_horarios_sol(datos_diarios: Dict) -> List[Dict]:
        """Extrae horarios de salida y puesta de sol."""
        horarios = []
        for i in range(len(datos_diarios["time"])):
            horarios.append({
                "fecha": datos_diarios["time"][i],
                "salida_sol": datos_diarios["sunrise"][i],
                "puesta_sol": datos_diarios["sunset"][i],
            })
        return horarios
    
    @staticmethod
    def calcular_horas_luz(horarios_sol: List[Dict]) -> List[Dict]:
        """Calcula horas de luz solar disponibles."""
        horas_luz = []
        for dia in horarios_sol:
            salida_raw = dia.get("salida_sol") or dia.get("salida")
            puesta_raw = dia.get("puesta_sol") or dia.get("puesta")
            fecha_str = dia.get("fecha")

            salida = None
            puesta = None

            # Intentar parseo ISO completo
            try:
                if isinstance(salida_raw, str):
                    salida = datetime.fromisoformat(salida_raw)
            except Exception:
                salida = None

            try:
                if isinstance(puesta_raw, str):
                    puesta = datetime.fromisoformat(puesta_raw)
            except Exception:
                puesta = None

            # Si no tenemos date-time completos, intentar combinar fecha + hora (formato HH:MM)
            if (salida is None or puesta is None) and fecha_str:
                try:
                    if salida is None and isinstance(salida_raw, str) and len(salida_raw) <= 8:
                        salida = datetime.fromisoformat(f"{fecha_str}T{salida_raw if ':' in salida_raw else salida_raw + ':00'}")
                except Exception:
                    salida = None

                try:
                    if puesta is None and isinstance(puesta_raw, str) and len(puesta_raw) <= 8:
                        puesta = datetime.fromisoformat(f"{fecha_str}T{puesta_raw if ':' in puesta_raw else puesta_raw + ':00'}")
                except Exception:
                    puesta = None

            # Si aún faltan valores, omitir este día
            if not salida or not puesta:
                continue

            horas = (puesta - salida).total_seconds() / 3600
            horas_luz.append({
                "fecha": fecha_str,
                "horas_luz": round(horas, 1),
                "salida": salida.strftime("%H:%M"),
                "puesta": puesta.strftime("%H:%M"),
            })
        return horas_luz
    
    @staticmethod
    def alertas_clima(clima_actual: Dict, pronostico: List[Dict]) -> List[str]:
        """Genera alertas basadas en condiciones climáticas."""
        alertas = []
        
        # Alerta por temperatura extrema
        if clima_actual["temperatura"] > 35:
            alertas.append("⚠️ ALERTA: Temperatura muy alta (>35°C). Aumentar riego y sombreo.")
        elif clima_actual["temperatura"] < 5:
            alertas.append("⚠️ ALERTA: Temperatura muy baja (<5°C). Riesgo de congelación.")
        
        # Alerta por lluvia próxima
        for dia in pronostico[:3]:
            if dia["precipitacion"] > 20:
                alertas.append(f"🌧️ Lluvia esperada el {dia['fecha']}: {dia['precipitacion']}mm. Reducir riego.")
        
        # Alerta por sequía
        lluvia_proximos_7_dias = sum([d["precipitacion"] for d in pronostico])
        if lluvia_proximos_7_dias < 5:
            alertas.append("🏜️ Sequía prevista en los próximos 7 días. Intensificar riego.")
        
        # Alerta por UV alto
        if clima_actual.get("uv_index", 0) > 8:
            alertas.append("☀️ Índice UV muy alto. Aumentar sombreo del cultivo.")
        
        if not alertas:
            alertas.append("✅ Condiciones climáticas normales.")
        
        return alertas


# Función de ejemplo para pruebas
if __name__ == "__main__":
    servicio = ClimaService()
    clima = servicio.obtener_clima_actual()
    print(f"Clima actual: {clima['actual']}")
    print(f"Alertas: {servicio.alertas_clima(clima['actual'], clima['pronostico_7_dias'])}")
