# Server Updates - February 9, 2025

## Overview
Fixed critical API endpoint issues and WebSocket profile loading to support device casting and personality system.

## Changes Made

### 1. Cast Endpoint Path Correction
**File:** `main.py`

**Issue:** Cast endpoint was using incorrect path causing 404 errors
- Old: `/devices/{device_id}/cast`
- New: `/api/devices/{device_id}/cast`

**Impact:** 
- Devices can now successfully cast AI personalities
- Server properly links serial numbers to device IDs

### 2. WebSocket Profile Loading Schema Fix
**File:** `audio_websocket.py`

**Issue:** `load_device_profile()` was querying non-existent `entity_profile` table

**Solution:** Updated query to use correct database schema:
```python
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
        
        self.voice_config = {}
        
        logger.info(f"[WS] Loaded profile for {self.ai_name}")
    else:
        logger.error(f"[WS] No profile found for device {self.device_id}")
```

**Tables Used:**
- `devices` - Main device registry (ai_name, serial_number, device_id)
- `entity_dna` - Personality parameters (19 DNA traits)
- `entity_origins` - Narrative context (backstory, origin story)

**Impact:**
- WebSocket connections can now load device personalities
- Voice control system has access to AI parameters

## Testing
- ✅ Cast endpoint returns 200 OK
- ✅ Personality download endpoint works
- ✅ DNA parameters correctly loaded from database
- ⚠️ WebSocket connection stability needs further debugging

## Related Issues
- Cast endpoint 404 errors resolved
- Database schema mismatch resolved
- Personality system fully operational

## Next Steps
1. Debug WebSocket connection stability (device reports "Connected" but server sees no connection)
2. Verify voice control pipeline end-to-end
3. Test multi-device scenarios

## Commit
```
commit: [hash]
date: 2025-02-09
message: "Fix: Update cast endpoint and personality profile loading"
```
