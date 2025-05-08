import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from aiohttp import ClientSession

# Datos hardcodeados de ejemplo
DATOS_CLIENTES = {
    "CL12345": {
        "nombre": "Juan Pérez",
        "email": "juan.perez@example.com",
        "pedidos": [
            {
                "id_pedido": "PED1001",
                "fecha": "2023-05-15",
                "total": 1250.50,
                "estado": "entregado",
                "productos": [
                    {"nombre": "Camisa", "cantidad": 2, "precio": 300},
                    {"nombre": "Pantalón", "cantidad": 1, "precio": 650.50}
                ]
            },
            {
                "id_pedido": "PED1002",
                "fecha": "2023-06-20",
                "total": 890.00,
                "estado": "en proceso",
                "productos": [
                    {"nombre": "Zapatos", "cantidad": 1, "precio": 890.00}
                ]
            }
        ]
    },
    "CL67890": {
        "nombre": "María García",
        "email": "maria.garcia@example.com",
        "pedidos": [
            {
                "id_pedido": "PED2001",
                "fecha": "2023-07-10",
                "total": 540.75,
                "estado": "entregado",
                "productos": [
                    {"nombre": "Bufanda", "cantidad": 3, "precio": 180.25}
                ]
            }
        ]
    }
}

# Modelo de entrada para la herramienta
class BusquedaPedidosInput(BaseModel):
    id_cliente: str = Field(description="Identificador único del cliente")
    estado_pedido: Optional[str] = Field(
        default=None, 
        description="Filtrar por estado del pedido (ej. 'entregado', 'en proceso')"
    )
    desde_fecha: Optional[str] = Field(
        default=None, 
        description="Filtrar pedidos desde esta fecha (formato YYYY-MM-DD)"
    )

def buscar_pedidos_cliente(
    id_cliente: str, 
    estado_pedido: Optional[str] = None, 
    desde_fecha: Optional[str] = None
):
    """
    Busca los pedidos de un cliente específico en la base de datos.
    Puede filtrarse por estado del pedido y fecha mínima.
    
    Args:
        id_cliente: Identificador del cliente
        estado_pedido: Estado del pedido para filtrar
        desde_fecha: Fecha mínima para filtrar pedidos
        
    Returns:
        Lista de pedidos que coinciden con los criterios o mensaje de error
    """
    # Verificar si el cliente existe
    cliente = DATOS_CLIENTES.get(id_cliente)
    if not cliente:
        return f"No se encontró ningún cliente con ID {id_cliente}"
    
    pedidos = cliente["pedidos"]
    
    # Aplicar filtros si se especificaron
    if estado_pedido:
        pedidos = [p for p in pedidos if p["estado"].lower() == estado_pedido.lower()]
    
    if desde_fecha:
        pedidos = [p for p in pedidos if p["fecha"] >= desde_fecha]
    
    if not pedidos:
        return f"El cliente {id_cliente} no tiene pedidos que coincidan con los criterios"
    
    # Formatear la respuesta para que sea legible
    resultado = {
        "cliente": {
            "nombre": cliente["nombre"],
            "email": cliente["email"]
        },
        "total_pedidos": len(pedidos),
        "pedidos": pedidos
    }
    
    return json.dumps(resultado, indent=2, ensure_ascii=False)

# Función para inicializar las herramientas
def initialize_tools(client_session: ClientSession):
    return [
        StructuredTool.from_function(
            func=buscar_pedidos_cliente,
            name="buscar_pedidos_cliente",
            description="""
            Utiliza esta herramienta para buscar los pedidos de un cliente específico.
            Requiere el ID del cliente y puede filtrarse por estado del pedido y fecha mínima.
            
            Ejemplo de entrada:
            {{
                "id_cliente": "CL12345",
                "estado_pedido": "entregado",
                "desde_fecha": "2023-01-01"
            }}
            
            Ejemplo de entrada:
            {{
                "id_cliente": "CL67890",
                "estado_pedido": null,
                "desde_fecha": null
            }}
            
            Devuelve los detalles de los pedidos o un mensaje si no se encuentran resultados.
            """,
            args_schema=BusquedaPedidosInput,
        )
    ]
