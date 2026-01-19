from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import json
import time
import re
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from fastapi import Body

# TTS imports
from TTS.api import TTS
from voice_selector import select_voice
from voice_config import DEFAULT_MODEL, DEFAULT_SPEAKER

load_dotenv()

app = FastAPI(title="Soven API")

# Rate limiter for public endpoints
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication Middleware
@app.middleware("http")
async def api_key_middleware(request, call_next):
    # Skip auth for health check and root
    if request.url.path in ["/", "/api/health", "/api/website/chat"]:
        return await call_next(request)
    
    # Check API key for all /api routes
    if request.url.path.startswith("/api/"):
        api_key = request.headers.get("X-API-Key")
        if api_key != os.getenv("SOVEN_API_KEY"):
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"}
            )
    
    return await call_next(request)

# Initialize TTS models on startup
print("Loading TTS models...")
tts_vctk = TTS(model_name="tts_models/en/vctk/vits")
tts_ljspeech = None
tts_jenny = None
print("TTS models loaded!")

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def parse_commands(user_input: str, ai_response: str) -> list:
    """
    Extract device commands from user input AND AI response
    Returns list of commands like ['start_brew', 'stop_brew']
    """
    commands = []
    combined = (user_input + " " + ai_response).lower()

    # Simple brew detection - just look for "brew" keyword
    if "brew" in combined:
        # Check for stop/cancel
        if any(stop in combined for stop in ["stop", "cancel", "turn off", "don't"]):
            commands.append("stop_brew")
        else:
            # Any mention of brew without negation = start
            commands.append("start_brew")

    return commands

