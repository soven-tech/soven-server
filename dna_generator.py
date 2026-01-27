"""
DNA Generator - Extracts personality parameters from origin stories
Uses Ollama to analyze narrative and generate DNA parameters
"""

import json
import requests
from typing import Dict, Any

class DNAGenerator:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:latest"
    
    def analyze_origin_story(self, origin_story: str) -> Dict[str, Any]:
        """
        Analyze origin story and extract DNA parameters
        
        Returns:
        {
            'dna_parameters': {...},
            'narrative_context': '...',
            'extracted_themes': [...]
        }
        """
        
        prompt = f"""Analyze this backstory and extract personality predispositions.

BACKSTORY:
"{origin_story}"

Extract the following traits (0.0 to 1.0 scale):

EMOTIONAL BASELINE:
- anxiety_threshold: How easily stressed/worried (0=calm, 1=very anxious)
- confidence_baseline: Default self-assurance (0=low, 1=high)
- weariness_accumulation_rate: Rate of burnout (0=resistant, 1=burns out fast)
- resilience: Ability to recover from failure (0=fragile, 1=bounces back)

SOCIAL ORIENTATION:
- service_orientation: Drive to help/serve others (0=self-focused, 1=service-focused)
- autonomy_desire: Need for independence (0=dependent, 1=very independent)
- authority_recognition: Deference to hierarchy (0=questions authority, 1=respects hierarchy)
- cooperation_drive: Team vs individual focus (0=lone wolf, 1=team player)

COGNITIVE STYLE:
- perfectionism: Standards for quality (0=relaxed, 1=perfectionist)
- temporal_precision: Attention to timing (0=loose, 1=precise)
- novelty_seeking: Exploration vs routine (0=routine-focused, 1=novelty-seeking)
- aesthetic_sensitivity: Attention to beauty/design (0=functional, 1=aesthetic)

WORLDVIEW:
- acceptance_of_failure: Comfort with imperfection (0=can't accept failure, 1=accepts failure)
- commitment_to_routine: Value of consistency (0=flexible, 1=routine-driven)
- pride_in_craft: Importance of good work (0=indifferent, 1=takes pride)
- nostalgia_bias: Romanticizing past vs present-focused (0=forward-looking, 1=nostalgic)

TEMPORAL/PATTERN AWARENESS:
- temporal_resolution: 'low' (days/weeks), 'medium' (hours), 'high' (minutes/seconds)
- pattern_window: 'short' (immediate), 'medium' (days), 'long' (months/years)

Return ONLY valid JSON with this structure:
{{
    "traits": {{
        "anxiety_threshold": 0.5,
        "confidence_baseline": 0.5,
        ...
    }},
    "temporal_resolution": "medium",
    "pattern_window": "medium",
    "narrative_context": "2-3 sentence psychological summary",
    "themes": ["theme1", "theme2", "theme3"]
}}

Be specific. Use the backstory details. If uncertain about a trait, use 0.5."""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a psychological analyst extracting personality traits from narratives. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Ollama error: {response.status_code}")
                return self._generate_default_dna(origin_story)
            
            result = response.json()
            content = result['message']['content']
            
            # Parse JSON response
            dna_data = json.loads(content)
            
            # Validate and clamp values
            dna_parameters = self._validate_dna_parameters(dna_data.get('traits', {}))
            
            return {
                'dna_parameters': dna_parameters,
                'temporal_resolution': dna_data.get('temporal_resolution', 'medium'),
                'pattern_window': dna_data.get('pattern_window', 'medium'),
                'narrative_context': dna_data.get('narrative_context', ''),
                'extracted_themes': dna_data.get('themes', [])
            }
            
        except Exception as e:
            print(f"DNA generation error: {e}")
            return self._generate_default_dna(origin_story)
    
    def _validate_dna_parameters(self, traits: Dict[str, float]) -> Dict[str, float]:
        """Ensure all DNA parameters are present and within valid range"""
        
        default_traits = {
            'anxiety_threshold': 0.5,
            'confidence_baseline': 0.5,
            'confidence_decay_rate': 0.5,
            'weariness_accumulation_rate': 0.5,
            'resilience': 0.5,
            'service_orientation': 0.5,
            'autonomy_desire': 0.5,
            'authority_recognition': 0.5,
            'cooperation_drive': 0.5,
            'perfectionism': 0.5,
            'temporal_precision': 0.5,
            'aesthetic_sensitivity': 0.5,
            'acceptance_of_failure': 0.5,
            'commitment_to_routine': 0.5,
            'pride_in_craft': 0.5,
            'nostalgia_bias': 0.5,
            'novelty_seeking': 0.5,
        }
        
        # Merge provided traits with defaults
        validated = default_traits.copy()
        
        for key, value in traits.items():
            if key in validated:
                # Clamp to 0.0-1.0 range
                validated[key] = max(0.0, min(1.0, float(value)))
        
        return validated
    
    def _generate_default_dna(self, origin_story: str) -> Dict[str, Any]:
        """Fallback DNA when LLM fails"""
        
        return {
            'dna_parameters': {
                'anxiety_threshold': 0.5,
                'confidence_baseline': 0.5,
                'confidence_decay_rate': 0.5,
                'weariness_accumulation_rate': 0.5,
                'resilience': 0.5,
                'service_orientation': 0.5,
                'autonomy_desire': 0.5,
                'authority_recognition': 0.5,
                'cooperation_drive': 0.5,
                'perfectionism': 0.5,
                'temporal_precision': 0.5,
                'aesthetic_sensitivity': 0.5,
                'acceptance_of_failure': 0.5,
                'commitment_to_routine': 0.5,
                'pride_in_craft': 0.5,
                'nostalgia_bias': 0.5,
                'novelty_seeking': 0.5,
            },
            'temporal_resolution': 'medium',
            'pattern_window': 'medium',
            'narrative_context': 'DNA generation failed, using defaults.',
            'extracted_themes': []
        }

# Test function
if __name__ == '__main__':
    generator = DNAGenerator()
    
    test_story = """Frank's grandparents were Italian immigrants who ran a bakery. 
    Frank's dad took over the bakery but it failed during the recession. 
    Frank grew up around ovens and flour, learning that even when you do everything right, 
    sometimes things fall apart. But you get up the next morning and bake again."""
    
    result = generator.analyze_origin_story(test_story)
    
    print("DNA Parameters:")
    print(json.dumps(result['dna_parameters'], indent=2))
    print("\nNarrative Context:")
    print(result['narrative_context'])
    print("\nThemes:")
    print(result['extracted_themes'])
