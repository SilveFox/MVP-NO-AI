"""Сброс прайса из seed_works.json (демо-версия)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.services.seed import reset_works

if __name__ == "__main__":
    db = SessionLocal()
    works, internal = reset_works(db)
    print(f"Прайс обновлён: {works} работ, {internal} внутренних тарифов")
