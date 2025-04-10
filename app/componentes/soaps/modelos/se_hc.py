from sqlalchemy import Column, Integer, String, DateTime, CHAR
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class SE_HC(Base):
    __tablename__ = 'SE_HC'

    Emp_Codigo = Column(Integer, nullable=False)
    HCL_CODIGO = Column(Integer, primary_key=True)
    HCL_FECHA = Column(DateTime)
    HCL_APPAT = Column(String(50))
    HCL_APMAT = Column(String(50))
    HCL_NOMBRE = Column(String(50))
    HCL_NUMCI = Column(String(20))
    HCL_SEXO = Column(CHAR(1))
    HCL_FECNAC = Column(DateTime)
    DEP_CODIGO_RES = Column(Integer)
    PRO_CODIGO_RES = Column(Integer)
    MUN_CODIGO_RES = Column(Integer)
    HCL_ESTCIV = Column(CHAR(1))
    HCL_DIRECC = Column(String(150))
    HCL_TELDOM = Column(String(50))
    PProCodPro = Column(Integer)
    HCL_LUGTRA = Column(String(50))
    HCL_DIRTRA = Column(String(150))
    HCL_TELTRA = Column(String(15))
    HCL_NOMFAM = Column(String(50))
    HCL_TELFAM = Column(String(15))
    HCL_NOMPAD = Column(String(50))
    HCL_NOMMAD = Column(String(50))
    HCL_CodCSB = Column(String(50))
    HCL_CodSegSoc = Column(String(500))
    HCL_CODFAM = Column(Integer)
    DEP_CODIGO_LN = Column(Integer)
    HCL_CODMEDICO = Column(Integer, default=0)
    zon_codigo = Column(Integer, default=0)
    HCL_USUMOD = Column(Integer, default=0)
    HCL_FECMOD = Column(DateTime)
    DEP_CODIGO_NAC = Column(Integer)
    PRO_CODIGO_NAC = Column(Integer)
    MUN_CODIGO_NAC = Column(Integer)
    hc_alfa = Column(CHAR(1))
    hc_NivelEstudio = Column(Integer)
    HCL_SUMI = Column(CHAR(1), nullable=False, default='N')
    HCL_SUMI_FECHA = Column(DateTime)
    HCL_ESTADO = Column(CHAR(1), nullable=False, default='A')
    HCL_TIPODOC = Column(Integer, default=1)
    hcl_migrado = Column(CHAR(1), default='N')
    idioma = Column(Integer)
    idiomamaterno = Column(Integer)
    autopertenencia = Column(Integer)
    hcl_Fum = Column(DateTime)
    hcl_NroEmbarazo = Column(Integer)
    codestabl = Column(String(50))
