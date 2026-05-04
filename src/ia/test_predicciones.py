"""
Pruebas para validar todos los módulos del sistema de IA predictiva.
Ejecutar: python -m src.ia.test_predicciones
"""

import json
from datetime import datetime
from .clima_service import ClimaService
from .enfermedades_modelo import modelo_enfermedades
from .predicciones_ia import obtener_prediccion_completa, PrediccionesIA


def prueba_clima_service():
    """Prueba 1: Servicio de clima"""
    print("\n" + "="*60)
    print("PRUEBA 1: SERVICIO DE CLIMA (Open-Meteo)")
    print("="*60)
    
    servicio = ClimaService()
    clima = servicio.obtener_clima_actual(-12.0, -77.0)
    
    if clima["status"] != "ok":
        print(f"❌ Error: {clima.get('error', 'Desconocido')}")
        return False
    
    print(f"✅ Clima obtenido exitosamente")
    print(f"\n📍 Ubicación: Lima, Perú (-12.0, -77.0)")
    print(f"\n🌡️ CLIMA ACTUAL:")
    print(f"   Temperatura: {clima['actual']['temperatura']}°C")
    print(f"   Humedad: {clima['actual']['humedad']}%")
    print(f"   Descripción: {clima['actual']['descripcion']}")
    print(f"   Velocidad viento: {clima['actual']['velocidad_viento']} km/h")
    
    print(f"\n☀️ HORARIOS DE SOL:")
    for h in clima['horarios_sol'][:3]:
        print(f"   {h['fecha']}: Salida {h['salida']} - Puesta {h['puesta']}")
    
    print(f"\n📅 PRÓXIMOS 3 DÍAS:")
    for p in clima['pronostico_7_dias'][:3]:
        print(f"   {p['fecha']}: {p['descripcion']} ({p['temp_min']}° - {p['temp_max']}°C)")
    
    return True


def prueba_enfermedades():
    """Prueba 2: Modelo de enfermedades"""
    print("\n" + "="*60)
    print("PRUEBA 2: PREDICCIÓN DE ENFERMEDADES")
    print("="*60)
    
    # Test 1: Condiciones óptimas (bajo riesgo)
    print("\n📊 Escenario 1: Condiciones ÓPTIMAS")
    resultado1 = modelo_enfermedades.predecir_riesgo_enfermedad(
        humedad_suelo=50,
        humedad_aire=55,
        temperatura=26,
        precipitacion_proxima=2
    )
    print(f"   Riesgo: {resultado1['probabilidad_enfermedad']:.1f}%")
    print(f"   Nivel: {resultado1['nivel_riesgo']} {resultado1['indicador']}")
    
    # Test 2: Condiciones de alto riesgo
    print("\n📊 Escenario 2: Condiciones de ALTO RIESGO")
    resultado2 = modelo_enfermedades.predecir_riesgo_enfermedad(
        humedad_suelo=85,
        humedad_aire=92,
        temperatura=18,
        precipitacion_proxima=20
    )
    print(f"   Riesgo: {resultado2['probabilidad_enfermedad']:.1f}%")
    print(f"   Nivel: {resultado2['nivel_riesgo']} {resultado2['indicador']}")
    print(f"   Enfermedades detectadas:")
    for e in resultado2['enfermedades_riesgo']:
        print(f"      {e}")
    print(f"   Recomendaciones:")
    for r in resultado2['recomendaciones'][:2]:
        print(f"      {r}")
    
    # Test 3: Condiciones moderadas
    print("\n📊 Escenario 3: Condiciones MODERADAS")
    resultado3 = modelo_enfermedades.predecir_riesgo_enfermedad(
        humedad_suelo=65,
        humedad_aire=72,
        temperatura=22,
        precipitacion_proxima=8
    )
    print(f"   Riesgo: {resultado3['probabilidad_enfermedad']:.1f}%")
    print(f"   Nivel: {resultado3['nivel_riesgo']} {resultado3['indicador']}")
    
    return True


def prueba_calendario_riegos():
    """Prueba 3: Calendario de riegos"""
    print("\n" + "="*60)
    print("PRUEBA 3: CALENDARIO DE RIEGOS (7 DÍAS)")
    print("="*60)
    
    predicciones = PrediccionesIA(-12.0, -77.0)
    clima = predicciones.clima_service.obtener_clima_actual(-12.0, -77.0)
    
    if clima["status"] != "ok":
        print(f"❌ Error: {clima.get('error')}")
        return False
    
    calendario = predicciones._calcular_riegos(45, clima['pronostico_7_dias'])
    
    print(f"\n💧 Humedad inicial del suelo: 45%")
    print(f"\n{'Fecha':<12} {'Necesidad':<10} {'Cantidad':<12} {'Horario':<20} {'Lluvia':<8}")
    print("-" * 70)
    
    agua_total = 0
    for dia in calendario[:7]:
        agua_total += dia['cantidad_litros_m2']
        print(f"{dia['fecha']:<12} {dia['necesidad']:<10} {dia['cantidad_litros_m2']}L/m²{' ':<5} {dia['horario_recomendado']:<20} {dia['lluvia_esperada']}mm")
    
    print(f"\nTotal de agua estimado: {agua_total:.1f} L/m² en 7 días")
    
    return True


