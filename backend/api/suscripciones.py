"""
Endpoints de suscripciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
from backend.database import get_db
from backend.api import schemas
from backend.models.usuario import Usuario
from backend.models.suscripcion import Suscripcion
from backend.services.email_service import EmailService
from backend.services.calendar_service import CalendarService
from loguru import logger

router = APIRouter(prefix="/api/suscripcion", tags=["suscripciones"])


@router.post("/crear", response_model=schemas.SuscripcionResponse, status_code=status.HTTP_201_CREATED)
async def crear_suscripcion(
    suscripcion_data: schemas.SuscripcionCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva suscripción"""
    try:
        # Verificar si el usuario ya existe
        usuario = db.query(Usuario).filter(Usuario.email == suscripcion_data.email).first()
        
        if not usuario:
            # Crear nuevo usuario
            token_confirmacion = secrets.token_urlsafe(32)
            usuario = Usuario(
                email=suscripcion_data.email,
                nombre=suscripcion_data.nombre or suscripcion_data.email.split('@')[0],
                token_confirmacion=token_confirmacion,
                confirmado=False
            )
            db.add(usuario)
            db.flush()
            
            # Enviar email de confirmación
            email_service = EmailService()
            calendar_service = CalendarService()
            
            email_service.send_confirmacion_suscripcion(
                to_email=usuario.email,
                nombre_usuario=usuario.nombre,
                token_confirmacion=token_confirmacion,
                calendar_url=calendar_service.get_calendar_url()
            )
        
        # Verificar si ya tiene suscripción activa
        suscripcion_existente = db.query(Suscripcion).filter(
            Suscripcion.usuario_id == usuario.id,
            Suscripcion.activa == True
        ).first()
        
        if suscripcion_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una suscripción activa para este email"
            )
        
        # Crear suscripción
        nueva_suscripcion = Suscripcion(
            usuario_id=usuario.id,
            regiones=suscripcion_data.regiones,
            areas_tematicas=suscripcion_data.areas_tematicas,
            presupuesto_min=suscripcion_data.presupuesto_min,
            presupuesto_max=suscripcion_data.presupuesto_max,
            tipos_beneficiario=suscripcion_data.tipos_beneficiario,
            notificar_email=True,
            activa=True
        )
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        
        logger.info(f"✓ Nueva suscripción creada para {usuario.email}")
        
        calendar_service = CalendarService()
        
        return schemas.SuscripcionResponse(
            message="Suscripción creada exitosamente. Revisa tu email para confirmar.",
            suscripcion_id=nueva_suscripcion.id,
            calendar_url=calendar_service.get_calendar_url(),
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear suscripción: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear suscripción: {str(e)}"
        )


@router.get("/{email}", response_model=schemas.Suscripcion)
async def obtener_suscripcion(email: str, db: Session = Depends(get_db)):
    """Obtener suscripción por email"""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    suscripcion = db.query(Suscripcion).filter(
        Suscripcion.usuario_id == usuario.id,
        Suscripcion.activa == True
    ).first()
    
    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró suscripción activa"
        )
    
    return suscripcion


@router.put("/{suscripcion_id}", response_model=schemas.MessageResponse)
async def actualizar_suscripcion(
    suscripcion_id: int,
    suscripcion_data: schemas.SuscripcionUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar filtros de suscripción"""
    suscripcion = db.query(Suscripcion).filter(Suscripcion.id == suscripcion_id).first()
    
    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscripción no encontrada"
        )
    
    # Actualizar campos
    for field, value in suscripcion_data.dict(exclude_unset=True).items():
        setattr(suscripcion, field, value)
    
    db.commit()
    logger.info(f"✓ Suscripción {suscripcion_id} actualizada")
    
    return schemas.MessageResponse(
        message="Suscripción actualizada exitosamente",
        success=True
    )


@router.delete("/{suscripcion_id}", response_model=schemas.MessageResponse)
async def cancelar_suscripcion(suscripcion_id: int, db: Session = Depends(get_db)):
    """Cancelar suscripción"""
    suscripcion = db.query(Suscripcion).filter(Suscripcion.id == suscripcion_id).first()
    
    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suscripción no encontrada"
        )
    
    suscripcion.activa = False
    db.commit()
    
    logger.info(f"✓ Suscripción {suscripcion_id} cancelada")
    
    return schemas.MessageResponse(
        message="Suscripción cancelada exitosamente",
        success=True
    )


@router.post("/confirmar", response_model=schemas.MessageResponse)
async def confirmar_suscripcion(token: str, db: Session = Depends(get_db)):
    """Confirmar suscripción con token"""
    usuario = db.query(Usuario).filter(Usuario.token_confirmacion == token).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token inválido"
        )
    
    usuario.confirmado = True
    usuario.token_confirmacion = None
    db.commit()
    
    logger.info(f"✓ Usuario {usuario.email} confirmado")
    
    return schemas.MessageResponse(
        message="Suscripción confirmada exitosamente",
        success=True
    )
