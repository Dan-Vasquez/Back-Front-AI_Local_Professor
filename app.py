# app.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import os
import json
import logging
import glob

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat IA API")

# Configurar CORS para permitir solicitudes desde el frontend
#Opcional, si el front esta en el mismo dominio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el origen exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio donde se almacenan los comportamientos de los agentes
AGENT_PROMPTS_DIR = "agent_prompts"
# Comportamiento por defecto
DEFAULT_AGENT = "default"

# Caché para almacenar los comportamientos cargados
agent_behaviors_cache: Dict[str, str] = {}

# Función para cargar comportamientos de agentes
def load_agent_behaviors():
    """Carga todos los comportamientos de agentes disponibles"""
    behaviors = {}
    
    # Buscar todos los archivos .txt en el directorio de prompts
    prompt_files = glob.glob(os.path.join(AGENT_PROMPTS_DIR, "*.txt"))
    
    for file_path in prompt_files:
        try:
            # Extraer el nombre del agente del nombre del archivo
            agent_name = os.path.basename(file_path).split('.')[0]
            
            # Leer el contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as file:
                behavior = file.read().strip()
                
            # Almacenar el comportamiento
            behaviors[agent_name] = behavior
            logger.info(f"Comportamiento cargado para el agente: {agent_name}")
            
        except Exception as e:
            logger.error(f"Error al cargar el comportamiento desde {file_path}: {str(e)}")
    
    return behaviors

# Cargar comportamientos al iniciar la aplicación
@app.on_event("startup")
async def startup_db_client():
    global agent_behaviors_cache
    agent_behaviors_cache = load_agent_behaviors()
    logger.info(f"Comportamientos de agentes cargados: {list(agent_behaviors_cache.keys())}")

# Modelos de datos
class Message(BaseModel):
    role: str  # "user", "assistant" o "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model_choice: str  # "local" o "api"
    agent_type: Optional[str] = DEFAULT_AGENT  # Tipo de agente a utilizar
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    model_used: str
    agent_used: str

# Endpoint para obtener los tipos de agentes disponibles
@app.get("/available-agents")
async def get_available_agents():
    """Devuelve la lista de agentes disponibles"""
    return {"agents": list(agent_behaviors_cache.keys())}

# Función para comunicarse con Ollama local
async def query_local_model(messages, agent_type=DEFAULT_AGENT, max_tokens=1000, temperature=0.7):
    try:
        # URL del servidor de Ollama - ajusta según tu configuración
        ollama_url = "http://localhost:11434/api/chat"
        
        # Agregar el mensaje del sistema si se especifica un tipo de agente
        formatted_messages = []
        
        # Agregar comportamiento del agente como mensaje del sistema
        agent_behavior = agent_behaviors_cache.get(agent_type, agent_behaviors_cache.get(DEFAULT_AGENT, ""))
        if agent_behavior:
            formatted_messages.append({"role": "system", "content": agent_behavior})
        
        # Agregar el resto de mensajes
        formatted_messages.extend([{"role": msg.role, "content": msg.content} for msg in messages])
        
        # Crear payload para Ollama
        payload = {
            "model": "llama3.2",  # Ajusta según el modelo que tengas instalado
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=payload, timeout=60.0)
            
            if response.status_code != 200:
                logger.error(f"Error en la respuesta de Ollama: {response.text}")
                raise HTTPException(status_code=500, detail="Error al comunicarse con el modelo local")
            
            result = response.json()
            return result["message"]["content"]
            
    except Exception as e:
        logger.error(f"Error al consultar el modelo local: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al consultar el modelo local: {str(e)}")

# Función para comunicarse con una API gratuita (ejemplo con NLP Cloud)
async def query_api_model(messages, agent_type=DEFAULT_AGENT, max_tokens=1000, temperature=0.7):
    try:
        # En este ejemplo usaremos NLP Cloud que ofrece un nivel gratuito
        # Necesitarás registrarte para obtener una API key
        api_url = "https://api.nlpcloud.io/v1/gpu/falcon-7b-instruct/chatbot"
        
        # Agregar comportamiento del agente
        agent_behavior = agent_behaviors_cache.get(agent_type, agent_behaviors_cache.get(DEFAULT_AGENT, ""))
        
        # Convertir mensajes al formato esperado por la API
        conversation = []
        
        # Agregar el comportamiento del agente como un mensaje del sistema
        if agent_behavior:
            conversation.append({"input": f"INSTRUCCIONES DEL SISTEMA: {agent_behavior}"})
            conversation.append({"output": "Entendido, seguiré estas instrucciones."})
        
        # Agregar el resto de mensajes
        for msg in messages:
            if msg.role == "user":
                conversation.append({"input": msg.content})
            else:
                conversation.append({"output": msg.content})
                
        # Verificar que haya al menos un mensaje para enviar
        if not conversation:
            raise HTTPException(status_code=400, detail="No hay mensajes para procesar")
            
        payload = {
            "input": messages[-1].content if messages[-1].role == "user" else "",
            "history": conversation[:-1] if messages[-1].role == "user" else conversation,
            "temperature": temperature,
            "max_length": max_tokens
        }
        
        # Necesitarás una API key
        # Para fines de demostración, esto podría estar en variables de entorno
        api_key = os.getenv("NLPCLOUD_API_KEY", "tu_api_key_aquí")
        
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, headers=headers, timeout=60.0)
            
            if response.status_code != 200:
                logger.error(f"Error en la respuesta de la API: {response.text}")
                raise HTTPException(status_code=500, detail="Error al comunicarse con la API del modelo")
            
            result = response.json()
            return result["response"]
            
    except Exception as e:
        logger.error(f"Error al consultar la API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la API: {str(e)}")

# Endpoint para el chat
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Verificar si el tipo de agente existe
        agent_type = request.agent_type
        if agent_type not in agent_behaviors_cache:
            logger.warning(f"Tipo de agente no encontrado: {agent_type}. Usando el agente por defecto.")
            agent_type = DEFAULT_AGENT
            
        if request.model_choice == "local":
            response_text = await query_local_model(
                request.messages, 
                agent_type=agent_type,
                max_tokens=request.max_tokens, 
                temperature=request.temperature
            )
            return ChatResponse(
                response=response_text, 
                model_used="Ollama - Llama 3.2",
                agent_used=agent_type
            )
            
        elif request.model_choice == "api":
            response_text = await query_api_model(
                request.messages, 
                agent_type=agent_type,
                max_tokens=request.max_tokens, 
                temperature=request.temperature
            )
            return ChatResponse(
                response=response_text, 
                model_used="API - NLP Cloud",
                agent_used=agent_type
            )
            
        else:
            raise HTTPException(status_code=400, detail="Opción de modelo no válida. Use 'local' o 'api'")
            
    except Exception as e:
        logger.error(f"Error en el endpoint de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento del chat: {str(e)}")

# Endpoint de verificación de estado
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "El servidor está funcionando correctamente"}

# Endpoint para verificar disponibilidad del modelo local
@app.get("/check-local-model")
async def check_local_model():
    try:
        # Verifica si Ollama está disponible
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            
        if response.status_code == 200:
            models = response.json().get("models", [])
            llama_available = any(model.get("name", "").startswith("llama3.2") for model in models)
            
            if llama_available:
                return {"status": "available", "message": "Llama 3.2 está disponible localmente"}
            else:
                return {"status": "unavailable", "message": "Llama 3.2 no está disponible. Verifica tu instalación de Ollama"}
        else:
            return {"status": "error", "message": "No se pudo conectar con Ollama"}
            
    except Exception as e:
        return {"status": "error", "message": f"Error al verificar el modelo local: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)