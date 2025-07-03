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

    nueva_ruta = models.RutaFija(
        id_conductor=ruta.id_conductor,
        nombre=ruta.nombre,
        descripcion=ruta.descripcion,
    )
    db.add(nueva_ruta)
    db.flush()  # Obtener id_ruta_fija antes de agregar paradas

    # Agregar paradas de estudiantes
    for parada in ruta.paradas_estudiantes:
        estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail=f"Estudiante con id {parada.id_estudiante} no encontrado")

        nueva_parada = models.ParadaRutaFija(
            id_ruta_fija=nueva_ruta.id_ruta_fija,
            id_estudiante=parada.id_estudiante,
            latitud=estudiante.lat_casa,
            longitud=estudiante.long_casa,
            orden=parada.orden,
            es_destino_final=False
        )
        db.add(nueva_parada)

    # Agregar parada final si se especificó
    parada_final = None
    if ruta.parada_final:
        orden_final = ruta.parada_final.orden or (len(ruta.paradas_estudiantes) + 1)
        parada_final = models.ParadaRutaFija(
            id_ruta_fija=nueva_ruta.id_ruta_fija,
            id_estudiante=None,
            latitud=ruta.parada_final.latitud,
            longitud=ruta.parada_final.longitud,
            orden=orden_final,
            es_destino_final=True
        )
        db.add(parada_final)

    db.commit()
    db.refresh(nueva_ruta)

    # Obtener paradas desde la base de datos para estructurar la respuesta
    paradas_db = (
        db.query(models.ParadaRutaFija)
        .filter_by(id_ruta_fija=nueva_ruta.id_ruta_fija)
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
        else:
            paradas_estudiantes_response.append(
                schemas.ParadaEstudianteRutaFijaResponse(
                    id_parada_ruta_fija=parada.id_parada_ruta_fija,
                    orden=parada.orden,
                    estudiante=schemas.EstudianteBasico.from_orm(parada.estudiante)
                )
            )

    return schemas.RutaFijaResponse(
        id_ruta_fija=nueva_ruta.id_ruta_fija,
        nombre=nueva_ruta.nombre,
        descripcion=nueva_ruta.descripcion,
        id_conductor=nueva_ruta.id_conductor,
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
            else:
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
                id_conductor=ruta.id_conductor,
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
        else:
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
        id_conductor=ruta.id_conductor,
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

    # Actualizar campos básicos
    if datos.nombre is not None:
        ruta.nombre = datos.nombre
    if datos.descripcion is not None:
        ruta.descripcion = datos.descripcion

    # Eliminar paradas antiguas
    db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).delete()

    orden_max = 0

    # Agregar paradas de estudiantes
    if datos.paradas_estudiantes:
        for parada in datos.paradas_estudiantes:
            estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
            if not estudiante:
                raise HTTPException(status_code=404, detail=f"Estudiante con id {parada.id_estudiante} no encontrado")

            orden = parada.orden if parada.orden and parada.orden > 0 else orden_max + 1

            parada_db = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=parada.id_estudiante,
                latitud=estudiante.lat_casa,
                longitud=estudiante.long_casa,
                orden=orden,
                es_destino_final=False
            )
            db.add(parada_db)
            orden_max = orden

    # Agregar parada final
    if datos.parada_final:
        orden_final = datos.parada_final.orden if datos.parada_final.orden and datos.parada_final.orden > 0 else orden_max + 1

        parada_final_db = models.ParadaRutaFija(
            id_ruta_fija=id_ruta_fija,
            id_estudiante=None,
            latitud=datos.parada_final.latitud,
            longitud=datos.parada_final.longitud,
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
        id_conductor=ruta.id_conductor,
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
    
