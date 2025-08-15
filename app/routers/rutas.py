from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, verificar_admin 
from datetime import datetime
from sqlalchemy import func

router = APIRouter(prefix="/Rutas", tags=["Rutas Fijas"])
@router.post("/RutaFija", response_model=schemas.RutaFijaResponse)
def crear_ruta_fija(
    ruta: schemas.RutaFijaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(verificar_admin)
):
    if usuario_actual.tipo_usuario != "administrador":
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear rutas fijas.")

    conductor = db.query(models.Conductor).filter_by(id_usuario=ruta.id_usuario_conductor).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado con ese ID de usuario.")

    # ----- Crear Ruta Fija IDA -----
    ruta_ida = models.RutaFija(
        id_conductor=conductor.id_conductor,
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        tipo="ida"
    )
    db.add(ruta_ida)
    db.flush()

    paradas_ida = []
    for parada in ruta.paradas_estudiantes:
        estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail=f"Estudiante con id {parada.id_estudiante} no encontrado")

        parada_ida = models.ParadaRutaFija(
            id_ruta_fija=ruta_ida.id_ruta_fija,
            id_estudiante=parada.id_estudiante,
            latitud=estudiante.lat_casa,
            longitud=estudiante.long_casa,
            orden=parada.orden,
            es_destino_final=False
        )
        db.add(parada_ida)
        paradas_ida.append((parada_ida, estudiante))

    parada_final_ida = None
    if ruta.parada_final:
        orden_final = ruta.parada_final.orden or (len(ruta.paradas_estudiantes) + 1)
        parada_final_ida = models.ParadaRutaFija(
            id_ruta_fija=ruta_ida.id_ruta_fija,
            id_estudiante=None,
            latitud=ruta.parada_final.latitud,
            longitud=ruta.parada_final.longitud,
            orden=orden_final,
            es_destino_final=True
        )
        db.add(parada_final_ida)

    # ----- Crear Ruta Fija VUELTA -----
    nombre_vuelta = f"{ruta.nombre} - Vuelta"
    ruta_vuelta = models.RutaFija(
        id_conductor=conductor.id_conductor,
        nombre=nombre_vuelta,
        descripcion=f"Ruta de retorno de: {ruta.nombre}",
        tipo="vuelta"
    )
    db.add(ruta_vuelta)
    db.flush()

    # Paradas hacia casa en orden inverso (sin colegio)
    paradas_reversas = list(reversed(paradas_ida))
    total = len(paradas_reversas)

    orden = 1
    for idx, (parada_ida, estudiante) in enumerate(paradas_reversas):
        parada_vuelta = models.ParadaRutaFija(
            id_ruta_fija=ruta_vuelta.id_ruta_fija,
            id_estudiante=estudiante.id_estudiante,
            latitud=estudiante.lat_casa,
            longitud=estudiante.long_casa,
            orden=orden,
            es_destino_final=False
        )
        db.add(parada_vuelta)
        orden += 1

    if paradas_reversas:
        estudiante_final = paradas_reversas[-1][1]
        parada_final_vuelta = models.ParadaRutaFija(
            id_ruta_fija=ruta_vuelta.id_ruta_fija,
            id_estudiante=estudiante_final.id_estudiante,
            latitud=estudiante_final.lat_casa,
            longitud=estudiante_final.long_casa,
            orden=orden,
            es_destino_final=True
        )
        db.add(parada_final_vuelta)

    db.commit()
    db.refresh(ruta_ida)

    paradas_db = (
        db.query(models.ParadaRutaFija)
        .filter_by(id_ruta_fija=ruta_ida.id_ruta_fija)
        .order_by(models.ParadaRutaFija.orden)
        .all()
    )

    paradas_estudiantes_response = []
    parada_final_response = None
    for parada in paradas_db:
        if parada.es_destino_final:
            parada_final_response = schemas.ParadaFinalRutaFijaResponse(
                id_parada_ruta_fija=parada.id_parada_ruta_fija,
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud
            )
        elif parada.estudiante:
            paradas_estudiantes_response.append(
                schemas.ParadaEstudianteRutaFijaResponse(
                    id_parada_ruta_fija=parada.id_parada_ruta_fija,
                    orden=parada.orden,
                    estudiante=schemas.EstudianteBasico.from_orm(parada.estudiante)
                )
            )

    return schemas.RutaFijaResponse(
        id_ruta_fija=ruta_ida.id_ruta_fija,
        nombre=ruta_ida.nombre,
        descripcion=ruta_ida.descripcion,
        tipo=ruta_ida.tipo,
        id_usuario_conductor=conductor.id_usuario,
        paradas=paradas_estudiantes_response,
        parada_final=parada_final_response
    )


