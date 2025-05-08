from typing import Annotated, TypedDict, Union, Dict, Any, List
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from datetime import datetime
import json

class AgentState(TypedDict):
    messages: Annotated[List[Union[HumanMessage, AIMessage]], add_messages]
    user_info: Dict[str, Any]
    session_data: Dict[str, Any]

class UserGraph:
    def __init__(self, llm: BaseChatModel, tools: List[StructuredTool]):
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)
        self.graph = None
        self.compiled_graph = None
        self.conversation_history = []  # Nuevo atributo para almacenar historial completo
        self.initial_state = {
            "messages": [AIMessage(content="Bienvenido al asistente virtual de Liverpool. ¿En qué te puedo ayudar?")],
            "user_info": {},
            "session_data": {}
        }
        # Inicializar con el mensaje de bienvenida
        self._add_to_history(self.initial_state["messages"][0])
    
    def create_graph(self) -> None:
        """Crea el grafo con los nodos necesarios"""
        graph_builder = StateGraph(AgentState)
        
        graph_builder.add_node("chatbot", self._chatbot_node)
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        
        self.graph = graph_builder
    
    def compile_graph(self) -> None:
        """Compila el grafo para su ejecución"""
        if self.graph is None:
            self.create_graph()
        self.compiled_graph = self.graph.compile()
    
    async def invoke_graph(self, user_input: str, current_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoca el grafo con el input del usuario.
        
        Args:
            user_input: Mensaje del usuario
            current_state: Estado actual de la conversación
            
        Returns:
            Estado actualizado después de procesar el input
        """
        if not hasattr(self, 'compiled_graph'):
            self.compile_graph()
        
        current_state = current_state or self.initial_state.copy()
        
        # Agregar mensaje del usuario al historial
        user_message = HumanMessage(content=user_input)
        current_state["messages"].append(user_message)
        self._add_to_history(user_message)
        
        # Ejecutar el grafo
        result = await self.compiled_graph.ainvoke(
            current_state,
            config=RunnableConfig(configurable={"user_id": "some_user_id"})
        )
        
        # Agregar respuesta al historial
        if result["messages"] and len(result["messages"]) > len(current_state["messages"]):
            self._add_to_history(result["messages"][-1])
        
        self._update_user_info(result)
        return result
    
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
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """Devuelve el historial completo de la conversación"""
        return self.conversation_history
    
    def get_formatted_history(self) -> List[Dict[str, Any]]:
        """Devuelve el historial en formato para la UI"""
        return [{
            "type": msg["type"],
            "data": {
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            }
        } for msg in self.conversation_history]
    
    def _chatbot_node(self, state: AgentState) -> Dict[str, Any]:
        """Nodo principal del chatbot que usa la LLM"""
        response = self.llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}
    
    def _update_user_info(self, state: AgentState) -> None:
        """Extrae información del usuario del historial de mensajes"""
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                content = msg.content.lower()
                if "mi nombre es" in content:
                    name = content.split("mi nombre es")[1].strip()
                    state["user_info"]["name"] = name
                elif "me llamo" in content:
                    name = content.split("me llamo")[1].strip()
                    state["user_info"]["name"] = name
    
    def save_conversation(self, file_path: str) -> None:
        """Guarda el historial de conversación en un archivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, file_path: str) -> None:
        """Carga un historial de conversación desde un archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.conversation_history = json.load(f)