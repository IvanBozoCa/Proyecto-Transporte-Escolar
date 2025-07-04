from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.auth import hash_contrasena, verificar_admin, get_current_user
from app.database import get_db
from typing import List
from pydantic import EmailStr

router = APIRouter(prefix="/admin", tags=["Administrador"])
# ---------- CREAR ADMIN ----------

@router.post("/apoderado", response_model=schemas.ApoderadoYEstudianteResponse)
def crear_apoderado_con_estudiante(
    datos: schemas.ApoderadoYEstudiantecreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(verificar_admin)
):
    # Validar que el correo no esté en uso
    if db.query(models.Usuario).filter_by(email=datos.apoderado.email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    # Crear el usuario apoderado
    nuevo_usuario = models.Usuario(
        nombre=datos.apoderado.nombre,
        email=datos.apoderado.email,
        telefono=datos.apoderado.telefono,
        tipo_usuario="apoderado",
        contrasena=hash_contrasena(datos.apoderado.contrasena)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear entidad Apoderado
    nuevo_apoderado = models.Apoderado(id_usuario=nuevo_usuario.id_usuario)
    db.add(nuevo_apoderado)
    db.commit()
    db.refresh(nuevo_apoderado)

    # Buscar id_conductor desde id_usuario_conductor (opcional)
    id_conductor_final = None
    if datos.estudiante.id_usuario_conductor:
        conductor = db.query(models.Conductor).filter_by(id_usuario=datos.estudiante.id_usuario_conductor).first()
        if not conductor:
            raise HTTPException(status_code=404, detail="Conductor no encontrado para ese usuario")
        id_conductor_final = conductor.id_conductor

    # Crear estudiante
    nuevo_estudiante = models.Estudiante(
        nombre=datos.estudiante.nombre,
        edad=datos.estudiante.edad,
        id_apoderado=nuevo_apoderado.id_apoderado,
        colegio=datos.estudiante.colegio,
        casa=datos.estudiante.casa,
        curso=datos.estudiante.curso,
        lat_casa=datos.estudiante.lat_casa,
        long_casa=datos.estudiante.long_casa,
        lat_colegio=datos.estudiante.lat_colegio,
        long_colegio=datos.estudiante.long_colegio,
        nombre_apoderado_secundario=datos.estudiante.nombre_apoderado_secundario,
        telefono_apoderado_secundario=datos.estudiante.telefono_apoderado_secundario,
        id_conductor=id_conductor_final
    )
    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)

    # Obtener id_usuario del conductor para incluir en el response
    usuario_conductor = None
    if nuevo_estudiante.id_conductor:
        conductor_asociado = db.query(models.Conductor).filter_by(id_conductor=nuevo_estudiante.id_conductor).first()
        if conductor_asociado:
            usuario_conductor = conductor_asociado.id_usuario

    return schemas.ApoderadoYEstudianteResponse(
        apoderado=schemas.UsuarioResponse(
            id_usuario=nuevo_usuario.id_usuario,
            nombre=nuevo_usuario.nombre,
            email=nuevo_usuario.email,
            telefono=nuevo_usuario.telefono,
            tipo_usuario=nuevo_usuario.tipo_usuario
        ),
        estudiante=schemas.EstudianteResponse(
            id_estudiante=nuevo_estudiante.id_estudiante,
            nombre=nuevo_estudiante.nombre,
            edad=nuevo_estudiante.edad,
            curso=nuevo_estudiante.curso,
            colegio=nuevo_estudiante.colegio,
            casa=nuevo_estudiante.casa,
            lat_casa=nuevo_estudiante.lat_casa,
            long_casa=nuevo_estudiante.long_casa,
            lat_colegio=nuevo_estudiante.lat_colegio,
            long_colegio=nuevo_estudiante.long_colegio,
            nombre_apoderado_secundario=nuevo_estudiante.nombre_apoderado_secundario,
            telefono_apoderado_secundario=nuevo_estudiante.telefono_apoderado_secundario,
            id_usuario_conductor=usuario_conductor  
        )
    )

# ---------- ACOMPAÑANTE ----------

@router.post("/acompanante", response_model=schemas.AcompananteResponse)
def crear_acompanante(
    acompanante: schemas.AcompananteCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    nuevo = models.Acompanante(**acompanante.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ---------- CREAR CONDUCTOR + FURGÓN ----------
@router.post("/conductor", response_model=schemas.ConductorCompletoResponse)
def crear_conductor_completo(

    datos: schemas.ConductorCompletoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    if db.query(models.Usuario).filter_by(email=datos.usuario.email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    nuevo_usuario = models.Usuario(
        nombre=datos.usuario.nombre,
        email=datos.usuario.email,
        telefono=datos.usuario.telefono,
        tipo_usuario="conductor",
        contrasena=hash_contrasena(datos.usuario.contrasena)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nuevo_conductor = models.Conductor(
        id_usuario=nuevo_usuario.id_usuario,
        patente=datos.datos_conductor.patente,
        modelo_vehiculo=datos.datos_conductor.modelo_vehiculo,
        casa=datos.datos_conductor.casa,
        lat_casa=datos.datos_conductor.lat_casa,
        long_casa=datos.datos_conductor.long_casa
    )
    db.add(nuevo_conductor)
    db.commit()

    return schemas.ConductorCompletoResponse(
    usuario=schemas.UsuarioResponse(
        id_usuario=nuevo_usuario.id_usuario,
        nombre=nuevo_usuario.nombre,
        email=nuevo_usuario.email,
        telefono=nuevo_usuario.telefono,
        tipo_usuario=nuevo_usuario.tipo_usuario
    ),
    datos_conductor=schemas.DatosConductorSchema(
        patente=nuevo_conductor.patente,
        modelo_vehiculo=nuevo_conductor.modelo_vehiculo,
        casa=nuevo_conductor.casa,
        lat_casa=nuevo_conductor.lat_casa,
        long_casa=nuevo_conductor.long_casa
    )
)



@router.post("/AsignarEstudianteConductor")
def asignar_estudiante_a_conductor(
    datos: schemas.EstudianteAConductor,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=datos.id_estudiante).first()
    conductor = db.query(models.Conductor).filter_by(id_usuario=datos.id_usuario_conductor).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado para ese usuario")

    estudiante.id_conductor = conductor.id_conductor
    db.commit()

    return {"mensaje": "Estudiante asignado al conductor correctamente"}

    
@router.post("/AsignarAcompanante")
def asignar_acompanante_a_conductor(
    id_conductor: int,
    id_acompanante: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    conductor = db.query(models.Conductor).filter_by(id_conductor=id_conductor).first()
    acompanante = db.query(models.Acompanante).filter_by(id_acompanante=id_acompanante).first()

    if not conductor or not acompanante:
        raise HTTPException(status_code=404, detail="Conductor o acompañante no encontrado")

    conductor.id_acompanante = id_acompanante
    db.commit()
    return {"mensaje": "Acompañante asignado correctamente"}


# ---------- ELIMINACIONES ----------

@router.delete("/apoderado/{id_usuario}")
def eliminar_apoderado(id_usuario: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    usuario = db.query(models.Usuario).filter_by(id_usuario=id_usuario, tipo_usuario="apoderado").first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Apoderado eliminado"}

@router.delete("/Estudiante/{id_estudiante}")
def eliminar_estudiante(id_estudiante: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(estudiante)
    db.commit()
    return {"mensaje": "Estudiante eliminado"}

@router.delete("/Conductor/{id_usuario}")
def eliminar_conductor(id_usuario: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    usuario = db.query(models.Usuario).filter_by(id_usuario=id_usuario, tipo_usuario="conductor").first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Conductor eliminado"}

@router.delete("/Acompanante/{id_acompanante}")
def eliminar_acompanante(id_acompanante: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    acompanante = db.query(models.Acompanante).filter_by(id_acompanante=id_acompanante).first()
    if not acompanante:
        raise HTTPException(status_code=404, detail="Acompañante no encontrado")
    db.delete(acompanante)
    db.commit()
    return {"mensaje": "Acompañante eliminado"}

# ---------- GET -----------


@router.get("/acompanantes", response_model=List[schemas.AcompananteResponse])
def listar_acompanantes(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    return db.query(models.Acompanante).all()

@router.get("/conductor/{id_usuario}", response_model=schemas.ConductorCompletoResponse)
def obtener_conductor_completo(
    id_usuario: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor or not conductor.usuario:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    usuario = conductor.usuario

    return schemas.ConductorCompletoResponse(
        usuario=schemas.UsuarioResponse(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            telefono=usuario.telefono,
            tipo_usuario=usuario.tipo_usuario
        ),
        datos_conductor=schemas.DatosConductorSchema(
            patente=conductor.patente,
            modelo_vehiculo=conductor.modelo_vehiculo,
            casa=conductor.casa,
            lat_casa=conductor.lat_casa,
            long_casa=conductor.long_casa
        )
    )



@router.get("/apoderado", response_model=List[schemas.ApoderadoConEstudiantes])
def obtener_apoderados_con_estudiantes(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    usuarios_apoderados = db.query(models.Usuario).filter_by(tipo_usuario="apoderado").all()
    resultado = []

    for usuario in usuarios_apoderados:
        apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario.id_usuario).first()
        if not apoderado:
            continue

        estudiantes_orm = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).all()

        estudiantes = [
            schemas.EstudianteSimple(
                id_estudiante=e.id_estudiante,
                nombre=e.nombre,
                edad=e.edad,
                curso=e.curso,
                casa=e.casa,
                lat_casa=e.lat_casa,
                long_casa=e.long_casa,
                colegio=e.colegio,
                lat_colegio=e.lat_colegio,
                long_colegio=e.long_colegio,
                nombre_apoderado_secundario=e.nombre_apoderado_secundario,
                telefono_apoderado_secundario=e.telefono_apoderado_secundario,
                id_usuario_conductor=e.conductor.usuario.id_usuario if e.conductor and e.conductor.usuario else None
            )
            for e in estudiantes_orm
        ]

        resultado.append(schemas.ApoderadoConEstudiantes(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            telefono=usuario.telefono,
            estudiantes=estudiantes
        ))

    return resultado

@router.get("/conductores", response_model=List[schemas.ConductorConAcompanante])
def obtener_conductores_con_acompanante(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    conductores = db.query(models.Conductor).join(models.Usuario).all()
    resultado = []
    for c in conductores:
        usuario = c.usuario
        acompanante = None
        if c.acompanante:
            acompanante = schemas.NombreAcompanante(nombre_completo=c.acompanante.nombre)
        
        resultado.append(schemas.ConductorConAcompanante(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            telefono=usuario.telefono,
            patente=c.patente,
            modelo_vehiculo=c.modelo_vehiculo,
            acompanante=acompanante
        ))
    return resultado




@router.get("/usuarios", response_model=List[schemas.UsuarioConDatos])
def listar_todos_los_usuarios(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    usuarios = db.query(models.Usuario).all()
    resultado = []

    for usuario in usuarios:
        item = {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "tipo_usuario": usuario.tipo_usuario,
            "datos_conductor": None,
            "datos_apoderado": None,
            "datos_acompanante": None
        }

        # Si es conductor
        if usuario.tipo_usuario == "conductor" and usuario.conductor:
            item["datos_conductor"] = {
                "id_conductor": usuario.conductor.id_conductor,
                "patente": usuario.conductor.patente,
                "modelo_vehiculo": usuario.conductor.modelo_vehiculo,
                "casa": usuario.conductor.casa,
                "lat_casa": float(usuario.conductor.lat_casa) if usuario.conductor.lat_casa else None,
                "long_casa": float(usuario.conductor.long_casa) if usuario.conductor.long_casa else None
            }

        # Si es apoderado
        elif usuario.tipo_usuario == "apoderado" and usuario.apoderado:
            estudiante = db.query(models.Estudiante).filter_by(id_apoderado=usuario.apoderado.id_apoderado).first()
            if estudiante:
                item["datos_apoderado"] = {
                    "id_apoderado": usuario.apoderado.id_apoderado,
                    "estudiante": {
                        "id_estudiante": estudiante.id_estudiante,
                        "nombre": estudiante.nombre,
                        "edad": estudiante.edad,
                        "curso": estudiante.curso,
                        "casa": estudiante.casa,
                        "lat_casa": float(estudiante.lat_casa) if estudiante.lat_casa else None,
                        "long_casa": float(estudiante.long_casa) if estudiante.long_casa else None,
                        "colegio": estudiante.colegio,
                        "lat_colegio": float(estudiante.lat_colegio) if estudiante.lat_colegio else None,
                        "long_colegio": float(estudiante.long_colegio) if estudiante.long_colegio else None,
                        "id_conductor": estudiante.id_conductor
                    }
                }

        # Si es acompañante
        elif usuario.tipo_usuario == "acompanante" and usuario.acompanante:
            item["datos_acompanante"] = {
                "nombre_completo": usuario.acompanante.nombre
            }

        resultado.append(item)

    return resultado

@router.get("/apoderado/{id_usuario}", response_model=schemas.ApoderadoConEstudiantes)
def obtener_apoderado_por_id(
    id_usuario: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    apoderado = db.query(models.Apoderado).filter_by(id_usuario=id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    usuario = apoderado.usuario 

    estudiantes = []
    for e in apoderado.estudiantes:
        id_usuario_conductor = None
        if e.conductor:
            id_usuario_conductor = e.conductor.id_usuario

        estudiantes.append(
            schemas.EstudianteSimple(
                id_estudiante=e.id_estudiante,
                nombre=e.nombre,
                edad=e.edad,
                curso=e.curso,
                casa=e.casa,
                lat_casa=e.lat_casa,
                long_casa=e.long_casa,
                colegio=e.colegio,
                lat_colegio=e.lat_colegio,
                long_colegio=e.long_colegio,
                id_usuario_conductor=id_usuario_conductor
            )
        )

    return schemas.ApoderadoConEstudiantes(
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        estudiantes=estudiantes
    )


@router.put("/usuario/{id_usuario}", response_model=schemas.UsuarioResponse)
def editar_usuario(
    id_usuario: int,
    cambios: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    usuario = db.query(models.Usuario).filter_by(id_usuario=id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for attr, value in cambios.dict(exclude_unset=True).items():
        if attr == "contrasena":
            setattr(usuario, attr, hash_contrasena(value))
        else:
            setattr(usuario, attr, value)

    db.commit()
    db.refresh(usuario)
    return usuario

@router.put("/estudiante/{id_estudiante}", response_model=schemas.EstudianteResponse)
def editar_estudiante(
    id_estudiante: int,
    cambios: schemas.EstudianteUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    for attr, value in cambios.dict(exclude_unset=True).items():
        setattr(estudiante, attr, value)

    db.commit()
    db.refresh(estudiante)
    return estudiante

@router.put("/acompanante/{id_acompanante}", response_model=schemas.AcompananteResponse)
def editar_acompanante(
    id_acompanante: int,
    cambios: schemas.AcompananteUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    acompanante = db.query(models.Acompanante).filter_by(id_acompanante=id_acompanante).first()
    if not acompanante:
        raise HTTPException(status_code=404, detail="Acompañante no encontrado")

    for attr, value in cambios.dict(exclude_unset=True).items():
        setattr(acompanante, attr, value)

    db.commit()
    db.refresh(acompanante)
    return acompanante

@router.put("/apoderado/{id_usuario}", response_model=schemas.ApoderadoYEstudianteResponse)
def editar_apoderado_con_estudiante(
    id_usuario: int,
    datos: schemas.ApoderadoYEstudiante,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    # Buscar apoderado
    apoderado = db.query(models.Apoderado).filter_by(id_usuario=id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    # Buscar usuario asociado
    usuario = db.query(models.Usuario).filter_by(id_usuario=apoderado.id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario asociado no encontrado")

    # Verificar duplicidad de correo
    email_existente = db.query(models.Usuario).filter(
        models.Usuario.email == datos.apoderado.email,
        models.Usuario.id_usuario != usuario.id_usuario
    ).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado por otro usuario.")

    # Actualizar datos del usuario
    usuario.nombre = datos.apoderado.nombre
    usuario.email = datos.apoderado.email
    usuario.telefono = datos.apoderado.telefono

    # Buscar estudiante
    estudiante = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).first()
    usuario_conductor = None

    if estudiante:
        estudiante.nombre = datos.estudiante.nombre
        estudiante.edad = datos.estudiante.edad
        estudiante.nombre_apoderado_secundario = datos.estudiante.nombre_apoderado_secundario
        estudiante.telefono_apoderado_secundario = datos.estudiante.telefono_apoderado_secundario
        estudiante.curso = datos.estudiante.curso
        estudiante.colegio = datos.estudiante.colegio
        estudiante.lat_casa = datos.estudiante.lat_casa
        estudiante.long_casa = datos.estudiante.long_casa
        estudiante.lat_colegio = datos.estudiante.lat_colegio
        estudiante.long_colegio = datos.estudiante.long_colegio

        # Actualizar conductor si se proporciona
        if datos.estudiante.id_usuario_conductor is not None:
            conductor = db.query(models.Conductor).filter_by(id_usuario=datos.estudiante.id_usuario_conductor).first()
            if not conductor:
                raise HTTPException(status_code=404, detail="Conductor no encontrado con ese ID de usuario.")
            estudiante.id_conductor = conductor.id_conductor
            usuario_conductor = conductor.id_usuario

        # Si ya tiene un conductor asignado, recuperar su id_usuario también
        elif estudiante.id_conductor:
            conductor_existente = db.query(models.Conductor).filter_by(id_conductor=estudiante.id_conductor).first()
            if conductor_existente:
                usuario_conductor = conductor_existente.id_usuario

    db.commit()
    db.refresh(usuario)
    if estudiante:
        db.refresh(estudiante)

    return schemas.ApoderadoYEstudianteResponse(
        apoderado=schemas.UsuarioResponse.from_orm(usuario),
        estudiante=schemas.EstudianteResponse(
            id_estudiante=estudiante.id_estudiante,
            nombre=estudiante.nombre,
            edad=estudiante.edad,
            curso=estudiante.curso,
            colegio=estudiante.colegio,
            casa=estudiante.casa,
            lat_casa=estudiante.lat_casa,
            long_casa=estudiante.long_casa,
            lat_colegio=estudiante.lat_colegio,
            long_colegio=estudiante.long_colegio,
            nombre_apoderado_secundario=estudiante.nombre_apoderado_secundario,
            telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario,
            id_usuario_conductor=usuario_conductor
        ) if estudiante else None
    )



@router.put("/conductor/{id_usuario}", response_model=schemas.ConductorCompletoResponse)
def editar_conductor_completo(
    id_usuario: int,
    datos: schemas.ConductorCompletoupdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    usuario = db.query(models.Usuario).filter_by(id_usuario=conductor.id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario asociado no encontrado")

    # Verificar si el nuevo email ya está en uso por otro usuario
    if datos.usuario.email:
        email_existente = db.query(models.Usuario).filter(
            models.Usuario.email == datos.usuario.email,
            models.Usuario.id_usuario != usuario.id_usuario
        ).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado por otro usuario.")

    # Actualizar datos del usuario
    if datos.usuario.nombre:
        usuario.nombre = datos.usuario.nombre
    if datos.usuario.email:
        usuario.email = datos.usuario.email
    if datos.usuario.telefono:
        usuario.telefono = datos.usuario.telefono


    # Actualizar datos del conductor
    if datos.datos_conductor.patente:
        conductor.patente = datos.datos_conductor.patente
    if datos.datos_conductor.modelo_vehiculo:
        conductor.modelo_vehiculo = datos.datos_conductor.modelo_vehiculo
    if datos.datos_conductor.casa:
        conductor.casa = datos.datos_conductor.casa
    if datos.datos_conductor.lat_casa:
        conductor.lat_casa = datos.datos_conductor.lat_casa
    if datos.datos_conductor.long_casa:
        conductor.long_casa = datos.datos_conductor.long_casa

    db.commit()
    db.refresh(usuario)
    db.refresh(conductor)

    return schemas.ConductorCompletoResponse(
        usuario=schemas.UsuarioResponse(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            telefono=usuario.telefono,
            tipo_usuario=usuario.tipo_usuario
        ),
        datos_conductor=schemas.DatosConductorSchema(
            patente=conductor.patente,
            modelo_vehiculo=conductor.modelo_vehiculo,
            casa=conductor.casa,
            lat_casa=conductor.lat_casa,
            long_casa=conductor.long_casa
        )
    )