@router.get("/RutasFijas", response_model=list[schemas.RutaFijaResponse])
def obtener_rutas_fijas_completas(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    rutas = db.query(models.RutaFija).all()
    resultados = []

    for ruta in rutas:
        # Obtener el usuario asociado al conductor
        conductor = db.query(models.Conductor).filter_by(id_conductor=ruta.id_conductor).first()
        id_usuario_conductor = conductor.id_usuario if conductor else None

        paradas_db = (
            db.query(models.ParadaRutaFija)
            .filter_by(id_ruta_fija=ruta.id_ruta_fija)
            .order_by(models.ParadaRutaFija.orden)
            .all()
        )

        paradas_estudiantes = []
        parada_final = None

        for parada in paradas_db:
            if parada.es_destino_final:
                parada_final = schemas.ParadaFinalRutaFijaResponse(
                id_parada_ruta_fija=parada.id_parada_ruta_fija,
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud
        )
            elif parada.estudiante:
                paradas_estudiantes.append(
                    schemas.ParadaEstudianteRutaFijaResponse(
                        id_parada_ruta_fija=parada.id_parada_ruta_fija,
                        orden=parada.orden,
                        estudiante=schemas.EstudianteBasico.from_orm(parada.estudiante)
            )
        )

        resultados.append(
            schemas.RutaFijaResponse(
                id_ruta_fija=ruta.id_ruta_fija,
                nombre=ruta.nombre,
                descripcion=ruta.descripcion,
                tipo=ruta.tipo,
                id_usuario_conductor=id_usuario_conductor,
                paradas=paradas_estudiantes,
                parada_final=parada_final
            )
        )

    return resultados


@router.get("/RutaFija/{id_ruta_fija}", response_model=schemas.RutaFijaResponse)
def obtener_ruta_fija_por_id(
    id_ruta_fija: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    ruta = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    # Obtener id_usuario del conductor
    conductor = db.query(models.Conductor).filter_by(id_conductor=ruta.id_conductor).first()
    id_usuario_conductor = conductor.id_usuario if conductor else None

    paradas_db = (
        db.query(models.ParadaRutaFija)
        .filter_by(id_ruta_fija=id_ruta_fija)
        .order_by(models.ParadaRutaFija.orden)
        .all()
    )

    paradas_estudiantes = []
    parada_final = None

    for parada in paradas_db:
        if parada.es_destino_final:
            parada_final = schemas.ParadaFinalRutaFijaResponse(
            id_parada_ruta_fija=parada.id_parada_ruta_fija,
            orden=parada.orden,
            latitud=parada.latitud,
            longitud=parada.longitud
        )
        elif parada.estudiante:
            paradas_estudiantes.append(
                schemas.ParadaEstudianteRutaFijaResponse(
                    id_parada_ruta_fija=parada.id_parada_ruta_fija,
                    orden=parada.orden,
                    estudiante=schemas.EstudianteBasico.from_orm(parada.estudiante)
            )
        )

    return schemas.RutaFijaResponse(
        id_ruta_fija=ruta.id_ruta_fija,
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        id_usuario_conductor=id_usuario_conductor,
        tipo=ruta.tipo,
        paradas=paradas_estudiantes,
        parada_final=parada_final
    )


@router.put("/RutaFija/{id_ruta_fija}", response_model=schemas.RutaFijaResponse)
def editar_ruta_fija(
    id_ruta_fija: int,
    datos: schemas.RutaFijaUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    ruta = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    tipo_ruta = ruta.tipo  # importante para decidir comportamiento

    if datos.nombre is not None:
        ruta.nombre = datos.nombre
    if datos.descripcion is not None:
        ruta.descripcion = datos.descripcion

    # Conductor
    if datos.id_usuario_conductor is not None:
        conductor = db.query(models.Conductor).filter_by(id_usuario=datos.id_usuario_conductor).first()
        if not conductor:
            raise HTTPException(status_code=404, detail="Conductor no encontrado")
        ruta.id_conductor = conductor.id_conductor
        conductor_usuario_id = datos.id_usuario_conductor
    else:
        conductor = db.query(models.Conductor).filter_by(id_conductor=ruta.id_conductor).first()
        conductor_usuario_id = conductor.id_usuario if conductor else None

    # Eliminar paradas anteriores
    db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).delete()

    estudiantes_ordenados = []

    # Agregar nuevas paradas de estudiantes
    if datos.paradas_estudiantes:
        for parada in datos.paradas_estudiantes:
            estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
            if not estudiante:
                raise HTTPException(status_code=404, detail=f"Estudiante con id {parada.id_estudiante} no encontrado")

            orden = parada.orden if parada.orden and parada.orden > 0 else len(estudiantes_ordenados) + 1

            parada_db = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=estudiante.id_estudiante,
                latitud=estudiante.lat_casa,
                longitud=estudiante.long_casa,
                orden=orden,
                es_destino_final=False
            )
            db.add(parada_db)
            estudiantes_ordenados.append((orden, estudiante))

    # Parada final
    if tipo_ruta == "ida":
        if datos.parada_final:
            orden_final = datos.parada_final.orden or (len(estudiantes_ordenados) + 1)
            parada_final_db = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=None,
                latitud=datos.parada_final.latitud,
                longitud=datos.parada_final.longitud,
                orden=orden_final,
                es_destino_final=True
            )
            db.add(parada_final_db)

    elif tipo_ruta == "vuelta":
        if estudiantes_ordenados:
            # Ordenar por orden asignado
            estudiante_final = sorted(estudiantes_ordenados, key=lambda x: x[0])[-1][1]
            orden_final = sorted(estudiantes_ordenados, key=lambda x: x[0])[-1][0] + 1

            parada_final_db = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=estudiante_final.id_estudiante,
                latitud=estudiante_final.lat_casa,
                longitud=estudiante_final.long_casa,
                orden=orden_final,
                es_destino_final=True
            )
            db.add(parada_final_db)

    db.commit()
    db.refresh(ruta)

    # Armar respuesta
    paradas = (
        db.query(models.ParadaRutaFija)
        .filter_by(id_ruta_fija=id_ruta_fija)
        .order_by(models.ParadaRutaFija.orden)
        .all()
    )

    paradas_estudiantes = []
    parada_final = None

    for parada in paradas:
        if parada.es_destino_final:
            parada_final = schemas.ParadaFinalRutaFijaResponse(
                id_parada_ruta_fija=parada.id_parada_ruta_fija,
                orden=parada.orden,
                latitud=parada.latitud,
                longitud=parada.longitud
            )
        else:
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

    return schemas.RutaFijaResponse(
        id_ruta_fija=ruta.id_ruta_fija,
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
        tipo=ruta.tipo,
        id_usuario_conductor=conductor_usuario_id,
        paradas=paradas_estudiantes,
        parada_final=parada_final
    )



@router.delete("/RutaFija/{id_ruta_fija}", status_code=204)
def eliminar_ruta_fija(
    id_ruta_fija: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    ruta_fija = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()

    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    # Eliminar primero las paradas asociadas
    db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).delete()

    # Luego eliminar la ruta fija
    db.delete(ruta_fija)
    db.commit()
    
