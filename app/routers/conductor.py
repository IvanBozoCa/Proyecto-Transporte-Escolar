from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date, datetime

router = APIRouter(
    prefix="/conductor",
    tags=["Conductor"]
)

@router.get("/me", response_model=schemas.ConductorCompleto)
def obtener_mi_info_conductor(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="No se encontró un conductor vinculado a este usuario.")

    usuario_schema = schemas.UsuarioResponse(
        id_usuario=usuario_actual.id_usuario,
        nombre=usuario_actual.nombre,
        email=usuario_actual.email,
        telefono=usuario_actual.telefono,
        tipo_usuario=usuario_actual.tipo_usuario
    )

    datos_conductor_schema = schemas.ConductorCreateDatos(
        patente=conductor.patente,
        modelo_vehiculo=conductor.modelo_vehiculo,
        casa= conductor.casa,
        lat_casa=conductor.lat_casa,
        long_casa=conductor.long_casa
    )
    
    return schemas.ConductorCompleto(
        usuario=usuario_schema,
        datos_conductor=datos_conductor_schema
    )
    
    
@router.get("/mis-estudiantes", response_model=List[schemas.EstudianteResponse])
def obtener_estudiantes_conductor(
    usuario_actual: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="No se encontró conductor para este usuario.")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    return estudiantes


@router.get("/mis-estudiantes-hoy", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_estudiantes_con_asistencia_hoy(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")

    estudiantes = conductor.estudiantes
    resultado = []

    for est in estudiantes:
        asistencia_hoy = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=date.today()
        ).first()

        asistencia_schema = schemas.AsistenciaHoyResponse.from_orm(asistencia_hoy) if asistencia_hoy else None

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_schema
        ))

    return resultado