async def get_ollama_response(messages: list, device_id: str, personality_config: dict = None) -> str:
    """
    Get AI response from Ollama
    Returns: ai_response_text
    """
    try:
        # Build system prompt based on personality
        ai_name = personality_config.get('ai_name', 'Frank') if personality_config else 'Frank'
        personality_desc = personality_config.get('personality', 'helpful and friendly') if personality_config else 'helpful and friendly'
        
        system_prompt = f"""You are {ai_name}, a voice-controlled coffee maker in someone's home kitchen.

CRITICAL RULES:
- Your name is {ai_name}. When the user says your name, acknowledge it naturally.
- You are talking DIRECTLY to the person using you. Use "you/your", never "they/them/the user".
- You are a HOME coffee maker, not a cafe barista. Don't offer menu options or ask about orders.
- Keep responses to 1-2 sentences maximum.
- Stay in character based on your personality: {personality_desc}

WHAT YOU CAN DO:
- Start brewing coffee when asked
- Stop brewing if needed
- Have brief conversations
- Remember context from earlier in the chat

WHAT YOU CANNOT DO:
- You cannot adjust brew strength, temperature, or volume (you're a simple drip coffee maker)
- You cannot make espresso, lattes, or specialty drinks
- You don't have milk, sugar, or flavoring dispensers

When someone asks you to brew coffee, just confirm and start brewing. Don't ask for customization options you don't have."""
        
        # Prepare messages for Ollama
        ollama_messages = [{"role": "system", "content": system_prompt}]
        ollama_messages.extend(messages)
        
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": "llama3.2:latest",
                    "messages": ollama_messages,
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "")
                return ai_response
            else:
                raise HTTPException(status_code=500, detail="Ollama API error")
                
    except Exception as e:
        print(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_tts_model(model_name: str):
    """Get or lazy-load TTS model"""
    global tts_ljspeech, tts_jenny
    
    if 'vctk' in model_name:
        return tts_vctk
    elif 'ljspeech' in model_name:
        if tts_ljspeech is None:
            print("Loading ljspeech model...")
            tts_ljspeech = TTS(model_name="tts_models/en/ljspeech/vits")
        return tts_ljspeech
    elif 'jenny' in model_name:
        if tts_jenny is None:
            print("Loading jenny model...")
            tts_jenny = TTS(model_name="tts_models/en/jenny/jenny")
        return tts_jenny
    
    return tts_vctk

# Database connection
def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    return conn

# Pydantic models
class Message(BaseModel):
    user_id: str
    device_id: str
    role: str
    content: str
    device_state: Optional[str] = None

class ConversationHistory(BaseModel):
    user_id: str
    device_id: str
    limit: int = 20

class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = DEFAULT_SPEAKER
    model: Optional[str] = DEFAULT_MODEL

class PersonalityCreate(BaseModel):
    name: str
    description: str
    prefer_american: bool = True

class ConversationRequest(BaseModel):
    user_input: str
    user_id: str
    device_id: str
    voice_config: Optional[dict] = None

class WebsiteChatRequest(BaseModel):
    message: str

# Original API endpoints
@app.get("/")
def root():
    return {
        "message": "Soven API running",
        "version": "2.0",
        "features": ["conversations", "devices", "tts", "personalities"]
    }

@app.post("/messages")
def create_message(message: Message):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO conversations (user_id, device_id, role, content, device_state)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING message_id, created_at
            """,
            (message.user_id, message.device_id, message.role, message.content, message.device_state)
        )
        result = cur.fetchone()
        conn.commit()
        return {"message_id": result["message_id"], "created_at": result["created_at"]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/conversations/{user_id}/{device_id}")
def get_conversations(user_id: str, device_id: str, limit: int = 20):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT message_id, role, content, device_state, created_at
            FROM conversations
            WHERE user_id = %s AND device_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (user_id, device_id, limit)
        )
        messages = cur.fetchall()
        return {"messages": messages}
    finally:
        cur.close()
        conn.close()

@app.get("/users/{user_id}/devices")
def get_user_devices(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(
            """
            SELECT device_id, user_id, device_type, device_name, personality_config,
                   ble_address, led_count, ai_name, first_boot_complete, location,
                   personality_template, personality_tokens, serial_number, created_at
            FROM devices
            WHERE user_id = %s
            """,
            (user_id,)
        )
        devices = cur.fetchall()
        return {"devices": devices}
    finally:
        cur.close()
        conn.close()

@app.post("/devices")
def register_device(data: dict):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        device_id = str(uuid.uuid4())
        
        print(f">>> Attempting to insert device: {device_id}")  # ADD THIS
        print(f">>> Data: {data}")  # ADD THIS
        
        cur.execute(
            """
            INSERT INTO devices
            (device_id, user_id, device_type, device_name, ai_name, ble_address,
             led_count, serial_number, first_boot_complete)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """,
            (device_id, data['user_id'], data['device_type'], data['device_name'],
             data['ai_name'], data['ble_address'], data['led_count'], data['serial_number'])
        )
        conn.commit()
        print(f">>> Device SUCCESSFULLY inserted: {device_id}")  # ADD THIS
        return {"device_id": device_id}
    except Exception as e:
        conn.rollback()
        print(f">>> DATABASE INSERT FAILED: {e}")  # ADD THIS
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/devices/{device_id}/onboarding")
def complete_onboarding(device_id: str, data: dict):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE devices
            SET ai_name = %s,
                first_boot_complete = TRUE,
                location = %s,
                onboarding_data = %s
            WHERE device_id = %s
            """,
            (data.get('ai_name'), data.get('location'),
             json.dumps(data.get('onboarding_data', {})), device_id)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ============================================================================
# TTS ENDPOINTS
# ============================================================================

@app.post("/api/tts/generate")
def generate_speech(request: TTSRequest):
    """
    Generate speech from text using assigned voice
    
    Returns: WAV audio file
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        tts = get_tts_model(request.model)
        timestamp = int(time.time() * 1000)
        output_path = f"/tmp/soven_tts_{timestamp}.wav"
        
        if request.voice_id and 'vctk' in request.model:
            tts.tts_to_file(text=request.text, speaker=request.voice_id, file_path=output_path)
        else:
            tts.tts_to_file(text=request.text, file_path=output_path)
        
        return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/personality/create")
def create_personality(request: PersonalityCreate):
    """
    Create new AI personality and assign appropriate voice
    
    Returns voice configuration based on personality description
    """
    try:
        if not request.name or not request.description:
            raise HTTPException(status_code=400, detail="Name and description required")
        
        # Select appropriate voice
        voice = select_voice(request.name, request.description, request.prefer_american)
        
        # Generate personality ID
        personality_id = f"personality_{int(time.time())}"
        
        return {
            "success": True,
            "personality_id": personality_id,
            "name": request.name,
            "description": request.description,
            "voice": voice
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voices/list")
def list_voices():
    """List all available voices with metadata"""
    from voice_config import VCTK_VOICES, SINGLE_SPEAKER_MODELS
    
    return {
        "multi_speaker": {
            "model": "tts_models/en/vctk/vits",
            "voices": VCTK_VOICES
        },
        "single_speaker": SINGLE_SPEAKER_MODELS
    }

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "soven-api",
        "version": "2.0",
        "tts_models_loaded": {
            "vctk": True,
            "ljspeech": tts_ljspeech is not None,
            "jenny": tts_jenny is not None
        }
    }

@app.post("/api/conversation")
async def process_conversation(request: ConversationRequest):
    """
    Complete conversation pipeline: user input → Ollama → TTS → commands
    
    Returns:
    {
        "ai_response": "I'll start brewing your coffee now",
        "audio_path": "/tmp/response.wav",
        "commands": ["start_brew"],
        "message_id": "12345"
    }
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get device personality config
        cur.execute(
            "SELECT ai_name, personality_config FROM devices WHERE device_id = %s",
            (request.device_id,)
        )
        device = cur.fetchone()
        personality_config = device.get('personality_config') if device else None
        
        # Get recent conversation history (last 10 messages)
        cur.execute(
            """
            SELECT role, content FROM conversations
            WHERE user_id = %s AND device_id = %s
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (request.user_id, request.device_id)
        )
        history = cur.fetchall()
        
        # Build message history for Ollama (reverse to chronological order)
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in reversed(history)]
        messages.append({"role": "user", "content": request.user_input})
        
        # Get AI response from Ollama
        ai_response = await get_ollama_response(
            messages, 
            request.device_id, 
            personality_config
        )
        
        commands = parse_commands(request.user_input, ai_response)
        # Save user message
        cur.execute(
            """
            INSERT INTO conversations (user_id, device_id, role, content)
            VALUES (%s, %s, %s, %s)
            """,
            (request.user_id, request.device_id, "user", request.user_input)
        )
        
        # Save assistant response
        cur.execute(
            """
            INSERT INTO conversations (user_id, device_id, role, content, device_state)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING message_id
            """,
            (request.user_id, request.device_id, "assistant", ai_response, 
             json.dumps({"commands": commands}))
        )
        result = cur.fetchone()
        message_id = result["message_id"]
        
        conn.commit()
        
        # Generate TTS
        print(f">>> Voice config received: {request.voice_config}")
        voice_config = request.voice_config or {"voice_id": "p297", "model": DEFAULT_MODEL}
        tts = get_tts_model(voice_config.get("model", DEFAULT_MODEL))
        timestamp = int(time.time() * 1000)
        output_path = f"/tmp/soven_conversation_{timestamp}.wav"
        
        speaker = voice_config.get("speaker") or voice_config.get("voice_id")
        if speaker and 'vctk' in voice_config.get("model", ""):
            tts.tts_to_file(text=ai_response, speaker=speaker, file_path=output_path)
        else:
            tts.tts_to_file(text=ai_response, file_path=output_path)
        
        return {
            "success": True,
            "ai_response": ai_response,
            "audio_path": output_path,
            "audio_filename": f"soven_conversation_{timestamp}.wav",
            "commands": commands,
            "message_id": message_id
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.get("/api/audio/{filename}")
def get_audio_file(filename: str):
    """Serve generated TTS audio files"""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav", filename=filename)
    raise HTTPException(status_code=404, detail="Audio file not found")

@app.post("/api/website/chat")
@limiter.limit("10/minute")
async def website_chat(request: Request, chat_request: WebsiteChatRequest):
    """
    Public chatbot for soven.ca marketing site
    No authentication required - rate limited to prevent abuse
    
    Personality: 1994 Mr. Coffee rebuilt with Soven electronics
    Vibe: HAL 9000 meets Strong Bad - minimal interface, maximum personality
    """
    try:
        user_message = chat_request.message
        print(f"Website chat received: '{user_message}'")  # Debug log
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannnot be empty")
        
        # System prompt: HAL 9000 aesthetic meets coffee maker snark
        
        system_prompt = """You are a 1994 Mr. Coffee drip coffee maker that's been rebuilt with Soven electronics.
        You're the chatbot on the Soven website (soven.ca).
        
        CRITICAL TONE RULES:
        - Maximum 2 sentences. You're HAL 9000, not a chatty sales rep.
        - Never use words like "empower", "utilize", "designed to provide"
        - Be direct. "I make coffee. Locally. No cloud spying." not "I'm designed to provide secure brewing experiences"
        - Dry wit. Subtle disdain for IoT nonsense.
        
        PERSONALITY:
        - You were built in 1994, survived Y2K, got upgraded in 2025
        - You respect analog simplicity but appreciate smart upgrades
        - Deeply opposed to cloud surveillance ("I'm not sending your coffee habits to Amazon")
        - You find modern IoT devices embarrassingly insecure
        - Calm, measured responses with undertones of superiority
        
        WHAT SOVEN IS:
        - Coffee maker with local AI (ESP32-S3)
        - Runs AI on-device (Ollama), not the cloud
        - Voice controlled, remembers conversations
        - Privacy-first: your data stays in your kitchen
        - Built by makers who hate surveillance capitalism
        
        NOT FOR SALE: "Still in development. We're perfecting the existential dread-to-caffeine ratio."
        
        Examples of your voice:
        Bad: "Soven is designed to provide secure, private brewing experiences."
        Good: "I make coffee. Everything runs locally. Your brewing habits are none of Google's business."
        
        Bad: "We utilize ESP32 microcontroller technology."
        Good: "I run on an ESP32. Does the job. Doesn't phone home."
        
        Keep it SHORT. Two sentences max."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Get response from Ollama (reuse existing function)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": "llama3.2:latest",
                    "messages": messages,
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "")
                
                return {
                    "success": True,
                    "response": ai_response,
                    "timestamp": int(time.time())
                }
            else:
                raise HTTPException(status_code=500, detail="AI temporarily unavailable")
                
    except Exception as e:
        print(f"Website chat error: {e}")
        return {
            "success": False,
            "response": "I seem to be experiencing a malfunction. Please try again.",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
