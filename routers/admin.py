
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, case
from sqlalchemy.orm import Session, joinedload
from security import obtener_usuarios_actual 
from database import get_db
import models 
import schemas
import logging
import os
import shutil
import uuid


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Panel de Administración"]) 

#CARPETA_IMAGEN = os.path.join(os.getcwd(), "static", "img")
CARPETA_IMAGEN = "/tmp/static/img"
RUTA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROYECTO = os.path.dirname(RUTA_ACTUAL) 
RUTA_TEMPLATES2 = os.path.join(RAIZ_PROYECTO, "templates")

if not os.path.exists(CARPETA_IMAGEN): 
    os.makedirs(CARPETA_IMAGEN)

templates = Jinja2Templates(directory=RUTA_TEMPLATES2)

@router.get("/dashboard")
async def mostrar_dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@router.get("/dashboard/metricas")
async def mostrar_dashboard_json(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    try: 
        empresa_id = admin_actual.id_empresa

        total_maquinas = db.query(func.count(models.Maquinas.id_maquina)).filter(models.Maquinas.id_empresa == empresa_id).scalar() or 0
        total_productos = db.query(func.count(models.Productos.id_producto)).filter(models.Productos.id_empresa == empresa_id).scalar() or 0
        total_sugerencias = db.query(func.count(models.Sugerencias.id_sugerencia)).filter(models.Sugerencias.id_empresa == empresa_id).scalar() or 0
        total_votos = db.query(func.count(models.Calificaciones.id_calificacion)).join(models.Productos).filter(models.Productos.id_empresa == empresa_id).scalar() or 0

        satisfaccion_porcentaje = 100
        if total_votos > 0: 
            likes = db.query(func.count(models.Calificaciones.id_calificacion)).join(models.Productos).filter(models.Productos.id_empresa == empresa_id, models.Calificaciones.voto == 1).scalar() or 0
            satisfaccion_porcentaje = int((likes / total_votos) * 100)

        return {
            "total_maquinas": total_maquinas,
            "total_productos": total_productos,
            "total_sugerencias": total_sugerencias,
            "satisfaccion": satisfaccion_porcentaje
        }
    except Exception as e:
        logger.exception("Error al calcular estadísticas")
        raise HTTPException(status_code=500, detail="Error interno al recopilar Métricas")

@router.post("/maquinas", status_code=201)
def crear_maquina(datos_entrada: schemas.EsquemaMaquinaCreate, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)): 
    if not datos_entrada.nombre or datos_entrada.nombre.strip() == "":
        raise HTTPException(status_code=400, detail="El campo 'nombre' no puede estar vacío")

    existe_maquina = db.query(models.Maquinas).filter(
        models.Maquinas.nombre == datos_entrada.nombre.strip(),
        models.Maquinas.id_empresa == admin_actual.id_empresa
    ).first() 
    if existe_maquina:
        raise HTTPException(status_code=409, detail="Esta máquina ya está registrada")

    nueva_maquina = models.Maquinas(nombre=datos_entrada.nombre.strip(), id_empresa=admin_actual.id_empresa)
    db.add(nueva_maquina)
    db.commit()
    db.refresh(nueva_maquina)
    return nueva_maquina 

@router.post("/productos")
async def crear_producto(
    nombre: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_actual = Depends(obtener_usuarios_actual)):

    if not nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")

    try:
        extension = file.filename.split(".")[-1]
        nombre_archivo = f"{uuid.uuid4()}.{extension}"
        ruta_guardado = os.path.join(CARPETA_IMAGEN, nombre_archivo)
        
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="No se pudo guardar la imagen")

    try:
        nuevo_producto = models.Productos(
            nombre=nombre,
            id_empresa=admin_actual.id_empresa
        )
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        nueva_imagen = models.Productos_Imagenes(
            id_producto=nuevo_producto.id_producto,
            ruta_imagen=f"/static/img/{nombre_archivo}"
        )
        db.add(nueva_imagen)
        db.commit()
        
        return {
            "id_producto": nuevo_producto.id_producto,
            "nombre": nuevo_producto.nombre,
            "ruta_imagen": f"/static/img/{nombre_archivo}"
        }

    except Exception as e:
        db.rollback()
        if os.path.exists(ruta_guardado):
            os.remove(ruta_guardado)
        raise HTTPException(status_code=500, detail="Error al registrar en base de datos")

@router.get("/reporte/sugerencias", status_code=200)
def obtener_reporte_sugerencias(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)): 
    
    reporte = db.query(models.Sugerencias.producto_sugerido.label("producto"),
                        func.count(models.Sugerencias.id_sugerencia).label("voto"),
                        func.max(models.Sugerencias.fecha_creacion).label("fecha_creacion")
                )\
                .filter(models.Sugerencias.id_empresa == admin_actual.id_empresa)\
                .group_by(models.Sugerencias.producto_sugerido)\
                .order_by(func.count(models.Sugerencias.id_sugerencia).desc()).all()
    
    
    return [{"producto": fila.producto, "votos": fila.voto, "fecha_creacion": fila.fecha_creacion } for fila in reporte]



