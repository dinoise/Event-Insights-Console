import json

from typing import Annotated, TypedDict, Union, Dict, Any, List

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from datetime import datetime

from .assistant_template import AssistantTemplate

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
    def _semmantic_search_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo principal del chatbot que usa la LLM"""
        
        state_mgs = state["messages"]

        input_prompt = (
            "Usa una busqueda semantica para obtener el dataset y la tabla donde están localizados los datos\n"
            f"Mensajes: {state_mgs}"
        )

        response = self.llm_with_tools.invoke([input_prompt])

        print(f"response {response}")

        return {"messages": [response]}
    
    def _bigquery_search_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo que formatea la salida de herramientas a Markdown"""
        last_msg = state["messages"][-1].content
        
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
        
        response = self.llm_with_tools.invoke([input_prompt])
        return {"messages": response}
    
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
        
        response = self.llm_with_tools.invoke([input_prompt])
        return {"messages": response}
    
    ##################################
    # Functions of functionalitites  #
    ##################################
    def create_graph(self) -> None:
        """Crea el grafo con los nodos necesarios"""
        # Creating the graph
        graph_builder = StateGraph(AgentState)
        
        # Nodes
        graph_builder.add_node("semmantic_search", self._semmantic_search_node)
        graph_builder.add_node("bigquery_search", self._bigquery_search_node)
        graph_builder.add_node("formatter", self._formatter_node)
        
        # Tool node
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)

        # Edges
        graph_builder.add_edge(START, "semmantic_search")
        graph_builder.add_edge("tools", "semmantic_search")
        graph_builder.add_conditional_edges("semmantic_search", 
                                            tools_condition)
        # graph_builder.add_edge("semmantic_search", "formatter")
        graph_builder.add_edge("semmantic_search", END)
        
        # Saving the graph
        self.graph = graph_builder
    
    def compile_graph(self) -> None:
        """Compila el grafo para su ejecución"""
        if self.graph is None:
            self.create_graph()
        self.compiled_graph = self.graph.compile()
    
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
