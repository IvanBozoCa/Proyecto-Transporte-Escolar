from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, verificar_admin 
from datetime import datetime

router = APIRouter(prefix="/rutas-fijas", tags=["Rutas Fijas"])
@router.post("/rutas-fijas/", response_model=schemas.RutaFijaResponse)
def crear_ruta_fija(
    ruta_data: schemas.RutaFijaCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    nueva_ruta = models.RutaFija(
        id_conductor=ruta_data.id_conductor,
        nombre=ruta_data.nombre
    )
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    for parada in ruta_data.paradas:
        nueva_parada = models.ParadaRutaFija(
            id_ruta_fija=nueva_ruta.id_ruta_fija,
            id_estudiante=parada.id_estudiante,
            orden=parada.orden
        )
        db.add(nueva_parada)

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

    if datos.paradas is not None:
        # Eliminar paradas anteriores
        db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).delete()
        # Agregar nuevas paradas
        for parada in datos.paradas:
            nueva_parada = models.ParadaRutaFija(
                id_ruta_fija=id_ruta_fija,
                id_estudiante=parada.id_estudiante,
                orden=parada.orden
            )
            db.add(nueva_parada)

    db.commit()
    db.refresh(ruta)

    paradas_actualizadas = db.query(models.ParadaRutaFija).filter_by(id_ruta_fija=id_ruta_fija).order_by(models.ParadaRutaFija.orden).all()

    return schemas.RutaFijaResponse(
        id_ruta_fija=ruta.id_ruta_fija,
        nombre=ruta.nombre,
        id_conductor=ruta.id_conductor,
        paradas=[
            schemas.ParadaRutaFijaResponse(
                id_estudiante=parada.id_estudiante,
                nombre_estudiante=parada.estudiante.nombre,
                orden=parada.orden
            ) for parada in paradas_actualizadas
        ]
    )


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


