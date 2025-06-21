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

'''
@router.put("/{id_ruta_fija}", response_model=schemas.RutaFijaResponse)
def actualizar_ruta_fija(
    id_ruta_fija: int,
    datos: schemas.RutaFijaUpdate,
    db: Session = Depends(get_db)
):
    ruta = db.query(models.RutaFija).filter(models.RutaFija.id_ruta_fija == id_ruta_fija).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    # Actualizar nombre y descripción si se proporcionan
    if datos.nombre is not None:
        ruta.nombre = datos.nombre
    if datos.descripcion is not None:
        ruta.descripcion = datos.descripcion

    # Si se proporciona una lista de paradas actualizamos
    if datos.paradas is not None:
        paradas_existentes = {p.id_estudiante: p for p in ruta.paradas}
        nuevos_ids = set()

        for parada in datos.paradas:
            nuevos_ids.add(parada.id_estudiante)
            if parada.id_estudiante in paradas_existentes:
                # Actualizar orden si cambió
                parada_existente = paradas_existentes[parada.id_estudiante]
                parada_existente.orden = parada.orden
            else:
                # Agregar nueva parada
                nueva_parada = models.ParadaRutaFija(
                    id_ruta_fija=id_ruta_fija,
                    id_estudiante=parada.id_estudiante,
                    orden=parada.orden
                )
                db.add(nueva_parada)

        # Eliminar paradas que ya no están
        for estudiante_id in list(paradas_existentes):
            if estudiante_id not in nuevos_ids:
                db.delete(paradas_existentes[estudiante_id])

    db.commit()
    db.refresh(ruta)
    return ruta
    

'''

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


@router.post("/rutas-dia-para-Conductor/generar/{id_ruta_fija}", response_model=schemas.RutaResponse)
def generar_ruta_dia(
    id_ruta_fija: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(verificar_admin)
):
    ruta_fija = db.query(models.RutaFija).filter_by(id_ruta_fija=id_ruta_fija).first()
    if not ruta_fija:
        raise HTTPException(status_code=404, detail="Ruta fija no encontrada")

    hoy = date.today()

    asistencias_false = db.query(models.Asistencia).filter_by(fecha=hoy, asiste=False).all()
    ids_no_asisten = {a.id_estudiante for a in asistencias_false}

    paradas_presentes = [
        parada for parada in ruta_fija.paradas if parada.id_estudiante not in ids_no_asisten
    ]

    if not paradas_presentes:
        raise HTTPException(status_code=400, detail="No hay estudiantes presentes para esta ruta hoy.")

    nueva_ruta = models.Ruta(
        id_conductor=ruta_fija.id_conductor,
        fecha=hoy,
        estado="activa",
        hora_inicio=datetime.now().time()  # Asegúrate de tener este campo en el modelo si lo necesitas
    )
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)

    estudiantes_respuesta = []

    for parada in paradas_presentes:
        estudiante = db.query(models.Estudiante).filter_by(id_estudiante=parada.id_estudiante).first()

        nueva_parada = models.Parada(
            id_ruta=nueva_ruta.id_ruta,
            id_estudiante=estudiante.id_estudiante,
            orden=parada.orden,
            latitud=estudiante.latitud,
            longitud=estudiante.longitud
        )
        db.add(nueva_parada)
        estudiantes_respuesta.append(estudiante)

    db.commit()
    db.refresh(nueva_ruta)

    return {
        "id_ruta": nueva_ruta.id_ruta,
        "id_conductor": nueva_ruta.id_conductor,
        "id_acompanante": nueva_ruta.id_acompanante,
        "fecha": nueva_ruta.fecha,
        "estado": nueva_ruta.estado,
        "hora_inicio": nueva_ruta.hora_inicio,
        "estudiantes": estudiantes_respuesta
    }
