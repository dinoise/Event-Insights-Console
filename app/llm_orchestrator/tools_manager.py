import requests
from os import getenv
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from typing import Optional, Dict, List

BASE_URL = getenv("BASE_URL", default="http://127.0.0.1:8080")

class ToolManager:
    """
    Clase para gestionar herramientas de LangGraph de manera organizada y extensible.
    """
    
    def __init__(self):
        self._tools: Dict[str, dict] = {
            "localizar_datos_cliente": {
                "function": self.semantic_search,
                "args_schema": SemanticSearchInput,
                "metadata": {
                    "category": "search",
                    "system": "SISTEMA DE BÚSQUEDA SEMÁNTICA - LIVERPOOL DATA LAKE"
                },
                "description": """
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
                """
            },
            "consultar_sistema_liverpool": {
                "function": self.generic_data_retrieval,
                "args_schema": GenericQueryInput,
                "metadata": {
                    "category": "query",
                    "system": "SISTEMA UNIFICADO DE CONSULTAS - LIVERPOOL DATA HUB"
                },
                "description": """
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
                """
            }
        }
            
    def get_tool(self, name: str) -> StructuredTool:
        """
        Obtiene una herramienta específica por nombre.
        
        Args:
            name: Nombre de la herramienta a recuperar
            
        Returns:
            Instancia de StructuredTool configurada
            
        Raises:
            KeyError: Si la herramienta no existe
        """
        if name not in self._tools:
            raise KeyError(f"Herramienta '{name}' no encontrada")
            
        tool_data = self._tools[name]
        return StructuredTool.from_function(
            func=tool_data["function"],
            name=name,
            description=tool_data["description"],
            args_schema=tool_data["args_schema"]
        )
    
    def get_all_tools(self) -> List[StructuredTool]:
        """
        Obtiene todas las herramientas registradas.
        
        Returns:
            Lista de todas las herramientas como StructuredTool
        """
        return [self.get_tool(name) for name in self._tools.keys()]

    def get_tools_by_category(self, category: str) -> List[StructuredTool]:
        """
        Obtiene herramientas filtradas por categoría.
        
        Args:
            category: Categoría para filtrar
            
        Returns:
            Lista de herramientas que pertenecen a la categoría
        """
        return [
            self.get_tool(name) 
            for name, data in self._tools.items() 
            if data["metadata"].get("category") == category
        ]
        
    def list_available_tools(self) -> List[str]:
        """
        Lista los nombres de todas las herramientas disponibles.
        
        Returns:
            Lista de nombres de herramientas
        """
        return list(self._tools.keys())
    
    ######################
    # Herramientas actuales #
    ######################
    
    @staticmethod
    def semantic_search(query: str, top_k: int = 1) -> dict:
        """Búsqueda semántica en PostgreSQL"""
        try:
            response = requests.get(
                url=f"{BASE_URL}/api/embeddings",
                params={"query": query, "top_k": top_k},
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
    
    @staticmethod
    def generic_data_retrieval(
        event_uuid: str,
        target_dataset: str,
        target_table: str
    ) -> dict:
        """Consulta genérica a BigQuery"""
        try:
            if not all([event_uuid, target_dataset, target_table]):
                return {"status": "error", "error": "Faltan parámetros requeridos"}
            
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
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"Error en la consulta: {str(e)}"
            }

######################
# Schemas de entrada #
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

# Instancia global para fácil acceso
tool_manager = ToolManager()
