from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class SE_HC(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    Emp_Codigo: int = Field(..., title="Código del Empresa")
    HCL_CODIGO: int = Field(...,
                            title="Código de Historia Clínica", primary_key=True)
    HCL_FECHA: Optional[datetime] = Field(
        None, title="Fecha de Historia Clínica")
    HCL_APPAT: Optional[str] = Field(
        None, max_length=50, title="Apellido Paterno")
    HCL_APMAT: Optional[str] = Field(
        None, max_length=50, title="Apellido Materno")
    HCL_NOMBRE: Optional[str] = Field(None, max_length=50, title="Nombre")
    HCL_NUMCI: Optional[str] = Field(None, max_length=20, title="Número de CI")
    HCL_SEXO: Optional[str] = Field(None, max_length=1, title="Sexo")
    HCL_FECNAC: Optional[datetime] = Field(None, title="Fecha de Nacimiento")
    DEP_CODIGO_RES: Optional[int] = Field(
        None, title="Código de Departamento de Residencia")
    PRO_CODIGO_RES: Optional[int] = Field(
        None, title="Código de Provincia de Residencia")
    MUN_CODIGO_RES: Optional[int] = Field(
        None, title="Código de Municipio de Residencia")
    HCL_ESTCIV: Optional[str] = Field(None, max_length=1, title="Estado Civil")
    HCL_DIRECC: Optional[str] = Field(None, max_length=150, title="Dirección")
    HCL_TELDOM: Optional[str] = Field(
        None, max_length=50, title="Teléfono Domicilio")
    PProCodPro: Optional[int] = Field(
        None, title="Código de Profesión del Padre")
    HCL_LUGTRA: Optional[str] = Field(
        None, max_length=50, title="Lugar de Trabajo")
    HCL_DIRTRA: Optional[str] = Field(
        None, max_length=150, title="Dirección de Trabajo")
    HCL_TELTRA: Optional[str] = Field(
        None, max_length=15, title="Teléfono de Trabajo")
    HCL_NOMFAM: Optional[str] = Field(
        None, max_length=50, title="Nombre Familiar")
    HCL_TELFAM: Optional[str] = Field(
        None, max_length=15, title="Teléfono Familiar")
    HCL_NOMPAD: Optional[str] = Field(
        None, max_length=50, title="Nombre del Padre")
    HCL_NOMMAD: Optional[str] = Field(
        None, max_length=50, title="Nombre de la Madre")
    HCL_CodCSB: Optional[str] = Field(None, max_length=50, title="Código CSB")
    HCL_CodSegSoc: Optional[str] = Field(
        None, max_length=500, title="Código de Seguro Social")
    HCL_CODFAM: Optional[int] = Field(None, title="Código Familiar")
    DEP_CODIGO_LN: Optional[int] = Field(
        None, title="Código de Departamento de Nacimiento")
    HCL_CODMEDICO: Optional[int] = Field(0, title="Código Médico")
    zon_codigo: Optional[int] = Field(0, title="Código de Zona")
    HCL_USUMOD: Optional[int] = Field(0, title="Usuario de Modificación")
    HCL_FECMOD: Optional[datetime] = Field(None, title="Fecha de Modificación")
    DEP_CODIGO_NAC: Optional[int] = Field(
        None, title="Código de Departamento de Nacimiento")
    PRO_CODIGO_NAC: Optional[int] = Field(
        None, title="Código de Provincia de Nacimiento")
    MUN_CODIGO_NAC: Optional[int] = Field(
        None, title="Código de Municipio de Nacimiento")
    hc_alfa: Optional[str] = Field(None, max_length=1, title="Alfa HC")
    hc_NivelEstudio: Optional[int] = Field(None, title="Nivel de Estudio")
    HCL_SUMI: str = Field("N", max_length=1, title="SUMI")
    HCL_SUMI_FECHA: Optional[datetime] = Field(None, title="Fecha SUMI")
    HCL_ESTADO: str = Field("A", max_length=1, title="Estado")
    HCL_TIPODOC: Optional[int] = Field(1, title="Tipo de Documento")
    hcl_migrado: Optional[str] = Field("N", max_length=1, title="Migrado HC")
    idioma: Optional[int] = Field(None, title="Idioma")
    idiomamaterno: Optional[int] = Field(None, title="Idioma Materno")
    autopertenencia: Optional[int] = Field(None, title="Autopertenencia")
    hcl_Fum: Optional[datetime] = Field(None, title="FUM")
    hcl_NroEmbarazo: Optional[int] = Field(None, title="Número de Embarazo")
    codestabl: Optional[str] = Field(
        None, max_length=50, title="Código Establecimiento")
