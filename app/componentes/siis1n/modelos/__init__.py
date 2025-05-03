from sqlalchemy.orm import relationship
from .persona import Persona
from .empleado import Empleado
from .centro import Centro
from .rol import Rol
from .usuario import Usuario
from .prestacion import Prestacion
from .grupo import Grupo
from .lista import Lista
from .paciente import Paciente
from .menu import Menu


# Definir las relaciones entre los modelos de forma dinamica

Centro.prestaciones = relationship("Prestacion", back_populates="centro")
Prestacion.centro = relationship("Centro", back_populates="prestaciones")


Centro.empleados = relationship("Empleado", back_populates="centro")
Empleado.centro = relationship("Centro", back_populates="empleados")


Empleado.persona = relationship("Persona", back_populates="empleados")
Persona.empleados = relationship("Empleado", back_populates="persona")

Empleado.usuario = relationship("Usuario", back_populates="empleado")
Usuario.empleado = relationship("Empleado", back_populates="usuario")

Paciente.persona = relationship("Persona", back_populates="paciente")
Persona.paciente = relationship("Paciente", back_populates="persona")

Grupo.lista = relationship("Lista", back_populates="grupo")
Lista.grupo = relationship("Grupo", back_populates="lista")

Usuario.rol = relationship("Rol", back_populates="usuario")
Rol.usuario = relationship("Usuario", back_populates="rol")
