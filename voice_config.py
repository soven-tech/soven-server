# voice_config.py
"""
Hybrid voice system configuration for Soven
Combines multi-speaker VCTK with single-speaker American models
"""

# VCTK Multi-speaker voices (British + some American)
VCTK_VOICES = {
    # American speakers (prioritize these for North American users)
    'p297': {'gender': 'F', 'age': 27, 'accent': 'American', 'region': 'New Jersey'},
    'p336': {'gender': 'M', 'age': 19, 'accent': 'American', 'region': 'New Jersey'},
    'p323': {'gender': 'F', 'age': 19, 'accent': 'American', 'region': 'New Jersey'},
    
    # British speakers (good variety for different personalities)
    'p225': {'gender': 'F', 'age': 23, 'accent': 'British', 'region': 'Southern England'},
    'p226': {'gender': 'M', 'age': 22, 'accent': 'British', 'region': 'Surrey'},
    'p227': {'gender': 'M', 'age': 38, 'accent': 'British', 'region': 'Cumbria'},
    'p228': {'gender': 'F', 'age': 22, 'accent': 'British', 'region': 'Southern England'},
    'p229': {'gender': 'F', 'age': 23, 'accent': 'British', 'region': 'Southern England'},
    'p230': {'gender': 'F', 'age': 22, 'accent': 'British', 'region': 'Stockton-on-tees'},
    'p232': {'gender': 'M', 'age': 23, 'accent': 'British', 'region': 'Southern England'},
    'p233': {'gender': 'F', 'age': 23, 'accent': 'British', 'region': 'Staffordshire'},
    'p234': {'gender': 'F', 'age': 22, 'accent': 'Scottish', 'region': 'West Dumfries'},
    'p236': {'gender': 'F', 'age': 23, 'accent': 'British', 'region': 'Manchester'},
    'p237': {'gender': 'M', 'age': 22, 'accent': 'Scottish', 'region': 'Fife'},
    'p238': {'gender': 'F', 'age': 22, 'accent': 'British', 'region': 'Potters Bar'},
    'p239': {'gender': 'F', 'age': 22, 'accent': 'British', 'region': 'Essex'},
    'p240': {'gender': 'F', 'age': 21, 'accent': 'British', 'region': 'Nottingham'},
    'p241': {'gender': 'M', 'age': 21, 'accent': 'Scottish', 'region': 'Inverness'},
    'p243': {'gender': 'M', 'age': 22, 'accent': 'British', 'region': 'London'},
    'p244': {'gender': 'M', 'age': 22, 'accent': 'British', 'region': 'Manchester'},
}

# Single-speaker American models (fallback options)
SINGLE_SPEAKER_MODELS = {
    'ljspeech': {
        'model_name': 'tts_models/en/ljspeech/vits',
        'gender': 'F',
        'accent': 'American',
        'age': 30,
        'description': 'Clear, professional female American voice'
    },
    'jenny': {
        'model_name': 'tts_models/en/jenny/jenny',
        'gender': 'F',
        'accent': 'American',
        'age': 28,
        'description': 'Warm, friendly female American voice'
    }
}

# Default model configuration
DEFAULT_MODEL = 'tts_models/en/vctk/vits'
DEFAULT_SPEAKER = 'p297'  # American female as default

def get_all_voices():
    """Return all available voices with metadata"""
    return {
        'multi_speaker': VCTK_VOICES,
        'single_speaker': SINGLE_SPEAKER_MODELS
    }

def get_voice_by_id(voice_id):
    """Get voice metadata by ID"""
    if voice_id in VCTK_VOICES:
        return {
            'type': 'multi_speaker',
            'model': DEFAULT_MODEL,
            'speaker': voice_id,
            'metadata': VCTK_VOICES[voice_id]
        }
    elif voice_id in SINGLE_SPEAKER_MODELS:
        return {
            'type': 'single_speaker',
            'model': SINGLE_SPEAKER_MODELS[voice_id]['model_name'],
            'speaker': None,
            'metadata': SINGLE_SPEAKER_MODELS[voice_id]
        }
    return None
