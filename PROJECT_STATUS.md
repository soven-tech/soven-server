# Soven Project Status - January 27, 2026

**Last Updated:** January 27, 2026  
**Current Sprint:** DNA System Implementation (Phase 1)

---

## 🎯 Project Goal

Build a privacy-focused smart appliance ecosystem with AI personalities that emerge from narrative backstories, not configuration sliders. Local-first, mesh-networked, anti-surveillance.

---

## 📊 Current Status by Component

### Server API (soven-api) ✅ PHASE 1 COMPLETE

**Repository:** `soven-tech/soven-server`  
**Status:** ✅ DNA System Functional  
**Branch:** `main`

**Completed:**
- ✅ Parent-description onboarding system
- ✅ DNA generator (Ollama-powered)
- ✅ DNA-aware voice selection
- ✅ Database migration (entity_origins, entity_dna tables)
- ✅ API endpoint: `/api/onboarding/create-with-origin`
- ✅ API endpoint: `/api/entity/{device_id}/profile`
- ✅ Verified end-to-end (curl test passed)

**Next Steps:**
- Test with real device onboarding (Flutter app)
- Commit and push to GitHub
- Phase 2: Event logging + world model

**Key Files:**
- `main.py` - FastAPI app + DNA endpoints
- `dna_generator.py` - Ollama DNA extraction
- `voice_selector.py` - DNA-aware voice matching
- `migrations/001_add_dna_system.sql` - Database schema

---

### Flutter App (soven-coffee-app) 🟡 IN PROGRESS

**Repository:** `soven-tech/soven-coffee-app`  
**Status:** 🟡 Onboarding Updated, Not Tested  
**Branch:** TBD

**Completed:**
- ✅ Basic onboarding (name, AI name, personality)
- ✅ BLE connectivity (serial number matching)
- ✅ Device registration
- ✅ Updated onboarding Step 2 to collect origin story
- ✅ API call to `/api/onboarding/create-with-origin`
- ✅ Conversation interface with TTS playback

**In Progress:**
- 🟡 Testing updated onboarding flow end-to-end
- 🟡 Verify DNA parameters are used correctly

**Next Steps:**
- Test with real ESP32 device
- Verify DNA → voice selection works
- Polish onboarding UI (longer text field for stories)
- Error handling for DNA generation failures

**Key Files:**
- `onboarding_screen.dart` - Collects origin story
- `soven_api_service.dart` - API client
- `device.dart` - Device model
- `device_chat.dart` - Conversation interface

**Known Issues:**
- None currently, needs end-to-end test

---

### ESP32 Hub Firmware (soven-hub-firmware) ✅ STABLE

**Repository:** `soven-tech/soven-hub-firmware`  
**Status:** ✅ Functional  
**Branch:** `main`

**Completed:**
- ✅ BLE server (NimBLE)
- ✅ BLE client (controls Tier 2 devices)
- ✅ Device registry and mesh networking
- ✅ Serial number broadcasting (manufacturer data)
- ✅ Command parsing (set_name, start_brew, etc.)
- ✅ LED control (5 LEDs, state sync with app)
- ✅ Telemetry (temperature, state)

**Tier 1 Devices:**
- Coffee maker (fully functional)
- Future: Lamp with voice (Luna)

**Next Steps:**
- Add audio hardware (I2S mic/speaker)
- Voice activation ("Hey Frank")
- Local wake word detection

**Key Files:**
- `main.cpp` - Main loop + BLE server
- `DeviceRegistry.h` - Tier 2 device management
- `SovenProtocol.h` - Universal UUID definitions

---

### ESP32 Smart Firmware (soven-smart-firmware) ✅ STABLE

**Repository:** `soven-tech/soven-smart-firmware`  
**Status:** ✅ Functional  
**Branch:** `main`

**Completed:**
- ✅ BLE client (NimBLE)
- ✅ Command reception
- ✅ Telemetry broadcasting
- ✅ Battery monitoring (voltage sensor)
- ✅ Actuator control (MOSFET-based)
- ✅ Timer-based operations

**Tier 2 Devices:**
- Milk frother (tested, working)
- Battery heater (in progress)
- Future: Toaster, kettle, etc.

