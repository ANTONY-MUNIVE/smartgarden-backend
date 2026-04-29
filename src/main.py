from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes import router as api_router
from src.ia.motor_ia import router as ia_router

app = FastAPI(title="Smart Garden School API")

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar al frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas principales del backend
app.include_router(api_router, prefix="/api")

# Rutas de Inteligencia Artificial
app.include_router(ia_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Garden School API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)