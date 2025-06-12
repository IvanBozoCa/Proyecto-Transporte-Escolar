from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Conductor
from app.auth import get_current_user, verificar_admin
from app import models, schemas
from typing import List

router = APIRouter(
    prefix="/apoderado",
    tags=["Apoderado"]
)

@router.get("/mis-estudiantes", response_model=List[schemas.EstudianteConConductor])
def obtener_mis_estudiantes(
    usuario_actual: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario sea apoderado
    if usuario_actual.tipo_usuario != "apoderado":
        raise HTTPException(status_code=403, detail="Solo los apoderados pueden acceder a esta información.")

    apoderado = db.query(models.Apoderado).filter_by(id_usuario=usuario_actual.id_usuario).first()
    if not apoderado:
        raise HTTPException(status_code=404, detail="No se encontró un apoderado vinculado a este usuario.")

    estudiantes = db.query(models.Estudiante).filter_by(id_apoderado=apoderado.id_apoderado).all()

    resultado = []
    for est in estudiantes:
        nombre_conductor = None
        if est.conductor and est.conductor.usuario:
            nombre_conductor = est.conductor.usuario.nombre

        resultado.append(schemas.EstudianteConConductor(
            id_estudiante=est.id_estudiante,
            nombre=est.nombre,
            edad=est.edad,
            direccion=est.direccion,
            curso=est.curso,
            colegio=est.colegio,
            nombre_conductor=nombre_conductor
        ))

    return resultado
