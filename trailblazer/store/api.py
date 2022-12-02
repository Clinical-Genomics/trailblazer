# -*- coding: utf-8 -*-
"""Store backend in Trailblazer"""
import datetime as dt
import io
import logging
import subprocess
from typing import Any, List, Optional

import alchy
import pandas as pd
import sqlalchemy as sqa
from alchy import Query
from dateutil.parser import parse as parse_datestr
from ruamel.yaml import safe_load

from trailblazer.constants import (
    COMPLETED_STATUS,
    FAILED_STATUS,
    ONGOING_STATUSES,
    SLURM_ACTIVE_CATEGORIES,
    STARTED_STATUSES,
)
from trailblazer.exc import EmptySqueueError, TrailblazerError
from trailblazer.store import models
from trailblazer.store.utils import formatters

LOG = logging.getLogger(__name__)


class BaseHandler:
    User = models.User
    Analysis = models.Analysis
    Job = models.Job
    Info = models.Info

    def setup(self):
        self.create_all()
        # add initial metadata record (for web interface)
        new_info = self.Info()
        self.add_commit(new_info)

    def info(self) -> models.Info:
        """Return metadata entry."""
        return self.Info.query.first()

    def set_latest_update_date(self):
        """
        used in CLI
        Update the latest updated date in the database."""
        metadata = self.info()
        metadata.updated_at = dt.datetime.now()
        self.commit()

    def get_analysis(self, case_id: str, started_at: dt.datetime, status: str) -> models.Analysis:
        """
        used in LOG
        Find a single analysis."""
        query = self.Analysis.query.filter_by(family=case_id, started_at=started_at, status=status)
        return query.first()

    def aggregate_failed(self, since_when: dt.date = None) -> List[dict]:
        """
        used in FRONTEND
        Count the number of failed jobs per category (name)."""

        categories = self.session.query(
            self.Job.name.label("name"),
            sqa.func.count(self.Job.id).label("count"),
        ).filter(self.Job.status == "failed")

        if since_when:
            categories = categories.filter(self.Job.started_at > since_when)

        categories = categories.group_by(self.Job.name).all()

        return [{"name": category.name, "count": category.count} for category in categories]

    def analyses(
        self,
        case_id: str = None,
        query: str = None,
        status: str = None,
        deleted: bool = None,
        temp: bool = False,
        before: dt.datetime = None,
        is_visible: bool = None,
        family: str = None,
        data_analysis: str = None,
        comment: str = None,
    ) -> Query:
        """
        used by REST +> CG
        Fetch analyses from the database."""
        if not case_id:
            case_id = family

        analysis_query = self.Analysis.query
        if case_id:
            analysis_query = analysis_query.filter_by(family=case_id)
        if query:  # to be deprecated
            analysis_query = analysis_query.filter(
                sqa.or_(
                    self.Analysis.family.ilike(f"%{query}%"),
                    self.Analysis.status.ilike(f"%{query}%"),
                    self.Analysis.data_analysis.ilike(f"%{query}%"),
                    self.Analysis.comment.ilike(f"%{query}%"),
                )
            )
        if status:
            analysis_query = analysis_query.filter_by(status=status)
        if isinstance(deleted, bool):
            analysis_query = analysis_query.filter_by(is_deleted=deleted)
        if temp:
            analysis_query = analysis_query.filter(self.Analysis.status.in_(ONGOING_STATUSES))
        if before:
            analysis_query = analysis_query.filter(self.Analysis.started_at < before)
        if is_visible is not None:
            analysis_query = analysis_query.filter_by(is_visible=is_visible)
        if data_analysis:
            analysis_query = analysis_query.filter(
                models.Analysis.data_analysis.ilike(f"%{data_analysis}%")
            )
        if comment:
            analysis_query = analysis_query.filter(models.Analysis.comment.ilike(f"%{comment}%"))

        return analysis_query.order_by(self.Analysis.started_at.desc())

    def analysis(self, analysis_id: int) -> Optional[models.Analysis]:
        """
        used by REST
        Get a single analysis by id."""
        return self.Analysis.query.get(analysis_id)

    def get_latest_analysis(self, case_id: str) -> Optional[models.Analysis]:
        return self.analyses(case_id=case_id).first()

    def get_latest_analysis_status(self, case_id: str) -> Optional[str]:
        """Get the latest analysis status for a case_id"""
        latest_analysis = self.get_latest_analysis(case_id=case_id)
        if latest_analysis:
            return latest_analysis.status

    def is_latest_analysis_ongoing(self, case_id: str) -> bool:
        """Check if the latest analysis is ongoing for a case_id"""
        latest_analysis_status = self.get_latest_analysis_status(case_id=case_id)
        return latest_analysis_status in ONGOING_STATUSES

    def is_latest_analysis_failed(self, case_id: str) -> bool:
        """Check if the latest analysis is failed for a case_id"""
        latest_analysis_status = self.get_latest_analysis_status(case_id=case_id)
        return latest_analysis_status == FAILED_STATUS

    def is_latest_analysis_completed(self, case_id: str) -> bool:
        """Check if the latest analysis is completed for a case_id"""
        latest_analysis = self.analyses(case_id=case_id).first()
        return bool(latest_analysis and latest_analysis.status == COMPLETED_STATUS)

    def has_latest_analysis_started(self, case_id: str) -> bool:
        """Check if analysis has started"""
        latest_analysis_status = self.get_latest_analysis_status(case_id=case_id)
        return latest_analysis_status in STARTED_STATUSES

    def add_pending_analysis(
        self,
        case_id: str,
        type: str,
        config_path: str,
        out_dir: str,
        priority: str,
        email: str = None,
        data_analysis: str = None,
        ticket_id: str = None,
    ) -> models.Analysis:
        """Add pending entry for an analysis."""
        started_at = dt.datetime.now()
        new_log = self.Analysis(
            family=case_id,
            status="pending",
            started_at=started_at,
            type=type,
            config_path=config_path,
            out_dir=out_dir,
            priority=priority,
            data_analysis=data_analysis,
            ticket_id=ticket_id,
        )
        new_log.user = self.user(email) if email else None
        self.add_commit(new_log)
        return new_log

    def add_user(self, name: str, email: str) -> models.User:
        """Add a new user to the database."""
        new_user = self.User(name=name, email=email)
        self.add_commit(new_user)
        return new_user

    def archive_user(self, user: models.User, archive: bool = True) -> None:
        """Archive user in the database."""
        user.is_archived = archive
        self.commit()

    def user(self, email: str, include_archived: bool = False) -> models.User:
        """Fetch a user from the database."""
        query = self.User.query

        if not include_archived:
            query = query.filter_by(is_archived=False)

        query = query.filter_by(email=email)

        return query.first()

    def users(
        self,
        name: str,
        email: str,
        include_archived: bool = False,
    ) -> Query:
        """Fetch all users from the database."""
        query = self.User.query

        if not include_archived:
            query = query.filter_by(is_archived=False)

        if name:
            query = query.filter(self.User.name.contains(name))
        if email:
            query = query.filter(self.User.email.contains(email))

        return query

    def jobs(self) -> Query:
        """Return all jobs in the database."""
        return self.Job.query

    def mark_analyses_deleted(self, case_id: str) -> Query:
        """mark analyses connected to a case as deleted"""
        old_analyses = self.analyses(case_id=case_id)
        if old_analyses.count() > 0:
            for old_analysis in old_analyses:
                old_analysis.is_deleted = True
            self.commit()
        return old_analyses

    def set_analysis_completed(self, analysis_id: int) -> None:
        analysis_obj = self.analysis(analysis_id=analysis_id)
        analysis_obj.status = "completed"
        self.commit()
        LOG.info(f"{analysis_obj.family} - status set to COMPLETED")

    def set_analysis_uploaded(self, case_id: str, uploaded_at: dt.datetime) -> None:
        """Setting analysis uploaded at."""
        analysis_obj: models.Analysis = self.get_latest_analysis(case_id=case_id)
        analysis_obj.uploaded_at: dt.datetime = uploaded_at
        self.commit()
        LOG.info(f"{analysis_obj.family} - uploaded at set to {uploaded_at}")

    def delete_analysis(self, analysis_id: int, force: bool = False) -> None:
        """Delete the analysis output."""
        analysis_obj = self.analysis(analysis_id=analysis_id)
        if not analysis_obj:
            raise TrailblazerError("Analysis not found")

        if not force and analysis_obj.status in ONGOING_STATUSES:
            raise TrailblazerError(
                f"Analysis for {analysis_obj.family} is currently running! Use --force flag to delete anyway."
            )
        LOG.info(f"Deleting analysis {analysis_id} for case {analysis_obj.family}")
        analysis_obj.delete()
        self.commit()

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> Any:
        """Args:
        job_id_file: Path to slurm id .YAML file as string
        case_id: Unique internal case identifier which is expected to by the only item in the .YAML dict
        ssh : Whether the request is executed from hasta or clinical-db"""
        job_id_dict = safe_load(open(job_id_file))
        submitted_job_ids = job_id_dict.get(next(iter(job_id_dict)))
        job_ids_string = ",".join(map(str, submitted_job_ids))
        if ssh:
            return (
                subprocess.check_output(
                    [
                        "ssh",
                        "hiseq.clinical@hasta.scilifelab.se",
                        "squeue",
                        "-j",
                        job_ids_string,
                        "-h",
                        "--states=all",
                        "-o",
                        "%A,%j,%T,%l,%M,%S",
                    ],
                    universal_newlines=True,
                )
                .strip()
                .replace("//n", "/n")
            )
        else:
            return subprocess.check_output(
                [
                    "squeue",
                    "-j",
                    job_ids_string,
                    "-h",
                    "--states=all",
                    "-o",
                    "%A,%j,%T,%l,%M,%S",
                ]
            )

    @staticmethod
    def get_time_elapsed_in_min(elapsed_string: Optional[str]) -> Optional[int]:
        """Parse SLURM elapsed time string into minutes"""
        if not elapsed_string or not isinstance(elapsed_string, str):
            return 0
        days = 0
        if "-" in elapsed_string:
            days = int(elapsed_string.split("-")[0])
            elapsed_string = elapsed_string.split("-")[1]
        split_timestamp = elapsed_string.split(":")
        if len(split_timestamp) < 3:
            split_timestamp = list("0" * (3 - len(split_timestamp))) + split_timestamp
        return int(
            (parse_datestr(":".join(split_timestamp)) - parse_datestr("0:0:0")).seconds / 60
            + days * 60
        )

    @staticmethod
    def parse_squeue_to_df(squeue_response: Any, ssh: bool) -> pd.DataFrame:
        """Reads queue response into a pandas dataframe for easy parsing.
        Raises:
            TrailblazerError: when no entries were returned by squeue command"""
        if not squeue_response:
            raise EmptySqueueError("No jobs found in SLURM registry")
        if ssh:
            parsed_df = pd.read_csv(
                io.StringIO(squeue_response),
                sep=",",
                header=None,
                na_values=["nan", "N/A", "None"],
                names=["id", "step", "status", "time_limit", "time_elapsed", "started"],
            )
        else:
            parsed_df = pd.read_csv(
                io.BytesIO(squeue_response),
                sep=",",
                header=None,
                na_values=["nan", "N/A", "None"],
                names=["id", "step", "status", "time_limit", "time_elapsed", "started"],
            )
        parsed_df["time_elapsed"] = parsed_df["time_elapsed"].apply(
            lambda x: Store.get_time_elapsed_in_min(x)
        )
        return parsed_df

    def update_jobs(self, analysis_obj: models.Analysis, jobs_dataframe: pd.DataFrame) -> None:
        """Parses job dataframe and creates job objects"""
        if len(jobs_dataframe) == 0:
            return
        formatter_func = formatters.formatter_map.get(
            analysis_obj.data_analysis, formatters.transform_undefined
        )
        jobs_dataframe["step"] = jobs_dataframe["step"].apply(lambda x: formatter_func(x))

        for job_obj in analysis_obj.failed_jobs:
            job_obj.delete()
        self.commit()
        analysis_obj.failed_jobs = [
            self.Job(
                analysis_id=analysis_obj.id,
                slurm_id=val.get("id"),
                name=val.get("step"),
                status=val.get("status").lower(),
                started_at=parse_datestr(val.get("started"))
                if isinstance(val.get("started"), str)
                else None,
                elapsed=val.get("time_elapsed"),
            )
            for ind, val in jobs_dataframe.iterrows()
        ]
        self.commit()

    def update_ongoing_analyses(self, ssh: bool = False) -> None:
        """Iterate over all analysis with ongoing status and query SLURM for current progress"""
        ongoing_analyses = self.analyses(temp=True)
        for analysis_obj in ongoing_analyses:
            try:
                self.update_run_status(analysis_id=analysis_obj.id, ssh=ssh)
            except Exception as e:
                LOG.error(
                    f"Failed to update {analysis_obj.family} - {analysis_obj.id}: {e.__class__.__name__}"
                )

    @staticmethod
    def get_elapsed_time(self, analysis_obj: models.Analysis) -> str:
        """Get elapsed time for the analysis"""
        return str(
            (
                dt.datetime.now()
                - min(
                    job_obj.started_at for job_obj in analysis_obj.failed_jobs if job_obj.started_at
                )
            )
        )

    def update_run_status(self, analysis_id: int, ssh: bool = False) -> None:
        """Query slurm for entries related to given analysis, and update the Trailblazer database"""
        analysis_obj = self.analysis(analysis_id)
        if not analysis_obj:
            LOG.warning(f"Analysis {analysis_id} not found!")
            return
        try:
            jobs_dataframe = self.parse_squeue_to_df(
                squeue_response=self.query_slurm(
                    job_id_file=analysis_obj.config_path, case_id=analysis_obj.family, ssh=ssh
                ),
                ssh=ssh,
            )
            self.update_jobs(analysis_obj=analysis_obj, jobs_dataframe=jobs_dataframe)

            status_distribution = round(
                jobs_dataframe.status.value_counts() / len(jobs_dataframe), 2
            )

            LOG.info(f"Status in SLURM: {analysis_obj.family} - {analysis_id}")
            LOG.info(jobs_dataframe)
            analysis_obj.progress = float(status_distribution.get("COMPLETED", 0.0))
            if status_distribution.get("FAILED") or status_distribution.get("TIMEOUT"):
                if status_distribution.get("RUNNING") or status_distribution.get("PENDING"):
                    analysis_obj.status = "error"
                else:
                    analysis_obj.status = "failed"

            elif status_distribution.get("COMPLETED") == 1:
                analysis_obj.status = "completed"

            elif status_distribution.get("PENDING") == 1:
                analysis_obj.status = "pending"

            elif status_distribution.get("RUNNING"):
                analysis_obj.status = "running"

            elif status_distribution.get("CANCELLED") and not (
                status_distribution.get("RUNNING") or status_distribution.get("PENDING")
            ):
                analysis_obj.status = "canceled"

            LOG.info(
                f"Updated status {analysis_obj.family} - {analysis_obj.id}: {analysis_obj.status} "
            )
            self.commit()

            analysis_obj.logged_at = dt.datetime.now()
        except Exception as e:
            LOG.error(f"Error logging case - {analysis_obj.family} : {e.__class__.__name__}")
            analysis_obj.status = "error"
            self.commit()

    @staticmethod
    def cancel_slurm_job(slurm_id: int, ssh: bool = False) -> None:
        """Cancel slurm job by slurm job ID"""
        if ssh:
            subprocess.Popen(
                ["ssh", "hiseq.clinical@hasta.scilifelab.se", "scancel", str(slurm_id)]
            )
        else:
            subprocess.Popen(["scancel", str(slurm_id)])

    def cancel_analysis(self, analysis_id: int, email: str = None, ssh: bool = False) -> None:
        """Cancel all ongoing slurm jobs associated with the analysis, and set job status to canceled"""
        analysis_obj = self.analysis(analysis_id=analysis_id)
        if not analysis_obj:
            raise TrailblazerError(f"Analysis {analysis_id} does not exist")

        if analysis_obj.status not in ONGOING_STATUSES:
            raise TrailblazerError(f"Analysis {analysis_id} is not running")

        for job_obj in analysis_obj.failed_jobs:
            if job_obj.status in SLURM_ACTIVE_CATEGORIES:
                LOG.info(f"Cancelling job {job_obj.slurm_id} - {job_obj.name}")
                self.cancel_slurm_job(job_obj.slurm_id, ssh=ssh)
        LOG.info(
            f"Case {analysis_obj.family} - Analysis {analysis_id}: all ongoing jobs cancelled successfully!"
        )
        self.update_run_status(analysis_id=analysis_id)
        analysis_obj.status = "canceled"
        analysis_obj.comment = (
            f"Analysis cancelled manually by user:"
            f" {(self.user(email).name if self.user(email) else (email or 'Unknown'))}!"
        )
        self.commit()


class Store(alchy.Manager, BaseHandler):
    def __init__(self, uri: str):
        super(Store, self).__init__(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=models.Model)
