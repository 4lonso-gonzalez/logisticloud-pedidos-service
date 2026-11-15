import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_crear_pedido_tarifa_estandar():
    payload = {
        "cliente_id": "COM-001",
        "destino": "Santiago Centro",
        "peso_kg": 2.0,
        "distancia_km": 10.0,
        "modalidad": "estandar"
    }
    response = client.post("/api/v1/pedidos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["tracking_id"].startswith("TRK-")
    assert data["costo_total_clp"] == 4300.0
    assert data["estado"] == "PEDIDO_CREADO_EVENTO_PUBLICADO"

def test_crear_pedido_tarifa_express():
    payload = {
        "cliente_id": "COM-002",
        "destino": "Providencia",
        "peso_kg": 2.0,
        "distancia_km": 10.0,
        "modalidad": "express"
    }
    response = client.post("/api/v1/pedidos", json=payload)
    assert response.status_code == 201
    assert response.json()["costo_total_clp"] == 6450.0

def test_modalidad_invalida():
    payload = {
        "cliente_id": "COM-003",
        "destino": "Maipú",
        "peso_kg": 1.5,
        "distancia_km": 15.0,
        "modalidad": "teletransportacion"
    }
    response = client.post("/api/v1/pedidos", json=payload)
    assert response.status_code == 400

def test_fitness_function_latencia_rnf01():
    """Fitness Function: Verifica RNF-01 (tiempo de respuesta < 400 ms)"""
    inicio = time.perf_counter()
    response = client.get("/health")
    duracion_ms = (time.perf_counter() - inicio) * 1000
    assert response.status_code == 200
    assert duracion_ms < 400.0