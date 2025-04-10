from datetime import date
from typing import Optional
from sqlalchemy.engine.row import Row
from uuid import uuid5, UUID, NAMESPACE_DNS


def codificar_hcl_codigo(hcl_codigo: int) -> str:
    return f"00000000-0000-0000-0000-{hcl_codigo:012d}"


def decodificar_id_persona(uuid_str: str) -> Optional[int]:
    try:
        uuid_obj = UUID(uuid_str)
        hcl_str = uuid_str[-12:]
        return int(hcl_str)
    except:
        return None


def transformar_se_hc_persona(fila: Row, nombre_centro: str) -> dict:
    """
    Transforma una fila de SE_HC (Row) a un dict compatible con Persona.
    """
    return {
        "id_persona": codificar_hcl_codigo(fila['hcl_codigo']),
        "ci": fila["hcl_numci"],
        "tipo": "P",
        "paterno": fila["hcl_appat"],
        "materno": fila["hcl_apmat"],
        "nombres": fila["hcl_nombre"],
        "fecha_nacimiento": fila["hcl_fecnac"].date() if fila["hcl_fecnac"] else None,
        "sexo": fila["sexo"],
        "direccion": {
            "direccion_domicilio": fila["hcl_direcc"],
        } if fila["hcl_direcc"] else None,
        "telefono": {
            "domicilio": fila["hcl_teldom"]
        },
        "procedencia": nombre_centro,
    }
