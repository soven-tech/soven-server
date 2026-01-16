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
        personality_name: Name of the AI (e.g., "Barista Bob")
        personality_description: User's description (e.g., "A cheerful morning helper")
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
        'accent': None
    }
    
    # Gender detection
    if any(word in description_lower for word in ['she', 'her', 'woman', 'female', 'girl', 'lady']):
        preferences['gender'] = 'F'
    elif any(word in description_lower for word in ['he', 'him', 'man', 'male', 'boy', 'guy']):
        preferences['gender'] = 'M'
    
    # Age hints
    if any(word in description_lower for word in ['young', 'youthful', 'fresh', 'teen']):
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
    
    # Score all VCTK voices
    candidates = []
    for speaker_id, metadata in VCTK_VOICES.items():
        score = 0
        
        # Accent preference (high priority)
        if prefer_american and metadata['accent'] == 'American':
            score += 15  # Strong preference for American
        elif preferences['accent'] and metadata['accent'] == preferences['accent']:
            score += 12
        elif metadata['accent'] == 'American':
            score += 8  # Still favor American if no specific preference
        elif metadata['accent'] in ['British', 'Scottish']:
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
    
    # If gender is specified and we want American, consider single-speaker models
    if preferences['gender'] == 'F' and prefer_american:
        # Add ljspeech as candidate
        candidates.append({
            'type': 'single_speaker',
            'model': SINGLE_SPEAKER_MODELS['ljspeech']['model_name'],
            'speaker': None,
            'metadata': SINGLE_SPEAKER_MODELS['ljspeech'],
            'score': 12  # Competitive score for American female
        })
        
        # Add jenny as candidate
        candidates.append({
            'type': 'single_speaker',
            'model': SINGLE_SPEAKER_MODELS['jenny']['model_name'],
            'speaker': None,
            'metadata': SINGLE_SPEAKER_MODELS['jenny'],
            'score': 12
        })
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Get top matches (randomize among ties for variety)
    top_score = candidates[0]['score']
    top_candidates = [c for c in candidates if c['score'] == top_score]
    
    selected = random.choice(top_candidates)
    
    print(f"\n{'='*60}")
    print(f"Voice Selection for: '{personality_name}'")
    print(f"Description: {personality_description}")
    print(f"{'='*60}")
    print(f"Selected: {selected['speaker'] if selected['speaker'] else selected['model']}")
    print(f"Type: {selected['type']}")
    print(f"Metadata: {selected['metadata']}")
    print(f"Score: {selected['score']}")
    print(f"Top 3 candidates:")
    for i, c in enumerate(top_candidates[:3], 1):
        speaker = c['speaker'] if c['speaker'] else c['model'].split('/')[-2]
        print(f"  {i}. {speaker} (score: {c['score']}) - {c['metadata'].get('accent', 'N/A')}")
    print(f"{'='*60}\n")
    
    return selected

# Test cases
if __name__ == '__main__':
    print("\n" + "="*70)
    print("TESTING HYBRID VOICE SELECTION PIPELINE")
    print("="*70)
    
    test_cases = [
        ("Barista Betty", "A cheerful young woman who loves mornings", True),
        ("Coffee Coach Carl", "A mature experienced guide", True),
        ("Scottish Sam", "A friendly Scottish gentleman", False),
        ("Morning Maven", "Energetic and helpful", True),  # No gender
        ("British Butler", "A proper English gentleman", False),
        ("Chill Companion", "Relaxed young person", True),
    ]
    
    for name, description, prefer_american in test_cases:
        voice = select_voice(name, description, prefer_american)
