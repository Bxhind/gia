from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

APP_NAME = "ПринтПлюс"
APP_VERSION = "1.0.0"

LOGO_PATH = BASE_DIR / "resources" / "logo.png"
ICON_PATH = BASE_DIR / "resources" / "app.ico"
