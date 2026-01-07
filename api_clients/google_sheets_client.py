"""Google Sheets API client for reading leads."""

import os
from typing import Dict, Any, Optional, List
from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

# Default values (can be overridden by environment variables)
DEFAULT_SPREADSHEET_ID = "1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew"
DEFAULT_SHEET_NAME = "TEST SHEET FOR CURSOR"


class GoogleSheetsClient:
    """Client for reading leads from Google Sheets."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.GOOGLE_API_KEY
        self.spreadsheet_id = config.GOOGLE_SHEET_ID or DEFAULT_SPREADSHEET_ID
        self.sheet_name = config.GOOGLE_SHEET_TAB_NAME or DEFAULT_SHEET_NAME
    
    def get_leads_from_sheet(
        self,
        sheet_name: Optional[str] = None,
        range_name: str = "A:Z"
    ) -> List[Dict[str, Any]]:
        """
        Fetch leads from Google Sheet.
        
        Args:
            sheet_name: Name of the sheet tab
            range_name: Cell range to read (e.g., "A:Z" for all columns)
        
        Returns:
            List of lead dictionaries
        """
        import httpx
        
        # Use instance sheet_name if not provided
        sheet_name = sheet_name or self.sheet_name
        
        # Google Sheets API v4 endpoint
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{sheet_name}!{range_name}"
        
        params = {
            "key": self.api_key,
            "majorDimension": "ROWS"
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                values = data.get("values", [])
                if not values:
                    logger.info("No data found in sheet")
                    return []
                
                # First row is headers
                headers = [h.lower().strip() for h in values[0]]
                
                # Convert rows to dictionaries
                leads = []
                for row in values[1:]:
                    lead = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            lead[header] = row[i].strip() if row[i] else ""
                        else:
                            lead[header] = ""
                    
                    # Only include rows with data
                    if any(lead.values()):
                        leads.append(lead)
                
                logger.info(f"Fetched {len(leads)} leads from Google Sheet")
                return leads
                
        except httpx.HTTPError as e:
            logger.error(f"Google Sheets API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading sheet: {e}")
            return []
    
    def get_unprocessed_leads(
        self,
        sheet_name: Optional[str] = None,
        status_column: str = "status"
    ) -> List[Dict[str, Any]]:
        """
        Get only unprocessed leads (where status is empty or 'pending').
        
        Args:
            sheet_name: Name of the sheet tab
            status_column: Column name for status
        
        Returns:
            List of unprocessed leads
        """
        all_leads = self.get_leads_from_sheet(sheet_name)
        
        unprocessed = []
        for lead in all_leads:
            status = lead.get(status_column, "").lower()
            if not status or status == "pending":
                unprocessed.append(lead)
        
        logger.info(f"Found {len(unprocessed)} unprocessed leads")
        return unprocessed


def convert_sheet_row_to_lead(row: Dict[str, Any]):
    """Convert a sheet row to a Lead object."""
    from models.lead import Lead
    
    # Map common column names to Lead fields
    name = row.get("name") or row.get("creator_name") or row.get("full_name") or ""
    handle = row.get("handle") or row.get("username") or row.get("instagram") or row.get("ig") or ""
    platform = row.get("platform") or "instagram"
    bio = row.get("bio") or row.get("description") or row.get("notes") or ""
    email = row.get("email") or ""
    linkedin = row.get("linkedin") or row.get("linkedin_url") or ""
    
    return Lead(
        name=name if name else None,
        handle=handle if handle else None,
        platform=platform.lower() if platform else "instagram",
        bio=bio if bio else None,
        email=email if email else None,
        linkedin_url=linkedin if linkedin else None
    )

