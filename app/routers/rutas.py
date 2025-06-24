from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, verificar_admin 
from datetime import datetime
from sqlalchemy import func

router = APIRouter(prefix="/rutas-fijas", tags=["Rutas Fijas"])
@router.post("/ruta-fija", response_model=schemas.RutaFijaResponse)
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
    db.flush()  # para obtener id_ruta_fija

    orden_max = 0

    # Agregar paradas de estudiantes
    for parada in ruta.paradas_estudiantes:
        estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
        if not estudiante:
            raise HTTPException(status_code=404, detail=f"Estudiante con ID {parada.id_estudiante} no encontrado")

        parada_fija = models.ParadaRutaFija(
            id_ruta_fija=nueva_ruta.id_ruta_fija,
            id_estudiante=estudiante.id_estudiante,
            latitud=estudiante.lat_casa,
            longitud=estudiante.long_casa,
            orden=parada.orden,
            es_destino_final=False
        )
        db.add(parada_fija)
        orden_max = max(orden_max, parada.orden)

    # Agregar parada final si viene
    if ruta.parada_final:
        parada_final = models.ParadaRutaFija(
            id_ruta_fija=nueva_ruta.id_ruta_fija,
            id_estudiante=None,
            latitud=ruta.parada_final.latitud,
            longitud=ruta.parada_final.longitud,
            orden=ruta.parada_final.orden or (orden_max + 1),
            es_destino_final=True
        )
        db.add(parada_final)

    db.commit()
    db.refresh(nueva_ruta)
    return nueva_ruta

# Obtener todas las rutas fijas de un conductor
@router.get("/conductor/{id_conductor}", response_model=list[schemas.RutaFijaResponse])
def obtener_rutas_fijas_conductor(
    id_conductor: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    rutas = db.query(models.RutaFija).filter_by(id_conductor=id_conductor).all()
    return rutas


@router.put("/rutas-fijas/{id_ruta_fija}", response_model=schemas.RutaFijaResponse)
def editar_ruta_fija(
    id_ruta_fija: int,
    datos: schemas.RutaFijaUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    ruta = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    if datos.nombre:
        ruta.nombre = datos.nombre
    if datos.descripcion is not None:
        ruta.descripcion = datos.descripcion

    if datos.paradas_estudiantes is not None or datos.parada_final is not None:
        # Eliminar paradas anteriores
        db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).delete()

        orden_actual = 1

        # Paradas de estudiantes
        if datos.paradas_estudiantes:
            for parada in datos.paradas_estudiantes:
                estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()
                if not estudiante:
                    raise HTTPException(status_code=404, detail=f"Estudiante con id {parada.id_estudiante} no encontrado")

                nueva_parada = models.ParadaRutaFija(
                    id_ruta_fija=id_ruta_fija,
                    id_estudiante=parada.id_estudiante,
                    latitud=estudiante.lat_casa,
                    longitud=estudiante.long_casa,
                    orden=orden_actual,
                    es_destino_final=False
                )
                db.add(nueva_parada)
                orden_actual += 1

        # Parada final
        if datos.parada_final:
            nueva_parada_final = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=None,
                latitud=datos.parada_final.latitud,
                longitud=datos.parada_final.longitud,
                orden=orden_actual,
                es_destino_final=True
            )
            db.add(nueva_parada_final)

    db.commit()
    db.refresh(ruta)

    return ruta


@router.delete("/rutas-fijas/{id_ruta_fija}", status_code=204)
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
    
@router.get("/rutas-fijas", response_model=list[schemas.RutaFijaResponse])
def obtener_rutas_fijas_completas(db: Session = Depends(get_db), _: models.Usuario = Depends(verificar_admin)):
    rutas = db.query(models.RutaFija).all()

    resultados = []
    for ruta in rutas:
        paradas = (
            db.query(models.ParadaRutaFija)
            .filter_by(id_ruta_fija=ruta.id_ruta_fija)
            .order_by(models.ParadaRutaFija.orden)
            .all()
        )

        parada_respuestas = [
        schemas.ParadaRutaFijaResponse(
        id_parada_ruta_fija=parada.id_parada_ruta_fija,
        orden=parada.orden,
        estudiante=schemas.EstudianteBasico(
            id_estudiante=parada.estudiante.id_estudiante,
            nombre=parada.estudiante.nombre
        )
    ) for parada in paradas
]


        resultados.append(
            schemas.RutaFijaResponse(
                id_ruta_fija=ruta.id_ruta_fija,
                nombre=ruta.nombre,
                id_conductor=ruta.id_conductor,
                paradas=parada_respuestas
            )
        )

    return resultados


@router.post("/ruta-fija/{id_ruta_fija}/agregar-parada-final")
def agregar_parada_final_ruta_fija(
    id_ruta_fija: int,
    datos: schemas.ParadaFinalRutaFijaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(verificar_admin)
):
    # Verifica que la ruta fija exista
    ruta_fija = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    # Verifica que no haya ya una parada final
    parada_existente = db.query(models.ParadaRutaFija).filter_by(
        id_ruta_fija=id_ruta_fija,
        es_destino_final=True
    ).first()
    if parada_existente:
        raise HTTPException(status_code=400, detail="La ruta fija ya tiene una parada final asignada")

    # Determina el orden (última parada + 1)
    ultimo_orden = db.query(func.max(models.ParadaRutaFija.orden)).filter_by(
        id_ruta_fija=id_ruta_fija).scalar()
    nuevo_orden = (ultimo_orden or 0) + 1

    # Crear nueva parada
    nueva_parada = models.ParadaRutaFija(
        id_ruta_fija=id_ruta_fija,
        id_estudiante=None,  # sin estudiante
        latitud=datos.latitud,
        longitud=datos.longitud,
        orden=nuevo_orden,
        es_destino_final=True
    )
    db.add(nueva_parada)
    db.commit()

    return {"mensaje": "Parada final agregada correctamente a la ruta fija"}
