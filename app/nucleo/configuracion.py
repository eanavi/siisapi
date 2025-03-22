from pydantic_settings import BaseSettings

class Configuracion(BaseSettings):
    app_name: str = "API Siis1n"
    admin_email: str
    items_per_user:int= 50
    pool_tiempo_espera: int
    conexiones_maximas: int
    conexiones_minimas: int
    tiempo_expiracion:int


    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES:int



    class Config:
        env_file = ".env"
        enf_file_encoding = 'utf-8'

config = Configuracion()