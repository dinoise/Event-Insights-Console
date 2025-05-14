import json

from typing import Annotated, TypedDict, Union, Dict, Any, List

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from datetime import datetime

from .assistant_template import AssistantTemplate

from llm_orchestrator.tools import semantic_search, generic_data_retrieval

class AgentState(TypedDict):
    messages: Annotated[List[Union[HumanMessage, AIMessage]], add_messages]
    user_info: Dict[str, Any]
    session_data: Dict[str, Any]

class UserGraph:
    def __init__(self, llm: BaseChatModel, tools: List[StructuredTool]):
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = self._initialize_llm_with_tools()
        self.graph = None
        self.compiled_graph = None
        self.conversation_history = []
        self.initial_state = self._create_initial_state()

        # Inicializar con el mensaje de bienvenida
        self._add_to_history(self.initial_state["messages"][0])
    
    #######################
    # Internal Functions  #
    #######################
    def _get_system_template(self):
        return AssistantTemplate.get_system_prompt()

    def _initialize_llm_with_tools(self):
        """Configura la LLM con herramientas y el template de sistema"""

        # Definir el prompt estructurado
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._get_system_template()),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        return prompt | self.llm.bind_tools(self.tools)
    
    def _create_initial_state(self):
        """Crea el estado inicial con el mensaje de bienvenida personalizado"""
        welcome_message = AIMessage(
            content=AssistantTemplate.get_initial_state()
        )
        return {
            "messages": [welcome_message],
            "user_info": {},
            "session_data": {}
        }
    
    def _get_message_objects(self) -> List[Union[HumanMessage, AIMessage]]:
        """Convierte el historial interno en objetos Message para LangChain"""
        messages = []
        for item in self.conversation_history:
            if item["type"] == "human":
                messages.append(HumanMessage(content=item["content"]))
            elif item["type"] == "ai":
                messages.append(AIMessage(content=item["content"]))
        return messages
    
    def _add_to_history(self, message: Union[HumanMessage, AIMessage]):
        """Añade un mensaje al historial de conversación"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "human" if isinstance(message, HumanMessage) else "ai",
            "content": message.content,
            "metadata": {
                "user_info": getattr(message, "user_info", {}),
                "session_data": getattr(message, "session_data", {})
            }
        }
        self.conversation_history.append(entry)

    ###################
    # Function nodes  #
    ###################
    def _semantic_search_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo optimizado para búsqueda semántica con una sola herramienta"""
        # 1. Obtener el mensaje del usuario
        user_query = next(
            (msg.content for msg in reversed(state["messages"]) 
            if isinstance(msg, HumanMessage)),
            ""
        )
        
        # 2. Seleccionar solo la herramienta que necesitas
        semantic_search_tool = next(
            (tool for tool in self.tools if tool.name == "localizar_datos_cliente"), 
            None
        )
        
        if not semantic_search_tool:
            raise ValueError("La herramienta 'localizar_datos_cliente' no está disponible")
        
        # 3. Configurar el LLM con solo esta herramienta
        llm_with_single_tool = self.llm.bind_tools([semantic_search_tool])
        
        # 4. Crear el prompt específico
        prompt = (
            "Realiza una búsqueda semántica para localizar dónde están almacenados los datos. "
            "Usa EXCLUSIVAMENTE la herramienta 'localizar_datos_cliente' con los siguientes parámetros:\n"
            f"Consulta del usuario: '{user_query}'\n\n"
            "Instrucciones:\n"
            "1. Usa SOLO la herramienta proporcionada\n"
            "2. Devuelve únicamente el JSON con la estructura requerida:\n"
            "- event_uuid\n"
            "- target_dataset\n"
            "- target_table"
        )
        
        # 5. Invocar el LLM
        response = llm_with_single_tool.invoke([HumanMessage(content=prompt)])
        
        print(f"\nResponse semantic search: {response}\n")
        
        # 6. Verificar si se llamó a la herramienta
        if response.tool_calls:
            # Si se llamó a la herramienta, ejecutarla
            tool_call = response.tool_calls[0]
            tool_output = semantic_search_tool.invoke(tool_call["args"])
            
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[tool_call],
                    ),
                    ToolMessage(
                        content=json.dumps(tool_output),
                        tool_call_id=tool_call["id"],
                    )
                ]
            }
        else:
            # Si no se llamó a la herramienta, devolver la respuesta directa
            return {"messages": [response]}
    

    def _bigquery_search_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo optimizado para consulta de datos con la herramienta específica"""
        try:
            # 1. Obtener el último mensaje
            last_msg = state["messages"][-1].content
            print(f"\nlast_msg: {last_msg}\n")
            
            # 2. Obtener la herramienta específica
            consultar_tool = next(
                tool for tool in self.tools 
                if tool.name == "consultar_sistema_liverpool"
            )
            
            # 3. Configurar LLM con solo esta herramienta y forzar su uso
            llm_with_tool = self.llm.bind_tools(
                [consultar_tool],
                tool_choice={
                    "type": "function", 
                    "function": {"name": "consultar_sistema_liverpool"}
                }
            )
            
            # 4. Crear prompt específico
            prompt = (
                f"Consulta información en los sistemas de Liverpool usando EXCLUSIVAMENTE "
                f"la herramienta 'consultar_sistema_liverpool' con estos parámetros:\n"
                f"{last_msg}\n\n"
                "Requisitos:\n"
                "- Usa EXACTAMENTE los metadatos proporcionados\n"
                "- Devuelve los datos completos en formato JSON\n"
                "- No uses ninguna otra herramienta o función"
            )
            
            print(f"\nprompt bigquery: {prompt}\n")
            
            # 5. Invocar el LLM
            response = llm_with_tool.invoke([HumanMessage(content=prompt)])
            
            print(f"\nresponse bigquery: {response}\n")
            
            # 6. Verificar y ejecutar la herramienta
            if not response.tool_calls:
                raise ValueError("El LLM no llamó a la herramienta como se esperaba")
            
            tool_call = response.tool_calls[0]
            tool_output = consultar_tool.invoke(tool_call["args"])
            
            # 7. Retornar la estructura adecuada de mensajes
            return {
                "messages": [
                    AIMessage(content="", tool_calls=[tool_call]),
                    ToolMessage(
                        content=json.dumps(tool_output),
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    )
                ]
            }
            
        except Exception as e:
            print(f"\nError en bigquery_search_node: {str(e)}\n")
            return {
                "messages": [
                    AIMessage(content=f"Error al consultar el sistema: {str(e)}")
                ]
            }
         
    def _formatter_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo que formatea la salida de herramientas a Markdown"""
        last_msg = state["messages"][-1].content
        print(f"formatter {last_msg}")
        
        # Prompt más específico para el formateo
        input_prompt = (
            "Por favor, formatea los siguientes datos como un mensaje Markdown claro y organizado "
            "para ser mostrado al cliente de Liverpool. Usa tablas o texto estructurado "
            "según corresponda:\n\n"
            f"Datos a formatear: {last_msg}\n\n"
            "Instrucciones adicionales:\n"
            "- Destaca los números de pedido/envío en **negrita**\n"
            "- Usa listas para items múltiples\n"
            "- Si hay fechas, usa formato DD/MM/YYYY\n"
            "- Mantén un tono profesional pero amable"
        )
        
        response = self.llm.invoke([input_prompt])
        return {"messages": response}
    
    def create_graph(self) -> None:
        """Grafo optimizado con flujo claro"""
        graph_builder = StateGraph(AgentState)
        
        # Nodos
        graph_builder.add_node("semantic_search", self._semantic_search_node)
        graph_builder.add_node("data_retrieval", self._bigquery_search_node)
        graph_builder.add_node("format_response", self._formatter_node)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # Conexiones principales
        graph_builder.set_entry_point("semantic_search")
        
        # graph_builder.add_edge("tools", "semantic_search")
        # graph_builder.add_conditional_edges("semantic_search", tools_condition)

        # graph_builder.add_edge("tools", "data_retrieval")
        # graph_builder.add_conditional_edges("data_retrieval", tools_condition)

        graph_builder.add_edge("semantic_search", "data_retrieval")

        graph_builder.add_edge("data_retrieval", "format_response")

        graph_builder.add_edge("format_response", END)
                
        self.graph = graph_builder

    def compile_graph(self) -> None:
        """Compila el grafo para su ejecución"""
        if self.graph is None:
            self.create_graph()
        self.compiled_graph = self.graph.compile()

        print(self.compiled_graph.get_graph().draw_mermaid())
    
    def invoke_graph(self, user_input: str) -> Dict[str, Any]:
        """
        Invoca el grafo con el input del usuario usando el estado interno.
        
        Args:
            user_input: Mensaje del usuario
            
        Returns:
            Estado actualizado después de procesar el input
        """
        if not hasattr(self, 'compiled_graph'):
            self.compile_graph()
        
        # Crear estado actual basado en el historial
        current_state = {
            "messages": self._get_message_objects(),  # Recupera todos los mensajes del historial
        }
        
        # Agregar nuevo mensaje del usuario
        user_message = HumanMessage(content=user_input)
        current_state["messages"].append(user_message)
        self._add_to_history(user_message)
        
        # Ejecutar el grafo
        result = self.compiled_graph.invoke(
            current_state,
            config=RunnableConfig(configurable={"user_id": "some_user_id"})
        )
        
        # Agregar respuesta al historial y actualizar estado
        if result["messages"] and len(result["messages"]) > len(current_state["messages"]):
            self._add_to_history(result["messages"][-1])
        
        return result

    def get_full_history(self) -> List[Dict[str, Any]]:
        """Devuelve el historial completo de la conversación"""
        return self.conversation_history
    
    def get_last_message(self) -> Dict[str, Any]:
        """Devuelve el último mensaje del historial"""
        return self.conversation_history[-1]
