from fastapi import FastAPI, HTTPException, Depends, Request, Form, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import httpx
import os
import json
import logging
import glob
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_sqlite import get_db, User, EnglishModule, UserProgress, create_tables
import auth

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat IA API")

# Configurar CORS
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

# Modelos de datos para autenticación
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str

# Modelos de datos para el chat
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

# Modelo para respuestas de módulos
class ModuleResponse(BaseModel):
    id: int
    level: str
    title: str
    description: str
    completed: Optional[bool] = False

# Modelo para marcar un módulo como completado
class ModuleCompletionRequest(BaseModel):
    module_id: int

# Cargar comportamientos al iniciar la aplicación y crear tablas de la base de datos
@app.on_event("startup")
async def startup_db_client():
    global agent_behaviors_cache
    agent_behaviors_cache = load_agent_behaviors()
    logger.info(f"Comportamientos de agentes cargados: {list(agent_behaviors_cache.keys())}")
    create_tables()
    logger.info("Tablas de la base de datos creadas")

# Endpoint para registrar un nuevo usuario
@app.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el usuario ya existe
        if User.get_by_username(db, user_data.username):
            raise HTTPException(
                status_code=400,
                detail="El nombre de usuario ya está en uso"
            )
        
        if User.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=400,
                detail="El correo electrónico ya está registrado"
            )
        
        # Crear nuevo usuario
        user = User.create(db, user_data.username, user_data.email, user_data.password)
        
        # Generar token de acceso
        access_token = auth.create_access_token(
            data={"sub": user.username}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Error al registrar el usuario. Verifica los datos."
        )
    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la solicitud"
        )

# Endpoint para iniciar sesión
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para obtener información del usuario actual
@app.get("/users/me", response_model=UserInfo)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

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
async def chat(request: ChatRequest, current_user: User = Depends(auth.get_current_user)):
    # Permitir chat como invitado o usuario autenticado
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

# Endpoint para obtener todos los módulos
@app.get("/modules", response_model=List[ModuleResponse])
async def get_all_modules(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """Devuelve todos los módulos disponibles e indica cuáles ha completado el usuario"""
    modules = EnglishModule.get_all(db)
    
    # Si hay un usuario autenticado, obtener sus módulos completados
    completed_modules = []
    if current_user:
        result = UserProgress.get_user_completed_modules(db, current_user.id)
        completed_modules = [row[0] for row in result]  # Extraer solo los IDs
    
    # Marcar los módulos completados
    response_modules = []
    for module in modules:
        module_dict = {
            "id": module.id,
            "level": module.level,
            "title": module.title,
            "description": module.description,
            "completed": module.id in completed_modules
        }
        response_modules.append(module_dict)
        
    return response_modules

# Endpoint para obtener módulos por nivel
@app.get("/modules/{level}", response_model=List[ModuleResponse])
async def get_modules_by_level(level: str, db: Session = Depends(get_db)):
    """Devuelve los módulos de un nivel específico"""
    modules = EnglishModule.get_by_level(db, level)
    if not modules:
        raise HTTPException(status_code=404, detail=f"No se encontraron módulos para el nivel {level}")
    return modules

# Endpoint para marcar un módulo como completado
@app.post("/modules/complete")
async def mark_module_completed(
    request: ModuleCompletionRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth.get_current_user)
):
    """Marca un módulo como completado por el usuario"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Debe estar autenticado")
    
    # Verificar que el módulo exista
    module = db.query(EnglishModule).filter(EnglishModule.id == request.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    
    # Marcar como completado
    progress = UserProgress.mark_completed(db, current_user.id, request.module_id)
    
    return {"status": "success", "message": "Módulo marcado como completado"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 