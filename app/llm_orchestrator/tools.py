import requests
import json

from os import getenv
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from typing import Optional

BASE_URL = getenv("BASE_URL", default="http://127.0.0.1:8080")

######################
# Search in Postgre  #
######################
class SemanticSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="""Consulta semántica para buscar datos de clientes. Puede ser:
        - ID de cliente (ej. 1999, 2000)
        - Nombre completo o parcial (ej. Luis Hernandez, Juan Martinez)
        - Número telefónico (ej. 5544332211)
        - Email (ej. example@gmail.com)""",
        min_length=2,
        max_length=100
    )
    
    top_k: Optional[int] = Field(
        default=1,
        description="Número máximo de resultados a devolver (por defecto 1)",
        ge=1,
        le=5
    )

def semantic_search(query: str, top_k: int = 1) -> dict:
    try:
        response = requests.get(
            url=f"{BASE_URL}/api/embeddings",
            params={
                "query": query,
                "top_k": top_k
            },
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()

        print(f"data {data}")
        print(f" ")
                    
        return data
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Error en la búsqueda: {str(e)}",
            "results": []
        }

######################
# Search in Bigquery  #
######################
class ClienteInput(BaseModel):
    id_cliente: str = Field(
        ...,
        description="ID único del cliente en formato Liverpool (ej. 1999 o 2001)"
    )
    
def get_cliente_data(id_cliente: str):
    """
    Obtiene datos completos de un cliente, sus pedidos y envíos desde el sistema de Liverpool.
    
    Args:
        id_cliente: ID del cliente en formato LIV-XXXXXXX o CLI-XXXXXXX
        
    Returns:
        Dict con estructura {
            "cliente": {datos_personales}, 
        }
        o mensaje de error descriptivo
    """
    try:        
        response = requests.get(
            url=f"{BASE_URL}/api/event-data",
            params={
                "id_cliente": id_cliente
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get('data'):
            return "No se encontró el cliente en el sistema."
        
        return data
        
    except requests.exceptions.Timeout:
        return "Error: Tiempo de espera agotado al consultar el servicio"
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}"
    except json.JSONDecodeError:
        return "Error: Respuesta inválida del servidor"

def initialize_tools():
    return [
        StructuredTool.from_function(
            func=semantic_search,
            name="localizar_datos_cliente",
            description="""
            SISTEMA DE BÚSQUEDA SEMÁNTICA - LIVERPOOL DATA LAKE

            Propósito:
            Localiza dónde están almacenados los datos de clientes en los data lakes de Liverpool
            mediante búsqueda semántica.
            Devuelve el como respuesta el JSON de salida de la funcion. Esto para pasar esta informacion al siguiente nodo

            Capacidades:
            - Busca por: ID, nombre, teléfono o email
            - Identifica el dataset y tabla exactos donde se almacenan los datos

            Reglas Estrictas:
            1. Devuelve un json que contenga el event_uuid (el cual es diferente al id del cliente, tenlo en cuenta), 
            el target_dataset y target_table donde están los datos. Basate en esta salida para dar la respuesta:
                {
                    "event_uuid": "cc733d33-5d67-4a46-8b84...",
                    "target_dataset": "nombre_dataset",
                    "target_table": "nombre_tabla"
                }

            Ejemplos:
            Action: localizar_datos_cliente
            Action Input: {"query": "id cliente 1999", "top_k": 1}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "email juan.perez@email.com", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "celular 5544332211", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "nombre Luis Hernandez", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla"
                            }
            """,
            args_schema=SemanticSearchInput,
        ),

        StructuredTool.from_function(
            func=get_cliente_data,
            name="consultar_sistema_clientes",
            description="""
            HERRAMIENTA ESPECIALIZADA DEL SISTEMA LIVERPOOL - MÓDULO DE CLIENTES

            Propósito:
            Consulta información completa de clientes registrados en Liverpool, incluyendo:
            - Datos personales del cliente
            - Historial de pedidos recientes (máximo 1)
            - Estado de envíos asociados

            Formato de Entrada:
            - ID de cliente de 4 digitos de largo o más
            - Ejemplo válido: 1999

            Comportamiento:
            1. Verifica automáticamente el formato del ID
            2. Consulta la base de datos central de Liverpool
            3. Devuelve datos estructurados en formato JSON

            Reglas Estrictas:
            Solo consultar con IDs válidos
            Nunca mostrar más de 1 pedido

            Ejemplo de Uso:
            Action: consultar_sistema_clientes
            Action Input: {"id_cliente": "2001"}
            """,
            args_schema=ClienteInput,
        )
    ]