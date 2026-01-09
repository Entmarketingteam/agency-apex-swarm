"""Google Sheets exporter using a Service Account (write access).

This complements `GoogleSheetsClient` (API-key read access).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional

from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class SheetsExportResult:
    spreadsheet_id: str
    sheet_name: str
    rows_written: int

    @property
    def url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"


class GoogleSheetsExporter:
    """Export prospects/leads to Google Sheets via service account."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(
        self,
        credentials_path: Optional[str] = None,
    ):
        self.credentials_path = (
            (credentials_path or config.GOOGLE_SHEETS_CREDENTIALS).strip()
        )
        if not self.credentials_path:
            raise ValueError(
                "GOOGLE_SHEETS_CREDENTIALS is required for write/export operations"
            )

        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service

        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES
        )
        self._service = build("sheets", "v4", credentials=creds)
        return self._service

    def _ensure_sheet(self, spreadsheet_id: str, sheet_name: str) -> None:
        """Create sheet tab if it doesn't exist."""
        service = self._get_service()

        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = meta.get("sheets", [])
        existing = {s["properties"]["title"] for s in sheets if "properties" in s}
        if sheet_name in existing:
            return

        logger.info(f"Creating sheet tab '{sheet_name}' in {spreadsheet_id}")
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]},
        ).execute()

    def _is_sheet_empty(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """Best-effort check whether A1 has content."""
        service = self._get_service()
        res = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1:A1")
            .execute()
        )
        values = res.get("values", [])
        return not values or not values[0] or not str(values[0][0]).strip()

    def export_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        headers: List[str],
        rows: List[List[Any]],
        mode: str = "append",  # append | replace
    ) -> SheetsExportResult:
        """
        Export rows to Google Sheets.

        - append: append rows; will write headers if sheet is empty
        - replace: clears sheet and writes headers + rows
        """
        if mode not in ("append", "replace"):
            raise ValueError("mode must be 'append' or 'replace'")

        service = self._get_service()
        self._ensure_sheet(spreadsheet_id, sheet_name)

        if mode == "replace":
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:Z",
            ).execute()

            values = [headers] + rows
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="RAW",
                body={"values": values},
            ).execute()

            written = len(rows)
            return SheetsExportResult(
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                rows_written=written,
            )

        # append
        include_headers = self._is_sheet_empty(spreadsheet_id, sheet_name)
        values = ([headers] if include_headers else []) + rows

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()

        written = len(rows)
        return SheetsExportResult(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            rows_written=written,
        )

    def export_prospects(
        self,
        spreadsheet_id: str,
        prospects: Iterable[Any],
        sheet_name: str = "Prospects",
        mode: str = "append",
    ) -> SheetsExportResult:
        """
        Export `models.prospect.Prospect` objects (or dicts matching its shape).
        """
        from models.prospect import Prospect

        prospect_rows: List[List[Any]] = []
        for p in prospects:
            if isinstance(p, Prospect):
                prospect_rows.append(p.to_sheet_row())
            else:
                prospect_rows.append(Prospect(**p).to_sheet_row())

        return self.export_rows(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            headers=Prospect.sheet_headers(),
            rows=prospect_rows,
            mode=mode,
        )

