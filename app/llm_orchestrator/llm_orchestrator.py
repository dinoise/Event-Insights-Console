import uuid
import asyncio

from typing import Any, Dict, Optional, List
from aiohttp import ClientSession, TCPConnector
from langchain.chat_models import init_chat_model

from .user_graph import UserGraph
from .tools import initialize_tools

class LLMOrchestrator:
    def __init__(self, model_name: str):
        self._user_sessions: Dict[str, UserGraph] = {}
        self.model_name = model_name
        self.connector = None
        self.client_session = None
        print(f"Model loaded: {self.model_name}")
    
    async def initialize(self):
        """Inicializa la sesión HTTP (aiohttp)"""
        self.connector = TCPConnector(limit=100)

        self.client_session = ClientSession(
            connector=self.connector,
            connector_owner=False,
            headers={},
            raise_for_status=True,
        )
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.client_session:
            await self.client_session.close()
        if self.connector:
            await self.connector.close()
    
    def get_user_session(self, session_id: str) -> Optional[UserGraph]:
        """Obtiene la sesión de usuario existente"""
        return self._user_sessions.get(session_id)
    
    def user_session_exists(self, session_id: str) -> bool:
        """Verifica si existe una sesión de usuario"""
        return session_id in self._user_sessions
    
    def user_session_create_sync(self, session_data: dict) -> str:
        """Versión síncrona para usar en rutas Flask normales"""
        return asyncio.run(self.user_session_create(session_data))
    
    async def user_session_create(self, session_data: Dict[str, Any] = None) -> str:
        """Crea una nueva sesión de usuario y devuelve su ID"""
        print("Crear session!")
        session_id = str(uuid.uuid4())
        print(f"Creating session {session_id}")

        print(f"Initializing llm...")
        # Inicializar modelo y herramientas
        llm = init_chat_model(self.model_name)
        print(f"Done!")
        
        print(f"Initializing tools...")
        tools = await self._initialize_tools()
        print(f"Done!")
        
        print("Creting graph...")
        # Crear grafo de usuario
        user_graph = UserGraph(llm=llm, tools=tools)
        user_graph.create_graph()
        print(f"Done!")

        print(f"Compiling graph")
        user_graph.compile_graph()
        print(f"Done!")
        
        # Guardar sesión
        self._user_sessions[session_id] = user_graph

        print(f"Session {session_id} created!")
        
        return session_id
    
    async def _initialize_tools(self) -> list:
        """Inicializa las herramientas para el agente"""
        
        return initialize_tools(self.client_session)
    
    def get_full_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Procesa un mensaje del usuario a través del grafo"""
        if not self.user_session_exists(session_id):
            session_id = self.user_session_create_sync()
        
        user_graph = self.get_user_session(session_id)
        
        # Obtener historial para la respuesta
        history = user_graph.get_full_history()
        
        return history

    async def process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Procesa un mensaje del usuario a través del grafo"""
        if not self.user_session_exists(session_id):
            session_id = await self.user_session_create()
        
        user_graph = self.get_user_session(session_id)
        current_state = user_graph.initial_state  # En una implementación real, recuperarías el estado actual
        
        # Procesar el mensaje
        new_state = await user_graph.invoke_graph(user_input, current_state)
        
        # Obtener historial para la respuesta
        history = user_graph.get_conversation_history(new_state)
        
        return {
            "session_id": session_id,
            "response": history[-1]["data"]["content"] if history else "",
            "history": history,
            "user_info": new_state["user_info"]
        }