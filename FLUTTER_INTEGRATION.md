# Soven Flutter App Integration Guide

This guide provides everything needed to integrate the Flutter app with the Soven Server API.

## API Configuration

### Base URL
```
Production: https://api.soven.ca
Local Dev: http://localhost:8000
```

### Authentication
All `/api/*` endpoints (except `/api/health`) require API key authentication.

**Header:**
```
X-API-Key: a6ab80229a083849fbc00e99e2d706b7470f33029e9eb9620bacc9489f7274f6
```

**Flutter Implementation:**
```dart
class SovenApiClient {
  static const String baseUrl = 'https://api.soven.ca';
  static const String apiKey = 'a6ab80229a083849fbc00e99e2d706b7470f33029e9eb9620bacc9489f7274f6';
  
  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    headers: {'X-API-Key': apiKey},
    connectTimeout: Duration(seconds: 30),
    receiveTimeout: Duration(seconds: 30),
  ));
}
```

---

## Core Endpoints

### 1. Health Check (No Auth Required)

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "soven-api",
  "version": "2.0",
  "tts_models_loaded": {
    "vctk": true,
    "ljspeech": false,
    "jenny": false
  }
}
```

**Flutter:**
```dart
Future<bool> checkApiHealth() async {
  try {
    final response = await _dio.get('/api/health');
    return response.data['status'] == 'healthy';
  } catch (e) {
    return false;
  }
}
```

---

### 2. Create AI Personality (Onboarding)

**Endpoint:** `POST /api/personality/create`

**Request:**
```json
{
  "name": "Maya",
  "description": "Graduate student in environmental science, works morning shifts. Encouraging but not annoyingly chipper.",
  "prefer_american": true
}
```

**Response:**
```json
{
  "success": true,
  "personality_id": "personality_1768617234",
  "name": "Maya",
  "description": "Graduate student in environmental science...",
  "voice": {
    "type": "multi_speaker",
    "model": "tts_models/en/vctk/vits",
    "speaker": "p297",
    "metadata": {
      "gender": "F",
      "age": 27,
      "accent": "American",
      "region": "New Jersey"
    },
    "score": 27
  }
}
```

**Flutter:**
```dart
Future<Map<String, dynamic>> createPersonality({
  required String name,
  required String description,
  bool preferAmerican = true,
}) async {
  final response = await _dio.post('/api/personality/create', data: {
    'name': name,
    'description': description,
    'prefer_american': preferAmerican,
  });
  
  return response.data;
}
```

**When to use:** During device onboarding when user describes their AI companion.

---

### 3. Complete Conversation (Main Flow)

**Endpoint:** `POST /api/conversation`

This is the **primary endpoint** for the voice interaction loop.

**Request:**
```json
{
  "user_input": "Can you start brewing my coffee?",
  "user_id": "8a1ac3bf-0ee0-45f7-853e-eaf7575ef0c3",
  "device_id": "96ebb670-07c8-49c3-93c8-14f40dc756ec",
  "voice_config": {
    "voice_id": "p297",
    "model": "tts_models/en/vctk/vits"
  }
}
```

**Response:**
```json
{
  "success": true,
  "ai_response": "I'll get the brew cycle started right away.",
  "audio_path": "/tmp/soven_conversation_1768617739303.wav",
  "commands": ["start_brew"],
  "message_id": "69a2b3b9-53ba-4e49-a76f-8e85cccec22e"
}
```

**Flutter:**
```dart
class ConversationResponse {
  final String aiResponse;
  final String audioPath;
  final List<String> commands;
  final String messageId;
  
  ConversationResponse.fromJson(Map<String, dynamic> json)
    : aiResponse = json['ai_response'],
      audioPath = json['audio_path'],
      commands = List<String>.from(json['commands']),
      messageId = json['message_id'];
}

Future<ConversationResponse> sendMessage({
  required String userInput,
  required String userId,
  required String deviceId,
  Map<String, String>? voiceConfig,
}) async {
  final response = await _dio.post('/api/conversation', data: {
    'user_input': userInput,
    'user_id': userId,
    'device_id': deviceId,
    'voice_config': voiceConfig ?? {
      'voice_id': 'p297',
      'model': 'tts_models/en/vctk/vits'
    },
  });
  
  return ConversationResponse.fromJson(response.data);
}
```

---

### 4. Get TTS Audio File

After receiving the conversation response, fetch the actual audio:

**Endpoint:** `GET {audio_path}` (relative to base URL)

**Flutter:**
```dart
Future<Uint8List> getAudioFile(String audioPath) async {
  // Note: audio_path is a local server path like /tmp/file.wav
  // We need to create an endpoint to serve these files
  // For now, the audio is generated but needs a download endpoint
  
  final response = await _dio.get(
    '/api/audio/${audioPath.split('/').last}',
    options: Options(responseType: ResponseType.bytes),
  );
  
  return response.data;
}
```

**TODO:** Server needs an endpoint to serve the generated audio files. Add this:
```python
@app.get("/api/audio/{filename}")
def get_audio_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found")
```

---

### 5. List Available Voices

**Endpoint:** `GET /api/voices/list`

**Response:**
```json
{
  "multi_speaker": {
    "model": "tts_models/en/vctk/vits",
    "voices": {
      "p297": {"gender": "F", "age": 27, "accent": "American"},
      "p336": {"gender": "M", "age": 19, "accent": "American"},
      ...
    }
  },
  "single_speaker": { ... }
}
```

**When to use:** If you want to let users preview/select voices manually.

---

## Complete Voice Interaction Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter App                               │
└─────────────────────────────────────────────────────────────┘
                           │
                    1. User speaks
                           │
                    ┌──────▼──────┐
                    │ Speech-to-  │
                    │    Text     │
                    └──────┬──────┘
                           │
              2. Send text to server
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Soven Server API                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ POST /api/conversation                                  │ │
│  │  ├─> Ollama (AI response)                              │ │
│  │  ├─> Command Parser (start_brew, etc)                  │ │
│  │  ├─> Coqui TTS (generate audio)                        │ │
│  │  └─> PostgreSQL (save conversation)                    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
          3. Return: {response, audio, commands}
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Flutter App                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 4. Download audio file                                  │ │
│  │ 5. Play audio (text-to-speech)                         │ │
│  │ 6. Execute commands via BLE → ESP32                    │ │
│  │    - start_brew → turn on coffee maker                 │ │
│  │    - stop_brew → turn off coffee maker                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Sample Implementation

### Complete Voice Chat Widget
```dart
class VoiceChatWidget extends StatefulWidget {
  final String userId;
  final String deviceId;
  final Map<String, String> voiceConfig;
  
