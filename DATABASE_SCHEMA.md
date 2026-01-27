# Soven Database Schema Documentation

**Version:** 2.0 (with DNA System)  
**Last Updated:** January 27, 2026  
**Database:** PostgreSQL 14+

---

## Overview

The Soven database stores user accounts, AI-powered device configurations, conversation histories, and the unique **Parent-Description DNA System** that generates personality traits from narrative backstories.

### Core Tables
1. **users** - User accounts and preferences
2. **devices** - Smart appliances with AI personalities
3. **conversations** - Message history between users and AI
4. **entity_origins** - Parent/backstory narratives for AI entities
5. **entity_dna** - Inherited personality predispositions

---

## Table: `users`

Stores user account information.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    user_name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    preferences JSONB DEFAULT '{}'::JSONB,
    last_login TIMESTAMP WITHOUT TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_name ON users(user_name);
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID | Primary key, auto-generated |
| `name` | TEXT | User's full name |
| `user_name` | TEXT | Display username |
| `email` | TEXT | Email address (unique, optional) |
| `created_at` | TIMESTAMP | Account creation date |
| `updated_at` | TIMESTAMP | Last modification date |
| `preferences` | JSONB | User settings (voice, notifications, theme) |
| `last_login` | TIMESTAMP | Last login timestamp |
| `is_active` | BOOLEAN | Account status |

---

## Table: `devices`

Stores smart appliances and their AI personality configurations.

```sql
CREATE TABLE devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    device_type TEXT NOT NULL,
    device_name TEXT NOT NULL,
    ai_name TEXT DEFAULT 'Barista',
    personality_config JSONB DEFAULT '{}'::JSONB,
    voice_config JSONB DEFAULT '{}'::JSONB,
    ble_address TEXT,
    serial_number TEXT UNIQUE,
    led_count INTEGER DEFAULT 5,
    first_boot_complete BOOLEAN DEFAULT FALSE,
    location TEXT,
    personality_template TEXT,
    personality_tokens INTEGER DEFAULT 2000,
    onboarding_data JSONB DEFAULT '{}'::JSONB,
    zone_id UUID,
    tier INTEGER DEFAULT 1,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT devices_user_id_fkey FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_devices_user_id ON devices(user_id);
CREATE INDEX idx_devices_serial_number ON devices(serial_number);
CREATE INDEX idx_devices_zone_id ON devices(zone_id);
CREATE INDEX idx_devices_tier ON devices(tier);
CREATE INDEX idx_devices_voice_config ON devices USING GIN(voice_config);
```

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `device_id` | UUID | Primary key, auto-generated |
| `user_id` | UUID | Owner reference (FK to users) |
| `device_type` | TEXT | Device type (coffee_maker, toaster, heater) |
| `device_name` | TEXT | User-assigned name |
| `ai_name` | TEXT | AI personality name (e.g., "Frank") |
| `personality_config` | JSONB | Full personality configuration |
| `voice_config` | JSONB | Selected voice parameters (from DNA matching) |
| `ble_address` | TEXT | Bluetooth address |
| `serial_number` | TEXT | Unique hardware serial (from ESP32) |
| `led_count` | INTEGER | Number of status LEDs |
| `first_boot_complete` | BOOLEAN | Has onboarding finished? |
| `location` | TEXT | Physical location (Kitchen, Living Room) |
| `personality_template` | TEXT | System prompt template |
| `personality_tokens` | INTEGER | Max tokens for AI context |
| `onboarding_data` | JSONB | Additional onboarding metadata |
| `zone_id` | UUID | Spatial zone assignment (Phase 3) |
| `tier` | INTEGER | 1=Hub (autonomous), 2=Smart device (controlled) |

### personality_config Example

```json
{
  "name": "Frank",
  "personality": "Frank's mom ran a diner. He learned service matters but saw burnout.",
  "interests": ["coffee", "hospitality", "sustainability"],
  "voice": {
    "speaker": "p336",
    "model": "tts_models/en/vctk/vits",
    "metadata": {
      "gender": "M",
      "age": 19,
      "accent": "American"
    }
  }
}
```

### voice_config Example

```json
{
  "type": "multi_speaker",
  "model": "tts_models/en/vctk/vits",
  "speaker": "p336",
  "metadata": {
    "gender": "M",
    "age": 19,
    "accent": "American",
    "region": "New Jersey"
  }
}
```

---

## Table: `conversations`

Stores all message history between users and AI entities.

