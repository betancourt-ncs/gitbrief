# gitbrief

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**gitbrief** is an event-driven automation tool that listens for your GitHub push events and uses an LLM to generate a professional, shareable brief delievered to Slack automatically.

The workflow: a developer pushes to GitHub, and gitbrief automatically produces a professional, human-readable brief of what was built, what stack was used, and what concepts were applied. The output is formatted for real social audiences: LinkedIn, Twitter/X, forums, communities, or any online/social media outlets.

This tool is best suited for developers who build in public, to make the project or features sharing process more efficient.


Push to GitHub. Get a social media-ready summary in Slack. No manual writing.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [License](#license)

---

## How It Works

```
GitHub push event
      │
      ▼
GitHub Webhook (POSTs to your server)
      │
      ▼
ngrok (tunnels external traffic to localhost)
      │
      ▼
FastAPI server (server.py)
      │
      ▼
payload_parser.py (extracts structured data from raw payload)
      │
      ▼
formatters/slack_social.py (calls OpenAI API, returns formatted brief)
      │
      ▼
slack.py (POSTs the brief to Slack via incoming webhook)
```

- **Inbound webhook** — GitHub POSTs to your public ngrok URL, which tunnels to your local FastAPI server.
- **Outbound webhook** — Your server POSTs the generated brief to Slack's incoming webhook URL.
- GitHub and Slack never talk to each other directly. Your server is the brain.

---

## Features

- Listens for GitHub push events via a FastAPI webhook endpoint
- Parses raw GitHub payloads into clean structured data (repo, pusher, branch, commits, file changes)
- Generates a formatted social brief using `gpt-4o-mini` via the OpenAI Responses API (includes what was built, stack used, and concepts applied)
- Posts the brief to a Slack channel via an incoming webhook
- Output is written in first person, scaled to push size, and formatted for LinkedIn, Twitter/X, or other socials

---

## Tech Stack

| Layer | Technology |
|---|---|
| Server | FastAPI + uvicorn |
| Tunneling | ngrok |
| LLM | OpenAI Responses API (`gpt-4o-mini`) |
| Slack integration | Incoming Webhooks |
| HTTP client | requests |
| Environment | python-dotenv |

---

## Project Structure

<details>
<summary>Click to expand</summary>

```
gitbrief/
├── formatters/
│   ├── __init__.py
│   └── slack_social.py     # Calls OpenAI, returns formatted social brief
├── server.py               # FastAPI app — receives GitHub webhook, orchestrates pipeline
├── payload_parser.py       # Extracts clean data from raw GitHub push payload
├── slack.py                # Posts formatted brief to Slack via outbound webhook
├── .env                    # API keys and config (never committed)
├── .gitignore
├── requirements.txt
└── README.md
```

</details>

---

## Installation

**Prerequisites:** Python 3.x, [ngrok](https://ngrok.com) (install via Homebrew: `brew install ngrok`)

```bash
# Clone the repo
git clone https://github.com/betancourt-ncs/gitbrief.git
cd gitbrief

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_incoming_webhook_url
```

<details>
<summary>Where to get these values</summary>

**OpenAI API Key**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys → Create new secret key
3. Copy immediately — you won't see it again

**Slack Webhook URL**
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From scratch
2. Enable **Incoming Webhooks** under Features
3. Add a new webhook to your workspace and select a channel
4. Copy the webhook URL

</details>

---

## Running Locally

gitbrief requires three things running simultaneously: your FastAPI server, an ngrok tunnel, and a configured GitHub webhook.

**1. Start the server**

```bash
uvicorn server:app --reload
```

**2. Start ngrok**

```bash
ngrok http --url=safeguard-circus-mortality.ngrok-free.dev 8000
```

**3. Configure the GitHub webhook**

In your GitHub repo → Settings → Webhooks → Add webhook:

| Field | Value |
|---|---|
| Payload URL | `https://your-ngrok-domain/webhook` |
| Content type | `application/json` |
| Events | Just the push event |

Once all three are running, push to your repo. Gitbrief will parse the event, generate a brief, and post it to Slack automatically.

---

## License

MIT

