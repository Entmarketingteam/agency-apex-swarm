"""SQLite database for prospect storage and management."""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

# Default database path
DEFAULT_DB_PATH = Path.home() / ".tiktok_prospecting.db"


class ProspectDatabase:
    """
    SQLite database for storing and managing prospects.
    
    Provides CRUD operations, filtering, and statistics for the
    creator prospecting workflow.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file (default: ~/.tiktok_prospecting.db)
        """
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Prospects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL CHECK(platform IN ('tiktok', 'twitter', 'instagram', 'youtube')),
                username TEXT NOT NULL,
                profile_url TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                instagram_username TEXT,
                hashtags TEXT,
                bio TEXT,
                follower_count INTEGER,
                engagement_rate REAL,
                search_query TEXT,
                found_date TEXT NOT NULL,
                status TEXT DEFAULT 'new' CHECK(status IN ('new', 'contacted', 'replied', 'interested', 'not_interested', 'converted')),
                priority TEXT DEFAULT 'medium' CHECK(priority IN ('high', 'medium', 'low')),
                contacted BOOLEAN DEFAULT 0,
                contacted_date TEXT,
                last_contact_date TEXT,
                next_followup_date TEXT,
                owner TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                platform TEXT,
                results_count INTEGER DEFAULT 0,
                prospects_with_email INTEGER DEFAULT 0,
                serpapi_credits_used INTEGER DEFAULT 1,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Outreach log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_email TEXT NOT NULL,
                outreach_type TEXT NOT NULL CHECK(outreach_type IN ('email', 'instagram_dm', 'linkedin_dm', 'follow_up')),
                template_used TEXT,
                subject TEXT,
                message_preview TEXT,
                send_status TEXT DEFAULT 'pending' CHECK(send_status IN ('pending', 'sent', 'failed', 'bounced')),
                error_message TEXT,
                response_received BOOLEAN DEFAULT 0,
                response_text TEXT,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_email) REFERENCES prospects(email)
            )
        """)
        
        # Email templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                template_type TEXT DEFAULT 'initial' CHECK(template_type IN ('initial', 'follow_up', 'partnership')),
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # DM templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dm_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                message TEXT NOT NULL,
                platform TEXT DEFAULT 'instagram' CHECK(platform IN ('instagram', 'linkedin')),
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Usage stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                date TEXT PRIMARY KEY,
                searches_run INTEGER DEFAULT 0,
                credits_used INTEGER DEFAULT 0,
                prospects_found INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_email ON prospects(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_platform ON prospects(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_contacted ON prospects(contacted)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_found_date ON prospects(found_date)")
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    # ==================== PROSPECT OPERATIONS ====================
    
    def insert_prospect(self, prospect: Dict[str, Any]) -> bool:
        """
        Insert a new prospect into the database.
        
        Args:
            prospect: Prospect data dictionary
        
        Returns:
            True if inserted, False if duplicate (email exists)
        """
        cursor = self.conn.cursor()
        
        # Serialize hashtags list to JSON
        hashtags = prospect.get("hashtags", [])
        if isinstance(hashtags, list):
            hashtags = json.dumps(hashtags)
        
        try:
            cursor.execute("""
                INSERT INTO prospects (
                    platform, username, profile_url, email, instagram_username,
                    hashtags, bio, follower_count, engagement_rate, search_query,
                    found_date, status, priority, contacted, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prospect.get("platform", "tiktok"),
                prospect.get("username", ""),
                prospect.get("profile_url", ""),
                prospect.get("email", ""),
                prospect.get("instagram_username", ""),
                hashtags,
                prospect.get("bio", ""),
                prospect.get("follower_count"),
                prospect.get("engagement_rate"),
                prospect.get("search_query", ""),
                prospect.get("found_date", datetime.now().isoformat()),
                prospect.get("status", "new"),
                prospect.get("priority", "medium"),
                0,  # contacted = False
                prospect.get("notes", ""),
            ))
            
            self.conn.commit()
            logger.info(f"Inserted prospect: {prospect.get('email')}")
            return True
            
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate prospect skipped: {prospect.get('email')}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Failed to insert prospect: {e}")
            return False
    
    def insert_prospects_batch(self, prospects: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Insert multiple prospects, skipping duplicates.
        
        Args:
            prospects: List of prospect data dictionaries
        
        Returns:
            Dict with counts: {"inserted": N, "duplicates": M, "errors": X}
        """
        results = {"inserted": 0, "duplicates": 0, "errors": 0}
        
        for prospect in prospects:
            try:
                if self.insert_prospect(prospect):
                    results["inserted"] += 1
                else:
                    results["duplicates"] += 1
            except Exception as e:
                logger.error(f"Error inserting prospect: {e}")
                results["errors"] += 1
        
        logger.info(f"Batch insert: {results}")
        return results
    
    def get_prospect_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a single prospect by email."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prospects WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_prospects(
        self,
        contacted: Optional[bool] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get prospects with optional filters.
        
        Args:
            contacted: Filter by contacted status
            platform: Filter by platform
            status: Filter by pipeline status
            priority: Filter by priority level
            date_from: Filter by found_date >= date_from
            date_to: Filter by found_date <= date_to
            owner: Filter by assigned owner
            limit: Maximum results to return
            offset: Pagination offset
        
        Returns:
            List of prospect dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM prospects WHERE 1=1"
        params = []
        
        if contacted is not None:
            query += " AND contacted = ?"
            params.append(1 if contacted else 0)
        
        if platform:
            query += " AND platform = ?"
            params.append(platform.lower())
        
        if status:
            query += " AND status = ?"
            params.append(status.lower())
        
        if priority:
            query += " AND priority = ?"
            params.append(priority.lower())
        
        if date_from:
            query += " AND found_date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND found_date <= ?"
            params.append(date_to)
        
        if owner:
            query += " AND owner = ?"
            params.append(owner)
        
        query += " ORDER BY found_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def update_prospect(self, email: str, updates: Dict[str, Any]) -> bool:
        """
        Update a prospect's fields.
        
        Args:
            email: Prospect email (identifier)
            updates: Dictionary of field -> new value
        
        Returns:
            True if updated, False otherwise
        """
        cursor = self.conn.cursor()
        
        # Build update query
        allowed_fields = [
            "platform", "username", "profile_url", "instagram_username",
            "hashtags", "bio", "follower_count", "engagement_rate",
            "status", "priority", "contacted", "contacted_date",
            "last_contact_date", "next_followup_date", "owner", "notes"
        ]
        
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                # Serialize hashtags if list
                if field == "hashtags" and isinstance(value, list):
                    value = json.dumps(value)
                params.append(value)
        
        if not set_clauses:
            return False
        
        # Always update updated_at
        set_clauses.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        params.append(email)
        
        try:
            cursor.execute(
                f"UPDATE prospects SET {', '.join(set_clauses)} WHERE email = ?",
                params
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to update prospect: {e}")
            return False
    
    def mark_contacted(
        self,
        email: str,
        notes: str = "",
        method: str = "email"
    ) -> bool:
        """
        Mark a prospect as contacted.
        
        Args:
            email: Prospect email
            notes: Optional notes about the contact
            method: Contact method (email, instagram_dm, etc.)
        
        Returns:
            True if updated
        """
        now = datetime.now().isoformat()
        
        updates = {
            "contacted": True,
            "contacted_date": now,
            "last_contact_date": now,
            "status": "contacted",
        }
        
        if notes:
            # Append to existing notes
            prospect = self.get_prospect_by_email(email)
            existing_notes = prospect.get("notes", "") if prospect else ""
            updates["notes"] = f"{existing_notes}\n[{now[:10]}] {method}: {notes}".strip()
        
        return self.update_prospect(email, updates)
    
    def delete_prospect(self, email: str) -> bool:
        """Delete a prospect by email."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM prospects WHERE email = ?", (email,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to delete prospect: {e}")
            return False
    
    # ==================== SEARCH HISTORY ====================
    
    def log_search(
        self,
        query: str,
        platform: Optional[str] = None,
        results_count: int = 0,
        prospects_with_email: int = 0,
        credits_used: int = 1
    ):
        """Log a search execution."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO search_history (query, platform, results_count, prospects_with_email, serpapi_credits_used)
            VALUES (?, ?, ?, ?, ?)
        """, (query, platform, results_count, prospects_with_email, credits_used))
        self.conn.commit()
        
        # Update daily usage stats
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO usage_stats (date, searches_run, credits_used, prospects_found)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                searches_run = searches_run + 1,
                credits_used = credits_used + excluded.credits_used,
                prospects_found = prospects_found + excluded.prospects_found
        """, (today, credits_used, prospects_with_email))
        self.conn.commit()
    
    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search history."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM search_history ORDER BY search_date DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== OUTREACH LOG ====================
    
    def log_outreach(
        self,
        prospect_email: str,
        outreach_type: str,
        template_used: Optional[str] = None,
        subject: Optional[str] = None,
        message_preview: Optional[str] = None,
        send_status: str = "sent"
    ):
        """Log an outreach attempt."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO outreach_log (
                prospect_email, outreach_type, template_used,
                subject, message_preview, send_status, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prospect_email, outreach_type, template_used,
            subject, message_preview[:500] if message_preview else None,
            send_status, datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def get_outreach_log(
        self,
        prospect_email: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get outreach log, optionally filtered by prospect."""
        cursor = self.conn.cursor()
        
        if prospect_email:
            cursor.execute("""
                SELECT * FROM outreach_log WHERE prospect_email = ?
                ORDER BY created_at DESC LIMIT ?
            """, (prospect_email, limit))
        else:
            cursor.execute("""
                SELECT * FROM outreach_log ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== TEMPLATES ====================
    
    def save_email_template(
        self,
        name: str,
        subject: str,
        body: str,
        template_type: str = "initial"
    ) -> bool:
        """Save or update an email template."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO email_templates (name, subject, body, template_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    subject = excluded.subject,
                    body = excluded.body,
                    template_type = excluded.template_type
            """, (name, subject, body, template_type))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def get_email_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all email templates."""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM email_templates WHERE active = 1")
        else:
            cursor.execute("SELECT * FROM email_templates")
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            Statistics dictionary
        """
        cursor = self.conn.cursor()
        
        # Total prospects
        cursor.execute("SELECT COUNT(*) FROM prospects")
        total = cursor.fetchone()[0]
        
        # By platform
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM prospects GROUP BY platform
        """)
        by_platform = {row["platform"]: row["count"] for row in cursor.fetchall()}
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM prospects GROUP BY status
        """)
        by_status = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Contacted stats
        cursor.execute("SELECT COUNT(*) FROM prospects WHERE contacted = 1")
        contacted = cursor.fetchone()[0]
        
        # Today's stats
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM usage_stats WHERE date = ?", (today,))
        today_row = cursor.fetchone()
        today_stats = dict(today_row) if today_row else {
            "searches_run": 0, "credits_used": 0, "prospects_found": 0
        }
        
        # This month's stats
        month_start = datetime.now().strftime("%Y-%m-01")
        cursor.execute("""
            SELECT SUM(searches_run) as searches, SUM(credits_used) as credits,
                   SUM(prospects_found) as prospects
            FROM usage_stats WHERE date >= ?
        """, (month_start,))
        month_row = cursor.fetchone()
        month_stats = {
            "searches_run": month_row["searches"] or 0,
            "credits_used": month_row["credits"] or 0,
            "prospects_found": month_row["prospects"] or 0,
        } if month_row else {"searches_run": 0, "credits_used": 0, "prospects_found": 0}
        
        return {
            "total_prospects": total,
            "by_platform": by_platform,
            "by_status": by_status,
            "contacted_count": contacted,
            "contacted_percentage": round(contacted / total * 100, 1) if total > 0 else 0,
            "uncontacted_count": total - contacted,
            "today": today_stats,
            "this_month": month_stats,
        }
    
    # ==================== EXPORT ====================
    
    def export_to_csv(self, filepath: str, **filters) -> str:
        """
        Export prospects to CSV file.
        
        Args:
            filepath: Output file path
            **filters: Filters to pass to get_prospects()
        
        Returns:
            File path
        """
        import csv
        
        prospects = self.get_prospects(**filters, limit=10000)
        
        if not prospects:
            logger.warning("No prospects to export")
            return filepath
        
        headers = list(prospects[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(prospects)
        
        logger.info(f"Exported {len(prospects)} prospects to {filepath}")
        return filepath
    
    def export_to_json(self, filepath: str, **filters) -> str:
        """Export prospects to JSON file."""
        prospects = self.get_prospects(**filters, limit=10000)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prospects, f, indent=2, default=str)
        
        logger.info(f"Exported {len(prospects)} prospects to {filepath}")
        return filepath
    
    # ==================== HELPERS ====================
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary with hashtags deserialized."""
        d = dict(row)
        
        # Deserialize hashtags from JSON
        if d.get("hashtags"):
            try:
                d["hashtags"] = json.loads(d["hashtags"])
            except json.JSONDecodeError:
                d["hashtags"] = []
        else:
            d["hashtags"] = []
        
        return d


# Singleton instance
_db_instance: Optional[ProspectDatabase] = None


def get_database(db_path: Optional[str] = None) -> ProspectDatabase:
    """Get or create database singleton."""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = ProspectDatabase(db_path)
    
    return _db_instance
