"""Импорт прайса из Excel в базу данных."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.services.seed import import_price_from_xlsx

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_price.py path/to/Shablon_SE.xlsx")
        sys.exit(1)
    path = Path(sys.argv[1])
    db = SessionLocal()
    count = import_price_from_xlsx(db, path)
    print(f"Imported/updated {count} positions")
