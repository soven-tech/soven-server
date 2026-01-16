# Soven Server API

Backend API for Soven intelligent coffee maker system. Handles conversations, TTS voice synthesis, device management, and AI personality configuration.

## Features

- 🎙️ **Text-to-Speech**: Coqui TTS with multiple voice personalities (American & British English)
- 💬 **Conversation History**: PostgreSQL-backed message storage
- 🤖 **AI Personalities**: Dynamic voice selection based on authentic personality descriptions
- 🔐 **API Authentication**: API key-based security
- ☁️ **Remote Access**: Cloudflare Tunnel integration
- 🔄 **Production Ready**: Systemd service with auto-restart

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL
- **TTS Engine**: Coqui TTS (VCTK multi-speaker model)
- **Voice Models**: 18+ voices (American, British, Scottish accents)
- **Deployment**: Systemd service with Cloudflare Tunnel

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- espeak-ng (for TTS phoneme processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/soven-tech/soven-server.git
cd soven-server
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install espeak-ng postgresql
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Set up PostgreSQL database:
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE soven;
CREATE USER soven WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE soven TO soven;
\q
```

7. Create database schema:
```sql
CREATE TABLE conversations (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    device_state JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    device_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    device_type VARCHAR(100),
    device_name VARCHAR(255),
    ai_name VARCHAR(255),
    personality_config JSONB,
    ble_address VARCHAR(100),
    led_count INTEGER,
    serial_number VARCHAR(100),
    first_boot_complete BOOLEAN DEFAULT FALSE,
    location VARCHAR(255),
    personality_template TEXT,
    personality_tokens JSONB,
    onboarding_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Running Locally
```bash
source venv/bin/activate
python main.py
```

API will be available at `http://localhost:8000`

### Production Deployment

1. Copy systemd service file:
```bash
sudo cp soven-api.service /etc/systemd/system/
```

2. Create log file:
```bash
sudo touch /var/log/soven-api.log
sudo chown soven:soven /var/log/soven-api.log
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable soven-api
sudo systemctl start soven-api
sudo systemctl status soven-api
```

4. Configure Cloudflare Tunnel for remote access (optional)

## API Endpoints

### Core Endpoints

- `GET /` - API status and version
- `GET /api/health` - Health check with TTS model status (no auth required)

### Conversations

- `POST /messages` - Store conversation message
- `GET /conversations/{user_id}/{device_id}` - Get conversation history

### Devices

- `GET /users/{user_id}/devices` - List user devices
- `POST /devices` - Register new device
- `POST /devices/{device_id}/onboarding` - Complete device setup

### TTS & Personalities

- `POST /api/tts/generate` - Generate speech from text
```json
  {
    "text": "Your coffee is ready",
    "voice_id": "p297",
    "model": "tts_models/en/vctk/vits"
  }
```

- `POST /api/personality/create` - Create AI personality with voice selection
```json
  {
    "name": "Jordan",
    "description": "Musician who gigs on weekends, laid back, knows every indie band",
    "prefer_american": true
  }
```

- `GET /api/voices/list` - List all available voices with metadata

### Authentication

All `/api/*` endpoints (except `/api/health`) require API key authentication:
```bash
curl -H "X-API-Key: your-api-key-here" https://api.soven.ca/api/endpoint
```

## Voice System

The server uses authentic personality-based voice selection. During onboarding, users describe their AI companion naturally (e.g., "A grad student who works mornings, encouraging but not annoyingly chipper") and the system intelligently selects an appropriate voice based on:

- **Gender** (detected from pronouns in description)
- **Age hints** (young, mature, experienced)
- **Accent preferences** (American, British, Scottish)
- **Personality traits** (friendly, professional, laid-back)

### Available Voices

**American English** (prioritized for North American users):
- p297: Female, 27, New Jersey
- p336: Male, 19, New Jersey  
- p323: Female, 19, New Jersey

**British English** (variety of regional accents):
- Multiple voices from Southern England, Manchester, Essex, etc.

**Scottish English**:
- p234, p237, p241: Various Scottish regional accents

### Example Personalities

Instead of generic AI assistants, Soven encourages authentic personalities:

- **Maya**: "Graduate student in environmental science, works morning shifts to fund research. Encouraging but not annoyingly chipper."
- **Jordan**: "Musician who gigs on weekends, makes coffee to pay rent. Laid back, knows every indie band."
- **Priya**: "Former tech worker who left corporate to open her own roastery someday. Knowledgeable about beans and extraction science."

## Architecture
```
Flutter App → Cloudflare Tunnel → Soven API (FastAPI)
                                        ↓
                                   PostgreSQL
                                        ↓
                                   Coqui TTS
                                        ↓
                                  ESP32 Devices (BLE)
```

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/soven

# API Security (generate with: openssl rand -hex 32)
SOVEN_API_KEY=your-secure-api-key-here

# Optional: Ollama for AI responses
OLLAMA_HOST=http://localhost:11434
```

### Generating API Keys
```bash
openssl rand -hex 32
```

## Development

### Project Structure
```
soven-api/
├── main.py                 # FastAPI application
├── voice_config.py         # Voice metadata and configuration
├── voice_selector.py       # AI personality to voice matching logic
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
└── soven-api.service      # Systemd service file
```

### Testing

Test health check:
```bash
curl http://localhost:8000/api/health
```

Test TTS generation:
```bash
curl -X POST http://localhost:8000/api/tts/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{"text": "Hello", "voice_id": "p297"}' \
  --output test.wav
```

Test personality creation:
```bash
curl -X POST http://localhost:8000/api/personality/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{"name": "Test", "description": "A friendly young woman", "prefer_american": true}'
```

## Related Repositories

- **Flutter App**: [soven-coffee-app](https://github.com/soven-tech/soven-coffee-app)
- **ESP32 Firmware**: [soven-coffee-firmware](https://github.com/soven-tech/soven-coffee-firmware)

## Roadmap

- [ ] Ollama integration for AI responses
- [ ] Multi-language support (French for Canadian market)
- [ ] Voice cloning for custom personalities
- [ ] WebSocket support for real-time conversations
- [ ] Redis caching for frequently used TTS outputs
- [ ] Prometheus metrics for monitoring

## License

[MIT License](LICENSE)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ for authentic AI interactions
