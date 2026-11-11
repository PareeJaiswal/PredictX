
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = Path(
    os.environ.get(
        "MAINTENANCE_DB",
        PROJECT_ROOT / "database" / "maintenance.db"
    )
)
