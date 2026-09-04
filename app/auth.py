from typing import Optional

from fastapi import Request
from itsdangerous import BadSignature, URLSafeSerializer

from app.config import settings
from app.models import Employee

serializer = URLSafeSerializer(settings.secret_key, salt="session")


def create_session(employee_id: int) -> str:
    return serializer.dumps({"employee_id": employee_id})


def get_session_employee_id(request: Request) -> Optional[int]:
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        return int(data.get("employee_id"))
    except (BadSignature, TypeError, ValueError):
        return None
