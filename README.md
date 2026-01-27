# Soven Server API

Backend API for Soven intelligent appliance system. Handles conversations, TTS voice synthesis, device management, and the unique **Parent-Description DNA System** for generating AI personalities from narrative backstories.

## 🎯 Unique Features

- **🧬 DNA-Based Personalities**: AI entities generated from parent/backstory narratives, not configuration sliders
- **🎙️ Authentic Voice Matching**: DNA parameters influence voice selection for genuine character
- **💾 Local-First**: All data stays on your home server, no cloud dependencies
- **🔗 Multi-Device Mesh**: Tier 1 hubs control Tier 2 smart devices via BLE
- **📊 World Model Foundation**: Infrastructure for personality emergence through experience (Phase 2)

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14+ with DNA system tables
- **AI Engine**: Ollama (llama3.2:3b) for DNA generation from narratives
- **TTS Engine**: Coqui TTS (VCTK multi-speaker + LJSpeech)
- **Voice Models**: 18+ voices (American, British, Scottish accents)
- **Deployment**: Systemd service with Cloudflare Tunnel

## Project Structure

```
soven-api/
├── main.py                      # FastAPI application + DNA endpoints
├── dna_generator.py             # Ollama-powered DNA extraction from stories
├── voice_selector.py            # DNA-aware voice matching
├── voice_config.py              # Voice metadata (18+ speakers)
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── soven-api.service            # Systemd service file
├── migrations/
│   └── 001_add_dna_system.sql   # DNA tables migration
├── DATABASE_SCHEMA.md           # Complete database documentation
├── FLUTTER_INTEGRATION.md       # Mobile app integration guide
└── WEBSITE_DEVELOPMENT.md       # Website integration plan
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Ollama with llama3.2:3b model
- espeak-ng (for TTS phoneme processing)

### Installation

```bash
# Clone repository
git clone https://github.com/soven-tech/soven-server.git
cd soven-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Install system dependencies
sudo apt-get update
sudo apt-get install espeak-ng postgresql

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Set up database
sudo -u postgres psql
```

```sql
CREATE DATABASE soven;
CREATE USER soven WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE soven TO soven;
\q
```

```bash
# Run migrations
psql postgresql://soven:your_password@localhost:5432/soven -f migrations/001_add_dna_system.sql

# Verify tables created
psql postgresql://soven:your_password@localhost:5432/soven -c "\dt"
# Should show: users, devices, conversations, entity_origins, entity_dna

# Start Ollama (if not running)
ollama serve &
ollama pull llama3.2:3b

# Run server
python main.py
```

API available at `http://localhost:8000`

## Core Concepts

### Parent-Description DNA System

Instead of configuring AI personalities with sliders, users provide a **backstory narrative** during onboarding:

> "Frank's mom was a tired waitress who worked doubles. Dad was never around. Frank grew up helping in the kitchen from age 7."

The system uses **Ollama to extract DNA parameters:**

```json
{
  "anxiety_threshold": 0.8,           // Very anxious (witnessed stress)
  "confidence_baseline": 0.4,         // Low confidence  
  "weariness_accumulation_rate": 1.0, // Burns out fast (mother modeled)
  "resilience": 0.2,                  // Struggles to recover
  "service_orientation": 0.9          // Strong service drive
}
```

**Plus AI-generated narrative context:**

> "Frank carries inherited service anxiety from watching his mother's burnout. Shows up reliably but carries baseline melancholy."

These DNA parameters:
- Influence voice selection (weary → older, lower-energy voice)
- Establish personality foundations
- Enable future world model development (Phase 2)

### Device Tiers

**Tier 1 (Autonomous Hubs):**
- Full AI personality with voice I/O
- ESP32-S3 with speakers/microphones
- Controls Tier 2 devices via BLE mesh
- Examples: Coffee maker, lamp with voice control

**Tier 2 (Smart Devices):**
- Simple actuators (no voice)
- ESP32-WROOM with basic sensors
- Controlled by nearest Tier 1 hub
- Examples: Milk frother, toaster, heater

## API Endpoints

### DNA System (New in v2.0)

#### Create Entity with Origin Story

```bash
POST /api/onboarding/create-with-origin
```

**Request:**
```json
{
  "user_id": "uuid",
  "device_id": "uuid",
  "ai_name": "Frank",
  "origin_story": "Frank's mom was a waitress...",
  "prefer_american": true
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "uuid",
  "dna_parameters": {
    "anxiety_threshold": 0.8,
    "confidence_baseline": 0.4,
    // ... 17 total parameters
  },
  "voice_config": {
    "type": "multi_speaker",
    "model": "tts_models/en/vctk/vits",
    "speaker": "p336",
    "metadata": {"gender": "M", "age": 19, "accent": "American"}
  },
  "narrative_context": "Frank carries inherited service anxiety...",
  "temporal_resolution": "high",
  "pattern_window": "short"
}
```

#### Get Entity Profile

```bash
GET /api/entity/{device_id}/profile
```

Returns complete entity profile (device + origins + DNA).

### Existing Endpoints

- `GET /api/health` - Health check (no auth)
- `POST /api/tts/generate` - Generate speech from text
- `POST /api/personality/create` - Create personality (legacy, use DNA endpoint)
- `GET /api/voices/list` - List available voices
- `POST /api/conversation` - Full conversation pipeline
- `POST /messages` - Store message
- `GET /conversations/{user_id}/{device_id}` - Get history
- `POST /devices` - Register device
- `GET /users/{user_id}/devices` - List devices

### Authentication

All `/api/*` endpoints (except `/api/health`) require API key:

```bash
curl -H "X-API-Key: your-key" https://api.soven.ca/api/endpoint
```

## Voice System

