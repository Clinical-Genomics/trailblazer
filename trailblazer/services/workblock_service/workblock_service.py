from datetime import UTC, datetime
from typing import cast

from trailblazer.dto.workblock_configuration import (
    WorkblockConfigurationRequest,
    WorkblockConfigurationResponse,
)
from trailblazer.exc import WorkblockConfigurationConflictError
from trailblazer.store.database import get_session
from trailblazer.store.models import User
from trailblazer.store.store import Store


class WorkblockService:
    def __init__(self, store: Store):
        self.store = store

    def get_workblock_configuration(self) -> WorkblockConfigurationResponse:
        """Return the shared workblock configuration."""
        configuration = self.store.get_workblock_configuration()

        if configuration is None:
            raise RuntimeError("Workblock configuration is missing")

        return WorkblockConfigurationResponse(
            version=configuration.version,
            workblocks=configuration.workblocks,
            updated_by=configuration.updated_by,
            updated_at=configuration.updated_at,
        )

    def update_workblock_configuration(
        self,
        data: WorkblockConfigurationRequest,
        user: User,
    ) -> WorkblockConfigurationResponse:
        """Save the shared workblock configuration."""
        current = self.get_workblock_configuration()

        if current.version != data.version:
            raise WorkblockConfigurationConflictError(
                "Workblock configuration has changed. Reload before saving."
            )

        workblocks = [block.model_dump() for block in data.workblocks]
        current_workblocks = [block.model_dump() for block in current.workblocks]

        if workblocks == current_workblocks:
            return current

        updated_by = cast(str, user.abbreviation)
        updated_at = datetime.now(UTC).replace(tzinfo=None)

        session = get_session()

        try:
            self.store.update_workblock_configuration(
                version=data.version,
                workblocks=workblocks,
                updated_by=updated_by,
                updated_at=updated_at,
            )
            response = self.get_workblock_configuration()
            session.commit()
            return response
        except Exception:
            session.rollback()
            raise