@router.get("/mis-rutas-fijas", response_model=List[schemas.RutaFijaResponse])
def obtener_mis_rutas_fijas(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden ver sus rutas fijas.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")

    rutas = db.query(models.RutaFija).filter_by(id_conductor=conductor.id_conductor).all()

    resultado = []
    for ruta in rutas:
        paradas = (
            db.query(models.ParadaRutaFija)
            .filter_by(id_ruta_fija=ruta.id_ruta_fija)
            .order_by(models.ParadaRutaFija.orden)
            .all()
        )

        paradas_estudiantes = []
        parada_final = None

        for parada in paradas:
            if parada.id_estudiante and parada.estudiante:
                paradas_estudiantes.append(
                    schemas.ParadaEstudianteRutaFijaResponse(
                        id_parada_ruta_fija=parada.id_parada_ruta_fija,
                        orden=parada.orden,
                        estudiante=schemas.EstudianteBasico(
                            id_estudiante=parada.estudiante.id_estudiante,
                            nombre=parada.estudiante.nombre
                        )
                    )
                )
            elif parada.es_destino_final:
                parada_final = schemas.ParadaFinalRutaFijaResponse(
                    id_parada_ruta_fija=parada.id_parada_ruta_fija,
                    orden=parada.orden,
                    latitud=parada.latitud,
                    longitud=parada.longitud
                )

        resultado.append(
            schemas.RutaFijaResponse(
                id_ruta_fija=ruta.id_ruta_fija,
                nombre=ruta.nombre,
                descripcion=ruta.descripcion,
                id_conductor=ruta.id_conductor,
                paradas=paradas_estudiantes,
                parada_final=parada_final
            )
        )

    return resultado

@router.post("/generar-ruta-dia/{id_ruta_fija}", response_model=schemas.RutaConParadasResponse)
def generar_ruta_dia(
    id_ruta_fija: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden generar rutas")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ruta_fija = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija, id_conductor=conductor.id_conductor).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada para este conductor")

    hoy = date.today()

    # Validar que no tenga una ruta activa
    ruta_activa = (
        db.query(models.Ruta)
        .filter_by(id_conductor=conductor.id_conductor, fecha=hoy, estado="activa")
        .first()
    )
    if ruta_activa:
        raise HTTPException(status_code=400, detail="Ya existe una ruta activa para hoy")

    nueva_ruta = models.Ruta(
        id_conductor=conductor.id_conductor,
        fecha=hoy,
        hora_inicio=datetime.now().time(),
        estado="activa"
    )
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    paradas_fijas = (
        db.query(models.ParadaRutaFija)
        .filter_by(id_ruta_fija=id_ruta_fija)
        .order_by(models.ParadaRutaFija.orden)
        .all()
    )

    for parada_fija in paradas_fijas:
        parada = models.Parada(
            id_ruta=nueva_ruta.id_ruta,
            orden=parada_fija.orden,
            latitud=parada_fija.latitud,
            longitud=parada_fija.longitud,
            recogido=False,
            entregado=False,
            id_estudiante=parada_fija.id_estudiante if not parada_fija.es_destino_final else None
        )
        db.add(parada)

    db.commit()
    db.refresh(nueva_ruta)

    # Preparar respuesta
    paradas_ordenadas = sorted(nueva_ruta.paradas, key=lambda p: p.orden)
    parada_responses = []
    for parada in paradas_ordenadas:
        estudiante = parada.estudiante
        parada_responses.append(
            schemas.ParadaResponse(
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud,
                recogido=parada.recogido,
                entregado=parada.entregado,
                estudiante=schemas.EstudianteSimple(
                    id_estudiante=estudiante.id_estudiante,
                    nombre=estudiante.nombre,
                    edad=estudiante.edad,
                    colegio=estudiante.colegio,
                    curso=estudiante.curso,
                    casa=estudiante.casa,
                    lat_casa=estudiante.lat_casa,
                    long_casa=estudiante.long_casa,
                    lat_colegio=estudiante.lat_colegio,
                    long_colegio=estudiante.long_colegio,
                    nombre_apoderado_secundario=estudiante.nombre_apoderado_secundario,
                    telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario
                ) if estudiante else None
            )
        )

    return schemas.RutaConParadasResponse(
        id_ruta=nueva_ruta.id_ruta,
        fecha=nueva_ruta.fecha,
        estado=nueva_ruta.estado,
        hora_inicio=nueva_ruta.hora_inicio,
        id_acompanante=nueva_ruta.id_acompanante,
        paradas=parada_responses
    )




@router.put("/finalizar-ruta-dia")
def finalizar_ruta_dia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Obtener al conductor desde el usuario
    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    # Buscar la ruta activa actual
    ruta = db.query(models.Ruta).filter_by(
        id_conductor=conductor.id_conductor,
        estado="activa"
    ).first()

    if not ruta:
        raise HTTPException(status_code=404, detail="No hay una ruta activa para finalizar")

    ruta.estado = "finalizada"
    ruta.hora_fin = datetime.now().time()
    db.commit()

    return {"mensaje": "Ruta finalizada exitosamente"}


@router.put("/parada/{id_parada}/recoger", response_model=schemas.ParadaResponse)
def marcar_parada_como_recogida(
    id_parada: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    parada = db.query(models.Parada).join(models.Ruta).filter(models.Parada.id_parada == id_parada).first()

    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")

    if parada.ruta.id_conductor != conductor.id_conductor:
        raise HTTPException(status_code=403, detail="Esta parada no pertenece a tu ruta")

    if parada.ruta.estado != "activa":
        raise HTTPException(status_code=400, detail="La ruta no está activa")

    parada.recogido = True
    db.commit()
    db.refresh(parada)

    return parada


@router.put("/parada/{id_parada}/entregar", response_model=schemas.ParadaResponse)
def entregar_estudiante(
    id_parada: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Acceso restringido a conductores")

    parada = db.query(models.Parada).filter_by(id_parada=id_parada).first()
    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada")

    ruta = parada.ruta
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    if ruta.estado != "activa":
        raise HTTPException(status_code=400, detail="No se puede modificar una ruta que no está activa")

    parada.entregado = True
    db.commit()
    db.refresh(parada)

    # Verifica si esta parada es el destino final
    if parada.es_destino_final:
        ruta.estado = "finalizada"
        ruta.hora_termino = datetime.now().time()
        db.commit()
        db.refresh(ruta)
        return parada  # Devolvemos la parada actualizada

    return parada
