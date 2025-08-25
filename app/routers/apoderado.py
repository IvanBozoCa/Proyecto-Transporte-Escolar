from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor, Asistencia
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date
from fastapi.responses import JSONResponse
from typing import Union
from app.firebase import notificaciones

router = APIRouter(
    prefix="/apoderado",
    tags=["Apoderado"]
)
@router.get("/me", response_model=schemas.ApoderadoResponse)
def obtener_mi_perfil_completo(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a este perfil")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).all()

    estudiantes_response = [
        schemas.EstudianteSimple(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            edad=est.edad,
            colegio=est.colegio,
            curso=est.curso,
            casa=est.casa,
            lat_casa=est.lat_casa,
            long_casa=est.long_casa,
            lat_colegio=est.lat_colegio,
            long_colegio=est.long_colegio,
            nombre_apoderado_secundario=est.nombre_apoderado_secundario,
            telefono_apoderado_secundario=est.telefono_apoderado_secundario,
            id_usuario_conductor=est.conductor.id_usuario if est.conductor else None
        )
        for est in estudiantes
    ]

    return schemas.ApoderadoResponse(
        id_apoderado=apoderado.id_apoderado,
        usuario=schemas.ApoderadoConEstudiantes(
            id_usuario=usuario_actual.id_usuario,
            nombre=usuario_actual.nombre,
            email=usuario_actual.email,
            telefono=usuario_actual.telefono,
            estudiantes=estudiantes_response
        )
    )

from datetime import date

@router.post("/asistencia", response_model=schemas.AsistenciaResponse)
def registrar_asistencia(
    asistencia: schemas.AsistenciaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="No autorizado")

    estudiante = db.query(models.Estudiante).filter_by(id_estudiante=asistencia.id_estudiante).first()
    if not estudiante or estudiante.id_apoderado != usuario_actual.apoderado.id_apoderado:
        raise HTTPException(status_code=403, detail="No autorizado para este estudiante")

    hoy = date.today()

    registro_existente = db.query(models.Asistencia).filter_by(
        id_estudiante=asistencia.id_estudiante,
        fecha=hoy
    ).first()

    if registro_existente:
        registro_existente.asiste = asistencia.asiste
        db.commit()
        db.refresh(registro_existente)
        asistencia_registrada = registro_existente
    else:
        nuevo = models.Asistencia(
            id_estudiante=asistencia.id_estudiante,
            fecha=hoy,
            asiste=asistencia.asiste
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        asistencia_registrada = nuevo

    # Enviar notificación al conductor si tiene token
    conductor = db.query(models.Conductor).filter_by(id_conductor=estudiante.id_conductor).first()
    if conductor and conductor.usuario and conductor.usuario.token_firebase:
        token_conductor = conductor.usuario.token_firebase.token
        notificaciones.enviar_notificacion_asistencia_conductor(estudiante.nombre, asistencia.asiste, token_conductor)

    return asistencia_registrada


@router.get("/hijos", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_hijos_con_asistencia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a esta información.")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado.")

    estudiantes = apoderado.estudiantes
    resultado = []

    for est in estudiantes:
        # Obtener asistencia más reciente
        asistencia = (
            db.query(models.Asistencia)
            .filter(models.Asistencia.id_estudiante == est.id_estudiante)
            .order_by(models.Asistencia.fecha.desc())
            .first()
        )

        if asistencia:
            asistencia_schema = schemas.AsistenciaHoyResponse.from_orm(asistencia)
        else:
            asistencia_schema = schemas.AsistenciaHoyResponse(
                fecha=date.today(),
                asiste=True
            )

        # Obtener ruta fija asociada a través de la parada del estudiante
        parada_fija = (
            db.query(models.ParadaRutaFija)
            .join(models.RutaFija)
            .filter(
                models.ParadaRutaFija.id_estudiante == est.id_estudiante,
                models.RutaFija.id_conductor == est.id_conductor
            )
            .first()
        )

        ruta_schema = schemas.RutaResumen(
            id=parada_fija.id_ruta_fija,
            nombre=parada_fija.ruta.nombre
        ) if parada_fija else None

        # Buscar parada activa del estudiante en la ruta del día
        parada_hoy = (
            db.query(models.Parada)
            .join(models.Ruta)
            .filter(
                models.Parada.id_estudiante == est.id_estudiante,
                models.Ruta.fecha == date.today(),
                models.Ruta.estado == "activa"
            )
            .first()
        )

        if parada_hoy:
            recogido = parada_hoy.recogido
            entregado = parada_hoy.entregado

            if recogido and entregado:
                estado_ruta = "entregado"
            elif recogido and not entregado:
                estado_ruta = "en ruta"
            else:
                estado_ruta = "pendiente"
        else:
            recogido = None
            entregado = None
            estado_ruta = None

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_schema,
            ruta=ruta_schema,
            recogido=recogido,
            entregado=entregado,
            estado_ruta=estado_ruta
        ))

    return resultado


