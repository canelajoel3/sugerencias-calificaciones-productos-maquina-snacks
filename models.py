from sqlalchemy import Column, INTEGER, DECIMAL, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from database import Base 
from datetime import datetime

class Maquinas(Base): 
    __tablename__ = "maquinas"

    id_maquina = Column(INTEGER(), autoincrement=True, primary_key=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(String(20), default="operativa")
    id_empresa = Column(INTEGER, ForeignKey("empresas.id_empresa", ondelete="SET NULL"))

    sugerencias = relationship("Sugerencias", back_populates="maquinas")
    calificaciones = relationship("Calificaciones", back_populates="maquinas")
    empresa = relationship("EmpresaBD", back_populates="maquinas")


class Productos(Base): 
    __tablename__ = "productos"

    id_producto = Column(INTEGER(), autoincrement=True, primary_key=True)
    nombre = Column(String(100), nullable=False)
    id_empresa = Column(INTEGER, ForeignKey("empresas.id_empresa", ondelete="SET NULL"))

    empresa = relationship("EmpresaBD", back_populates="productos")
    calificaciones = relationship("Calificaciones", back_populates="productos")
    imagenes = relationship("Productos_Imagenes", back_populates="productos", cascade="all, delete-orphan")


class Sugerencias(Base): 
    __tablename__ = "sugerencias"

    id_sugerencia = Column(INTEGER(), autoincrement=True, primary_key=True)
    id_maquina = Column(INTEGER(), ForeignKey("maquinas.id_maquina", ondelete="SET NULL"))
    producto_sugerido = Column(String(100), nullable=False)
    fecha_creacion = Column(DATETIME(), default=datetime.now)
    id_empresa = Column(INTEGER, ForeignKey("empresas.id_empresa", ondelete="SET NULL"))

    maquinas = relationship("Maquinas", back_populates="sugerencias") 
    empresa = relationship("EmpresaBD", back_populates="sugerencias")


class Calificaciones(Base): 
    __tablename__ = "calificaciones"

    id_calificacion = Column(INTEGER(), autoincrement=True, primary_key=True)
    id_maquina = Column(INTEGER(), ForeignKey("maquinas.id_maquina", ondelete="SET NULL"))
    id_producto = Column(INTEGER(), ForeignKey("productos.id_producto", ondelete="SET NULL"))
    voto = Column(INTEGER(), nullable=False)
    fecha_creacion = Column(DATETIME(), default=datetime.now)
    id_empresa = Column(INTEGER, ForeignKey("empresas.id_empresa", ondelete="SET NULL"))

    maquinas = relationship("Maquinas", back_populates="calificaciones") 
    productos = relationship("Productos", back_populates="calificaciones")
    empresa = relationship("EmpresaBD", back_populates="calificaciones")


class UsuariosBD(Base):
    __tablename__  = "usuarios"

    id_usuario = Column(INTEGER(), primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(80), nullable=False)
    email = Column(String(100), unique= True)
    contrasena = Column(String(302))
    rol = Column(String(20), default="admin")
    fecha_registro = Column(DATETIME(), default=datetime.now)
    id_empresa = Column(INTEGER, ForeignKey("empresas.id_empresa", ondelete="SET NULL"))
    empresa = relationship("EmpresaBD", back_populates="usuarios")
    

class EmpresaBD(Base): 
    __tablename__ = "empresas"

    id_empresa = Column(INTEGER, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    fecha_creacion = Column(DATETIME, default=datetime.now)

    productos = relationship("Productos", back_populates="empresa")
    maquinas = relationship("Maquinas", back_populates="empresa")
    sugerencias = relationship("Sugerencias", back_populates="empresa")
    calificaciones = relationship("Calificaciones", back_populates="empresa")
    usuarios = relationship("UsuariosBD", back_populates="empresa")


class Productos_Imagenes(Base): 
    __tablename__ = "productos_imagenes"

    id_imagen = Column(INTEGER, primary_key=True, autoincrement=True)
    id_producto = Column(INTEGER, ForeignKey("productos.id_producto", ondelete="CASCADE"), nullable=False)
    ruta_imagen = Column(String(255), nullable=False) 

    productos = relationship("Productos", back_populates="imagenes")

    
