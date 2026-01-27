
"""
Voice Selector - DNA-aware voice matching for Soven entities
"""

from voice_config import VCTK_VOICES
import random

def select_voice(personality_name, personality_description, prefer_american=True, dna_parameters=None):
    """
    Select appropriate voice based on personality description AND DNA parameters
    
    Args:
        personality_name: Name of the AI (e.g., "Frank")
        personality_description: User's description OR origin story
        prefer_american: Bool - prioritize American accents (default True for Canadian users)
        dna_parameters: Dict - DNA traits from parent story (optional)
    
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
        'energy': 0.5,  # NEW: from DNA
    }
    
    # Gender detection (explicit mentions only)
    if any(word in description_lower for word in ['she', 'her', 'woman', 'female', 'girl', 'lady']):
        preferences['gender'] = 'F'
    elif any(word in description_lower for word in ['he', 'him', 'man', 'male', 'boy', 'guy']):
        preferences['gender'] = 'M'
    
    # Age hints from description
    if any(word in description_lower for word in ['young', 'youthful', 'fresh', 'energetic']):
        preferences['age_range'] = (18, 25)
    elif any(word in description_lower for word in ['mature', 'experienced', 'wise', 'older']):
        preferences['age_range'] = (35, 60)
    elif any(word in description_lower for word in ['depressed', 'weary', 'tired', 'cynical']):
        preferences['age_range'] = (28, 45)  # Mature voice for weary personalities
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
    
    # NEW: Use DNA parameters to influence voice selection
    if dna_parameters:
        # Energy level from DNA
        weariness = dna_parameters.get('weariness_accumulation_rate', 0.5)
        confidence = dna_parameters.get('confidence_baseline', 0.5)
        preferences['energy'] = (confidence - weariness) / 2 + 0.5  # Normalize to 0-1
        
        # Adjust age range based on DNA
        if weariness > 0.7 or dna_parameters.get('nostalgia_bias', 0.5) > 0.7:
            # Weary or nostalgic → older voice
            preferences['age_range'] = (max(preferences['age_range'][0], 30), min(preferences['age_range'][1] + 10, 60))
    
    # Score all VCTK voices
    candidates = []
    for speaker_id, metadata in VCTK_VOICES.items():
        score = 0
        
        # Accent preference (high priority)
        if prefer_american and metadata['accent'] == 'American':
            score += 20  # Strong preference for American
        elif preferences['accent'] and metadata['accent'] == preferences['accent']:
            score += 15
        elif metadata['accent'] == 'American':
            score += 8  # Still favor American if no specific preference
        elif metadata['accent'] in ['English', 'Scottish']:
            score += 5  # British/Scottish are acceptable
        
        # Gender match
        if preferences['gender'] and metadata['gender'] == preferences['gender']:
            score += 10
        elif not preferences['gender']:
            score += 5  # No preference, all welcome
        
        # Age match
        if preferences['age_range']:
            age = metadata['age']
            if preferences['age_range'][0] <= age <= preferences['age_range'][1]:
                score += 7
            else:
                score += 2  # Still usable, just not ideal
        else:
            score += 5
        
        candidates.append({
            'type': 'multi_speaker',
            'model': 'tts_models/en/vctk/vits',
            'speaker': speaker_id,
            'metadata': metadata,
            'score': score
        })
    
    # Sort by score and pick best match
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Get top matches (in case of ties, randomize for variety)
    top_score = candidates[0]['score']
    top_candidates = [c for c in candidates if c['score'] == top_score]
    
    selected = random.choice(top_candidates)
    
    print(f"Selected voice: {selected['speaker']} for '{personality_name}'")
    print(f"Metadata: {selected['metadata']}")
    print(f"Score: {selected['score']}")
    if dna_parameters:
        print(f"DNA-influenced energy: {preferences['energy']:.2f}")
    
    return selected

# Test function
if __name__ == '__main__':
    print("=" * 60)
    print("Testing Voice Selection with DNA")
    print("=" * 60)
    
    # Test 1: Without DNA
    print("\n--- Test 1: Basic selection (no DNA) ---")
    result1 = select_voice(
        personality_name="Frank",
        personality_description="tired barista, works mornings",
        prefer_american=True
    )
    print(f"Selected: {result1['speaker']}")
    print(f"Metadata: {result1['metadata']}")
    
    # Test 2: With DNA parameters
    print("\n--- Test 2: Selection WITH DNA ---")
    test_dna = {
        'weariness_accumulation_rate': 0.8,  # Very weary
        'confidence_baseline': 0.3,          # Low confidence
        'nostalgia_bias': 0.7                # Nostalgic
    }
    
    result2 = select_voice(
        personality_name="Frank",
        personality_description="Italian baker family, knows burnout",
        prefer_american=True,
        dna_parameters=test_dna
    )
    print(f"Selected: {result2['speaker']}")
    print(f"Metadata: {result2['metadata']}")
    
    # Test 3: Origin story style
    print("\n--- Test 3: Origin story input ---")
    origin_story = "Frank's mom was a waitress who worked doubles. Frank grew up in the kitchen."
    
    result3 = select_voice(
        personality_name="Frank",
        personality_description=origin_story,
        prefer_american=True,
        dna_parameters={'service_orientation': 0.9, 'weariness_accumulation_rate': 0.6}
    )
    print(f"Selected: {result3['speaker']}")
    print(f"Metadata: {result3['metadata']}")
    
    print("\n" + "=" * 60)
    print("Voice selection tests complete!")
    print("=" * 60)
