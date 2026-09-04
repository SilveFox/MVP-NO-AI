"""Поиск работ по части слов (кириллица, SQLite)."""

from app.models import WorkItem


def normalize(text: str) -> str:
    return (text or "").lower().replace("ё", "е")


def work_matches_query(work: WorkItem, query: str) -> bool:
    """Проверка: все фрагменты запроса встречаются в коде или названии."""
    q = query.strip()
    if not q:
        return True
    haystack = normalize(f"{work.code} {work.name}")
    tokens = [normalize(t) for t in q.split() if t.strip()]
    return all(token in haystack for token in tokens)


def filter_works(works: list[WorkItem], query: str) -> list[WorkItem]:
    q = query.strip()
    if not q:
        return works
    return [w for w in works if work_matches_query(w, q)]
