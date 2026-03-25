import contextlib
import os
from typing import Any, Optional

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

API_KEY = os.environ["POKEMON_TCG_API_KEY"]
BASE_URL = "https://api.pokemontcg.io/v2"

APP_RUNNER_HOST = "APP RUNNER ENDPOINT URL"

mcp = FastMCP(
    "pokemon-tcg",
    instructions="Search Pokemon cards, sets, and pricing data from the Pokemon TCG API.",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            APP_RUNNER_HOST,
        ],
        allowed_origins=[
            f"https://{APP_RUNNER_HOST}",
        ],
    ),
)

def api_headers() -> dict[str, str]:
    return {
        "X-Api-Key": API_KEY,
        "Accept": "application/json",
    }

async def get_json(path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{BASE_URL}{path}",
            headers=api_headers(),
            params=params or {},
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def search_cards(query: str, page: int = 1, page_size: int = 10) -> dict[str, Any]:
    data = await get_json(
        "/cards",
        params={
            "q": query,
            "page": page,
            "pageSize": min(page_size, 50),
        },
    )

    results = []
    for card in data.get("data", []):
        tcgplayer = card.get("tcgplayer", {}) or {}
        prices = tcgplayer.get("prices", {}) or {}

        results.append({
            "id": card.get("id"),
            "name": card.get("name"),
            "number": card.get("number"),
            "rarity": card.get("rarity"),
            "set": card.get("set", {}).get("name"),
            "small_image": card.get("images", {}).get("small"),
            "tcgplayer_url": tcgplayer.get("url"),
            "price_types": list(prices.keys()) if isinstance(prices, dict) else [],
        })

    return {
        "page": data.get("page"),
        "pageSize": data.get("pageSize"),
        "count": data.get("count"),
        "totalCount": data.get("totalCount"),
        "results": results,
    }

@mcp.tool()
async def get_card(card_id: str) -> dict[str, Any]:
    data = await get_json(f"/cards/{card_id}")
    card = data["data"]

    return {
        "id": card.get("id"),
        "name": card.get("name"),
        "supertype": card.get("supertype"),
        "subtypes": card.get("subtypes"),
        "hp": card.get("hp"),
        "types": card.get("types"),
        "rarity": card.get("rarity"),
        "number": card.get("number"),
        "artist": card.get("artist"),
        "set": {
            "id": card.get("set", {}).get("id"),
            "name": card.get("set", {}).get("name"),
            "series": card.get("set", {}).get("series"),
            "releaseDate": card.get("set", {}).get("releaseDate"),
        },
        "images": card.get("images"),
        "tcgplayer": card.get("tcgplayer"),
        "cardmarket": card.get("cardmarket"),
    }

@mcp.tool()
async def search_sets(query: str, page: int = 1, page_size: int = 10) -> dict[str, Any]:
    data = await get_json(
        "/sets",
        params={
            "q": query,
            "page": page,
            "pageSize": min(page_size, 50),
        },
    )

    results = []
    for s in data.get("data", []):
        results.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "series": s.get("series"),
            "printedTotal": s.get("printedTotal"),
            "total": s.get("total"),
            "releaseDate": s.get("releaseDate"),
            "symbol": s.get("images", {}).get("symbol"),
            "logo": s.get("images", {}).get("logo"),
        })

    return {
        "page": data.get("page"),
        "pageSize": data.get("pageSize"),
        "count": data.get("count"),
        "totalCount": data.get("totalCount"),
        "results": results,
    }

@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with mcp.session_manager.run():
        yield

app = Starlette(
    routes=[
        Mount("/", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
