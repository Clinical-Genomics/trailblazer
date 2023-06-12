import datetime as dt

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.models import Info


class UpdateHandler(BaseHandler_2):
    """Class for updating items in the database."""

    def set_latest_update_date(self) -> None:
        """Update when the database was last updated."""
        info: Info = self._get_query(table=Info).first()
        info.updated_at: dt.datetime = dt.datetime.now()
        self.commit()
