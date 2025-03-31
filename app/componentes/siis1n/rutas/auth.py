from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.componentes.siis1n.servicios.usuario import ServicioUsuario
from app.nucleo.baseDatos import leer_bd
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), bd: Session = Depends(leer_bd)):
    """ Ruta de autenticacion de usuario """
    servicio_usuario = ServicioUsuario()
    token = servicio_usuario.autenticar(
        bd, form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}
