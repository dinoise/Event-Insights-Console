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
        print(f"response {response}")
        response_data = response.json().get("data")
        
        print(f"response_data {response_data}")

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
            Este es el primer paso que se debe realizar cuando se piden datos de un cliente, un pedido 
            o un envío. Busca información en la base de datos de Liverpool.
            Sólo devuelve la información obtenida de este Tool.
            Devuelve la información en una tabla con formato Markdown
            Ejemplo de uso: Buscar información del cliente con ID CL12345
            """,
            args_schema=QueryInput,
        )
    ]