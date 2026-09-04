import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    master = "master"
    dispatcher = "dispatcher"
    admin = "admin"


class ReportStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    city: Mapped[str] = mapped_column(String(80), default="Город")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.master)
    pin: Mapped[str] = mapped_column(String(20), default="1234")
    is_active: Mapped[bool] = mapped_column(default=True)

    reports: Mapped[list["Report"]] = relationship(back_populates="employee")


class WorkItem(Base):
    __tablename__ = "work_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500))
    unit: Mapped[str] = mapped_column(String(50), default="шт.")
    tariff: Mapped[float | None] = mapped_column(Float, nullable=True)
    operation_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="Прочее")
    is_internal: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    lines: Mapped[list["ReportLine"]] = relationship(back_populates="work_item")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    report_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.draft)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship(back_populates="reports")
    lines: Mapped[list["ReportLine"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )

    @property
    def total_amount(self) -> float:
        return sum(line.amount for line in self.lines)


class ReportLine(Base):
    __tablename__ = "report_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    work_item_id: Mapped[int] = mapped_column(ForeignKey("work_items.id"))
    quantity: Mapped[float] = mapped_column(Float)
    unit_price: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)

    report: Mapped["Report"] = relationship(back_populates="lines")
    work_item: Mapped["WorkItem"] = relationship(back_populates="lines")
