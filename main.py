from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel

# ==========================================
# 1. CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
# Cambia 'usuario', 'contraseña', 'localhost' y 'nombre_bd' por tus datos reales
DATABASE_URL = "postgresql://postgres:KWezgubTgHeUDiygNdkSKOinVJkvaWqb@crossover.proxy.rlwy.net:46796/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. MODELO DE SQLALCHEMY (Base de datos)
# ==========================================
class ProductoDB(Base):
    __tablename__ = "productos"

    # Solo mapeamos las columnas que necesitamos para el cotizador
    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_interno = Column(String, unique=True, index=True)
    nombre = Column(String)
    precio_venta = Column(Float) # Si usas Numeric/Decimal en Postgres, Float funciona bien aquí

# ==========================================
# 3. ESQUEMA DE PYDANTIC (Respuesta JSON)
# ==========================================
class ProductoResponse(BaseModel):
    id_producto: int
    codigo_interno: str | None = None
    nombre: str
    precio_venta: float

    # Esto permite que Pydantic lea directamente del modelo de SQLAlchemy
    model_config = {"from_attributes": True}

# ==========================================
# 4. APLICACIÓN FASTAPI Y CORS
# ==========================================
app = FastAPI(title="API Cotizador Herrajes")

# Configuración de CORS para permitir peticiones desde tu React (Vite usa el puerto 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://cotizador-frontend-blush.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de la BD en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. ENDPOINTS
# ==========================================
@app.get("/api/productos", response_model=list[ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    # Hace un SELECT * FROM productos;
    productos = db.query(ProductoDB).all()
    return productos