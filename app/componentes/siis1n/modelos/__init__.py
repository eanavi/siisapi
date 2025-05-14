# -*- coding: utf-8 -*-
from sqlalchemy.orm import relationship
from .base import ParametroBase

from .persona import Persona
from .empleado import Empleado
from .centro import Centro
from .rol import Rol
from .menu import Menu
from .rol_menu import RolMenu
from .usuario import Usuario
from .prestacion import Prestacion
from .grupo import Grupo
from .variables import Variables
from .lista import Lista
from .paciente import Paciente
from .prestacion import Prestacion
from .menu import Menu
from .turno import Turno
from .reserva import Reserva




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

# Definir la relación para Turno
Turno.empleado = relationship("Empleado", back_populates="turnos")
Empleado.turnos = relationship("Turno", back_populates="empleado")

Prestacion.turnos = relationship("Turno", back_populates="prestacion")
Turno.prestacion = relationship("Prestacion", back_populates="turnos")

Prestacion.variables = relationship("Variables", back_populates="prestacion")
Variables.prestacion = relationship("Prestacion", back_populates="variables")

# Definir la relación para Reserva
Reserva.turno = relationship("Turno", back_populates="reservas")
Turno.reservas = relationship("Reserva", back_populates="turno")

Reserva.paciente = relationship("Paciente", back_populates="reservas")
Paciente.reservas = relationship("Reserva", back_populates="paciente")

# Definir la relación para Prestacion
