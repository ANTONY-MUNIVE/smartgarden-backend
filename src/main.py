import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.api.routes import router as api_router
from src.ia.motor_ia import router as ia_router

app = FastAPI(title="Smart Garden School API")

frontend_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,https://smartgarden-frontend.vercel.app",
)
allowed_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
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


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Smart Garden School API",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)