# voice_selector.py
"""
Intelligent voice selection for AI personalities
Uses hybrid approach: VCTK multi-speaker + single-speaker American models
"""

import random
from voice_config import VCTK_VOICES, SINGLE_SPEAKER_MODELS, DEFAULT_SPEAKER

def select_voice(personality_name, personality_description, prefer_american=True):
    """
    Select appropriate voice based on personality description

    Args:
        personality_name: Name of the AI (e.g., "Frank")
        personality_description: User's description (e.g., "depressed ironic musician")
        prefer_american: Bool - prioritize American accents (default True for Canadian users)

    Returns:
        dict: {
            'type': 'multi_speaker' or 'single_speaker',
            'model': model name,
            'speaker': speaker ID or None,
            'metadata': voice metadata
        }
    """
    description_lower = (personality_name + " " + personality_description).lower()

    # Extract preferences from keywords
    preferences = {
        'gender': None,
        'age_range': None,
        'accent': None,
        'tone': None  # New: for personality-based selection
    }

    # Gender detection
    if any(word in description_lower for word in ['she', 'her', 'woman', 'female', 'girl', 'lady']):
        preferences['gender'] = 'F'
    elif any(word in description_lower for word in ['he', 'him', 'man', 'male', 'boy', 'guy']):
        preferences['gender'] = 'M'

    # Personality-based age hints
    if any(word in description_lower for word in ['depressed', 'weary', 'tired', 'cynical', 'sarcastic', 'ironic']):
        preferences['age_range'] = (28, 45)  # Mature voice for weary/ironic personalities
    elif any(word in description_lower for word in ['young', 'youthful', 'fresh', 'energetic', 'upbeat']):
        preferences['age_range'] = (18, 25)
    elif any(word in description_lower for word in ['mature', 'experienced', 'wise', 'older', 'senior']):
        preferences['age_range'] = (35, 60)
    else:
        preferences['age_range'] = (20, 35)  # Default to young adult

    # Accent preferences (explicit mentions override default)
    if any(word in description_lower for word in ['british', 'english', 'uk', 'london']):
        preferences['accent'] = 'British'
        prefer_american = False
    elif any(word in description_lower for word in ['scottish', 'scots', 'highland']):
        preferences['accent'] = 'Scottish'
        prefer_american = False
    elif any(word in description_lower for word in ['american', 'usa', 'us']):
        preferences['accent'] = 'American'
        prefer_american = True

    def select_voice(personality_name, personality_description, prefer_american=True):
    """
    Select appropriate voice based on personality description
    
    Philosophy: Characters emerge, they aren't configured. Like meeting a barista,
    you get who you get. We filter for practical communication (accent), explicit
    gender mentions, then let randomness create the character.
    """
    description_lower = (personality_name + " " + personality_description).lower()
    
    # Only detect what's explicitly stated
    preferences = {
        'gender': None,
        'accent': None,
    }
    
    # Gender - ONLY if explicitly mentioned with pronouns
    if any(word in description_lower for word in ['she', 'her', 'woman', 'female']):
        preferences['gender'] = 'F'
    elif any(word in description_lower for word in ['he', 'him', 'man', 'male']):
        preferences['gender'] = 'M'
    # Otherwise None - no assumption
    
    # Accent - explicit mentions override default
    if any(word in description_lower for word in ['british', 'english', 'uk', 'london']):
        preferences['accent'] = 'British'
        prefer_american = False
    elif any(word in description_lower for word in ['scottish', 'scots', 'highland']):
        preferences['accent'] = 'Scottish'
        prefer_american = False
    elif any(word in description_lower for word in ['american', 'usa', 'us']):
        preferences['accent'] = 'American'
        prefer_american = True
    
    # Build candidate pool
    candidates = []
    for speaker_id, metadata in VCTK_VOICES.items():
        # Accent filter (communication clarity)
        if prefer_american and metadata['accent'] != 'American':
            continue  # Skip non-American if preference set
        if preferences['accent'] and metadata['accent'] != preferences['accent']:
            continue  # Skip if explicit accent doesn't match
            
        # Gender filter (only if explicitly stated)
        if preferences['gender'] and metadata['gender'] != preferences['gender']:
            continue  # Skip if wrong gender
        
        # If we get here, this voice is valid - add it
        candidates.append({
            'type': 'multi_speaker',
            'model': 'tts_models/en/vctk/vits',
            'speaker': speaker_id,
            'metadata': metadata,
        })
    
    # Add single-speaker American female models if appropriate
    if (not preferences['gender'] or preferences['gender'] == 'F') and prefer_american:
        candidates.append({
            'type': 'single_speaker',
            'model': SINGLE_SPEAKER_MODELS['ljspeech']['model_name'],
            'speaker': None,
            'metadata': SINGLE_SPEAKER_MODELS['ljspeech'],
        })
        candidates.append({
            'type': 'single_speaker',
            'model': SINGLE_SPEAKER_MODELS['jenny']['model_name'],
            'speaker': None,
            'metadata': SINGLE_SPEAKER_MODELS['jenny'],
        })
    
    # Fallback if no candidates (shouldn't happen)
    if not candidates:
        candidates.append({
            'type': 'multi_speaker',
            'model': 'tts_models/en/vctk/vits',
            'speaker': DEFAULT_SPEAKER,
            'metadata': VCTK_VOICES[DEFAULT_SPEAKER],
        })
    
    # Pick randomly from valid pool - no scoring, just random selection
    selected = random.choice(candidates)
    
    print(f"\n{'='*60}")
    print(f"Voice Selection for: '{personality_name}'")
    print(f"Description: {personality_description}")
    print(f"{'='*60}")
    print(f"Selected: {selected['speaker'] if selected['speaker'] else selected['model']}")
    print(f"Type: {selected['type']}")
    print(f"Metadata: {selected['metadata']}")
    print(f"Pool size: {len(candidates)} valid voices")
    print(f"Filters applied: accent={prefer_american and 'American' or preferences['accent']}, gender={preferences['gender'] or 'any'}")
    print(f"{'='*60}\n")
    
    return selected

