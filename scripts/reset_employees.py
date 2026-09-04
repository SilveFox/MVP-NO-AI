"""Сброс списка сотрудников из seed_employees.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.services.seed import reset_employees

if __name__ == "__main__":
    db = SessionLocal()
    count = reset_employees(db)
    print(f"Добавлено сотрудников: {count}")
