import requests

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
        
        response_json = response.json()

        data = response_json.get("data", {})
        
        data["query"] = query

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
class GenericQueryInput(BaseModel):
    event_uuid: str = Field(
        ...,
        description="UUID único del registro a consultar (obtenido de búsqueda semántica)",
        min_length=36,
        max_length=36
    )
    target_dataset: str = Field(
        ...,
        description="Nombre del dataset donde se encuentran los datos",
        examples=["ds_silver_delivernow", "ds_gold_customers"]
    )
    target_table: str = Field(
        ...,
        description="Nombre de la tabla específica con los datos",
        examples=["tb_lvp_clientes_v1", "tb_pedidos_activos"]
    )

def generic_data_retrieval(
    event_uuid: str,
    target_dataset: str,
    target_table: str
) -> dict:
    try:
        # Validación básica
        if not all([event_uuid, target_dataset, target_table]):
            return {
                "status": "error",
                "error": "Faltan parámetros requeridos"
            }
        
        # Construir payload para la API
        payload = {
            "event_uuid": event_uuid,
            "target_dataset": target_dataset,
            "target_table": target_table
        }
        
        response = requests.get(
            url=f"{BASE_URL}/api/event-data",
            params=payload,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        return data
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": f"Error en la consulta: {str(e)}"
        }

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
                    "target_table": "nombre_tabla",
                    "embedding_event_message": "id_cliente: 1901 cliente_nombres: Mario ...",
                    "query": "id cliente 1901"
                }

            Ejemplos:
            Action: localizar_datos_cliente
            Action Input: {"query": "id cliente 1999", "top_k": 1}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla",
                                "embedding_event_message": "id_cliente: 1999 cliente_nombres: Mario ...",
                                "query": "id cliente 1999"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "email juan.perez@email.com", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla",
                                "embedding_event_message": "id_cliente: 1901 cliente_nombres: Mario ...",
                                "query": "email juan.perez@email.com"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "celular 5544332211", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla",
                                "embedding_event_message": "id_cliente: 1901 cliente_nombres: Mario ...",
                                "query": "celular 5544332211"
                            }
            ---
            Action: localizar_datos_cliente
            Action Input: {"query": "nombre Luis Hernandez", "top_k": 5}
            Action Output: {
                                "event_uuid": "cc733d33-5d67-4a46-8b84...",
                                "target_dataset": "nombre_dataset",
                                "target_table": "nombre_tabla",
                                "embedding_event_message": "id_cliente: 1901 cliente_nombres: Luis ...",
                                "query": "nombre Luis Hernandez"
                            }
            """,
            args_schema=SemanticSearchInput,
        ),

        StructuredTool.from_function(
            func=generic_data_retrieval,
            name="consultar_sistema_liverpool",
            description="""
            SISTEMA UNIFICADO DE CONSULTAS - LIVERPOOL DATA HUB

            Propósito:
            Consulta información detallada en los sistemas de Liverpool usando metadatos
            obtenidos previamente por búsqueda semántica.

            Datos que puede consultar:
            - Información completa de clientes
            - Detalles de pedidos específicos
            - Estados y rutas de envíos

            Requisitos de Entrada:
            1. event_uuid: Identificador único del registro (36 caracteres)
            2. target_dataset: Nombre del dataset (ej. ds_silver_delivernow)
            3. target_table: Nombre de la tabla (ej. tb_lvp_clientes_v1)

            Reglas Estrictas:
            1. Siempre validar que los metadatos provengan de búsqueda semántica
            2. Limitar consultas a 1 registro por vez
            3. Nunca exponer campos sensibles (ej. contraseñas, datos bancarios)
            4. Mantener estructura de respuesta estándar

            Ejemplos Válidos:
            Action: consultar_sistema_liverpool
            Action Input: {
                "event_uuid": "e6eee544-3f68-4172-aa2e-c8a5d8e2a7f9",
                "target_dataset": "ds_silver_delivernow",
                "target_table": "tb_lvp_clientes_v1"
            }
            ---
            Action: consultar_sistema_liverpool
            Action Input: {
                "event_uuid": "a1b2c3d4-5678-90ef-1234-567890abcdef",
                "target_dataset": "ds_gold_orders",
                "target_table": "tb_pedidos_2024"
            }
            """,
            args_schema=GenericQueryInput,
        )
    ]