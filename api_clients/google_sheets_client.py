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
    
    def _get_sheet_headers(self, sheet_name: Optional[str] = None) -> Dict[str, int]:
        """
        Get column headers and their indices.
        
        Args:
            sheet_name: Name of the sheet tab
        
        Returns:
            Dictionary mapping column names (lowercase) to column indices (0-based)
        """
        import httpx
        
        sheet_name = sheet_name or self.sheet_name
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{sheet_name}!1:1"
        
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
                if not values or not values[0]:
                    return {}
                
                headers = {}
                for i, header in enumerate(values[0]):
                    headers[header.lower().strip()] = i
                
                return headers
        except Exception as e:
            logger.error(f"Error getting sheet headers: {e}")
            return {}
    
    def _find_row_by_handle(
        self,
        handle: str,
        sheet_name: Optional[str] = None,
        handle_column: str = "handle"
    ) -> Optional[int]:
        """
        Find the row number (1-based) for a given handle.
        
        Args:
            handle: Instagram handle (with or without @)
            sheet_name: Name of the sheet tab
            handle_column: Column name to search in
        
        Returns:
            Row number (1-based) or None if not found
        """
        # Normalize handle
        handle = handle.lstrip("@").lower().strip()
        
        sheet_name = sheet_name or self.sheet_name
        all_leads = self.get_leads_from_sheet(sheet_name)
        
        # Search for matching handle
        for idx, lead in enumerate(all_leads, start=2):  # Start at row 2 (row 1 is headers)
            lead_handle = lead.get(handle_column, "").lstrip("@").lower().strip()
            if lead_handle == handle:
                return idx
        
        return None
    
    def update_lead_status(
        self,
        handle: str,
        status: str,
        updates: Optional[Dict[str, Any]] = None,
        sheet_name: Optional[str] = None
    ) -> bool:
        """
        Update lead status and other fields in Google Sheet.
        
        Args:
            handle: Instagram handle (with or without @)
            status: New status (e.g., "completed", "failed", "skipped")
            updates: Dictionary of additional fields to update
                e.g., {"email": "user@example.com", "vibe_score": 85}
            sheet_name: Name of the sheet tab
        
        Returns:
            True if successful, False otherwise
        """
        import httpx
        
        sheet_name = sheet_name or self.sheet_name
        updates = updates or {}
        
        # Find the row
        row_num = self._find_row_by_handle(handle, sheet_name)
        if not row_num:
            logger.warning(f"Could not find row for handle: {handle}")
            return False
        
        # Get headers to map column names to indices
        headers = self._get_sheet_headers(sheet_name)
        if not headers:
            logger.error("Could not get sheet headers")
            return False
        
        # Prepare update data
        update_data = {"status": status}
        update_data.update(updates)
        
        # Map field names to column indices
        # Common field mappings
        field_mappings = {
            "email": ["email"],
            "vibe_score": ["vibe_score", "vibe score", "score"],
            "research": ["research", "research_summary", "research summary", "notes"],
            "linkedin": ["linkedin", "linkedin_url", "linkedin url"],
            "name": ["name", "creator_name", "full_name"],
            "bio": ["bio", "description"],
        }
        
        # Build update requests
        update_requests = []
        
        for field, value in update_data.items():
            if value is None:
                continue
            
            # Find column index
            col_idx = None
            if field in field_mappings:
                for col_name in field_mappings[field]:
                    if col_name in headers:
                        col_idx = headers[col_name]
                        break
            
            if col_idx is None:
                # Try direct match
                if field.lower() in headers:
                    col_idx = headers[field.lower()]
            
            if col_idx is not None:
                # Convert to A1 notation (e.g., A2, B2, AA2, etc.)
                def num_to_col_letter(n):
                    """Convert 0-based column index to Excel column letter (A, B, ..., Z, AA, AB, ...)"""
                    result = ""
                    while n >= 0:
                        result = chr(65 + (n % 26)) + result
                        n = n // 26 - 1
                    return result
                
                col_letter = num_to_col_letter(col_idx)
                cell_range = f"{sheet_name}!{col_letter}{row_num}"
                
                update_requests.append({
                    "range": cell_range,
                    "values": [[str(value)]]
                })
        
        if not update_requests:
            logger.warning(f"No valid columns found to update for handle: {handle}")
            return False
        
        # Batch update using Google Sheets API
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values:batchUpdate"
        
        params = {"key": self.api_key}
        
        payload = {
            "valueInputOption": "USER_ENTERED",
            "data": update_requests
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, params=params, json=payload)
                response.raise_for_status()
                
                logger.info(f"Updated lead {handle}: status={status}, fields={list(updates.keys())}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Google Sheets API error updating {handle}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Error updating sheet for {handle}: {e}")
            return False
    
    def append_lead(
        self,
        lead_data: Dict[str, Any],
        sheet_name: Optional[str] = None
    ) -> bool:
        """
        Append a new lead row to Google Sheet.
        
        Args:
            lead_data: Dictionary with lead fields (handle, name, platform, etc.)
            sheet_name: Name of the sheet tab
        
        Returns:
            True if successful
        """
        import httpx
        
        sheet_name = sheet_name or self.sheet_name
        
        # Get headers to determine column order
        headers = self._get_sheet_headers(sheet_name)
        if not headers:
            logger.warning("Could not get sheet headers, trying to append anyway")
            # Try to append with common column order
            headers = {
                "handle": 0, "name": 1, "platform": 2, "email": 3,
                "status": 4, "source": 5, "created_at": 6
            }
        
        # Build row data in correct column order
        max_col = max(headers.values()) if headers else 10
        row_values = [""] * (max_col + 1)
        
        # Map lead_data to columns
        for field, value in lead_data.items():
            # Find column index
            col_idx = None
            if field.lower() in headers:
                col_idx = headers[field.lower()]
            else:
                # Try common variations
                variations = {
                    "handle": ["handle", "username", "instagram", "ig"],
                    "name": ["name", "creator_name", "full_name"],
                    "platform": ["platform"],
                    "email": ["email"],
                    "status": ["status"],
                    "source": ["source", "origin"],
                    "bio": ["bio", "description", "notes"],
                    "linkedin": ["linkedin", "linkedin_url", "linkedin url"]
                }
                for key, aliases in variations.items():
                    if field.lower() in aliases:
                        for alias in aliases:
                            if alias in headers:
                                col_idx = headers[alias]
                                break
                        if col_idx:
                            break
            
            if col_idx is not None and value:
                row_values[col_idx] = str(value)
        
        # Append row using Google Sheets API
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{sheet_name}!A:append"
        
        params = {
            "key": self.api_key,
            "valueInputOption": "USER_ENTERED",
            "insertDataOption": "INSERT_ROWS"
        }
        
        payload = {
            "values": [row_values]
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, params=params, json=payload)
                response.raise_for_status()
                
                logger.info(f"Appended lead to sheet: {lead_data.get('handle', 'unknown')}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Google Sheets API error appending lead: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Error appending lead to sheet: {e}")
            return False
    
    def update_lead_after_processing(
        self,
        handle: str,
        result: Dict[str, Any],
        sheet_name: Optional[str] = None
    ) -> bool:
        """
        Update lead in sheet after processing is complete.
        If lead doesn't exist, creates it first.
        
        Args:
            handle: Instagram handle
            result: Processing result from orchestrator
            sheet_name: Name of the sheet tab
        
        Returns:
            True if successful
        """
        sheet_name = sheet_name or self.sheet_name
        
        # Check if lead exists
        row_num = self._find_row_by_handle(handle, sheet_name)
        
        if not row_num:
            # Lead doesn't exist, create it first
            logger.info(f"Lead {handle} not found in sheet, creating new row")
            lead_data = {
                "handle": f"@{handle.lstrip('@')}",
                "platform": "instagram",
                "status": "processing",
                "source": "slack"
            }
            if not self.append_lead(lead_data, sheet_name):
                logger.error(f"Failed to create lead row for {handle}")
                return False
        
        status = result.get("status", "unknown")
        
        # Extract data from result
        updates = {}
        
        # Get email from contact discovery
        contact_data = result.get("steps", {}).get("contact_discovery", {})
        if contact_data.get("email"):
            updates["email"] = contact_data["email"]
        if contact_data.get("linkedin_url"):
            updates["linkedin"] = contact_data["linkedin_url"]
        
        # Get vibe score (convert to 0-100 if needed)
        vibe_check = result.get("steps", {}).get("vibe_check", {})
        vibe_score = vibe_check.get("score")
        if vibe_score is not None:
            # Convert 0-10 scale to 0-100 if needed
            if isinstance(vibe_score, (int, float)) and vibe_score <= 10:
                updates["vibe_score"] = int(vibe_score * 10)
            else:
                updates["vibe_score"] = int(vibe_score)
        
        # Get research summary (use content, not summary)
        research = result.get("steps", {}).get("research", {})
        research_text = research.get("content") or research.get("summary") or ""
        # Handle error messages - don't save generic error text
        if research_text and "don't have direct" not in research_text.lower() and "can't reliably" not in research_text.lower():
            updates["research"] = str(research_text)[:500]  # Limit length
        elif research.get("error"):
            updates["research"] = f"Research error: {research.get('error')}"
        
        # Map status
        status_map = {
            "completed": "completed",
            "failed": "failed",
            "skipped": "skipped",
            "processing": "processing"
        }
        final_status = status_map.get(status, status)
        
        return self.update_lead_status(handle, final_status, updates, sheet_name)


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