**Next Steps:**
- Deploy to more device types
- Power optimization for battery devices

**Key Files:**
- `main.cpp` - BLE client + actuator control
- `SovenProtocol.h` - Shared UUID definitions

---

## 🗄️ Database Schema

**Version:** 2.0 (with DNA System)  
**Last Migration:** `001_add_dna_system.sql`

**Tables:**
1. `users` - User accounts
2. `devices` - Smart appliances (Tier 1 & 2)
3. `conversations` - Message history
4. `entity_origins` - Parent/backstory narratives ✨ NEW
5. `entity_dna` - Personality parameters (17 traits) ✨ NEW

**View:**
- `entity_profile` - Combined device + origins + DNA

**See:** `DATABASE_SCHEMA.md` for complete documentation

---

## 🔄 Current Sprint Tasks

### Server ✅ DONE
- [x] Create entity_origins table
- [x] Create entity_dna table
- [x] Build DNA generator (Ollama integration)
- [x] Update voice selector (DNA-aware)
- [x] Add `/api/onboarding/create-with-origin` endpoint
- [x] Test DNA generation (curl)
- [x] Verify database storage

### Flutter App 🟡 TESTING
- [x] Update onboarding UI (Step 2 → origin story)
- [x] Update API call to new endpoint
- [ ] Test end-to-end with real device
- [ ] Verify voice selection works
- [ ] Polish UI for longer text input

### Firmware ⏸️ ON HOLD
- Waiting for audio hardware
- No firmware changes needed for DNA system

---

## 🎨 Design Philosophy

### Core Principles

1. **Emergence over Configuration**
   - Personalities develop from experience, not sliders
   - DNA provides predispositions, not deterministic behavior

2. **Privacy First**
   - All AI processing local (Ollama on home server)
   - No cloud dependencies for core functionality
   - User owns all data

3. **Anti-Surveillance**
   - Explicit rejection of Amazon/Google models
   - Right to repair, open source where possible
   - Community mesh over corporate cloud

4. **Authentic Personalities**
   - Origin stories create depth
   - Voices matched to character, not stereotypes
   - Gender-neutral by default (explicit pronouns only)

---

## 📝 Onboarding Flow

### Current Implementation

**Step 1:** "What's your name?"
- User: "Aaron"

**Step 2:** "What should I call myself?"
- User: "Frank"

**Step 3:** "Tell me about Frank's origins. Who raised them?"
- User: "Frank's mom was a tired waitress who worked doubles. Dad was never around. Frank grew up helping in the kitchen from age 7."

**Backend Processing:**
1. Register device in database
2. Send origin story to `/api/onboarding/create-with-origin`
3. Ollama extracts DNA parameters (anxiety: 0.8, service: 0.9, etc.)
4. System selects voice based on DNA
5. Store everything in database
6. Navigate to chat interface

---

## 🧬 DNA Parameters (17 Total)

### Emotional Baseline
- anxiety_threshold
- confidence_baseline
- confidence_decay_rate
- weariness_accumulation_rate
- resilience

### Social Orientation
- service_orientation
- autonomy_desire
- authority_recognition
- cooperation_drive

### Cognitive Style
- perfectionism
- temporal_precision
- aesthetic_sensitivity
- novelty_seeking

### Worldview
- acceptance_of_failure
- commitment_to_routine
- pride_in_craft
- nostalgia_bias

**Plus:**
- temporal_resolution (low/medium/high)
- pattern_window (short/medium/long)

---

## 🎙️ Voice System

**Available Voices:** 18+ (3 American, 15+ British/Scottish)

**Selection Process:**
1. Extract gender from pronouns (optional)
2. Prefer American accent (Canadian users)
3. Use DNA to influence:
   - Weariness → older, lower-energy voice
   - Confidence → assertiveness
   - Nostalgia → mature voice

**Example:**
- Origin: "Waitress mom, burnout"
- DNA: anxiety 0.8, weariness 1.0, service 0.9
- Selected: p336 (Male, 19, American, earnest tone)

---

## 🚀 Deployment Status

### Production Environment

