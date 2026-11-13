import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    timeout=30.0,
    max_retries=2
)

# Allowing file reference from other locations or working directories
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# Lookup table mapping event types to format pair
EVENT_TO_PAIR = {
    "push": "direct_push.txt",
    "pull_request": "direct_pr.txt",
    "release": "direct_release.txt"
}


# Return file contents as a string given a filename
def load_prompt(filename):
    with open(PROMPTS_DIR / filename, 'r', encoding="utf-8") as f:
        return f.read()


# Produce the right instruction string (full prompt) given an event type
def build_instructions(event_type):
    core = load_prompt("DIRECT_CORE.TXT")
    pair = load_prompt(EVENT_TO_PAIR[event_type])
    return core + "\n\n" + pair


# Generate output by calling the LLM given the parsed data
def generate_direct_brief(parsed_data):
    instructions = build_instructions(parsed_data["event_type"])

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=json.dumps(parsed_data),
        temperature=0.7,
        max_output_tokens=300
    )

    return response.output_text