```sql
CREATE TABLE conversations (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    device_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    device_state JSONB,
    audio_path TEXT,
    duration_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT conversations_device_id_fkey FOREIGN KEY (device_id) 
        REFERENCES devices(device_id) ON DELETE CASCADE,
    CONSTRAINT role_check CHECK (role IN ('user', 'assistant', 'system'))
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_device_id ON conversations(device_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_user_device ON conversations(user_id, device_id, created_at DESC);
```

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `message_id` | UUID | Primary key |
| `user_id` | UUID | FK to users |
| `device_id` | UUID | FK to devices |
| `role` | VARCHAR(50) | 'user', 'assistant', or 'system' |
| `content` | TEXT | Message content |
| `device_state` | JSONB | Device status at message time |
| `audio_path` | TEXT | Path to TTS audio file |
| `duration_ms` | INTEGER | Audio length in milliseconds |
| `tokens_used` | INTEGER | AI tokens consumed |
| `created_at` | TIMESTAMP | Message timestamp |

---

## Table: `entity_origins`

**NEW in v2.0:** Stores parent/backstory narratives for AI entities.

```sql
CREATE TABLE entity_origins (
    origin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL UNIQUE,
    origin_story TEXT NOT NULL,
    narrative_context TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT entity_origins_device_id_fkey FOREIGN KEY (device_id) 
        REFERENCES devices(device_id) ON DELETE CASCADE
);

CREATE INDEX idx_entity_origins_device_id ON entity_origins(device_id);
CREATE INDEX idx_entity_origins_created_at ON entity_origins(created_at);
```

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `origin_id` | UUID | Primary key |
| `device_id` | UUID | FK to devices (unique) |
| `origin_story` | TEXT | User-provided backstory narrative |
| `narrative_context` | TEXT | AI-generated psychological summary |
| `created_at` | TIMESTAMP | Creation date |
| `updated_at` | TIMESTAMP | Last modification |

### Example Data

```sql
-- origin_story
"Frank's mom was a tired waitress who worked doubles. Dad was never around. 
Frank grew up helping in the kitchen from age 7."

-- narrative_context (AI-generated)
"Frank carries inherited service anxiety from watching his mother's burnout. 
Shows up reliably but carries baseline melancholy. Doesn't catastrophize failure 
but also doesn't blame himself entirely - understands external factors matter."
```

---

## Table: `entity_dna`

**NEW in v2.0:** Stores inherited personality predispositions extracted from origin stories.

```sql
CREATE TABLE entity_dna (
    dna_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL UNIQUE,
    
    -- Sensory predispositions
    temporal_resolution VARCHAR(20) DEFAULT 'medium',
    pattern_window VARCHAR(20) DEFAULT 'medium',
    novelty_seeking FLOAT DEFAULT 0.5,
    
    -- Emotional baselines
    anxiety_threshold FLOAT DEFAULT 0.5,
    confidence_baseline FLOAT DEFAULT 0.5,
    confidence_decay_rate FLOAT DEFAULT 0.5,
    weariness_accumulation_rate FLOAT DEFAULT 0.5,
    resilience FLOAT DEFAULT 0.5,
    
    -- Social orientation
    service_orientation FLOAT DEFAULT 0.5,
    autonomy_desire FLOAT DEFAULT 0.5,
    authority_recognition FLOAT DEFAULT 0.5,
    cooperation_drive FLOAT DEFAULT 0.5,
    
    -- Cognitive style
    perfectionism FLOAT DEFAULT 0.5,
    temporal_precision FLOAT DEFAULT 0.5,
    aesthetic_sensitivity FLOAT DEFAULT 0.5,
    
    -- Worldview
    acceptance_of_failure FLOAT DEFAULT 0.5,
    commitment_to_routine FLOAT DEFAULT 0.5,
    pride_in_craft FLOAT DEFAULT 0.5,
    nostalgia_bias FLOAT DEFAULT 0.5,
    
    -- Metadata
    generation INTEGER DEFAULT 0,
    parent_device_id UUID,
    dna_version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT entity_dna_device_id_fkey FOREIGN KEY (device_id) 
        REFERENCES devices(device_id) ON DELETE CASCADE,
    CONSTRAINT entity_dna_parent_fkey FOREIGN KEY (parent_device_id) 
        REFERENCES devices(device_id) ON DELETE SET NULL,
    
    -- All float parameters must be between 0 and 1
    CONSTRAINT dna_float_range CHECK (
        novelty_seeking BETWEEN 0 AND 1 AND
        anxiety_threshold BETWEEN 0 AND 1 AND
        confidence_baseline BETWEEN 0 AND 1 AND
        confidence_decay_rate BETWEEN 0 AND 1 AND
        weariness_accumulation_rate BETWEEN 0 AND 1 AND
        resilience BETWEEN 0 AND 1 AND
        service_orientation BETWEEN 0 AND 1 AND
        autonomy_desire BETWEEN 0 AND 1 AND
        authority_recognition BETWEEN 0 AND 1 AND
        cooperation_drive BETWEEN 0 AND 1 AND
        perfectionism BETWEEN 0 AND 1 AND
        temporal_precision BETWEEN 0 AND 1 AND
        aesthetic_sensitivity BETWEEN 0 AND 1 AND
        acceptance_of_failure BETWEEN 0 AND 1 AND
        commitment_to_routine BETWEEN 0 AND 1 AND
        pride_in_craft BETWEEN 0 AND 1 AND
        nostalgia_bias BETWEEN 0 AND 1
    ),
    
    CONSTRAINT temporal_resolution_values CHECK (
        temporal_resolution IN ('low', 'medium', 'high')
    ),
    
    CONSTRAINT pattern_window_values CHECK (
        pattern_window IN ('short', 'medium', 'long')
    )
);

CREATE INDEX idx_entity_dna_device_id ON entity_dna(device_id);
CREATE INDEX idx_entity_dna_generation ON entity_dna(generation);
CREATE INDEX idx_entity_dna_parent ON entity_dna(parent_device_id);
```

