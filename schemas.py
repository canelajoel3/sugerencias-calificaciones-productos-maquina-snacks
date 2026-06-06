from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime 
from enum import IntEnum
from typing import List


configuracion_orm = ConfigDict(from_attributes=True)


class EsquemaSugerenciaBase(BaseModel):
    producto_sugerido: str 

class EsquemaSugerenciaCreate(EsquemaSugerenciaBase): 
    pass 

class EsquemaSugerenciaResponse(EsquemaSugerenciaBase):
    id_sugerencia: int
    id_maquina: int
    fecha_creacion: datetime
    model_config = configuracion_orm

class VotoEnum(IntEnum):
    dislike = 0
    like = 1

class EsquemaCalificacionBase(BaseModel):
    id_producto: int
    voto: VotoEnum

class EsquemaCalificacionCreate(EsquemaCalificacionBase): 
    pass 

class EsquemaCalificacionResponse(EsquemaCalificacionBase): 
    id_calificacion: int
    id_maquina: int
    fecha_creacion: datetime
    model_config = configuracion_orm


class EsquemaMaquinaBase(BaseModel):
    nombre: str

class EsquemaMaquinaCreate(EsquemaMaquinaBase):
    estado: str = "Operativa"

class EsquemaMaquinaResponse(EsquemaMaquinaBase):
    id_maquina: int
    estado: str
    model_config = configuracion_orm

class MaquinaUpdate(BaseModel):
    nombre: str
    estado: str


class EsquemaProductoBase(BaseModel):
    nombre: str 

class EsquemaProductoCreate(EsquemaProductoBase):
    pass 



class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    contrasena: str = Field(..., min_length=8)
    nombre_empresa: str

@field_validator('contrasena')
@classmethod
def validar_complejidad(cls, v): 
    if not any(char.isupper() for char in v):
        raise ValueError('La contraseña debe tener al menos una mayúscula')
    if not any(char.isdigit() for char in v): 
        raise ValueError('La contraseña debe tener al menos un número')
    return v 




class UsuarioLogin(BaseModel):
    email: str
    contrasena: str 


class UsuarioResponse(BaseModel): 
    id_usuario: int 
    nombre: str 
    apellido: str
    email: str 
    rol: str 
    id_empresa: int 
    fecha_registro: datetime
    model_config = configuracion_orm


class EsquemaToken(BaseModel):
    access_token: str
    token_type: str


class EmpresaCreate(BaseModel):
    nombre: str 

class EmpresaResponse(BaseModel):
    id_empresa: int 
    nombre: str 
    fecha_creacion: datetime
    model_config = configuracion_orm


class ImagenResponse(BaseModel):
    id_imagen: int
    ruta_imagen: str
    model_config = configuracion_orm


class EsquemaProductoResponse(EsquemaProductoBase):
    id_producto: int
    nombre: str
    imagenes: List[ImagenResponse] = []
    model_config = configuracion_orm