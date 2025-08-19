from fastapi import APIRouter, Depends, HTTPException ,Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin, verificar_tipo_usuario
from app import models, schemas
from typing import List
from datetime import date, datetime
from app.firebase import notificaciones

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
    
    
@router.get("/estudiantes", response_model=List[schemas.EstudianteResponse])
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

    estudiantes_response = [
        schemas.EstudianteResponse(
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
            id_conductor=e.id_conductor,
            id_usuario_conductor=e.conductor.id_usuario if e.conductor else None
        )
        for e in estudiantes
    ]

    return estudiantes_response


@router.get("/asistenciaEstudiantes", response_model=List[schemas.EstudianteConAsistenciaHoy])
def listar_estudiantes_con_asistencia_hoy(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")

    ruta_fija = db.query(models.RutaFija).filter_by(id_conductor=conductor.id_conductor).first()
    ruta_resumen = schemas.RutaResumen(
        id=ruta_fija.id_ruta_fija,
        nombre=ruta_fija.nombre
    ) if ruta_fija else None

    estudiantes = conductor.estudiantes
    resultado = []

    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante
        ).order_by(models.Asistencia.fecha.desc()).first()

        if asistencia:
            asistencia_schema = schemas.AsistenciaHoyResponse(
                fecha=asistencia.fecha,
                asiste=asistencia.asiste
            )
        else:
            # Asistencia implícita (por defecto asiste)
            asistencia_schema = schemas.AsistenciaHoyResponse(
                fecha=date.today(),
                asiste=True
            )

        resultado.append(schemas.EstudianteConAsistenciaHoy(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            curso=est.curso,
            colegio=est.colegio,
            asistencia=asistencia_schema,
            ruta=ruta_resumen
        ))

    return resultado

@router.get("/estudiantesenRutaActiva", response_model=List[schemas.EstudianteHoyConParada])
def listar_estudiantes_en_ruta_activa(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden acceder a esta información.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")

    hoy = date.today()
    ruta_activa = (
        db.query(models.Ruta)
        .filter_by(id_conductor=conductor.id_conductor, fecha=hoy, estado="activa")
        .first()
    )
    if not ruta_activa:
        raise HTTPException(status_code=404, detail="No hay ruta activa para hoy.")

    paradas = (
        db.query(models.Parada)
        .filter_by(id_ruta=ruta_activa.id_ruta)
        .order_by(models.Parada.orden)
        .all()
    )

    resultado = []

    for parada in paradas:
        if not parada.id_estudiante:
            continue  # Saltamos la parada final

        estudiante = parada.estudiante
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=estudiante.id_estudiante,
            fecha=hoy
        ).first()
        asistencia_schema = schemas.AsistenciaHoyResponse.from_orm(asistencia) if asistencia else None

        resultado.append(schemas.EstudianteHoyConParada(
            id_estudiante=estudiante.id_estudiante,
            nombre=estudiante.nombre,
            curso=estudiante.curso,
            colegio=estudiante.colegio,
            asistencia=asistencia_schema,
            recogido=parada.recogido,
            entregado=parada.entregado,
            orden=parada.orden
        ))

    return resultado

@router.get("/RutasFijas", response_model=List[schemas.RutaFijaResponse])
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
                tipo=ruta.tipo,
                id_usuario_conductor=usuario_actual.id_usuario,  # Aquí el cambio correcto
                paradas=paradas_estudiantes,
                parada_final=parada_final
            )
        )

    return resultado

@router.post("/GenerarRuta/{id_ruta_fija}", response_model=schemas.RutaConParadasResponse)
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

    tokens = set()

    for parada_fija in paradas_fijas:
        # Lógica de asistencia actualizada: solo se excluye si hay registro con asiste=False
        if parada_fija.id_estudiante and not parada_fija.es_destino_final:
            asistencia = db.query(models.Asistencia).filter_by(
                id_estudiante=parada_fija.id_estudiante
            ).order_by(models.Asistencia.fecha.desc()).first()

            if asistencia and asistencia.asiste is False:
                continue  # Se excluye si tiene asistencia explícitamente negativa

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

        if not parada_fija.es_destino_final and parada_fija.id_estudiante:
            estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada_fija.id_estudiante).first()
            if estudiante and estudiante.apoderado and estudiante.apoderado.usuario:
                token = estudiante.apoderado.usuario.token_firebase
                if isinstance(token, str) and token.strip():
                    tokens.add(token.strip())

    if tokens:
        try:
            print(f"[INFO] Enviando notificación de inicio a {len(tokens)} apoderados.")
            notificaciones.enviar_notificacion_inicio_ruta(
                titulo="Ruta iniciada",
                cuerpo="La ruta escolar del día ha comenzado.",
                tokens=list(tokens)
            )
            notificaciones.enviar_inicio_ruta(conductor.id_conductor)
        except Exception as e:
            print(f"Error al enviar notificación grupal: {e}")

    db.commit()
    db.refresh(nueva_ruta)

    paradas_ordenadas = sorted(nueva_ruta.paradas, key=lambda p: p.orden)
    parada_responses = []
    for parada in paradas_ordenadas:
        estudiante = parada.estudiante
        parada_responses.append(
            schemas.ParadaResponse(
                id_parada=parada.id_parada,
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
                    telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario,
                    id_usuario_conductor=estudiante.id_conductor
                ) if estudiante else None
            )
        )

    notificaciones.marcar_ruta_activa(conductor.id_conductor)
    return schemas.RutaConParadasResponse(
        id_ruta=nueva_ruta.id_ruta,
        fecha=nueva_ruta.fecha,
        estado=nueva_ruta.estado,
        hora_inicio=nueva_ruta.hora_inicio,
        id_acompanante=nueva_ruta.id_acompanante,
        paradas=parada_responses
    )

