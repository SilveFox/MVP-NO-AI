# MVP — веб-сервис отчётов без ИИ

Структурированный сбор отчётов от сотрудников: выбор работ из прайса,
автоматический расчёт сумм, утверждение диспетчером, экспорт в XLSX/TXT/CSV.

## Быстрый старт

```bash
cd mvp-no-ai
pip install -r requirements.txt
python run.py
```

Откройте в браузере: **http://127.0.0.1:8000**

## Учётные записи (по умолчанию)

| Роль | ФИО | PIN |
|------|-----|-----|
| Мастер | любой из списка (34 чел.) | `1234` |
| Диспетчер | Диспетчер | `0000` |
| Админ | Администратор | `admin` |

## Возможности MVP

- Вход по ФИО + PIN
- Форма отчёта: поиск работы, категории, количество
- Автоподстановка тарифа и расчёт суммы
- Отправка отчёта на проверку
- Панель диспетчера: утверждение / возврат
- Экспорт: XLSX (3 листа), TXT, CSV
- База: **15** позиций прайса (3 категории × 5 работ) + 5 сотрудников (3 мастера + диспетчер + админ)

## Структура проекта

```
mvp-no-ai/
├── run.py                 # Запуск сервера
├── requirements.txt
├── data/
│   ├── seed_works.json    # Прайс из Shablon_SE.xlsx
│   ├── seed_employees.json
│   ├── internal_tariffs.json
│   └── reports.db         # SQLite (создаётся при запуске)
└── app/
    ├── main.py            # FastAPI приложение
    ├── models.py          # Модели БД
    ├── routers/           # Маршруты веб и API
    ├── services/          # Расчёты, экспорт, seed
    ├── templates/         # HTML шаблоны
    └── static/            # CSS, JS
```

## Обновление прайса

Положите новый Excel в `data/` и выполните (в Python):

```python
from app.database import SessionLocal
from app.services.seed import import_price_from_xlsx
from pathlib import Path
db = SessionLocal()
import_price_from_xlsx(db, Path("data/Shablon_SE.xlsx"))
```

## Дальнейшее развитие

- [ ] Избранные работы
- [ ] Бригады и деление суммы
- [ ] Заполнение оригинального Shablon_SE.xlsx
- [ ] PWA / мобильная оптимизация
- [ ] Импорт прайса через UI