  @override
  _VoiceChatWidgetState createState() => _VoiceChatWidgetState();
}

class _VoiceChatWidgetState extends State<VoiceChatWidget> {
  final SovenApiClient _api = SovenApiClient();
  final BleService _ble = BleService();
  final AudioPlayer _audioPlayer = AudioPlayer();
  final SpeechToText _speech = SpeechToText();
  
  bool _isListening = false;
  bool _isThinking = false;
  String _transcript = '';
  
  Future<void> startListening() async {
    bool available = await _speech.initialize();
    if (!available) return;
    
    setState(() {
      _isListening = true;
      _transcript = '';
    });
    
    _speech.listen(
      onResult: (result) {
        setState(() => _transcript = result.recognizedWords);
        
        if (result.finalResult) {
          _processVoiceCommand(result.recognizedWords);
        }
      },
    );
  }
  
  Future<void> _processVoiceCommand(String text) async {
    if (text.trim().isEmpty) return;
    
    setState(() {
      _isListening = false;
      _isThinking = true;
    });
    
    try {
      // Send to server
      final response = await _api.sendMessage(
        userInput: text,
        userId: widget.userId,
        deviceId: widget.deviceId,
        voiceConfig: widget.voiceConfig,
      );
      
      // Execute ESP32 commands via BLE
      for (String command in response.commands) {
        await _ble.sendCommand(command);
      }
      
      // Get and play audio
      final audioData = await _api.getAudioFile(response.audioPath);
      await _audioPlayer.play(BytesSource(audioData));
      
      setState(() => _isThinking = false);
      
    } catch (e) {
      print('Error: $e');
      setState(() => _isThinking = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (_isListening)
          Text('Listening: $_transcript'),
        if (_isThinking)
          CircularProgressIndicator(),
        ElevatedButton(
          onPressed: _isThinking ? null : startListening,
          child: Icon(_isListening ? Icons.mic : Icons.mic_none),
        ),
      ],
    );
  }
}
```

---

## Device Commands

The server automatically detects and returns commands based on AI response:

| Command | Trigger Phrases | ESP32 Action |
|---------|----------------|--------------|
| `start_brew` | "start brewing", "make coffee", "brew" | Turn on coffee maker |
| `stop_brew` | "stop", "cancel", "turn off" | Turn off coffee maker |

**Extending commands:** Update `parse_commands()` function in `main.py`

---

## Error Handling
```dart
try {
  final response = await _api.sendMessage(...);
} on DioException catch (e) {
  if (e.response?.statusCode == 403) {
    // Invalid API key
    showError('Authentication failed');
  } else if (e.response?.statusCode == 500) {
    // Server error
    showError('Server error: ${e.response?.data['detail']}');
  } else {
    // Network error
    showError('Connection failed');
  }
}
```

---

## Testing Checklist

- [ ] API health check works
- [ ] Personality creation during onboarding
- [ ] Voice config stored in device record
- [ ] Complete conversation flow (speech → AI → TTS → BLE)
- [ ] Audio playback works
- [ ] Commands execute on ESP32
- [ ] Works on local network
- [ ] Works remotely via Cloudflare Tunnel
- [ ] Handles errors gracefully

---

## Next Steps

1. **Add audio download endpoint** to server (see TODO above)
2. **Integrate with existing BLE service** for command execution
3. **Update onboarding flow** to use personality creation endpoint
4. **Test end-to-end** with real device

---

## Related Documentation

- **Server Repo**: https://github.com/soven-tech/soven-server
- **Flutter App Repo**: https://github.com/soven-tech/soven-coffee-app
- **ESP32 Firmware Repo**: https://github.com/soven-tech/soven-coffee-firmware

## Support

For server-side issues, reference chat: **"Conversational AI coffee maker with ESP32"**

For app/firmware issues, reference chat: **"ESP32 coffee maker AI integration"**
