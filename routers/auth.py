from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from database import get_db
import models 
import schemas 
from security import generar_hash_password, verificar_password, crear_token_acceso


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=schemas.UsuarioResponse)
def registrar_nuevo_usuario(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)): 
    try: 
        usuario_existente = db.query(models.UsuariosBD).filter(models.UsuariosBD.email == datos.email).first()

        if usuario_existente:
            raise HTTPException(status_code=400, detail="El correo electronico ya está en uso.")
        
        nueva_empresa = models.EmpresaBD(nombre=datos.nombre_empresa)
        db.add(nueva_empresa)
        db.commit()
        db.refresh(nueva_empresa)

        hash_password = generar_hash_password(datos.contrasena)
        usuarios_nuevo = models.UsuariosBD(
            nombre = datos.nombre,
            apellido = datos.apellido,
            email = datos.email,
            contrasena = hash_password,
            id_empresa = nueva_empresa.id_empresa, 
            rol = "admin"
        )

        db.add(usuarios_nuevo)
        db.commit()
        db.refresh(usuarios_nuevo)

        return usuarios_nuevo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el registro.")

@router.post("/login")
def iniciar_sesion(credenciales: schemas.UsuarioLogin, db: Session = Depends(get_db)):

    usuario_existente = db.query(models.UsuariosBD).filter(models.UsuariosBD.email == credenciales.email).first()

    if not usuario_existente: 
        raise HTTPException(status_code=404, detail="Email o Password incorrectas.")
    
    password_guardada = verificar_password(credenciales.contrasena, usuario_existente.contrasena)

    if password_guardada is False: 
        raise HTTPException(status_code=401, detail="Email o Password incorrectas.")
    
    datos_token = {
        "sub": str(usuario_existente.id_usuario),
        "nombre": usuario_existente.nombre,
        "id_empresa": str(usuario_existente.id_empresa)
    }

    token_generado = crear_token_acceso(datos_usuarios=datos_token)

    return {
        "access_token": token_generado,
        "token_type": "bearer"
    }
