from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.extension import Extension
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.narrative import Narrative

from app.nucleo.configuracion import config
from app.componentes.fhir.constantes import SISTEMA_CI, SISTEMA_RN, SISTEMA_SNIS
from app.componentes.siis1n.esquemas.paciente import PacientePersona
from app.componentes.siis1n.modelos.centro import Centro
from datetime import date

CATALOGO_BASE = f"{config.CADENA_DOMINIO}/listas/"

def codeable(codigo:str, catalogo: str) -> CodeableConcept:
    return CodeableConcept(
        coding = [Coding(
            system=f"{CATALOGO_BASE}/{catalogo}", # La URL del sistema para el código
            code=str(codigo).strip() # Asegura que el código sea una cadena y se eliminen los espacios en blanco
        )]
    )

def persona_a_patient_fhir(persona : PacientePersona, centro: Centro | dict) -> Patient:
    
    gender_map = {
        "M":"male",
        "F":"female",
        "N":"unknown"
    }

    mapa_estado_civil = {
        "1": {
            "code": "S",
            "display": "Never Married",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        "2": {
            "code": "M",
            "display": "Married",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        "3": {
            "code": "D",
            "display": "Divorced",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        "4": {
            "code":"W",
            "display":"Widowed",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        "5": {
            "code": "T",
            "display":"Domestic partner",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        "6":{
            "code":"UNK",
            "display":"unknown",
            "system":"http://terminology.hl7.org/CodeSystem/v3-NullFlavor"

        }
    }

    identificadores = []


    if persona.ci:
        if persona.ci.startswith("RN"):
            identificadores.append(Identifier(
                system=SISTEMA_RN,
                value=codigo_rn,
                use="temp"
            ))
        else:
            identificadores.append(Identifier(
                system=SISTEMA_CI,
                value=persona.ci.strip(),
                use="official"
            ))
    
    family = " ".join(
        filter(None, [persona.paterno, persona.materno])
    ).strip()    
    
    nombres = HumanName(
        use="official",
        family = family if family else None,
        given=[persona.nombres.strip()]
    )

    telecom = []
    
    if persona.telefono:
        for tipo, numero in persona.telefono.items():
            if numero:
                telecom.append(
                    ContactPoint(
                        system="phone", 
                        value=numero.strip(),
                        use="mobile" if tipo == "celular" else "home"
                    )
                )
    
    if persona.correo:
        for tipo, email in persona.correo.items():
            if email:
                telecom.append(
                    ContactPoint(
                        system="email",
                        value=email.strip()
                    )
                )
    

    direcciones = []

    if persona.direccion:
        for dir_item in persona.direccion:
            d = dir_item.direccion
            direcciones.append(
                Address(
                    text=" ".join(filter(None, [
                        d.zona,
                        d.calle,
                        d.numero,
                        d.ciudad
                    ])).strip(),
                    city=d.ciudad,
                    state=d.ciudad,
                    country='Bolivia'
                )
            )
    
    estado_civil = None
    if persona.estado_civil:
        detalle = mapa_estado_civil.get(persona.estado_civil.strip(), mapa_estado_civil["6"])
        estado_civil = CodeableConcept(
            coding = [
                Coding(
                    system=detalle["system"],
                    code=detalle["code"],
                    display=detalle["display"]
                )
            ]
        )

    centro_org = None

    if centro:
        centro_org = Reference(
            reference=f"Organization/{centro.id_centro}",
            display=centro.nombre_centro
        )
    
    narrativa = Narrative(
        status="generated",
        div=f"<div xmlns='http://www.w3.org/1999/xhtml'>"
        f"Paciente {persona.nombres} {family}"
        f"</div>"
    )






    extensiones = [
        Extension(
            url=f"{CATALOGO_BASE}grupo/ocupacion",
            valueCodeableConcept=codeable(persona.ocupacion, "ocupacion")
        )
    ]



    return Patient(
        id=str(persona.id_persona),
        text=narrativa,
        identifier=identificadores,
        active=True,
        name=[nombres],
        telecom=telecom if telecom else None,
        gender=gender_map.get(persona.sexo),
        birthDate=persona.fecha_nacimiento,
        address=direcciones if direcciones else None,
        extension=extensiones,
        maritalStatus=estado_civil,
        managingOrganization=centro_org
    )

def mapear_paciente_a_fhir(persona, paciente, centro=None) -> Patient:
    gender_map = {
        "M":"male",
        "F":"female",
        "N":"unknown"
    }

    mapa_estado_civil = {
        1: {
            "code": "S",
            "display": "Never Married",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        2: {
            "code": "M",
            "display": "Married",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        3: {
            "code": "D",
            "display": "Divorced",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        4: {
            "code":"W",
            "display":"Widowed",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        5: {
            "code": "T",
            "display":"Domestic partner",
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"
        },
        6:{
            "code":"UNK",
            "display":"unknown",
            "system":"http://terminology.hl7.org/CodeSystem/v3-NullFlavor"

        }
    }

    identificadores = [
        Identifier(
            use="official",
            system=SISTEMA_CI,
            value=persona.ci.strip()
        )
    ]

    family = " ".join(
        filter(None, [[persona.paterno, pesona.materno]])
    ).strip()

    name = HumanName(
        use="official",
        family=family if family else None,
        given=[persona.nombres.strip()]
    )

    telecom = []

    if persona.telefono:
        for  tipo, numero in persona.telefono.items():
            telecom.append(
                ContactPoint(
                    system="phone",
                    value=numero.strip(),
                    use="mobile" if tipo == "celular" else "home"
                )
            )
    
    if persona.correo:
        for tipo, email in persona.correo.items():
            telecom.append(
                ContactPoint(
                    system="email",
                    value=email.strip()
                )
            )
    
    direcciones = []

    if persona.direccion:
        for dir_item in persona.direccion:
            direccion = dir_item.get("direccion", {})
            direcciones.append(
                Address(
                    text=" ".join(filter(None, [
                        direccion.get("zona"),
                        direccion.get("calle"),
                        direccion.get("numero"),
                        direccion.get("ciudad")
                    ])).strip(),
                    city=direccion.get("ciudad"),
                    state=direccion.get("ciudad"),
                    country="Bolivia"
                )
            )
    
    estado_civil = None
    if paciente.estado_civil:
        estado_civil = mapa_estado_civil(paciente.estado_civil, )
        estado_civil = CodeableConcept(
            coding=[
                coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                    code=paciente.estado_civil,
                    display=paciente.estado_civil
                )
            ]
        )
    
    centro_org = None
    if centro:
        centro_org = Reference(
            reference=f"Organization/{centro.id_centro}",
            display=centro.nombre_centro
        )
    
    narrativa = Narrative(
        status="generated",
        div=f"<div xmlns='http://www.w3.org/1999/xhtml'>"
            f"Paciente {persona.nombres} {family}"
            f"</div>"
    )

    patient = Patient(
        id=str(persona.id_persona),
        text=narrativa,
        identifier=identificadores,
        active=True,
        name=[name],
        telecom=telecom if telecom else None,
        gender=gender_map.get(persona.sexo),
        birthDate=persona.fecha_nacimiento,
        address=direcciones if direcciones else None,
        maritalStatus=estado_civil,
        managingOrganization=centro_org
    )

    return patient



def patient_fhir_a_persona(patient: Patient) -> dict:
    ci = None
    rn = None

    for ident in patient.identifier or []:
        if ident.system == SISTEMA_CI:
            ci = ident.value
        
        if ident.system == SISTEMA_RN:
            rn = ident.value
    name = patient.name[0]

    return {
        "ci": ci,
        "rn": rn,
        "nombres": " ".join(name.given),
        "paterno": name.family,
        "fecha_nacimiento":patient.birthDate,
        "sexo": "M" if patient.gender == "male" else "F"
    }
