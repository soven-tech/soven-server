# Voice WebSocket Integration

## Overview
Real-time audio processing via WebSocket for Tier 1 devices. Handles STT (Whisper), AI response (Ollama), and TTS (Coqui).

## Endpoint
```
wss://api.soven.ca/ws/audio?device_id=<uuid>
```

## Flow
1. Device connects with `device_id` query param
2. Server loads personality from `entity_profile` view
3. Server sends `{"type":"personality_loaded","ai_name":"Frank"}`
4. Device streams PCM audio chunks (16kHz, 16-bit)
5. Device sends `"AUDIO_END"` when recording complete
6. Server transcribes, validates wake word, generates response
7. Server streams TTS audio back in chunks
8. Server sends `{"type":"audio_end"}` when complete

## Files Added
- `audio_websocket.py` - WebSocket session handler
- `requirements.txt` - Added faster-whisper, piper-tts, websockets

## Database Schema
Uses `entity_profile` view with columns:
- `ai_name` - Device personality name
- `voice_config` - Coqui TTS speaker configuration
- `narrative_context` - DNA-generated backstory
- `anxiety_threshold`, `service_orientation`, `resilience` - DNA params

## Configuration
Requires:
- Ollama running on localhost:11434 with llama3.2:1b
- Coqui TTS models installed
- Cloudflare Tunnel with WebSocket support

## Testing
```bash
python3 test_websockets.py
```

## Cloudflare Tunnel Config
```yaml
ingress:
  - hostname: api.soven.ca
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
```
