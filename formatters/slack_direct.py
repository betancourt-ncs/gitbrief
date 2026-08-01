import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

with open("formatters/direct_prompt.txt", "r", encoding="utf-8") as f:
    instructions = f.read()


def generate_direct_brief(parsed_data):
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=json.dumps(parsed_data),
        temperature=0.7,
        max_output_tokens=300
    )

    return response.output_text


# Test
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from payload_parser import parse_push_event
    with open("sample_payload.json") as f:
        payload = json.load(f)

    parsed_payload = parse_push_event(payload)
    print(generate_direct_brief(parsed_payload))
