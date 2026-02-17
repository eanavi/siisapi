from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.nucleo.configuracion import config
from urllib.parse import quote_plus
from typing import Generator, Dict

instancia_mssql: Dict[str, Engine] = {}


def crear_motor_mssql(servidor: str, base_datos: str, usuario: str, clave: str, puerto: int) -> Engine:
    llave = f"{servidor}_{base_datos}_{puerto}"
    if llave in instancia_mssql:
        return instancia_mssql[llave]

    cadena_conexion = (f"mssql+pyodbc://{usuario}:{quote_plus(clave)}@{servidor},{puerto}/{base_datos}"
                       f"?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes")

    motor = create_engine(
        cadena_conexion,
        poolclass=QueuePool,
        pool_size=50,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False,
        connect_args={"timeout": 10}
    )

    instancia_mssql[llave] = motor
    return motor


def obtener_sesion_mssql(servidor: str, base_datos: str, 
                         usuario: str, clave: str, puerto: int) -> Generator[Session, None, None]:
    motor = crear_motor_mssql(servidor, base_datos, usuario, clave, puerto)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
