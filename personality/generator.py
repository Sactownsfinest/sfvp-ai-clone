#!/usr/bin/env python3
"""
SFVP AI Script Generator
Runs locally on CPU — no GPU needed, no cost.
Requires: Ollama installed + llama3.1:8b pulled
Install Ollama: https://ollama.com/download
Pull model: ollama pull llama3.1:8b
"""

import sys
import os
import json
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
BASE_DIR = Path(__file__).parent

SYSTEM_PROMPT_FILE = BASE_DIR / "system_prompt.txt"
WRITING_SAMPLES_FILE = BASE_DIR.parent / "assets" / "personality" / "writing_samples.txt"
SCRIPTS_DIR = BASE_DIR.parent / "scripts"

AD_TYPES = {
    "1": ("Product Spotlight", "Highlight a specific product or service with pricing or offer"),
    "2": ("Sale / Promo",      "Announce a limited-time deal, discount, or special offer"),
    "3": ("Brand Story",       "Share who SFVP is, why it exists, what makes it different"),
    "4": ("Event / Drop",      "Promote an upcoming event, product drop, or pop-up"),
    "5": ("Testimonial Style", "Speak as if telling a friend exactly why they need SFVP"),
    "6": ("Custom / Free",     "You describe exactly what you want"),
}

LENGTHS = {
    "1": ("15 seconds", "30-40 words"),
    "2": ("30 seconds", "60-80 words"),
    "3": ("60 seconds", "120-150 words"),
}


def load_system_prompt():
    if not SYSTEM_PROMPT_FILE.exists():
        print(f"ERROR: system_prompt.txt not found at {SYSTEM_PROMPT_FILE}")
        sys.exit(1)
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")


def load_writing_samples():
    if not WRITING_SAMPLES_FILE.exists():
        return ""
    samples = WRITING_SAMPLES_FILE.read_text(encoding="utf-8").strip()
    if not samples:
        return ""
    lines = [l.strip() for l in samples.splitlines() if l.strip()]
    preview = lines[:20]
    return "\n\nHere are real examples of how Shennel writes and speaks (use these as style reference):\n" + "\n".join(f'- "{s}"' for s in preview)


def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            if not any(MODEL.split(":")[0] in m for m in models):
                print(f"\nWARNING: Model '{MODEL}' not found in Ollama.")
                print(f"Run this command first: ollama pull {MODEL}\n")
            return True
    except Exception:
        pass
    print("\nERROR: Ollama is not running.")
    print("Start it with: ollama serve")
    print("Or download from: https://ollama.com/download\n")
    return False


def generate_script(ad_type_name, topic, length_label, word_count, system_prompt, writing_samples):
    user_prompt = f"""Write a video ad script for Sactown's Finest Vinyl & Print.

Ad type: {ad_type_name}
Topic/Details: {topic}
Target length: {length_label} ({word_count})

IMPORTANT:
- Write ONLY the spoken script, nothing else
- No stage directions, no [brackets], no labels like "Hook:" or "CTA:"
- Write exactly as Shennel would say it out loud
- Stick strictly to the word count
- End with a clear call-to-action (visit website, DM us, link in bio, etc.)
{writing_samples}"""

    payload = {
        "model": MODEL,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": True,
        "options": {
            "temperature": 0.85,
            "top_p": 0.92,
            "repeat_penalty": 1.15,
        }
    }

    print(f"\n{'='*55}")
    print(f"  SFVP AI CLONE — Generating {length_label} script...")
    print(f"{'='*55}\n")

    full_response = ""
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as resp:
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    print(token, end="", flush=True)
                    full_response += token
                    if chunk.get("done"):
                        break
    except Exception as e:
        print(f"\nERROR during generation: {e}")
        return None

    print(f"\n\n{'='*55}")
    return full_response.strip()


def save_script(script, ad_type_name, topic):
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in " _-").strip().replace(" ", "_")
    filename = SCRIPTS_DIR / f"{ad_type_name.replace(' ', '_')}_{safe_topic}.txt"
    filename.write_text(script, encoding="utf-8")
    print(f"Script saved to: {filename}")


def main():
    print("\n" + "="*55)
    print("  SACTOWN'S FINEST — AI Script Generator")
    print("  Powered by Ollama + Llama 3.1 (free, local)")
    print("="*55)

    if not check_ollama():
        sys.exit(1)

    system_prompt = load_system_prompt()
    writing_samples = load_writing_samples()

    if writing_samples:
        print("  Writing samples loaded — personality dialed in.")
    else:
        print("  No writing samples found yet — add them to assets/personality/writing_samples.txt for better results.")

    print("\nAD TYPE — Pick what kind of script you need:\n")
    for key, (name, desc) in AD_TYPES.items():
        print(f"  {key}. {name}")
        print(f"     {desc}")

    while True:
        choice = input("\nEnter number (1-6): ").strip()
        if choice in AD_TYPES:
            ad_type_name, ad_type_desc = AD_TYPES[choice]
            break
        print("Pick a number 1-6.")

    if choice == "6":
        topic = input("\nDescribe exactly what you want the script to say or promote:\n> ").strip()
    else:
        topic = input(f"\nWhat product, deal, or topic? Be specific — the more detail, the better:\n> ").strip()

    print("\nLENGTH — How long should the video be?\n")
    for key, (label, words) in LENGTHS.items():
        print(f"  {key}. {label}  ({words})")

    while True:
        length_choice = input("\nEnter number (1-3): ").strip()
        if length_choice in LENGTHS:
            length_label, word_count = LENGTHS[length_choice]
            break
        print("Pick 1, 2, or 3.")

    script = generate_script(ad_type_name, topic, length_label, word_count, system_prompt, writing_samples)

    if script:
        while True:
            action = input("\nSave this script? (y=yes/approved, n=no, r=rejected): ").strip().lower()
            if action == "y":
                save_script(script, ad_type_name, topic)
                approved_dir = SCRIPTS_DIR / "approved"
                approved_dir.mkdir(exist_ok=True)
                safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in " _-").strip().replace(" ", "_")
                (approved_dir / f"{ad_type_name.replace(' ', '_')}_{safe_topic}.txt").write_text(script, encoding="utf-8")
                print("Saved to approved scripts.")
                break
            elif action == "r":
                rejected_dir = SCRIPTS_DIR / "rejected"
                rejected_dir.mkdir(exist_ok=True)
                safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in " _-").strip().replace(" ", "_")
                (rejected_dir / f"{ad_type_name.replace(' ', '_')}_{safe_topic}.txt").write_text(script, encoding="utf-8")
                print("Saved to rejected. This helps train better scripts over time.")
                break
            elif action == "n":
                print("Script discarded.")
                break

        again = input("\nGenerate another script? (y/n): ").strip().lower()
        if again == "y":
            main()


if __name__ == "__main__":
    main()