@router.get("/ubicacionConductor/{id_usuario}", response_model=schemas.UbicacionConductorResponse)
def obtener_ubicacion_conductor(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    # Solo usuarios autenticados pueden acceder
    if usuario_actual.tipo_usuario not in ["apoderado", "conductor", "administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Buscar al conductor a partir del id_usuario
    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ubicacion = db.query(models.UbicacionConductor).filter_by(id_conductor=conductor.id_conductor).first()
    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada para el conductor")

    return schemas.UbicacionConductorResponse(
        latitud=ubicacion.latitud,
        longitud=ubicacion.longitud,
        timestamp=ubicacion.timestamp
    )

@router.get("/conductor", response_model=schemas.ConductorConAcompanante)
def obtener_conductor_asignado(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="No autorizado")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    estudiante = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="No se encontró estudiante asociado al apoderado")

    parada = (
        db.query(models.Parada)
        .filter_by(id_estudiante=estudiante.id_estudiante)
        .join(models.Ruta)
        .first()
    )
    if not parada or not parada.ruta:
        raise HTTPException(status_code=404, detail="No se encontró una ruta asignada al estudiante")

    conductor = parada.ruta.conductor
    if not conductor or not conductor.usuario:
        raise HTTPException(status_code=404, detail="Conductor no asignado correctamente")

    return schemas.ConductorConAcompanante(
    id_usuario=conductor.usuario.id_usuario,
    nombre=conductor.usuario.nombre,
    email=conductor.usuario.email,
    telefono=conductor.usuario.telefono,
    patente=conductor.patente,
    modelo_vehiculo=conductor.modelo_vehiculo,
    acompanante=schemas.NombreAcompanante(
        nombre_completo=conductor.acompanante.nombre
    ) if conductor.acompanante else None
)

@router.get("/verruta", response_model=schemas.RutaConParadasResponse)
def obtener_ruta_activa_apoderado(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a esta ruta")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="Apoderado no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).all()
    if not estudiantes:
        raise HTTPException(status_code=404, detail="No se encontraron estudiantes asociados")
    ids_hijos = {est.id_estudiante for est in estudiantes}
    

    hoy = date.today()

    # Buscar la primera ruta activa en la que esté algún estudiante del apoderado
    ruta = (
        db.query(models.Ruta)
        .join(models.Parada)
        .filter(
            models.Ruta.fecha == hoy,
            models.Ruta.estado == "activa",
            models.Parada.id_estudiante.in_(ids_hijos)
        )
        .first()
    )

    if not ruta:
        raise HTTPException(status_code=404, detail="No se encontró una ruta activa para los estudiantes")

    paradas_ordenadas = sorted(ruta.paradas, key=lambda p: p.orden)
    parada_responses = []
    for parada in paradas_ordenadas:
        estudiante = parada.estudiante
        es_hijo = parada.id_estudiante in ids_hijos 

        parada_responses.append(
            schemas.ParadaResponse(
                id_parada=parada.id_parada,
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud,
                recogido=parada.recogido,
                entregado=parada.entregado,
                es_hijo=es_hijo,
                estudiante=schemas.EstudianteSimple.from_orm(estudiante) if estudiante else None
            )
        )

    return schemas.RutaConParadasResponse(
        id_ruta=ruta.id_ruta,
        fecha=ruta.fecha,
        estado=ruta.estado,
        hora_inicio=ruta.hora_inicio,
        id_acompanante=ruta.id_acompanante,
        tipo=ruta.tipo,
        paradas=parada_responses
    )