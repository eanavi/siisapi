import pytest
from httpx import AsyncClient
from uuid import uuid4
from app.componentes.siis1n.modelos.persona import Persona
from app.componentes.siis1n.esquemas.persona import PersonaCreate
from datetime import date


@pytest.mark.asyncio
async def test_listar_personas(client, db_session, auth_headers):
    # Arrange: Crear una persona en la base de datos
    persona = Persona(
        id_persona=uuid4(),
        tipo="E",
        ci=str(uuid4())[:8],
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()

    # Act: Hacer la solicitud GET
    response = client.get(
        "/personas/?pagina=1&tamanio=10", headers=auth_headers)

    print("Persss")
    print(response.json())  # Debugging line to check the response
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["pagina"] == 1
    assert data["tamanio"] == 10
    assert len(data["items"]) >= 1


"""
@pytest.mark.asyncio
async def test_buscar_personas(client, db_session, auth_headers):
    # Arrange
    persona = Persona(
        id_persona=uuid4(),
        tipo="E",
        ci="1234567",
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()

    # Act
    response = client.get("/personas/buscar/Juan?pagina=1&tamanio=10", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["nombres"] == "Juan" for item in data["items"])
"""


@pytest.mark.asyncio
async def test_obtener_persona(client, db_session, auth_headers):
    # Arrange
    id_persona = uuid4()
    persona = Persona(
        id_persona=id_persona,
        tipo="E",
        ci=str(uuid4())[:8],
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()

    # Act
    response = client.get(f"/personas/{id_persona}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id_persona"] == str(id_persona)
    assert data["nombres"] == "Juan"


@pytest.mark.asyncio
async def test_obtener_persona_no_encontrada(client, auth_headers):
    # Act
    response = client.get(f"/personas/{uuid4()}", headers=auth_headers)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Objeto no encontrado"


@pytest.mark.asyncio
async def test_crear_persona(client, db_session, auth_headers, persona_data):
    # Act
    response = client.post(
        "/personas/", json=persona_data, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["nombres"] == "Juan"


@pytest.mark.asyncio
async def test_actualizar_persona(client, db_session, auth_headers, persona_data):
    # Arrange
    id_persona = uuid4()
    persona = Persona(
        id_persona=id_persona,
        tipo="E",
        ci=str(uuid4())[:8],
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()
    updated_data = persona_data.copy()
    updated_data["nombres"] = "Pedro"

    import ipdb
    ipdb.set_trace()

    # Act
    response = client.put(f"/personas/{id_persona}",
                          json=updated_data, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["nombres"] == "Pedro"


@pytest.mark.asyncio
async def test_eliminar_persona(client, db_session, auth_headers):
    # Arrange
    id_persona = uuid4()
    persona = Persona(
        id_persona=id_persona,
        tipo="E",
        ci=str(uuid4())[:8],
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()

    # Act
    response = client.delete(f"/personas/{id_persona}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json() is True

    # Verificar que el estado cambió a 'A'
    db_persona = db_session.query(Persona).filter(
        Persona.id_persona == id_persona).first()
    assert db_persona.estado_reg == "A"


@pytest.mark.asyncio
async def test_eliminar_persona_fisico(client, db_session, auth_headers):
    # Arrange
    id_persona = uuid4()
    persona = Persona(
        id_persona=id_persona,
        tipo="E",
        ci=str(uuid4())[:8],
        paterno="Gomez",
        materno="Perez",
        nombres="Juan",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        estado_reg="V"
    )
    db_session.add(persona)
    db_session.commit()

    # Act
    response = client.delete(
        f"/personas/fisico/{id_persona}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json() is True

    # Verificar que la persona fue eliminada físicamente
    db_persona = db_session.query(Persona).filter(
        Persona.id_persona == id_persona).first()
    assert db_persona is None


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    # Act: Intentar acceder sin token
    response = client.get("/personas/")

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Autenticacion requerida"
