from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.nucleo.configuracion import config
from app.componentes.siis1n.modelos.base import ModeloBase

engine = create_engine(
    url=config.DB_URL,
    pool_size=config.conexiones_minimas,
    max_overflow=config.conexiones_maximas,
    pool_timeout=config.tiempo_expiracion,
    pool_recycle=config.pool_tiempo_espera,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_bd():
    try:
        ModeloBase.metadata.create_all(bind=engine)
        print(f"Base de datos inicializada correctamente.")
    except SQLAlchemyError as e:
        print(f"Error al inicializar la base de datos: {e}")


def leer_bd():
    bd = SessionLocal()
    try:
        yield bd
    except SQLAlchemyError as e:
        print(f"Error al obtener la sesion de la base de datos: {e}")
        bd.rollback()  # Revertir cualquier transaccion
        raise
    finally:
        bd.close()