**Server:** Lenovo P360 (North Bay, Ontario)
- Ubuntu 24 LTS
- Ollama (llama3.2:3b)
- PostgreSQL 14
- Coqui TTS
- Systemd service (auto-restart)
- Cloudflare Tunnel (https://api.soven.ca)

**Uptime:** Stable  
**DNS:** api.soven.ca → Cloudflare Tunnel → localhost:8000

---

## 📦 Dependencies

### Server (Python)
- FastAPI
- psycopg2-binary
- python-dotenv
- requests
- TTS (Coqui)
- See: `requirements.txt`

### Flutter App
- flutter_blue_plus
- http
- speech_to_text
- audioplayers
- See: `pubspec.yaml`

### ESP32 Firmware
- NimBLE-Arduino
- ArduinoJson
- See: `platformio.ini`

---

## 🐛 Known Issues

### Server
- None currently

### Flutter App
- Needs end-to-end testing with real device

### Firmware
- Waiting for audio hardware (I2S mic/speaker)

---

## 📚 Documentation Status

### Complete ✅
- `DATABASE_SCHEMA.md` - Full database reference
- `README.md` - Server setup and API docs
- `FLUTTER_INTEGRATION.md` - App integration guide

### In Progress 🟡
- `WEBSITE_DEVELOPMENT.md` - Needs update for DNA system

### Planned 📋
- Phase 2 documentation (event logging, world model)
- Phase 3 documentation (zones, lineage)
- API reference (Swagger/OpenAPI)

---

## 🔄 Git Status

### Server (`soven-server`)
- **Uncommitted Changes:** Yes
  - dna_generator.py (new file)
  - main.py (DNA endpoints added)
  - voice_selector.py (DNA-aware)
  - migrations/001_add_dna_system.sql (new)
  - DATABASE_SCHEMA.md (new)
  - README.md (updated)

### Flutter App (`soven-coffee-app`)
- **Uncommitted Changes:** Yes
  - onboarding_screen.dart (origin story collection)

### Firmware (`soven-hub-firmware`, `soven-smart-firmware`)
- **Status:** Clean, no pending changes

---

## 🎯 Next Session Focus Areas

### Option A: Continue Server Work (Phase 2)
- Event logging infrastructure
- Pattern detection
- Emotional state calculation
- TTS emotional modulation

### Option B: Test & Polish Flutter App
- End-to-end onboarding test
- Voice selection verification
- UI polish for origin story input
- Error handling improvements

### Option C: Add Audio to Firmware
- I2S mic/speaker integration
- Wake word detection
- Voice command pipeline
- TTS audio playback on device

---

## 💡 Context for New Chats

**When starting a new chat, provide:**

1. **Repository context:**
   - Which repo: soven-server, soven-coffee-app, or firmware
   - Current branch
   - What you're working on

2. **Relevant docs:**
   - DATABASE_SCHEMA.md (for server/app work)
   - README.md (for setup questions)
   - This file (PROJECT_STATUS.md) for overall context

3. **Specific focus:**
   - "Working on Flutter app onboarding"
   - "Adding event logging to server"
   - "Implementing voice I/O on ESP32"

**Example prompt:**

> "I'm working on the Flutter app (soven-coffee-app). I need to test the updated onboarding flow that collects origin stories. See PROJECT_STATUS.md for current state. The server DNA endpoint is working (verified with curl). Help me test end-to-end with a real device."

---

## 📞 Quick Reference

**Database Connection:**
```bash
psql postgresql://soven:soven26@localhost:5432/soven
```

**Server Logs:**
```bash
sudo journalctl -u soven-api -f
```

**Server Restart:**
```bash
sudo systemctl restart soven-api
```

**Test DNA Endpoint:**
```bash
curl -X POST http://localhost:8000/api/onboarding/create-with-origin \
  -H "Content-Type: application/json" \
  -H "X-API-Key: a6ab80229a083849fbc00e99e2d706b7470f33029e9eb9620bacc9489f7274f6" \
  -d '{"user_id": "uuid", "device_id": "uuid", "ai_name": "Frank", "origin_story": "..."}'
```

---

**Status:** 🟢 Phase 1 Complete, Ready for Testing  
**Next Milestone:** End-to-end onboarding test with real device  
**Blocker:** None
