"""
config.py

Project configuration and bath definitions. Uses relative paths so the repo
is portable (works on any host when cloned).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "bath_monitor.db"
IMAGE_DIR = BASE_DIR / "images"

# Keys used as table names; labels are German for display.
BATHS = {
    "olympia": {"label": "Olympia-Schwimmhalle", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30182"},
    "north": {"label": "Nordbad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30184"},
    "miller": {"label": "Müllersches Volksbad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30197"},
    "michaeli": {"label": "Michaelibad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30208"},
    "dante": {"label": "Dantebad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=129"},
    "west": {"label": "Westbad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30199"},
    "south": {"label": "Südbad", "apiUrl": "https://counter.ticos-systems.cloud/api/gates/counter?organizationUnitIds=30187"},
}
