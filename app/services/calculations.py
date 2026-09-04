from app.models import WorkItem


def resolve_unit_price(work: WorkItem) -> float:
    if work.operation_price is not None and work.operation_price > 0:
        return work.operation_price
    if work.tariff is not None and work.tariff > 0:
        return work.tariff
    return 0.0


def calculate_line_amount(work: WorkItem, quantity: float) -> tuple[float, float]:
    unit_price = resolve_unit_price(work)
    return unit_price, round(unit_price * quantity, 2)
