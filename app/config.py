from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Отчёты SE — MVP"
    secret_key: str = "change-me-in-production-mvp-se-2026"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'reports.db'}"
    data_dir: Path = BASE_DIR / "data"
    template_xlsx: Path | None = None

    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
