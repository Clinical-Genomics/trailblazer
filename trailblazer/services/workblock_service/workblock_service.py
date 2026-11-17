from trailblazer.dto.workblock_configuration import (
    WorkblockConfigurationRequest,
    WorkblockConfigurationResponse,
)
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
        raise NotImplementedError