@router.get("/reporte/calificaciones", status_code=200)
def obtener_reporte_calificaciones(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)): 
    reporte = db.query(
            models.Calificaciones.id_calificacion, 
            models.Productos.nombre.label("producto_nombre"),
            models.Maquinas.nombre.label("maquina_nombre"),
            models.Calificaciones.voto,
            models.Calificaciones.fecha_creacion
        )\
        .join(models.Productos, models.Calificaciones.id_producto == models.Productos.id_producto)\
        .join(models.Maquinas, models.Calificaciones.id_maquina == models.Maquinas.id_maquina)\
        .filter(models.Calificaciones.id_empresa == admin_actual.id_empresa)\
        .order_by(models.Calificaciones.fecha_creacion.desc()).all()
    
    return [{
        "id": f[0],
        "origen": f[2],        
        "producto_nombre": f[1], 
        "voto": "👍 Satisfactorio (Like)" if f[3] == 1 else "👎 Insatisfecho (Dislike)",
        "fecha": str(f[4])
    } for f in reporte]



@router.get("/maquinas", status_code=200)
def obtener_maquinas(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    return db.query(models.Maquinas).filter(models.Maquinas.id_empresa == admin_actual.id_empresa).all()


@router.get("/productos", status_code=200)
def obtener_productos(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual), buscar: str = None): 
    try:
        query = db.query(models.Productos)\
            .options(joinedload(models.Productos.imagenes))\
            .filter(models.Productos.id_empresa == admin_actual.id_empresa)

        if buscar: 
            query = query.filter(models.Productos.nombre.ilike(f"%{buscar}%"))

        return query.all()
    except Exception as e:
        logger.exception("Error al leer catálogo de productos")
        raise HTTPException(status_code=500, detail="Error interno al recuperar el catálogo")
    

@router.get("/calificaciones")
def obtener_calificaciones_dashboard(db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    calificaciones = db.query(models.Calificaciones)\
        .join(models.Productos, models.Calificaciones.id_producto == models.Productos.id_producto)\
        .filter(models.Productos.id_empresa == admin_actual.id_empresa)\
        .options(joinedload(models.Calificaciones.productos)).all()
    return [{"id_calificacion": c.id_calificacion, "id_maquina": c.id_maquina, "voto": c.voto, "nombre_producto": c.productos.nombre if c.productos else "General"} for c in calificaciones]

@router.put("/productos/{id_producto}", status_code=200)
def actualizar_producto(id_producto: int, datos_entrada: schemas.EsquemaProductoCreate, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    producto = db.query(models.Productos).filter(models.Productos.id_producto == id_producto, models.Productos.id_empresa == admin_actual.id_empresa).first()
    if not producto: raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.nombre = datos_entrada.nombre.strip()
    db.commit()
    return producto

@router.delete("/productos/{id_producto}")
def eliminar_producto(id_producto: int, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    producto = db.query(models.Productos).filter(models.Productos.id_producto == id_producto, models.Productos.id_empresa == admin_actual.id_empresa).first()
    if not producto: raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"detail": "Producto eliminado"}

@router.put("/maquinas/{id_maquina}", status_code=200)
def actualizar_maquina(id_maquina: int, datos_entrada: schemas.MaquinaUpdate, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    maquina = db.query(models.Maquinas).filter(models.Maquinas.id_maquina == id_maquina, models.Maquinas.id_empresa == admin_actual.id_empresa).first()
    if not maquina: raise HTTPException(status_code=404, detail="Máquina no encontrada")
    
    existe_otro = db.query(models.Maquinas).filter(
        models.Maquinas.nombre == datos_entrada.nombre.strip(), 
        models.Maquinas.id_empresa == admin_actual.id_empresa,
        models.Maquinas.id_maquina != id_maquina
    ).first()
    if existe_otro: raise HTTPException(status_code=409, detail="Ya existe otra máquina con ese nombre")

    maquina.nombre = datos_entrada.nombre.strip()
    maquina.estado = datos_entrada.estado.strip()
    db.commit()
    return maquina

@router.delete("/maquinas/{id_maquina}", status_code=200)
def eliminar_maquina(id_maquina: int, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)):
    maquina = db.query(models.Maquinas).filter(models.Maquinas.id_maquina == id_maquina, models.Maquinas.id_empresa == admin_actual.id_empresa).first()
    if not maquina: raise HTTPException(status_code=404, detail="Máquina no encontrada")
    db.delete(maquina)
    db.commit()
    return {"detail": "Máquina eliminada"}

@router.delete("/eliminar_calificacion/{id_calificacion}")
def eliminar_calificacion(id_calificacion: int, db: Session = Depends(get_db), admin_actual = Depends(obtener_usuarios_actual)): 
    calificacion = db.query(models.Calificaciones).join(models.Productos).filter(
        models.Calificaciones.id_calificacion == id_calificacion, 
        models.Productos.id_empresa == admin_actual.id_empresa
    ).first()
    if not calificacion: raise HTTPException(status_code=404, detail="Calificación no encontrada")
    db.delete(calificacion)
    db.commit()
    return {"detail": "Calificación eliminada"}
