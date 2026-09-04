from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session, joinedload

from app.auth import create_session, get_session_employee_id
from app.database import get_db
from app.models import Employee, Report, ReportLine, ReportStatus, UserRole, WorkItem
from app.services.calculations import calculate_line_amount
from app.services.search import filter_works

router = APIRouter()
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def require_user(request: Request, db: Session) -> Employee:
    eid = get_session_employee_id(request)
    if not eid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get(Employee, eid)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    employees = (
        db.query(Employee)
        .filter(Employee.is_active.is_(True))
        .order_by(Employee.full_name)
        .all()
    )
    return templates.TemplateResponse(
        request, "login.html", {"employees": employees, "error": None}
    )


@router.post("/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    full_name = str(form.get("full_name", "")).strip()
    pin = str(form.get("pin", "")).strip()
    user = db.query(Employee).filter(Employee.full_name == full_name).first()
    if not user or user.pin != pin:
        employees = db.query(Employee).filter(Employee.is_active.is_(True)).all()
        return templates.TemplateResponse(
            request,
            "login.html",
            {"employees": employees, "error": "Неверное ФИО или PIN"},
            status_code=400,
        )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie("session", create_session(user.id), httponly=True, max_age=86400 * 7)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session")
    return response


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    eid = get_session_employee_id(request)
    if not eid:
        return RedirectResponse("/login")
    user = db.get(Employee, eid)
    if user.role in (UserRole.dispatcher, UserRole.admin):
        return RedirectResponse("/dispatcher")
    return RedirectResponse("/report")


@router.get("/report", response_class=HTMLResponse)
def report_page(
    request: Request,
    report_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    if user.role != UserRole.master:
        return RedirectResponse("/dispatcher")

    d = date.fromisoformat(report_date) if report_date else date.today()
    report = (
        db.query(Report)
        .options(joinedload(Report.lines).joinedload(ReportLine.work_item))
        .filter(Report.employee_id == user.id, Report.report_date == d)
        .first()
    )
    categories = (
        db.query(WorkItem.category)
        .filter(WorkItem.is_active.is_(True))
        .distinct()
        .order_by(WorkItem.category)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "report_form.html",
        {
            "user": user,
            "report": report,
            "report_date": d,
            "categories": [c[0] for c in categories],
            "message": request.query_params.get("msg"),
        },
    )


@router.get("/api/works")
def api_works(
    q: str = Query(""),
    category: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(WorkItem).filter(WorkItem.is_active.is_(True))
    if category:
        query = query.filter(WorkItem.category == category)
    items = query.order_by(WorkItem.code).all()
    items = filter_works(items, q)[:50]
    return [
        {
            "id": w.id,
            "code": w.code,
            "name": w.name,
            "unit": w.unit,
            "tariff": w.tariff,
            "price": w.operation_price or w.tariff or 0,
            "category": w.category,
        }
        for w in items
    ]


@router.post("/report/line")
async def add_line(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    form = await request.form()
    report_date = date.fromisoformat(str(form.get("report_date")))
    work_item_id = int(form.get("work_item_id"))
    quantity = float(str(form.get("quantity")).replace(",", "."))
    note = str(form.get("note") or "").strip() or None

    work = db.get(WorkItem, work_item_id)
    if not work:
        raise HTTPException(404, "Работа не найдена")

    report = (
        db.query(Report)
        .filter(Report.employee_id == user.id, Report.report_date == report_date)
        .first()
    )
    if not report:
        report = Report(employee_id=user.id, report_date=report_date, status=ReportStatus.draft)
        db.add(report)
        db.flush()
    elif report.status not in (ReportStatus.draft, ReportStatus.rejected):
        return RedirectResponse("/report?msg=Отчёт уже отправлен", status_code=303)

    unit_price, amount = calculate_line_amount(work, quantity)
    db.add(
        ReportLine(
            report_id=report.id,
            work_item_id=work.id,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount,
            note=note,
        )
    )
    db.commit()
    return RedirectResponse(f"/report?report_date={report_date.isoformat()}", status_code=303)


@router.post("/report/line/{line_id}/delete")
async def delete_line(line_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    line = db.get(ReportLine, line_id)
    if not line:
        raise HTTPException(404)
    report = db.get(Report, line.report_id)
    if report.employee_id != user.id or report.status not in (ReportStatus.draft, ReportStatus.rejected):
        raise HTTPException(403)
    report_date = report.report_date.isoformat()
    db.delete(line)
    db.commit()
    return RedirectResponse(f"/report?report_date={report_date}", status_code=303)


@router.post("/report/submit")
async def submit_report(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    form = await request.form()
    report_date = date.fromisoformat(str(form.get("report_date")))
    report = (
        db.query(Report)
        .filter(Report.employee_id == user.id, Report.report_date == report_date)
        .first()
    )
    if not report or not report.lines:
        return RedirectResponse("/report?msg=Добавьте хотя бы одну работу", status_code=303)
    report.status = ReportStatus.submitted
    db.commit()
    return RedirectResponse("/report?msg=Отчёт отправлен на проверку", status_code=303)


@router.get("/dispatcher", response_class=HTMLResponse)
def dispatcher_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role not in (UserRole.dispatcher, UserRole.admin):
        return RedirectResponse("/report")

    reports = (
        db.query(Report)
        .options(
            joinedload(Report.employee),
            joinedload(Report.lines).joinedload(ReportLine.work_item),
        )
        .order_by(Report.report_date.desc(), Report.id.desc())
        .limit(100)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "dispatcher.html",
        {"user": user, "reports": reports, "message": request.query_params.get("msg")},
    )


@router.get("/dispatcher/report/{report_id}", response_class=HTMLResponse)
def dispatcher_report_detail(report_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role not in (UserRole.dispatcher, UserRole.admin):
        return RedirectResponse("/report")

    report = (
        db.query(Report)
        .options(
            joinedload(Report.employee),
            joinedload(Report.lines).joinedload(ReportLine.work_item),
        )
        .filter(Report.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(404, "Отчёт не найден")

    return templates.TemplateResponse(
        request,
        "report_detail.html",
        {"user": user, "report": report, "message": request.query_params.get("msg")},
    )


@router.post("/dispatcher/{report_id}/approve")
def approve_report(report_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role not in (UserRole.dispatcher, UserRole.admin):
        raise HTTPException(403)
    report = db.get(Report, report_id)
    if report:
        report.status = ReportStatus.approved
        db.commit()
    return RedirectResponse("/dispatcher?msg=Отчёт утверждён", status_code=303)


@router.post("/dispatcher/{report_id}/reject")
async def reject_report(report_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role not in (UserRole.dispatcher, UserRole.admin):
        raise HTTPException(403)
    report = db.get(Report, report_id)
    if report:
        report.status = ReportStatus.rejected
        db.commit()
    return RedirectResponse("/dispatcher?msg=Отчёт возвращён на доработку", status_code=303)


@router.get("/export")
def export_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role not in (UserRole.dispatcher, UserRole.admin):
        return RedirectResponse("/report")
    return templates.TemplateResponse(request, "export.html", {"user": user})
