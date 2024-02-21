from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.summaries_response import Summary
from trailblazer.store.models import Analysis


def get_status_count(analyses: list[Analysis], status: TrailblazerStatus) -> int:
    return len([a for a in analyses if a.status == status])


def create_summary(analyses: list[Analysis]) -> Summary:
    """Create a summary of the analyses."""
    total: int = len(analyses)
    delivered: int = get_status_count(analyses=analyses, status=TrailblazerStatus.COMPLETED)
    running: int = get_status_count(analyses=analyses, status=TrailblazerStatus.RUNNING)
    cancelled: int = get_status_count(analyses=analyses, status=TrailblazerStatus.CANCELLED)
    failed = get_status_count(analyses=analyses, status=TrailblazerStatus.FAILED)
    return Summary(
        order_id=analyses[0].order_id,
        total=total,
        delivered=delivered,
        running=running,
        cancelled=cancelled,
        failed=failed,
    )
