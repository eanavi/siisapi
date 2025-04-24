from cachetools import TTLCache
from typing import Dict

conexion_cache: TTLCache[str, Dict] = TTLCache(
    maxsize=1000, ttl=3600)  # 1 hora de TTL
# Cache para almacenar conexiones a bases de datos


def guardar_datos_conexion(token: str, datos: Dict):
    conexion_cache[token] = datos


def obtener_datos_conexion(token: str) -> Dict:
    return conexion_cache.get(token, None)
