from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user  # Corrección aquí

router = APIRouter(prefix="/rutas", tags=["Rutas"])


@router.get("/conductor/{id_usuario}/ruta-diaria", response_model=list[schemas.EstudianteResponse])
def obtener_ruta_diaria(
    id_usuario: int,
    fecha: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario_token != "conductor" or usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta ruta")

    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    estudiantes_presentes = []
    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=fecha,
            asiste=True
        ).first()
        if asistencia:
            estudiantes_presentes.append(est)

    estudiantes_ordenados = sorted(estudiantes_presentes, key=lambda e: e.hora_entrada)

    return estudiantes_ordenados


@router.get("/conductor/{id_usuario}/puntos-mapa")
def obtener_puntos_ruta_para_mapa(
    id_usuario: int,
    fecha: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user)
):
    if usuario_actual.tipo_usuario_token != "conductor" or usuario_actual.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta ruta")

    conductor = db.query(models.Conductor).filter_by(id_usuario=id_usuario).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    estudiantes = db.query(models.Estudiante).filter_by(id_conductor=conductor.id_conductor).all()

    presentes = []
    for est in estudiantes:
        asistencia = db.query(models.Asistencia).filter_by(
            id_estudiante=est.id_estudiante,
            fecha=fecha,
            asiste=True
        ).first()
        if asistencia:
            presentes.append(est)

    presentes_ordenados = sorted(presentes, key=lambda e: e.hora_entrada)

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
