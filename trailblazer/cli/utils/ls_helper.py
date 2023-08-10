from typing import Dict, Tuple

from trailblazer.constants import TrailblazerStatus, TrailblazerStatusColor
from trailblazer.store.models import Analysis


def _get_ls_analysis_message(analysis: Analysis) -> Tuple[str, str]:
    """Return the log message for the analysis."""
    message: str = (
        f"{analysis.id} | {analysis.family} {analysis.started_at.date()} "
        f"[{analysis.type.upper()}/{analysis.status.upper()}]"
    )
    message_map: Dict[str, tuple] = {
        TrailblazerStatus.PENDING: (
            f"{analysis.id} | {analysis.family} [{analysis.status.upper()}]",
            TrailblazerStatusColor.PENDING,
        ),
        TrailblazerStatus.RUNNING: (
            f"{message} - {analysis.progress * 100}/100",
            TrailblazerStatusColor.RUNNING,
        ),
        TrailblazerStatus.COMPLETED: (
            f"{message} - {analysis.completed_at}",
            TrailblazerStatusColor.COMPLETED,
        ),
        TrailblazerStatus.FAILED: (message, TrailblazerStatusColor.FAILED),
    }
    return message_map.get(analysis.status, (message, TrailblazerStatusColor.DEFAULT))
