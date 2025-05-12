from os import getenv
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

BASE_URL = getenv("BASE_URL", default="http://127.0.0.1:8080")

class QueryInput(BaseModel):
    query: str = Field(description="Search query")

def search(query: str):
    """
    Función síncrona para buscar datos de clientes/pedidos/envíos
    """
    try:
        response = requests.get(
            url=f"{BASE_URL}/api/embeddings",
            params={"top_k": "5", "query": query},
            timeout=10
        )
        
        response.raise_for_status() 
        response_data = response.json().get("data")
        
        if not response_data:
            return "No se encontraron resultados para la búsqueda."
        return response_data
        
    except requests.exceptions.RequestException as e:
        return f"Error al realizar la búsqueda: {str(e)}"

def initialize_tools():
    return [
        StructuredTool.from_function(
            func=search,
            name="buscar_datos_cliente_pedido_envio",
            description="""
            Herramienta especializada para buscar información en la base de datos de Liverpool.
            Debe ser el primer paso cuando se solicitan datos de clientes, pedidos o envíos.

            FORMATO DE BÚSQUEDA:
            - Para clientes: 'cliente <id_cliente>' o 'cliente <nombre/apellido>'
            - Para pedidos: 'pedido <id_pedido>' o 'pedido cliente <id_cliente>'
            - Para envíos: 'envío <id_envío>' o 'envío pedido <id_pedido>'

            RESULTADOS:
            - Organiza la información en tablas claras
            - Incluye solo datos verificados de la base de datos
            - Si no hay resultados, devuelve "No se encontraron coincidencias"

            EJEMPLOS DE USO:
            1. Buscar cliente por ID: 'cliente 1227'
            2. Buscar pedidos de cliente: 'pedido cliente 1832'
            3. Buscar envío específico: 'envío ENV45678'

            NORMAS ESTRICTAS:
            1. Nunca inventar información
            2. Solo usar datos de la respuesta de la API
            3. Limitar resultados a 5 registros como máximo
            """,
            args_schema=QueryInput,
        )
    ]