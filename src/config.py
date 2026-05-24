from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "employees.db"

OLLAMA_MODEL = "llama3.1"
OLLAMA_BASE_URL = "http://localhost:11434"

ALLOWED_DEPARTMENTS = ["Sales", "Marketing", "Engineering"]