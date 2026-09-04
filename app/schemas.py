from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models import ReportStatus, UserRole


class WorkItemOut(BaseModel):
    id: int
    code: str
    name: str
    unit: str
    tariff: float | None
    operation_price: float | None
    category: str
    is_internal: bool

    model_config = {"from_attributes": True}


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    city: str
    role: UserRole

    model_config = {"from_attributes": True}


class ReportLineCreate(BaseModel):
    work_item_id: int
    quantity: float = Field(gt=0)
    note: str | None = None


class ReportLineOut(BaseModel):
    id: int
    work_item_id: int
    quantity: float
    unit_price: float
    amount: float
    note: str | None
    work_code: str | None = None
    work_name: str | None = None
    work_unit: str | None = None

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: int
    employee_id: int
    report_date: date
    status: ReportStatus
    comment: str | None
    total_amount: float
    employee_name: str | None = None
    lines: list[ReportLineOut] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    full_name: str
    pin: str = "1234"
