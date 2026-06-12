import pytest
from fastapi.testclient import TestClient
from main import app 
from database import get_db, Base, engine
from security import obtener_usuarios_actual 
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MockAdmin:
    id_usuario = 1
    id_empresa = 1
    nombre = "Admin de Prueba"

def override_obtener_usuarios_actual(): 
    return MockAdmin() 

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[obtener_usuarios_actual] = override_obtener_usuarios_actual
    
    yield  
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

cliente = TestClient(app) 


def test_inicio():
    response = cliente.get("/")
    assert response.status_code == 200

def test_mostrar_dashboard():
    response = cliente.get("/admin/dashboard")
    assert response.status_code == 200
    assert "html" in response.text.lower()

def test_crear_maquina():
    payload = {"nombre": "Máquina Pasillo B"}
    response = cliente.post("/admin/maquinas", json=payload)
    assert response.status_code == 201
    datos = response.json()
    assert datos["nombre"] == "Máquina Pasillo B"
    assert "id_maquina" in datos 

def test_maquina_vacia_error():
    payload = {"nombre": " "}
    response = cliente.post("/admin/maquinas", json=payload) 
    assert response.status_code == 400
    assert response.json()["detail"] == "El campo 'nombre' no puede estar vacío"

def test_obtener_reporte_sugerencias():
    response = cliente.get("/admin/reporte/sugerencias")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_eliminar_producto_no_encontrado():
    id_inexistente = 99999
    response = cliente.delete(f"/admin/productos/{id_inexistente}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Producto no encontrado"