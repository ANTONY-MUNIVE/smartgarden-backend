# SmartGarden Backend

FastAPI backend para el sistema de jardín inteligente educativo con integración de base de datos PostgreSQL/Supabase.

## 📋 Requisitos

- Python 3.8+
- PostgreSQL (o Supabase)
- pip

## 🚀 Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/smartgarden-backend.git
cd smartgarden-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Edita .env y configura:
# - DATABASE_URL: conexión a Supabase/PostgreSQL
# - DATABASE_URL_POOLER: pooler alternativo (opcional)
```

5. **Ejecutar servidor de desarrollo**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`
Documentación Swagger: `http://localhost:8000/docs`

## 📦 Estructura del Proyecto

```
src/
├── main.py                 # Punto de entrada
├── application/
│   └── use_cases/          # Lógica de negocio
├── domain/
│   ├── entities/           # Modelos de dominio
│   └── ports/              # Interfaces
├── infrastructure/
│   ├── database.py         # Configuración BD
│   ├── adapters/           # Repositorios
│   └── api/
│       └── routes.py       # Endpoints
└── ia/
    └── motor_ia.py         # Módulo de IA
```

## 🗄️ Base de Datos

Usa Supabase PostgreSQL con SSL y soporte de pooler. Ejecuta migraciones:

```bash
# Ver migraciones disponibles
alembic current

# Aplicar migraciones
alembic upgrade head
```

## 🌐 Desplegar en Producción

### Opción 1: Railway
```bash
railway login
railway link
railway deploy
```

### Opción 2: Render
1. Conecta repositorio a Render
2. El archivo `render.yaml` ya deja listo el servicio web
3. Agrega variables de entorno en Render
4. Verifica el despliegue en `https://TU-APP.onrender.com/health`

La respuesta esperada debe ser similar a:
```json
{
    "status": "ok",
    "service": "Smart Garden School API",
    "environment": "production"
}
```

### Opción 3: Heroku
```bash
heroku create smartgarden-backend
heroku config:set DATABASE_URL=your_database_url
git push heroku main
```

## 📝 API Endpoints

- `POST /auth/login` - Login de usuarios
- `GET /experimentos` - Listar experimentos
- `POST /experimentos` - Crear experimento
- `GET /sensores` - Estado de sensores
- `GET /recomendaciones` - Recomendaciones de IA

Ver documentación completa en `/docs`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte de SmartGardenSchool - Educativo

## 📧 Contacto

Equipo de desarrollo: dev@smartgarden.local
