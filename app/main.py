from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid

app = FastAPI(
    title="LogistiCloud - Microservicio de Pedidos y Despachos",
    version="1.0.0"
)

# --- PATRÓN STRATEGY: Cálculo Dinámico de Tarifas ---
class EstrategiaTarifa(ABC):
    @abstractmethod
    def calcular(self, peso_kg: float, distancia_km: float) -> float:
        pass

class TarifaEstandar(EstrategiaTarifa):
    def calcular(self, peso_kg: float, distancia_km: float) -> float:
        return round(2500 + (peso_kg * 300) + (distancia_km * 120), 2)

class TarifaExpress(EstrategiaTarifa):
    def calcular(self, peso_kg: float, distancia_km: float) -> float:
        return round((2500 + (peso_kg * 300) + (distancia_km * 120)) * 1.5, 2)

ESTRATEGIAS = {
    "estandar": TarifaEstandar(),
    "express": TarifaExpress()
}

# --- MODELOS DE DATOS ---
class PedidoRequest(BaseModel):
    cliente_id: str = Field(..., min_length=3)
    destino: str = Field(..., min_length=3)
    peso_kg: float = Field(..., gt=0)
    distancia_km: float = Field(..., gt=0)
    modalidad: str = Field(default="estandar")

# Base de datos simulada en memoria para demostración CI/CD
pedidos_db = {}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "srv-pedidos", "version": "1.0.0"}

@app.post("/api/v1/pedidos", status_code=201)
def crear_pedido(pedido: PedidoRequest):
    estrategia = ESTRATEGIAS.get(pedido.modalidad.lower())
    if not estrategia:
        raise HTTPException(status_code=400, detail="Modalidad de envío no soportada")

    costo_envio = estrategia.calcular(pedido.peso_kg, pedido.distancia_km)
    tracking_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"

    registro = {
        "tracking_id": tracking_id,
        "cliente_id": pedido.cliente_id,
        "destino": pedido.destino,
        "modalidad": pedido.modalidad.lower(),
        "costo_total_clp": costo_envio,
        "estado": "PEDIDO_CREADO_EVENTO_PUBLICADO"
    }
    pedidos_db[tracking_id] = registro
    return registro

@app.get("/api/v1/pedidos/{tracking_id}")
def obtener_pedido(tracking_id: str):
    pedido = pedidos_db.get(tracking_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Orden de despacho no encontrada")
    return pedido