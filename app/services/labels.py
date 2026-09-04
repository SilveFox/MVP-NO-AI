"""Русские подписи для экспорта и интерфейса."""

from app.models import ReportStatus

STATUS_LABELS: dict[str, str] = {
    ReportStatus.draft.value: "Черновик",
    ReportStatus.submitted.value: "На проверке",
    ReportStatus.approved.value: "Утверждён",
    ReportStatus.rejected.value: "Возвращён",
}


def status_label(status: ReportStatus | str) -> str:
    value = status.value if isinstance(status, ReportStatus) else str(status)
    return STATUS_LABELS.get(value, value)
