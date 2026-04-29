import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

# Datos simulados para entrenamiento inicial
data = {
    "humedad_suelo": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
    "temperatura": [35, 33, 32, 30, 28, 27, 26, 25, 24, 23, 22],
    "luz": [900, 850, 800, 750, 700, 650, 600, 550, 500, 450, 400],
    "humedad_aire": [40, 45, 50, 55, 60, 62, 65, 68, 70, 72, 75],
    "humedad_futura": [18, 23, 28, 33, 38, 43, 48, 53, 58, 63, 68]
}

df = pd.DataFrame(data)

X = df[["humedad_suelo", "temperatura", "luz", "humedad_aire"]]
y = df["humedad_futura"]

modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X, y)

predicciones = modelo.predict(X)

mae = mean_absolute_error(y, predicciones)
rmse = np.sqrt(mean_squared_error(y, predicciones))

print("Modelo entrenado correctamente")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

joblib.dump(modelo, "src/ia/modelo_humedad.pkl")
print("Modelo guardado en src/ia/modelo_humedad.pkl")