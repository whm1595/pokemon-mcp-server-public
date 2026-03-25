# Pokemon TCG MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes Pokemon Trading Card Game data as tools for AI assistants. It wraps the [Pokemon TCG API](https://pokemontcg.io/) and serves results over stateless streamable HTTP.

## Tools

| Tool | Description |
|------|-------------|
| `search_cards` | Search for cards using query syntax (e.g. `name:"Pikachu"`, `set.name:"Base"`). Returns ID, name, rarity, set, image, TCGplayer URL, and available price types. Supports pagination (max 50 per page). |
| `get_card` | Fetch full details for a single card by ID (e.g. `base1-4`). Returns stats, types, artist, set info, images, and pricing data from TCGplayer and Cardmarket. |
| `search_sets` | Search for card sets/expansions (e.g. `series:"Scarlet & Violet"`). Returns set name, series, card counts, release date, symbol, and logo. Supports pagination. |

## Requirements

- Python 3.11+
- A [Pokemon TCG API key](https://dev.pokemontcg.io/)

## Setup

```bash
pip install -r requirements.txt
export POKEMON_TCG_API_KEY=your_api_key_here
python server.py
```

The server runs on port 8000 using streamable HTTP transport at the root path (`/`).

## Dependencies

- `mcp[cli]` — Model Context Protocol SDK
- `httpx` — async HTTP client
- `starlette` — ASGI framework
- `uvicorn` — ASGI server

## Deployment

Configured for [AWS App Runner](https://aws.amazon.com/apprunner/) via `apprunner.yaml` on Python 3.11. The API key is pulled from AWS Secrets Manager at runtime.

## Example queries

Once connected to an MCP client:

- "What's the price of a Charizard from Base Set?"
- "Show me all cards in the Scarlet & Violet series"
- "Get details for card base1-4"
