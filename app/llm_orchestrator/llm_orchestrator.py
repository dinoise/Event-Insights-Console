import uuid
from typing import Any, Dict, Optional, List
from vertexai import agent_engines

class LLMOrchestrator:
    def __init__(self, resource_id: str):
        self._user_sessions: Dict[str, Any] = {}  # Ahora almacenará las sesiones de ADK
        self.remote_app = agent_engines.get(resource_id)
        print(f"Conectado al agente remoto: {resource_id}")
        
    def get_user_session(self, session_id: str) -> Optional[Any]:
        """Obtiene la sesión de usuario existente"""
        return self._user_sessions.get(session_id)
    
    def user_session_exists(self, session_id: str) -> bool:
        """Verifica si existe una sesión de usuario"""
        return session_id in self._user_sessions
    
    def user_session_reset(self, session_id: str) -> None:
        """Reinicia una sesión de usuario"""
        if not self.user_session_exists(session_id):
            session_id = self.user_session_create()
            return
        
        # Con ADK, podrías crear una nueva sesión o limpiar el historial
        del self._user_sessions[session_id]
        self._user_sessions[session_id] = self._create_adk_session(session_id)
        
    def user_session_create(self) -> str:
        """Crea una nueva sesión de usuario y devuelve su ID"""
        session_id = str(uuid.uuid4())
        print(f"Creando nueva sesión ADK: {session_id}")
        
        # Crear y almacenar la sesión ADK
        self._user_sessions[session_id] = self._create_adk_session(session_id)
        
        return session_id
    
    def _create_adk_session(self, session_id: str) -> Any:
        """Crea una sesión en el agente remoto de ADK"""
        remote_session = self.remote_app.create_session(user_id=session_id)
        return remote_session
    
    def _extract_response_text(self, response_events):
        """Extrae texto de respuesta y busca imágenes en los eventos"""
        response_text = ""
        image_data = []
        
        for event in response_events:
            # Buscar texto en las partes del contenido
            if 'content' in event and 'parts' in event['content']:
                for part in event['content']['parts']:
                    if 'text' in part:
                        response_text += part['text'] + "\n"

            if 'actions' in event and 'artifact_delta' in event['actions']:
                artifacts = event['actions']['artifact_delta']
                print("artifact delta", artifacts)
                for artifact_name, artifact_value in artifacts.items():
                    print("artifact_name", artifact_name)
                    image_data.append(artifact_name)
        
        if image_data:
            # Si encontramos una imagen, la devolvemos junto con el texto
            return {
                "text": response_text.strip(),
                "image": image_data  # Esto sería los datos binarios de la imagen
            }
        
        return response_text.strip()
            
    def process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Envía un mensaje al agente ADK y procesa la respuesta"""
        if not self.user_session_exists(session_id):
            session_id = self.user_session_create()
        
        remote_session = self.get_user_session(session_id)
        
        # Enviar mensaje al agente remoto
        response_events = []
        try:
            for event in self.remote_app.stream_query(
                user_id=session_id,
                session_id=remote_session['id'],
                message=user_input,
            ):
                print("EVENT ===> ", event)
                response_events.append(event)
            
            # Extraer respuesta (puede incluir texto e imagen)
            response = self._extract_response_text(response_events)
            
            if isinstance(response, dict) and 'image' in response:
                # Si hay imagen, devolverla junto con el texto
                return {
                    "type": "ai",
                    "content": response["text"],
                    "contentType": "img",
                    "image": response["image"],
                    "metadata": {}
                }
            else:
                # Solo texto
                return {
                    "type": "ai",
                    "content": response,
                    "metadata": {}
                }
                
        except Exception as e:
            print(f"Error en process_message: {e}")
            return {
                "type": "error",
                "data": "Lo siento, ocurrió un error al procesar tu mensaje",
                "metadata": {"error": str(e)}
            }

    def get_full_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de la conversación"""
        if not self.user_session_exists(session_id):
            return []
        
        # ADK no proporciona historial completo directamente, 
        # podrías implementar un caché local si lo necesitas
        return [{
            "type": "info",
            "content": "El historial completo no está disponible con ADK",
            "metadata": {}
        }]