def prueba_horarios_sol():
    """Prueba 4: Horarios de luz solar"""
    print("\n" + "="*60)
    print("PRUEBA 4: HORARIOS DE SOL Y LUZ SOLAR")
    print("="*60)
    
    predicciones = PrediccionesIA(-12.0, -77.0)
    clima = predicciones.clima_service.obtener_clima_actual(-12.0, -77.0)
    
    if clima["status"] != "ok":
        print(f"❌ Error: {clima.get('error')}")
        return False
    
    horarios = predicciones.clima_service.calcular_horas_luz(clima['horarios_sol'])
    
    print(f"\n{'Fecha':<12} {'Salida':<8} {'Puesta':<8} {'Horas Luz':<12}")
    print("-" * 50)
    
    for h in horarios[:7]:
        print(f"{h['fecha']:<12} {h['salida']:<8} {h['puesta']:<8} {h['horas_luz']:.1f}h")
    
    promedio = sum([h['horas_luz'] for h in horarios[:7]]) / 7
    print(f"\nPromedio de horas de luz: {promedio:.1f} horas/día")
    
    if promedio >= 10:
        print("✅ Luz suficiente para la mayoría de cultivos")
    elif promedio >= 8:
        print("⚠️ Luz moderada, algunos cultivos pueden necesitar suplemento")
    else:
        print("❌ Luz insuficiente, considerar cultivos de sombra")
    
    return True


def prueba_prediccion_completa():
    """Prueba 5: Predicción integrada completa"""
    print("\n" + "="*60)
    print("PRUEBA 5: PREDICCIÓN COMPLETA INTEGRADA 🚀")
    print("="*60)
    
    resultado = obtener_prediccion_completa(
        humedad_suelo=55,
        temperatura=24,
        luz=750,
        humedad_aire=68,
        lat=-12.0,
        lon=-77.0
    )
    
    if "error" in resultado:
        print(f"❌ Error: {resultado['error']}")
        return False
    
    print(f"\n✅ Análisis completo generado exitosamente")
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   Timestamp: {resultado['timestamp']}")
    print(f"   Ubicación: ({resultado['ubicacion']['lat']}, {resultado['ubicacion']['lon']})")
    
    print(f"\n🌡️ CLIMA ACTUAL:")
    print(f"   Temperatura: {resultado['clima_actual']['temperatura']}°C")
    print(f"   Humedad: {resultado['clima_actual']['humedad']}%")
    print(f"   Condición: {resultado['clima_actual']['descripcion']}")
    
    print(f"\n💧 CALENDARIO DE RIEGOS (próximos 3 días):")
    for dia in resultado['calendario_riegos'][:3]:
        print(f"   {dia['fecha']}: {dia['necesidad']} ({dia['cantidad_litros_m2']}L/m²) - {dia['horario_recomendado']}")
    
    print(f"\n🦠 RIESGO DE ENFERMEDAD:")
    print(f"   {resultado['riesgo_enfermedad']['indicador']} Nivel: {resultado['riesgo_enfermedad']['nivel_riesgo']}")
    print(f"   Probabilidad: {resultado['riesgo_enfermedad']['probabilidad_enfermedad']:.1f}%")
    if resultado['riesgo_enfermedad']['enfermedades_riesgo']:
        print(f"   Enfermedades potenciales:")
        for e in resultado['riesgo_enfermedad']['enfermedades_riesgo'][:2]:
            print(f"      {e}")
    
    print(f"\n☀️ HORARIOS DE SOL (próximos 3 días):")
    for h in resultado['horarios_sol_optimo'][:3]:
        print(f"   {h['fecha']}: {h['horas_luz']:.1f}h de luz ({h['salida']} - {h['puesta']})")
    
    print(f"\n💡 RECOMENDACIONES GENERALES:")
    for rec in resultado['recomendaciones_generales']:
        print(f"   {rec}")
    
    return True


def ejecutar_todas_pruebas():
    """Ejecuta todas las pruebas de validación"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  PRUEBAS DE VALIDACIÓN - SISTEMA DE IA PREDICTIVA".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    pruebas = [
        ("Servicio de Clima", prueba_clima_service),
        ("Modelo de Enfermedades", prueba_enfermedades),
        ("Calendario de Riegos", prueba_calendario_riegos),
        ("Horarios de Sol", prueba_horarios_sol),
        ("Predicción Completa", prueba_prediccion_completa),
    ]
    
    resultados = []
    
    for nombre, prueba in pruebas:
        try:
            resultado = prueba()
            resultados.append((nombre, "✅ PASSOU" if resultado else "❌ FALHOU"))
        except Exception as e:
            print(f"\n❌ EXCEPCIÓN en {nombre}: {str(e)}")
            resultados.append((nombre, f"❌ EXCEPCIÓN: {str(e)[:30]}"))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    for nombre, resultado in resultados:
        print(f"{nombre:<30} {resultado}")
    
    exitosas = sum(1 for _, r in resultados if "✅" in r)
    total = len(resultados)
    
    print(f"\n📊 {exitosas}/{total} pruebas exitosas ({int(exitosas/total*100)}%)")
    
    if exitosas == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! Sistema listo para producción.")
    else:
        print(f"\n⚠️ {total - exitosas} prueba(s) con problemas. Revisar logs.")
    
    return exitosas == total


if __name__ == "__main__":
    ejecutar_todas_pruebas()
