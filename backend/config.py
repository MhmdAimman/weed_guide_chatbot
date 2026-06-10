import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
PERSIST_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "weed_guide"
PDF_PATH = str(BASE_DIR / "manual.pdf")
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500

TOPICS = {
    "identification": "Identification",
    "identify": "Identification",
    "id": "Identification",
    "control": "Control Methods",
    "controls": "Control Methods",
    "control methods": "Control Methods",
    "life cycle": "Life Cycle",
    "lifecycle": "Life Cycle",
    "life-cycle": "Life Cycle",
}

SPECIES_BY_CATEGORY = {
    "thistle": ["Bull thistle", "Canada thistle", "Musk thistle", "Scotch thistle"],
    "knapweed": ["Diffuse knapweed", "Spotted knapweed", "Russian knapweed"],
    "mustard": ["Shepard's purse", "Tansey mustard"],
    "bindweed": ["Field Bindweed"],
}

SPECIES_ALIASES = {
    "bull thistle": "Bull thistle",
    "canada thistle": "Canada thistle",
    "musk thistle": "Musk thistle",
    "scotch thistle": "Scotch thistle",
    "houndstongue": "Houndstongue",
    "diffuse knapweed": "Diffuse knapweed",
    "spotted knapweed": "Spotted knapweed",
    "russian knapweed": "Russian knapweed",
    "hoary cress": "Hoary Cress (Whitetop)",
    "whitetop": "Hoary Cress (Whitetop)",
    "salt cedar": "Salt Cedar (Tamarisk)",
    "saltcedar": "Salt Cedar (Tamarisk)",
    "tamarisk": "Salt Cedar (Tamarisk)",
    "common mullein": "Common Mullein",
    "locoweed": "Locoweed (Wooly)",
    "wooly locoweed": "Locoweed (Wooly)",
    "field bindweed": "Field Bindweed",
    "perennial pepperweed": "Perennial Pepperweed",
    "kochia": "Kochia",
    "russian olive": "Russian Olive",
    "rabbit brush": "Rabbit Brush",
    "rabbitbrush": "Rabbit Brush",
    "cheatgrass": "Cheatgrass - Downy brome",
    "downy brome": "Cheatgrass - Downy brome",
    "shepard's purse": "Shepard's purse",
    "shepherd's purse": "Shepard's purse",
    "tansey mustard": "Tansey mustard",
    "tansy mustard": "Tansey mustard",
    "common cocklebur": "Common Cocklebur",
}

SPECIES_TO_CATEGORY = {
    species.lower(): category
    for category, species_names in SPECIES_BY_CATEGORY.items()
    for species in species_names
}