### Available Voices

**American English** (3 speakers - prioritized for North America):
- p297: Female, 27, New Jersey
- p336: Male, 19, New Jersey
- p323: Female, 19, New Jersey

**British English** (15+ speakers - various regions)

**Scottish English** (3 speakers)

### DNA-Influenced Voice Selection

Voice matching now considers:
- **DNA parameters**: Weariness → older voice, low confidence → less assertive
- **Gender**: Only from explicit pronouns (he/she/they)
- **Accent**: American default for Canadian users
- **Origin story content**: Implicit personality cues

**Example:**

```
Origin: "Frank's mom ran a diner, worked herself to exhaustion"
DNA: high weariness (0.8), low confidence (0.4), high service (0.9)
Selected: p336 (Male, 19, American) - earnest, not overly confident
```

## Production Deployment

### Systemd Service

```bash
# Copy service file
sudo cp soven-api.service /etc/systemd/system/

# Create log file
sudo touch /var/log/soven-api.log
sudo chown soven:soven /var/log/soven-api.log

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable soven-api
sudo systemctl start soven-api
sudo systemctl status soven-api

# View logs
sudo journalctl -u soven-api -f
```

### Cloudflare Tunnel (Optional)

For remote access via `https://api.soven.ca`:

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create soven-api

# Configure tunnel
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/soven/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: api.soven.ca
    service: http://localhost:8000
  - service: http_status:404
```

```bash
# Run tunnel as service
cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## Development

### Testing DNA Generation

```bash
cd /home/soven/soven-api
source venv/bin/activate

# Test DNA generator directly
python3 dna_generator.py

# Test API endpoint
curl -X POST http://localhost:8000/api/onboarding/create-with-origin \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "user_id": "test-uuid",
    "device_id": "test-uuid",
    "ai_name": "TestFrank",
    "origin_story": "Frank grew up in a busy restaurant kitchen...",
    "prefer_american": true
  }'
```

### Database Queries

```bash
# Connect to database
psql postgresql://soven:password@localhost:5432/soven

# Check entity profile
SELECT * FROM entity_profile WHERE ai_name = 'Frank';

# Check DNA parameters
SELECT device_id, anxiety_threshold, service_orientation, weariness_accumulation_rate
FROM entity_dna;

# Check origin stories
SELECT device_id, origin_story, narrative_context
FROM entity_origins;
```

## Architecture

```
Flutter App (User)
    ↓
Cloudflare Tunnel (Remote Access)
    ↓
Soven API (FastAPI)
    ├→ Ollama (DNA Generation)
    ├→ Coqui TTS (Voice Synthesis)
    └→ PostgreSQL (Data Storage)
    ↓
ESP32 Devices (BLE Mesh)
    ├→ Tier 1 Hubs (Autonomous, Voice)
    └→ Tier 2 Devices (Controlled, Silent)
```

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://soven:password@localhost:5432/soven

# API Security (generate with: openssl rand -hex 32)
SOVEN_API_KEY=your-64-char-hex-key

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Optional: Custom TTS settings
TTS_CACHE_DIR=/tmp/tts_cache
```

### Generating API Keys

```bash
openssl rand -hex 32
```

## Related Repositories

- **Flutter App**: [soven-coffee-app](https://github.com/soven-tech/soven-coffee-app)
- **ESP32 Hub Firmware**: [soven-hub-firmware](https://github.com/soven-tech/soven-hub-firmware)
- **ESP32 Smart Device Firmware**: [soven-smart-firmware](https://github.com/soven-tech/soven-smart-firmware)

## Roadmap

### Phase 1: DNA Foundation ✅ (COMPLETE)
- [x] Parent-description onboarding
- [x] DNA parameter extraction (Ollama)
- [x] DNA-aware voice selection
- [x] Database storage (entity_origins, entity_dna)

### Phase 2: World Model & Events (Q1 2026)
- [ ] Event logging (every interaction tracked)
- [ ] Pattern detection (temporal, causal, social)
- [ ] Emotional state calculation
- [ ] TTS emotional modulation (voice reflects current mood)

### Phase 3: Multi-Entity & Zones (Q2 2026)
- [ ] Zone management (kitchen, living room, etc.)
- [ ] Entity lineage (parent/child relationships)
- [ ] Inter-entity communication
- [ ] Sibling/descendant creation

### Phase 4: Community Network (Q3 2026)
- [ ] Local mesh (neighbor discovery)
- [ ] Federated learning (share patterns, not data)
- [ ] Resource coordination (energy, tools, food)

## Troubleshooting

### Ollama Timeout During DNA Generation

```python
# In dna_generator.py, increase timeout:
response = requests.post(..., timeout=60)  # Default is 30
```

### DNA Parameters Not Saving

```sql
-- Check constraints
SELECT * FROM entity_dna WHERE device_id = 'your-device-id';

-- Verify all parameters are 0.0-1.0
```

### Voice Selection Ignoring DNA

```python
# Verify DNA parameters are passed:
print(f"DNA params being used: {dna_parameters}")
```

### Migration Errors

```bash
# Rollback migration
psql postgresql://soven:password@localhost:5432/soven

BEGIN;
DROP VIEW IF EXISTS entity_profile;
DROP TABLE IF EXISTS entity_dna CASCADE;
DROP TABLE IF EXISTS entity_origins CASCADE;
ROLLBACK;

# Re-run migration
psql postgresql://soven:password@localhost:5432/soven -f migrations/001_add_dna_system.sql
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT License](LICENSE)

## Support

- **Documentation**: See `DATABASE_SCHEMA.md` for complete database reference
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

---

**Built with ❤️ for authentic AI personalities**

*"Personalities aren't configured. They emerge."*
