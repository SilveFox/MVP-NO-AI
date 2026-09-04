from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export import export_csv, export_txt, export_xlsx

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/txt")
def download_txt(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    content = export_txt(db, from_date, to_date)
    return Response(
        content=content.encode("utf-8-sig"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=\"otchet.txt\"; filename*=UTF-8''%D0%BE%D1%82%D1%87%D1%91%D1%82.txt"},
    )


@router.get("/csv")
def download_csv(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    content = export_csv(db, from_date, to_date)
    return Response(
        content=content.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=\"otchet.csv\"; filename*=UTF-8''%D0%BE%D1%82%D1%87%D1%91%D1%82.csv"},
    )


@router.get("/xlsx")
def download_xlsx(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    data = export_xlsx(db, from_date, to_date)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=\"otchet.xlsx\"; filename*=UTF-8''%D0%BE%D1%82%D1%87%D1%91%D1%82.xlsx"},
    )
