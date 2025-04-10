import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.principal import app
from app.nucleo.baseDatos import leer_bd
from app.componentes.siis1n.modelos.persona import Persona
from app.componentes.siis1n.modelos.base import ModeloBase
from uuid import uuid4
import jwt  # Usamos PyJWT
from app.nucleo.seguridad import SECRET_KEY, ALGORITHM

# Configuración de la base de datos en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# Sobrescribimos la dependencia de la base de datos


def override_leer_bd():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[leer_bd] = override_leer_bd


@pytest.fixture(scope="module")
def client():
    print("Creando tablas...")
    ModeloBase.metadata.create_all(bind=engine)
    print("Tablas creadas:", ModeloBase.metadata.tables.keys())
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session():
    """Fixture para la sesión de base de datos"""
    db = TestingSessionLocal()
    yield db
    db.query(Persona).delete()
    db.commit()
    db.close()
    # Eliminar las tablas después de cada prueba
    # ModeloBase.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers():
    """Fixture para generar headers con token JWT válido usando PyJWT"""
    payload = {"sub": "test_user", "rol": "Administrador"}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def persona_data():
    """Datos de ejemplo para una persona"""
    return {
        "tipo": "E",
        "ci": str(uuid4())[:8],
        "paterno": "Gomez",
        "materno": "Perez",
        "nombres": "Juan",
        "fecha_nacimiento": "1990-01-01",
        "sexo": "M",
        "direccion": [{"tipo": "personal", "direccion": {"zona": "Centro", "calle": "Av. Principal", "numero": "123", "ciudad": "La Paz"}}],
        "telefono": {"tipo": "personal", "numero": "7777777"},
        "correo": {"tipo": "personal", "correo": "juan@example.com"}
    }
