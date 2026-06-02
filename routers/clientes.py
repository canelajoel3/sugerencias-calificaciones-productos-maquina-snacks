from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db 
import models 
import schemas
import logging 
import os
from fastapi.templating import Jinja2Templates



logger = logging.getLogger(__name__) 

router = APIRouter(prefix="/clientes", 
                tags=["Clientes QR"]) 


RAIZ_VENDING = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_TEMPLATES = os.path.join(RAIZ_VENDING, "templates")

templates = Jinja2Templates(directory=RUTA_TEMPLATES)


@router.get("/maquina/{id_maquina}")
async def mostrar_pantalla_movil(id_maquina: int, request: Request):
    return templates.TemplateResponse(
        "cliente.html",
        name="cliente.html",
        context={
            "request": request,
            "id_maquina": id_maquina}
    )

@router.get("/maquina/{id_maquina}/productos")
def obtener_productos_por_maquina(id_maquina: int, db: Session = Depends(get_db)):

    maquina = db.query(models.Maquinas).filter(models.Maquinas.id_maquina == id_maquina).first()
    if not maquina: 
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    
    productos = db.query(models.Productos).filter(models.Productos.id_empresa == maquina.id_empresa).all()

    return productos

@router.post("/maquina/{id_maquina}/sugerir", status_code=201)
def registrar_sugerencia(id_maquina: int, datos_entrada: schemas.EsquemaSugerenciaCreate, db: Session = Depends(get_db)):


    if not datos_entrada.producto_sugerido.strip():
        raise HTTPException(status_code=400, detail="El campo 'producto sugerido' no puede estar vacío")

    texto_limpio = datos_entrada.producto_sugerido.strip()

    existe_maquina = db.query(models.Maquinas).filter(models.Maquinas.id_maquina == id_maquina).first()
    if not existe_maquina:
        raise HTTPException(status_code=404, detail="La Máquina especificada no existe")
    
    try: 
        nueva_sugerencia = models.Sugerencias(
            id_maquina = id_maquina,
            producto_sugerido = texto_limpio,
            id_empresa= existe_maquina.id_empresa
        ) 

        db.add(nueva_sugerencia)
        db.commit()
        db.refresh(nueva_sugerencia) 

        return nueva_sugerencia 
    
    except Exception as e:
        logger.exception("Error al registrar sugerencia en la Máquina")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al procesar la sugerencia")


@router.post("/maquina/{id_maquina}/calificar", status_code=201)
def registrar_calificacion(id_maquina: int, datos_entrada: schemas.EsquemaCalificacionCreate, db: Session = Depends(get_db)):

    existe_maquina = db.query(models.Maquinas).filter(models.Maquinas.id_maquina == id_maquina).first()
    if not existe_maquina:
        raise HTTPException(status_code=404, detail="La Máquina especificada no existe")
    
    existe_producto = db.query(models.Productos).filter(models.Productos.id_producto == datos_entrada.id_producto).first()
    if not existe_producto:
        raise HTTPException(status_code=404, detail="El producto que intentas calificar no existe en el catálogo")

    if datos_entrada.voto not in [0,1]: 
        raise HTTPException(status_code=400, detail="Voto inválido. Solo se permite 1 (Like) o 0 (Dislike)")

    try: 
        nueva_calificacion = models.Calificaciones(
            id_maquina= id_maquina,
            id_producto= datos_entrada.id_producto,
            voto= datos_entrada.voto,
            id_empresa= existe_maquina.id_empresa
        )

        db.add(nueva_calificacion)
        db.commit()
        db.refresh(nueva_calificacion)
        return nueva_calificacion
    
    except Exception as e:
        logger.exception("Error al registrar calificación en la Máquina")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al procesar la Calificación")


@router.get("/sugerencias")
def obtener_sugerencias_detalladas(db: Session = Depends(get_db)):
    try:
        lista_sugerencias = db.query(models.Sugerencias).all()

        return lista_sugerencias
    
    except Exception as e:
        logger.exception("Error al leer sugerencias de clientes")
        raise HTTPException(status_code=500, detail="Error al obtener el listado de sugerencias")
        

@router.get("/productos", status_code=200)
def obtener_productos(db: Session = Depends(get_db)): 
    try: 
        lista_productos = db.query(models.Productos).all()
        return lista_productos
    except Exception as e: 
        logger.exception("Error al recuperar catálogo desde el router de clientes")
        raise HTTPException(
            status_code=500, 
            detail="Error interno en el servidor al recuperar el catálogo de productos"
        )