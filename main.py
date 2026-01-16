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

# TTS imports
from TTS.api import TTS
from voice_selector import select_voice
from voice_config import DEFAULT_MODEL, DEFAULT_SPEAKER

load_dotenv()

app = FastAPI(title="Soven API")

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
    if request.url.path in ["/", "/api/health"]:
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
        return {"device_id": device_id}
    except Exception as e:
        conn.rollback()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
