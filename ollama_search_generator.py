#!/usr/bin/env python3
"""
Ollama-Powered Search Term Generator
Uses local LLM via Ollama to generate intelligent YouTube search terms
"""

import json
import requests
from typing import List
from channel_database import ChannelDatabase

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral:7b-instruct"  # Using your installed model

def check_ollama_available() -> bool:
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def list_ollama_models() -> List[str]:
    """List available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except:
        pass
    return []

def generate_with_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Generate text using Ollama"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
        else:
            print(f"Error: Ollama returned status {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""

def generate_search_terms_ollama(existing_terms: List[str], num_terms: int = 30, model: str = DEFAULT_MODEL) -> List[str]:
    """Generate search terms using Ollama"""
    
    prompt = f"""You are an expert at finding YouTube channels about prepping, survival, self-reliance, and emergency preparedness.

I've already used these search terms on YouTube:
{chr(10).join(f"- {term}" for term in existing_terms[:15])}
{'...' if len(existing_terms) > 15 else ''}

Generate {num_terms} NEW YouTube search terms that will help discover related channels. Focus on:

**Core Topics:**
- Prepping and survivalism
- Off-grid living and homesteading
- Emergency preparedness and disaster response
- Self-reliance and self-sufficiency
- Bushcraft and wilderness survival
- Urban survival and city prepping
- Food storage, preservation, and production
- Water purification and storage
- Alternative energy and power systems
- Medical preparedness and first aid
- Communications (ham radio, etc.)
- Security and self-defense

**Search Term Guidelines:**
- Make them specific but not too narrow (3-5 words ideal)
- Mix popular topics with niche specializations
- Include scenario-based terms (grid down, blackout, etc.)
- Include skill-based terms (how to, tutorial, guide)
- Include time-based terms (90 day, long term, etc.)
- Consider seasonal variations (winter survival, summer prep)
- Think about different audience levels (beginner, advanced)
- Avoid terms that are too similar to existing ones

**Output Format:**
Return ONLY a valid JSON array of strings, nothing else. Format:
["term 1", "term 2", "term 3"]

Generate {num_terms} diverse search terms now:"""

    print(f"🤖 Generating search terms with Ollama ({model})...")
    print(f"📝 Prompt: {len(prompt)} characters")
    
    response = generate_with_ollama(prompt, model)
    
    if not response:
        return []
    
    # Try to extract JSON from response
    try:
        # Look for JSON array in response
        start = response.find('[')
        end = response.rfind(']') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            terms = json.loads(json_str)
            
            # Validate and clean
            valid_terms = []
            for term in terms:
                if isinstance(term, str) and len(term) > 3 and len(term) < 100:
                    # Clean up
                    term = term.strip().strip('"\'')
                    if term and term.lower() not in [t.lower() for t in existing_terms]:
                        valid_terms.append(term)
            
            return valid_terms[:num_terms]
        else:
            print("⚠️ Could not find JSON array in response")
            print(f"Response preview: {response[:200]}...")
            return []
    except json.JSONDecodeError as e:
        print(f"⚠️ Could not parse JSON: {e}")
        print(f"Response preview: {response[:200]}...")
        return []

def analyze_term_quality(term: str, model: str = DEFAULT_MODEL) -> dict:
    """Analyze the quality of a search term using Ollama"""
    
    prompt = f"""Analyze this YouTube search term for finding prepper/survival channels: "{term}"

Rate it on:
1. Specificity (1-10): How specific is it?
2. Relevance (1-10): How relevant to prepping/survival?
3. Popularity (1-10): How likely to return results?

Respond with ONLY a JSON object:
{{"specificity": X, "relevance": X, "popularity": X, "note": "brief comment"}}"""

    response = generate_with_ollama(prompt, model)
    
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    
    return {"specificity": 5, "relevance": 5, "popularity": 5, "note": "Could not analyze"}

def generate_targeted_terms(niche: str, num_terms: int = 10, model: str = DEFAULT_MODEL) -> List[str]:
    """Generate search terms for a specific niche"""
    
    prompt = f"""Generate {num_terms} YouTube search terms specifically about: {niche}

Context: Finding channels about prepping, survival, and self-reliance with focus on {niche}.

Return ONLY a JSON array:
["term 1", "term 2", ...]"""

    response = generate_with_ollama(prompt, model)
    
    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    
    return []

def main():
    """Main function"""
    print("🤖 Ollama-Powered Search Term Generator")
    print("=" * 60)
    
    # Check Ollama availability
    if not check_ollama_available():
        print("❌ Ollama is not running!")
        print("\n💡 To install and start Ollama:")
        print("   1. Install: brew install ollama")
        print("   2. Start server: ollama serve")
        print("   3. Pull a model: ollama pull llama3.2")
        print("\nOr visit: https://ollama.ai/")
        return
    
    print("✓ Ollama server is running")
    
    # List available models
    models = list_ollama_models()
    if models:
        print(f"✓ Available models: {', '.join(models)}")
        model = models[0]  # Use first available model
        print(f"✓ Using model: {model}")
    else:
        print("⚠️ No models found. Please pull a model:")
        print("   ollama pull llama3.2")
        return
    
    # Connect to database
    db = ChannelDatabase()
    db.connect()
    
    existing_terms = [row['search_term'] for row in db.get_all_search_terms()]
    
    if not existing_terms:
        existing_terms = [
            "prepper grid down",
            "survival knowledge",
            "off grid living",
            "SHTF preparation",
            "collapse survival",
            "emergency preparedness tutorial",
            "homesteading self reliance",
            "survival library",
            "prepper checklist 2025",
            "90 day blackout survival"
        ]
        for term in existing_terms:
            db.add_search_term(term, 'default')
    
    print(f"\n📚 Existing search terms: {len(existing_terms)}")
    
    # Generate new terms
    print(f"\n🎯 Generating 30 new search terms with {model}...")
    print("⏳ This may take 30-60 seconds...")
    
    new_terms = generate_search_terms_ollama(existing_terms, num_terms=30, model=model)
    
    if not new_terms:
        print("\n❌ Failed to generate terms. Check Ollama server.")
        db.close()
        return
    
    print(f"\n✨ Generated {len(new_terms)} new search terms:")
    print()
    
    for i, term in enumerate(new_terms, 1):
        print(f"  {i:2d}. {term}")
        db.add_search_term(term, 'ollama_generated')
    
    # Save to file
    with open('ollama_generated_terms.txt', 'w') as f:
        for term in new_terms:
            f.write(f"{term}\n")
    
    print(f"\n✓ Saved to ollama_generated_terms.txt")
    
    # Combine with existing
    all_terms = existing_terms + new_terms
    with open('all_search_terms.txt', 'w') as f:
        for term in all_terms:
            f.write(f"{term}\n")
    
    print(f"✓ Updated all_search_terms.txt ({len(all_terms)} total terms)")
    
    db.close()
    
    print(f"\n🎉 Success! You now have {len(all_terms)} search terms")
    print("\n💡 Next steps:")
    print("   1. Review ollama_generated_terms.txt")
    print("   2. Edit find_more_channels.py to use all_search_terms.txt")
    print("   3. Run: python3 find_more_channels.py")
    print("   4. Run: python3 ollama_channel_analyzer.py (to filter results)")

if __name__ == "__main__":
    main()

