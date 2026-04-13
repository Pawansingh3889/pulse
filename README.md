# Pulse

Personal AI briefing assistant. Tech news, military/defense, world politics, EPL & Champions League scores, hiking suggestions, and travel ideas. Powered by local AI via Ollama.

## Features

- **Tech News** — live from Hacker News (top stories, scores, comments)
- **Military & Defense** — aggregated from Reddit defense communities
- **World Politics** — world news and geopolitics feed
- **Football** — EPL and Champions League live scores via ESPN
- **Hiking & Travel** — curated UK + India trek suggestions with difficulty filters
- **Ask AI** — ask anything using Gemma 3 12B locally. No cloud. No tracking.

## Setup

```bash
pip install streamlit requests
ollama pull gemma3:12b
streamlit run app.py
```

## APIs Used (All Free, No Keys Needed)

| Source | What | Limit |
|---|---|---|
| Hacker News Firebase | Tech news | Unlimited |
| Reddit JSON | Military, politics | Unlimited |
| ESPN Scoreboard | EPL, Champions League | Unlimited |
| Ollama (local) | AI queries | No limit, runs on your machine |

## Stack

Python, Streamlit, Ollama (Gemma 3 12B), Hacker News API, Reddit JSON, ESPN API

## Privacy

Everything runs locally. News fetched from public APIs. AI runs on Ollama — no data leaves your machine.
