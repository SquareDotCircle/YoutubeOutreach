#!/usr/bin/env python3
"""
LLM-Powered Search Term Generator
Uses AI to generate promising YouTube search terms for finding related channels
"""

import json
import subprocess
from typing import List
from channel_database import ChannelDatabase

def generate_search_terms_with_llm(existing_terms: List[str], num_terms: int = 20) -> List[str]:
    """
    Generate new search terms using an LLM
    Uses Claude via the terminal (requires anthropic CLI or similar)
    """
    
    prompt = f"""You are helping find YouTube channels about prepping, survival, self-reliance, and related topics.

Current search terms we've used:
{chr(10).join(f"- {term}" for term in existing_terms)}

Generate {num_terms} NEW YouTube search terms that will help discover related channels. Focus on:
- Prepper/survival content
- Off-grid living and homesteading  
- Emergency preparedness
- Self-reliance and self-sufficiency
- Bushcraft and wilderness survival
- Urban survival
- Food storage and preservation
- Water purification
- Alternative energy
- Collapse scenarios

Make the terms:
- Specific enough to find relevant channels
- Different from the existing terms
- Likely to return results on YouTube
- Mix of popular and niche topics

Return ONLY a JSON array of search terms, like:
["term 1", "term 2", "term 3"]

No explanation, just the JSON array."""

    print("🤖 Generating search terms with LLM...")
    print(f"📝 Prompt length: {len(prompt)} characters")
    
    # Try multiple methods to get LLM response
    new_terms = []
    
    # Method 1: Try using anthropic CLI if available
    try:
        result = subprocess.run(
            ['anthropic', 'complete', '--prompt', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            new_terms = json.loads(response)
            print(f"✓ Generated {len(new_terms)} terms using Anthropic CLI")
            return new_terms
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    
    # Method 2: Fallback to algorithmic generation
    print("⚠ LLM not available, using algorithmic generation")
    new_terms = generate_terms_algorithmic(existing_terms, num_terms)
    
    return new_terms


def generate_terms_algorithmic(existing_terms: List[str], num_terms: int = 20) -> List[str]:
    """
    Fallback: Generate terms algorithmically by combining keywords
    """
    
    # Topic categories
    main_topics = [
        "prepper", "survival", "homesteading", "off grid", "self reliance",
        "bushcraft", "preparedness", "SHTF", "collapse", "emergency"
    ]
    
    subtopics = [
        "water purification", "food storage", "solar power", "gardening",
        "hunting", "fishing", "foraging", "first aid", "security",
        "communication", "shelter", "fire making", "navigation",
        "winter survival", "urban survival", "wilderness", "skills",
        "tools", "gear review", "bug out", "bug in", "stockpiling",
        "canning", "dehydrating", "primitive", "tactics", "strategies"
    ]
    
    modifiers = [
        "beginner", "advanced", "ultimate", "essential", "best",
        "2025", "2026", "practical", "realistic", "long term",
        "short term", "family", "solo", "urban", "rural", "tips",
        "guide", "tutorial", "how to", "mistakes", "checklist"
    ]
    
    time_periods = [
        "90 day", "1 year", "30 day", "72 hour", "long term",
        "short term", "winter", "summer", "first week", "first month"
    ]
    
    scenarios = [
        "grid down", "power outage", "economic collapse", "natural disaster",
        "pandemic", "civil unrest", "supply chain", "blackout", "war",
        "emp", "nuclear", "earthquake", "flood", "hurricane"
    ]
    
    # Extract used keywords from existing terms
    used_combinations = set()
    for term in existing_terms:
        used_combinations.add(term.lower())
    
    new_terms = []
    
    # Generate combinations
    import random
    
    # Type 1: [scenario] + [main_topic]
    for _ in range(num_terms // 5):
        scenario = random.choice(scenarios)
        topic = random.choice(main_topics)
        term = f"{scenario} {topic}"
        if term not in used_combinations:
            new_terms.append(term)
            used_combinations.add(term)
    
    # Type 2: [modifier] + [main_topic] + [subtopic]
    for _ in range(num_terms // 5):
        mod = random.choice(modifiers)
        topic = random.choice(main_topics)
        sub = random.choice(subtopics)
        term = f"{mod} {topic} {sub}"
        if term not in used_combinations and len(new_terms) < num_terms:
            new_terms.append(term)
            used_combinations.add(term)
    
    # Type 3: [time_period] + [main_topic]
    for _ in range(num_terms // 5):
        time = random.choice(time_periods)
        topic = random.choice(main_topics)
        term = f"{time} {topic}"
        if term not in used_combinations and len(new_terms) < num_terms:
            new_terms.append(term)
            used_combinations.add(term)
    
    # Type 4: [main_topic] + [subtopic] + [modifier]
    for _ in range(num_terms // 5):
        topic = random.choice(main_topics)
        sub = random.choice(subtopics)
        mod = random.choice(modifiers)
        term = f"{topic} {sub} {mod}"
        if term not in used_combinations and len(new_terms) < num_terms:
            new_terms.append(term)
            used_combinations.add(term)
    
    # Type 5: Just subtopics with modifiers
    while len(new_terms) < num_terms:
        sub1 = random.choice(subtopics)
        sub2 = random.choice(subtopics)
        if sub1 != sub2:
            term = f"{sub1} {sub2}"
            if term not in used_combinations:
                new_terms.append(term)
                used_combinations.add(term)
    
    return new_terms[:num_terms]


def save_search_terms_to_file(terms: List[str], filename: str = 'generated_search_terms.txt'):
    """Save search terms to a file"""
    with open(filename, 'w') as f:
        for term in terms:
            f.write(f"{term}\n")
    print(f"✓ Saved {len(terms)} search terms to {filename}")


def main():
    """Generate new search terms and save them"""
    print("🔍 LLM-Powered Search Term Generator")
    print("=" * 50)
    
    # Connect to database to get existing terms
    db = ChannelDatabase()
    db.connect()
    
    existing_terms = [row['search_term'] for row in db.get_all_search_terms()]
    
    if not existing_terms:
        # Default starting terms if database is empty
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
        
        # Add them to database
        for term in existing_terms:
            db.add_search_term(term, 'default')
    
    print(f"\n📚 Existing search terms: {len(existing_terms)}")
    for term in existing_terms[:5]:
        print(f"  - {term}")
    if len(existing_terms) > 5:
        print(f"  ... and {len(existing_terms) - 5} more")
    
    # Generate new terms
    print(f"\n🤖 Generating 20 new search terms...")
    new_terms = generate_search_terms_with_llm(existing_terms, num_terms=20)
    
    print(f"\n✨ Generated {len(new_terms)} new search terms:")
    for i, term in enumerate(new_terms, 1):
        print(f"  {i}. {term}")
        db.add_search_term(term, 'llm_generated')
    
    # Save to file
    save_search_terms_to_file(new_terms)
    
    # Save all terms together
    all_terms = existing_terms + new_terms
    save_search_terms_to_file(all_terms, 'all_search_terms.txt')
    
    db.close()
    
    print(f"\n✓ Total search terms now: {len(all_terms)}")
    print("\n💡 Next step: Use these terms in find_more_channels.py")
    print("   Or run: python3 batch_channel_finder.py")


if __name__ == "__main__":
    main()