@router.put("/FinalizarRuta")
def finalizar_ruta(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ruta = db.query(models.Ruta).filter_by(id_conductor=conductor.id_conductor, estado="activa").first()
    if not ruta:
        raise HTTPException(status_code=404, detail="No hay ruta activa")

    ruta.estado = "finalizada"
    ruta.hora_termino = datetime.now().time()
    db.commit()

    notificaciones.eliminar_ubicacion_conductor(conductor.id_conductor)
    notificaciones.eliminar_ruta_activa(conductor.id_conductor)
    return {"mensaje": "Ruta finalizada correctamente"}

@router.put("/recogerEstudiante/{id_estudiante}", response_model=schemas.ParadaResponse)
def recoger_estudiante(
    id_estudiante: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="No autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ruta_activa = db.query(models.Ruta).filter_by(id_conductor=conductor.id_conductor, estado="activa").first()
    if not ruta_activa:
        raise HTTPException(status_code=404, detail="No tienes una ruta activa en curso")

    parada = db.query(models.Parada).filter_by(
        id_ruta=ruta_activa.id_ruta,
        id_estudiante=id_estudiante
    ).first()

    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada para este estudiante en la ruta activa")

    if parada.recogido:
        raise HTTPException(status_code=400, detail="Este estudiante ya fue recogido")

    # Marcar como recogido
    parada.recogido = True

    estudiante = parada.estudiante
    if estudiante and estudiante.apoderado:
        token_entry = db.query(models.TokenFirebase).filter_by(id_usuario=estudiante.apoderado.id_usuario).first()
        if token_entry and token_entry.token:
            notificaciones.enviar_notificacion(
                token=token_entry.token,
                titulo="Estudiante recogido",
                cuerpo=f"Tu hijo/a {estudiante.nombre} ha sido recogido por el conductor {usuario_actual.nombre}."
            )

    db.commit()
    db.refresh(parada)

    return schemas.ParadaResponse(
        id_parada=parada.id_parada,
        orden=parada.orden,
        latitud=parada.latitud,
        longitud=parada.longitud,
        recogido=parada.recogido,
        entregado=parada.entregado,
        estudiante=schemas.EstudianteResponse(
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
            telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario,
            id_usuario_conductor=estudiante.conductor.id_usuario if estudiante.conductor else None
        )
    )

@router.put("/RecalcularRutaActiva", response_model=schemas.RutaConParadasResponse)
def recalcular_ruta_dia(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Solo los conductores pueden recalcular rutas")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    hoy = date.today()
    ruta = db.query(models.Ruta).filter_by(id_conductor=conductor.id_conductor, fecha=hoy, estado="activa").first()
    if not ruta:
        raise HTTPException(status_code=404, detail="No hay ruta activa")

    db.query(models.Parada).filter_by(id_ruta=ruta.id_ruta).delete()

    ruta_fija = db.query(models.RutaFija).filter_by(id_conductor=conductor.id_conductor).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    paradas_fijas = db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=ruta_fija.id_ruta_fija).order_by(models.ParadaRutaFija.orden).all()

    for parada_fija in paradas_fijas:
        nueva_parada = models.Parada(
            id_ruta=ruta.id_ruta,
            orden=parada_fija.orden,
            latitud=parada_fija.latitud,
            longitud=parada_fija.longitud,
            recogido=False,
            entregado=False,
            id_estudiante=parada_fija.id_estudiante if not parada_fija.es_destino_final else None
        )
        db.add(nueva_parada)

    db.commit()
    db.refresh(ruta)

    paradas_actualizadas = db.query(models.Parada).filter_by(id_ruta=ruta.id_ruta).order_by(models.Parada.orden).all()

    parada_responses = []
    for parada in paradas_actualizadas:
        estudiante = parada.estudiante
        parada_responses.append(
            schemas.ParadaResponse(
                id_parada=parada.id_parada,
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud,
                recogido=parada.recogido,
                entregado=parada.entregado,
                estudiante=schemas.EstudianteSimple.from_orm(estudiante) if estudiante else None
            )
        )

    return schemas.RutaConParadasResponse(
        id_ruta=ruta.id_ruta,
        fecha=ruta.fecha,
        estado=ruta.estado,
        hora_inicio=ruta.hora_inicio,
        id_acompanante=ruta.id_acompanante,
        paradas=parada_responses
    )

@router.get("/parada/{id_parada}", response_model=schemas.ParadaResponse)
def obtener_parada_por_id(
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

    estudiante = parada.estudiante

    return schemas.ParadaResponse(
        id_parada=parada.id_parada,
        orden=parada.orden,
        latitud=parada.latitud,
        longitud=parada.longitud,
        recogido=parada.recogido,
        entregado=parada.entregado,
        estudiante=schemas.EstudianteResponse(
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
            telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario,
            id_usuario_conductor=estudiante.conductor.id_usuario if estudiante.conductor else None
        )
    )

@router.put("/entregarEstudiante/{id_estudiante}", response_model=schemas.ParadaResponse)
def entregar_estudiante(
    id_estudiante: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Acceso restringido a conductores")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    ruta_activa = db.query(models.Ruta).filter_by(id_conductor=conductor.id_conductor, estado="activa").first()
    if not ruta_activa:
        raise HTTPException(status_code=404, detail="No tienes una ruta activa")

    parada = db.query(models.Parada).filter_by(
        id_ruta=ruta_activa.id_ruta,
        id_estudiante=id_estudiante
    ).first()

    if not parada:
        raise HTTPException(status_code=404, detail="Parada no encontrada para este estudiante en la ruta activa")

    if parada.entregado:
        raise HTTPException(status_code=400, detail="Este estudiante ya fue entregado")

    # Marcar como entregado
    parada.entregado = True

    # Enviar notificación al apoderado
    estudiante = parada.estudiante
    if estudiante and estudiante.apoderado:
        token_entry = db.query(models.TokenFirebase).filter_by(id_usuario=estudiante.apoderado.id_usuario).first()
        if token_entry and token_entry.token:
            notificaciones.enviar_notificacion(
                token=token_entry.token,
                titulo="Estudiante entregado",
                cuerpo=f"Tu hijo/a {estudiante.nombre} ha sido entregado por el conductor {usuario_actual.nombre}."
            )

    # Finalizar ruta si es la última parada
    if parada.es_destino_final:
        ruta_activa.estado = "finalizada"
        ruta_activa.hora_termino = datetime.now().time()
        db.commit()
        db.refresh(ruta_activa)
        try:
            notificaciones.enviar_finalizacion_ruta(ruta_activa.id_conductor)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al notificar finalización: {str(e)}")

    db.commit()
    db.refresh(parada)

    return schemas.ParadaResponse(
        id_parada=parada.id_parada,
        orden=parada.orden,
        latitud=parada.latitud,
        longitud=parada.longitud,
        recogido=parada.recogido,
        entregado=parada.entregado,
        estudiante=schemas.EstudianteResponse(
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
            telefono_apoderado_secundario=estudiante.telefono_apoderado_secundario,
            id_usuario_conductor=estudiante.conductor.id_usuario if estudiante.conductor else None
        )
    )

@router.put("/ubicacion")
def actualizar_ubicacion_conductor(
    latitud: float = Query(..., description="Latitud actual del conductor"),
    longitud: float = Query(..., description="Longitud actual del conductor"),
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario != "conductor":
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    conductor = db.query(models.Conductor).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    try:
        # Actualizar en Firebase
        notificaciones.enviar_ubicacion_conductor(conductor.id_conductor, latitud, longitud)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar en Firebase: {str(e)}")

    # Guardar también en la base de datos
    ubicacion_existente = db.query(models.UbicacionConductor).filter_by(id_conductor=conductor.id_conductor).first()
    timestamp_actual = datetime.now()

    if ubicacion_existente:
        ubicacion_existente.latitud = latitud
        ubicacion_existente.longitud = longitud
        ubicacion_existente.timestamp = timestamp_actual
    else:
        nueva_ubicacion = models.UbicacionConductor(
            id_conductor=conductor.id_conductor,
            latitud=latitud,
            longitud=longitud,
            timestamp=timestamp_actual
        )
        db.add(nueva_ubicacion)

    db.commit()

    return {"mensaje": "Ubicación actualizada en base de datos y Firebase"}
