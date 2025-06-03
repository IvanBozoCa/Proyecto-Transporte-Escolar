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

@router.post("/crear-admin", response_model=schemas.UsuarioResponse)
def crear_admin_manual(
    nombre: str = Body(...),
    email: EmailStr = Body(...),
    telefono: str = Body(...),
    contrasena: str = Body(..., min_length=8),
    clave_secreta: str = Body(...),
    db: Session = Depends(get_db)
):
    if clave_secreta != "CLAVE_ULTRA_SECRETA":
        raise HTTPException(status_code=401, detail="Clave incorrecta")

    if db.query(models.Usuario).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    nuevo_admin = models.Usuario(
        nombre=nombre,
        email=email,
        telefono=telefono,
        contrasena=hash_contrasena(contrasena),
        tipo_usuario="administrador"
    )
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)
    return nuevo_admin

# ---------- CREAR APODERADO + ESTUDIANTE ----------

@router.post("/apoderado-estudiante", response_model=schemas.ApoderadoYEstudianteResponse)
def crear_apoderado_con_estudiante(
    datos: schemas.ApoderadoYEstudiante,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(verificar_admin)
):
    if db.query(models.Usuario).filter_by(email=datos.apoderado.email).first():
        raise HTTPException(status_code=400, detail="Correo ya registrado")

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


    nuevo_apoderado = models.Apoderado(
        id_usuario=nuevo_usuario.id_usuario,
        direccion=datos.estudiante.direccion  
    )
    db.add(nuevo_apoderado)
    db.commit()
    db.refresh(nuevo_apoderado)

    nuevo_estudiante = models.Estudiante(
        nombre=datos.estudiante.nombre,
        edad=datos.estudiante.edad,
        direccion=datos.estudiante.direccion,
        latitud=datos.estudiante.latitud,
        longitud=datos.estudiante.longitud,
        hora_entrada=datos.estudiante.hora_entrada,
        id_apoderado=nuevo_apoderado.id_apoderado,  
        nombre_apoderado_secundario=datos.estudiante.nombre_apoderado_secundario,
        telefono_apoderado_secundario=datos.estudiante.telefono_apoderado_secundario
    )
    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)

    return schemas.ApoderadoYEstudianteResponse(
        apoderado=schemas.UsuarioResponse.model_validate(nuevo_usuario),
        estudiante=schemas.EstudianteResponse.model_validate(nuevo_estudiante)
    )

# ---------- CREAR CONDUCTOR + FURGÓN ----------

@router.post("/conductor-completo", response_model=schemas.UsuarioResponse)
def crear_conductor_completo(
    datos: schemas.ConductorCompleto,
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
        codigo_vinculacion=datos.datos_conductor.codigo_vinculacion
    )
    db.add(nuevo_conductor)
    db.commit()

    return nuevo_usuario

# ---------- ACOMPAÑANTE ----------

@router.post("/acompanantes", response_model=schemas.AcompananteResponse)
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

@router.get("/acompanantes", response_model=List[schemas.AcompananteResponse])
def listar_acompanantes(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    return db.query(models.Acompanante).all()

# ---------- GET EXTENDIDOS ----------

@router.get("/apoderados-detalle", response_model=List[schemas.ApoderadoConEstudiantes])
def obtener_apoderados_con_estudiantes(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    apoderados = db.query(models.Usuario).filter_by(tipo_usuario="apoderado").all()
    resultado = []
    for ap in apoderados:
        estudiantes = db.query(models.Estudiante).filter_by(id_apoderado=ap.id_usuario).all()
        resultado.append(schemas.ApoderadoConEstudiantes(
            id_usuario=ap.id_usuario,
            nombre=ap.nombre,
            email=ap.email,
            telefono=ap.telefono,
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
        acompanante = c.acompanante
        resultado.append(schemas.ConductorConAcompanante(
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            telefono=usuario.telefono,
            patente=c.patente,
            modelo_vehiculo=c.modelo_vehiculo,
            codigo_vinculacion=c.codigo_vinculacion,
            acompanante=acompanante
        ))
    return resultado

# ---------- ASIGNACIONES ----------

@router.post("/asignar-estudiante-conductor")
def asignar_estudiante_a_conductor(
    id_estudiante: int,
    id_conductor: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=id_estudiante).first()
    conductor = db.query(models.Conductor).filter_by(id_conductor=id_conductor).first()

    if not estudiante or not conductor:
        raise HTTPException(status_code=404, detail="Estudiante o conductor no encontrado")

    estudiante.id_conductor = id_conductor
    db.commit()
    return {"mensaje": "Estudiante asignado al conductor"}

@router.post("/asignar-acompanante")
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

@router.delete("/estudiante/{id_estudiante}")
def eliminar_estudiante(id_estudiante: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=id_estudiante).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(estudiante)
    db.commit()
    return {"mensaje": "Estudiante eliminado"}

@router.delete("/conductor/{id_usuario}")
def eliminar_conductor(id_usuario: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    usuario = db.query(models.Usuario).filter_by(id_usuario=id_usuario, tipo_usuario="conductor").first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Conductor eliminado"}

@router.delete("/acompanante/{id_acompanante}")
def eliminar_acompanante(id_acompanante: int, db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    acompanante = db.query(models.Acompanante).filter_by(id_acompanante=id_acompanante).first()
    if not acompanante:
        raise HTTPException(status_code=404, detail="Acompañante no encontrado")
    db.delete(acompanante)
    db.commit()
    return {"mensaje": "Acompañante eliminado"}

# ---------- EDICIONES ----------

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

@router.put("/conductor-datos/{id_conductor}")
def editar_datos_conductor(
    id_conductor: int,
    cambios: schemas.ConductorUpdateDatos,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    conductor = db.query(models.Conductor).filter_by(id_conductor=id_conductor).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    for attr, value in cambios.dict(exclude_unset=True).items():
        setattr(conductor, attr, value)

    db.commit()
    db.refresh(conductor)
    return {
        "mensaje": "Datos del conductor actualizados correctamente",
        "conductor": {
            "id": conductor.id_conductor,
            "patente": conductor.patente,
            "modelo_vehiculo": conductor.modelo_vehiculo,
            "codigo_vinculacion": conductor.codigo_vinculacion
        }
    }


@router.get("/conductor/{id_usuario}", response_model=schemas.ConductorConAcompanante)
def obtener_conductor_detalle(
    id_usuario: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    usuario = db.query(models.Usuario).filter_by(id_usuario=id_usuario, tipo_usuario="conductor").first()
    if not usuario or not usuario.conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    conductor = usuario.conductor
    acompanante = conductor.acompanante

    return schemas.ConductorConAcompanante(
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        patente=conductor.patente,
        modelo_vehiculo=conductor.modelo_vehiculo,
        codigo_vinculacion=conductor.codigo_vinculacion,
        acompanante=acompanante
    )
@router.get("/conductor/{id_usuario}/puntos-mapa")
def obtener_puntos_ruta_para_mapa(
    id_usuario: int,
    fecha: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor" or usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta ruta")

    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    # Filtrar por asistencia
    presentes = []
    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=fecha,
            asiste=True
        ).first()
        if asistencia:
            presentes.append(est)

    # Ordenar por hora de entrada
    presentes_ordenados = sorted(presentes, key=lambda e: e.hora_entrada)

    # Construir respuesta para mapa
    puntos = [
        {
            "nombre": est.nombre,
            "lat": est.latitud,
            "lng": est.longitud,
            "hora_entrada": est.hora_entrada.strftime("%H:%M")
        }
        for est in presentes_ordenados
    ]

    return puntos
