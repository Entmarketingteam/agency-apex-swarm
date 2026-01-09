"""Google Sheets API client for reading leads."""

import os
import re
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
    from datetime import datetime
    from dateutil import parser as date_parser
    
    # Map common column names to Lead fields
    name = row.get("name") or row.get("creator_name") or row.get("full_name") or ""
    handle = row.get("handle") or row.get("username") or row.get("instagram") or row.get("ig") or ""
    platform = row.get("platform") or "instagram"
    bio = row.get("bio") or row.get("description") or row.get("notes") or ""
    email = row.get("email") or ""
    linkedin = row.get("linkedin") or row.get("linkedin_url") or ""
    profile_url = row.get("profile url") or row.get("profile_url") or row.get("url") or ""
    instagram_handle = row.get("instagram_handle") or row.get("instagram") or row.get("ig") or ""
    
    # Outreach / pipeline fields (optional)
    status = row.get("status") or ""
    owner = row.get("owner") or ""
    priority = row.get("priority") or ""
    search_query = row.get("search query") or row.get("search_query") or ""
    
    def _parse_bool(value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        v = str(value).strip().lower()
        if not v:
            return None
        if v in ("true", "yes", "y", "1", "checked"):
            return True
        if v in ("false", "no", "n", "0"):
            return False
        return None
    
    def _parse_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        v = str(value).strip()
        if not v:
            return None
        v = v.replace(",", "")
        try:
            return int(float(v))
        except Exception:
            return None
    
    def _parse_date(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        v = str(value).strip()
        if not v:
            return None
        try:
            return date_parser.parse(v)
        except Exception:
            return None
    
    def _parse_hashtags(value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(x).strip().lstrip("#") for x in value if str(x).strip()]
        raw = str(value)
        # Handles: "#LTK, #wellness" or "LTK wellness"
        parts = [p.strip() for p in re.split(r"[,;\n]", raw) if p.strip()]
        tags = []
        for p in parts:
            if not p:
                continue
            if " " in p and not p.startswith("#"):
                # if someone pasted "LTK wellness"
                tags.extend([x.strip().lstrip("#") for x in p.split() if x.strip()])
            else:
                tags.append(p.lstrip("#"))
        return list(dict.fromkeys([t for t in tags if t]))  # de-dupe, preserve order
    
    return Lead(
        name=name if name else None,
        handle=handle if handle else None,
        platform=platform.lower() if platform else "instagram",
        profile_url=profile_url if profile_url else None,
        bio=bio if bio else None,
        hashtags=_parse_hashtags(row.get("hashtags") or row.get("tags") or ""),
        follower_count=_parse_int(row.get("follower_count") or row.get("follower count") or row.get("followers")),
        email=email if email else None,
        linkedin_url=linkedin if linkedin else None,
        instagram_handle=instagram_handle if instagram_handle else None,
        status=status if status else None,
        contacted=_parse_bool(row.get("contacted")),
        contacted_date=_parse_date(row.get("contacted date") or row.get("contacted_date")),
        last_contact=_parse_date(row.get("last contact") or row.get("last_contact")),
        next_follow_up=_parse_date(row.get("next follow-up") or row.get("next_follow-up") or row.get("next_follow_up")),
        owner=owner if owner else None,
        priority=priority if priority else None,
        search_query=search_query if search_query else None,
        found_date=_parse_date(row.get("found date") or row.get("found_date")),
    )

