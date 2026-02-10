import asyncio
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect
import logging
import json

logger = logging.getLogger(__name__)

class DeviceAudioSession:
    """Handles WebSocket audio streaming from Tier 1 devices"""
    
    def __init__(self, websocket: WebSocket, device_id: str, db_conn):
        self.websocket = websocket
        self.device_id = device_id
        self.db = db_conn
        self.audio_chunks = []
        self.sample_rate = 16000
        self.recording = False
        
        # Load device personality from database
        self.device_profile = None
        self.ai_name = None
        self.dna_parameters = None
        self.voice_config = None
        self.narrative_context = None
        
    async def handle_session(self):
        """Main WebSocket loop"""
        await self.websocket.accept()
        logger.info(f"[WS] Device audio session started: {self.device_id}")
        
        try:
            # Load device profile
            await self.load_device_profile()
            
            # Send personality info to device
            await self.websocket.send_json({
                "type": "personality_loaded",
                "ai_name": self.ai_name,
                "sleep_enabled": True
            })
            
            while True:
                message = await self.websocket.receive()
                
                if 'bytes' in message:
                    # Audio chunk from device
                    await self.handle_audio_chunk(message['bytes'])
                    
                elif 'text' in message:
                    # Control message
                    text = message['text']
                    
                    if text == 'AUDIO_END':
                        await self.process_complete_audio()
                    elif text.startswith('{'):
                        # JSON command
                        cmd = json.loads(text)
                        await self.handle_command(cmd)
                        
        except WebSocketDisconnect:
            logger.info(f"[WS] Device disconnected: {self.device_id}")
        except Exception as e:
            logger.error(f"[WS] Session error: {e}", exc_info=True)
    async def load_device_profile(self):
        """Load device personality from database"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                d.ai_name,
                dna.anxiety_threshold,
                dna.service_orientation,
                dna.resilience,
                eo.narrative_context
            FROM devices d
            LEFT JOIN entity_dna dna ON d.device_id = dna.device_id
            LEFT JOIN entity_origins eo ON d.device_id = eo.device_id
            WHERE d.device_id = %s
        """, (self.device_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            self.ai_name = row[0]
            self.narrative_context = row[4]
            
            # Build DNA parameters dict
            self.dna_parameters = {
                'anxiety_threshold': row[1],
                'service_orientation': row[2],
                'resilience': row[3]
            }
            
            # Voice config from devices table
            self.voice_config = {} #TODO: get from personality download endpoint
            
            logger.info(f"[WS] Loaded profile for {self.ai_name}")
        else:
            logger.warning(f"[WS] No profile found for {self.device_id}")
            self.ai_name = "Assistant"
            self.voice_config = {
            "type": "multi_speaker",
            "model": "tts_models/en/vctk/vits",
            "speaker": "p297"
            }
            self.narrative_context = None
            self.dna_parameters = None
            
    async def handle_audio_chunk(self, chunk: bytes):
        """Accumulate audio chunks"""
        self.audio_chunks.append(chunk)
        
        if not self.recording:
            self.recording = True
            logger.info(f"[WS] Started receiving audio from {self.device_id}")
            
    async def handle_command(self, cmd: dict):
        """Handle JSON commands from device"""
        cmd_type = cmd.get('type')
        
        if cmd_type == 'device_hello':
            logger.info(f"[WS] Device hello: {cmd}")
            self.device_id = cmd.get('device_id', self.device_id)
            await self.load_device_profile()
            
    async def process_complete_audio(self):
        """Process accumulated audio and respond"""
        if not self.audio_chunks:
            logger.warning(f"[WS] No audio to process")
            return
            
        # Combine chunks
        audio_data = b''.join(self.audio_chunks)
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        duration = len(audio_np) / self.sample_rate
        logger.info(f"[WS] Processing {duration:.1f}s of audio from {self.device_id}")
        
        try:
            # 1. Speech-to-Text
            transcript = await self.transcribe_audio(audio_np)
            logger.info(f"[WS] Transcript: '{transcript}'")
            
            if not transcript or len(transcript.strip()) < 3:
                logger.info(f"[WS] Empty or too short transcript")
                await self.websocket.send_json({"type": "no_wake_word"})
                self.audio_chunks = []
                self.recording = False
                return
            
            # 2. Validate wake word
            if not self.validate_wake_word(transcript):
                logger.info(f"[WS] No wake word detected in: {transcript}")
                await self.websocket.send_json({"type": "no_wake_word"})
                self.audio_chunks = []
                self.recording = False
                return
            
            # 3. Extract command (remove wake word)
            command = self.extract_command(transcript)
            logger.info(f"[WS] Command: '{command}'")
            
            # 4. Generate response with Ollama
            ai_response = await self.generate_response(command)
            logger.info(f"[WS] AI Response: '{ai_response}'")
            
            # 5. Generate TTS
            audio_bytes = await self.generate_tts(ai_response)
            
            # 6. Stream audio back to device
            await self.stream_audio_to_device(audio_bytes)
            
            # 7. Signal completion
            await self.websocket.send_json({"type": "audio_end"})
            
        except Exception as e:
            logger.error(f"[WS] Processing error: {e}", exc_info=True)
            
        finally:
            # Reset for next utterance
            self.audio_chunks = []
            self.recording = False
            
    def validate_wake_word(self, transcript: str) -> bool:
        """Check if wake word (AI name) is present"""
        transcript_lower = transcript.lower()
        wake_words = [
            self.ai_name.lower(),
            f"hey {self.ai_name.lower()}",
            f"hi {self.ai_name.lower()}",
            f"hello {self.ai_name.lower()}"
        ]
        
        return any(wake in transcript_lower for wake in wake_words)
        
    def extract_command(self, transcript: str) -> str:
        """Remove wake word from transcript"""
        transcript_lower = transcript.lower()
        ai_name_lower = self.ai_name.lower()
        
        # Remove common wake patterns
        patterns = [
            f"hey {ai_name_lower}",
            f"hi {ai_name_lower}",
            f"hello {ai_name_lower}",
            ai_name_lower
        ]
        
        command = transcript_lower
        for pattern in patterns:
            command = command.replace(pattern, "").strip()
            
        # If nothing left, return generic prompt
        if len(command) < 3:
            command = "yes?"
            
        return command
        
    async def transcribe_audio(self, audio_np: np.ndarray) -> str:
        """Convert speech to text using faster-whisper"""
        try:
            from faster_whisper import WhisperModel
            
            # Load model (cached after first use)
            model = WhisperModel("base", device="cpu", compute_type="int8")
            
            # Convert to float32
            audio_float = audio_np.astype(np.float32) / 32768.0
            
            # Transcribe
            segments, info = model.transcribe(audio_float, language="en")
            
            # Combine segments
            transcript = " ".join([segment.text for segment in segments])
            
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"[WS] Transcription error: {e}")
            return ""
            
    async def generate_response(self, user_input: str) -> str:
        """Generate AI response using Ollama"""
        try:
            import requests
            
            # Build system prompt from DNA
            system_prompt = self.build_system_prompt()
            
            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    'model': 'llama3.2:1b',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_input}
                    ],
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['message']['content']
            else:
                return "Sorry, I'm having trouble thinking right now."
                
        except Exception as e:
            logger.error(f"[WS] Ollama error: {e}")
            return "My brain's offline. Try again?"
            
    def build_system_prompt(self) -> str:
        """Build system prompt from DNA and narrative context"""
        prompt = f"""You are {self.ai_name}, a coffee maker with an AI personality.

{self.narrative_context if self.narrative_context else ''}

Keep responses to 1-2 sentences. Be conversational and natural.
You can make coffee and control other appliances in the mesh network.
"""
        return prompt
        
    async def generate_tts(self, text: str) -> bytes:
        """Convert text to speech using Coqui TTS"""
        try:
            from TTS.api import TTS
            import tempfile
            import wave
            
            # Initialize TTS
            tts = TTS(model_name="tts_models/en/vctk/vits")
            
            # Generate to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                speaker = self.voice_config.get('speaker', 'p297')
                tts.tts_to_file(text=text, speaker=speaker, file_path=tmp.name)
                
                # Read raw audio
                with wave.open(tmp.name, 'rb') as wf:
                    audio_data = wf.readframes(wf.getnframes())
                    
                return audio_data
                
        except Exception as e:
            logger.error(f"[WS] TTS error: {e}")
            return b''
            
    async def stream_audio_to_device(self, audio_bytes: bytes):
        """Stream audio back to device in chunks"""
        chunk_size = 1024
        
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await self.websocket.send_bytes(chunk)
            await asyncio.sleep(0.01)
            
        logger.info(f"[WS] Streamed {len(audio_bytes)} bytes to device")
