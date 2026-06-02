from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from database import get_db
import bcrypt
import os 
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
import models

load_dotenv()



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
minutos_env = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

MINUTOS_EXPIRACION = int(minutos_env)

reusable_oauth2 = HTTPBearer()


def obtener_usuarios_actual(token_credenciales: HTTPAuthorizationCredentials = Depends(reusable_oauth2), db: Session = Depends(get_db)):

    token_string = token_credenciales.credentials

    credenciales_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales o el token expiro.",
        headers={"www-Authenticate": "Bearer"},
    )
    try: 
        payload = jwt.decode(token_string, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        if id_usuario is None: 
            raise credenciales_exception 
        
    except PyJWTError: 
        raise credenciales_exception 
    
    usuario = db.query(models.UsuariosBD).filter(models.UsuariosBD.id_usuario == int(id_usuario)).first()

    if usuario is None:
        raise credenciales_exception
    
    return usuario 


def crear_token_acceso(datos_usuarios: dict):
    payload = datos_usuarios.copy()

    fecha_expiracion = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACION)

    payload.update({"exp": fecha_expiracion})
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token 


def generar_hash_password(password_plana: str): 
    password_bytes = password_plana.encode('utf-8')

    salt = bcrypt.gensalt()

    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verificar_password(password_plana: str, password_guardar_db: str) -> bool: 

    password_bytes = password_plana.encode('utf-8')
    db_bytes = password_guardar_db.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, db_bytes)