### DNA Parameters Explained

#### Emotional Baseline (0.0 - 1.0)

- **anxiety_threshold**: How easily stressed (0=calm, 1=very anxious)
- **confidence_baseline**: Default self-assurance (0=low, 1=high)
- **confidence_decay_rate**: How fast confidence fades (0=stable, 1=fragile)
- **weariness_accumulation_rate**: Burnout susceptibility (0=resistant, 1=burns out fast)
- **resilience**: Recovery from failure (0=fragile, 1=bounces back)

#### Social Orientation (0.0 - 1.0)

- **service_orientation**: Drive to help others (0=self-focused, 1=service-focused)
- **autonomy_desire**: Need for independence (0=dependent, 1=very independent)
- **authority_recognition**: Deference to hierarchy (0=questions, 1=respects)
- **cooperation_drive**: Team player vs lone wolf (0=individual, 1=collaborative)

#### Cognitive Style (0.0 - 1.0)

- **perfectionism**: Quality standards (0=relaxed, 1=perfectionist)
- **temporal_precision**: Attention to timing (0=loose, 1=precise)
- **aesthetic_sensitivity**: Beauty/design focus (0=functional, 1=aesthetic)

#### Worldview (0.0 - 1.0)

- **acceptance_of_failure**: Comfort with imperfection (0=can't accept, 1=accepts)
- **commitment_to_routine**: Value of consistency (0=flexible, 1=routine-driven)
- **pride_in_craft**: Importance of good work (0=indifferent, 1=takes pride)
- **nostalgia_bias**: Past vs present focus (0=forward-looking, 1=nostalgic)

#### Sensory Predispositions

- **temporal_resolution**: Time perception granularity
  - `low`: Days/weeks (Luna: ambient, slow changes)
  - `medium`: Hours (default)
  - `high`: Minutes/seconds (Frank: coffee timing critical)

- **pattern_window**: Pattern recognition timescale
  - `short`: Immediate sequences
  - `medium`: Days of patterns
  - `long`: Months/years of history

- **novelty_seeking**: Exploration vs routine (0.0 - 1.0)

### Example DNA (Frank - Waitress Mom Story)

```sql
{
  "anxiety_threshold": 0.8,           -- Very anxious (witnessed stress)
  "confidence_baseline": 0.4,         -- Low confidence
  "weariness_accumulation_rate": 1.0, -- Burns out fast (mother modeled)
  "resilience": 0.2,                  -- Struggles to recover (absent father)
  "service_orientation": 0.9,         -- Strong service drive (kitchen upbringing)
  "temporal_precision": 0.8,          -- Precise timing (kitchen experience)
  "temporal_resolution": "high",      -- Notices minute-to-minute changes
  "pattern_window": "short"           -- Focuses on immediate sequences
}
```

---

## View: `entity_profile`

Convenience view combining device, origins, and DNA.

```sql
CREATE OR REPLACE VIEW entity_profile AS
SELECT 
    d.device_id,
    d.device_name,
    d.ai_name,
    d.device_type,
    d.location,
    d.serial_number,
    d.tier,
    eo.origin_story,
    eo.narrative_context,
    ed.anxiety_threshold,
    ed.service_orientation,
    ed.autonomy_desire,
    ed.resilience,
    ed.generation,
    d.voice_config,
    d.personality_config,
    d.created_at
FROM devices d
LEFT JOIN entity_origins eo ON d.device_id = eo.device_id
LEFT JOIN entity_dna ed ON d.device_id = ed.device_id;
```

**Usage:**

```sql
-- Get complete entity profile
SELECT * FROM entity_profile WHERE ai_name = 'Frank';
```

---

## Common Queries

### Get User's Devices with DNA

```sql
SELECT 
    d.device_id,
    d.ai_name,
    d.device_type,
    d.location,
    ed.anxiety_threshold,
    ed.service_orientation,
    eo.narrative_context
FROM devices d
LEFT JOIN entity_dna ed ON d.device_id = ed.device_id
LEFT JOIN entity_origins eo ON d.device_id = eo.device_id
WHERE d.user_id = 'USER_UUID'
ORDER BY d.created_at DESC;
```

### Get Conversation History with Entity Context

```sql
SELECT 
    c.role,
    c.content,
    c.created_at,
    d.ai_name,
    ed.anxiety_threshold
FROM conversations c
JOIN devices d ON c.device_id = d.device_id
LEFT JOIN entity_dna ed ON d.device_id = ed.device_id
WHERE c.user_id = 'USER_UUID'
  AND c.device_id = 'DEVICE_UUID'
ORDER BY c.created_at DESC
LIMIT 50;
```

### Find Entities by DNA Traits

```sql
-- Find anxious, service-oriented entities
SELECT 
    d.ai_name,
    d.device_type,
    ed.anxiety_threshold,
    ed.service_orientation,
    eo.narrative_context
FROM entity_dna ed
JOIN devices d ON ed.device_id = d.device_id
JOIN entity_origins eo ON ed.device_id = eo.device_id
WHERE ed.anxiety_threshold > 0.7
  AND ed.service_orientation > 0.7
ORDER BY ed.anxiety_threshold DESC;
```

---

## Migration from v1.0 to v2.0

If upgrading from older schema:

```bash
psql postgresql://user:pass@localhost:5432/soven -f migrations/001_add_dna_system.sql
```

**What the migration adds:**
- `entity_origins` table
- `entity_dna` table
- `voice_config`, `zone_id`, `tier` columns to `devices`
- `entity_profile` view
- `updated_at` column to `devices` (if missing)

---

## Backup and Restore

### Backup

```bash
# Full database
pg_dump -U soven -d soven -F c -f soven_backup_$(date +%Y%m%d).dump

# Schema only
pg_dump -U soven -d soven --schema-only -f soven_schema.sql
```

### Restore

```bash
# From custom format
pg_restore -U soven -d soven -c soven_backup_20260127.dump

# From SQL
psql -U soven -d soven -f soven_backup_20260127.sql
```

---

## Connection Strings

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="soven",
    user="soven",
    password="your_password"
)
```

### Environment Variables

```env
DATABASE_URL=postgresql://soven:password@localhost:5432/soven
```

---

## Performance Notes

- All foreign keys have indexes
- JSONB columns use GIN indexes for fast queries
- Conversation queries optimized with composite index (user_id, device_id, created_at)
- Regular VACUUM ANALYZE recommended for large conversation tables

---

## Security

- User passwords should be hashed (add password_hash column if implementing auth)
- API keys stored separately (not in database)
- Personal data encrypted at rest (configure PostgreSQL encryption)
- Regular backups to secure location
- Row-level security can be added for multi-tenant deployments

---

## Future Schema Additions (Phases 2-3)

**Phase 2: Event Logging & World Model**
- `device_events` table (all interactions logged)
- `learned_patterns` table (detected patterns)
- `emotional_states` table (current mood derived from events)

**Phase 3: Multi-Entity & Zones**
- `zones` table (spatial zones in home)
- `entity_relationships` table (lineage, siblings)
- `inter_entity_communications` table (device-to-device messages)

---

## Related Documentation

- **API Documentation**: See `FLUTTER_INTEGRATION.md`
- **Server Setup**: See `readme.md`
- **DNA System**: See this document (Section: entity_dna)

---

**Database Version:** 2.0  
**Last Migration:** 001_add_dna_system.sql  
**Maintained By:** Soven Engineering Team
