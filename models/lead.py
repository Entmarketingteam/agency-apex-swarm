"""Lead data models and schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class Lead(BaseModel):
    """Lead data model."""
    
    # Basic Information
    id: Optional[str] = None
    name: Optional[str] = None
    handle: Optional[str] = Field(None, description="Social media handle (Instagram, TikTok, etc.)")
    platform: Optional[str] = Field(None, description="Platform: instagram, tiktok, linkedin, etc.")
    profile_url: Optional[str] = Field(None, description="Full profile URL")
    
    # Contact Information
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    instagram_handle: Optional[str] = Field(None, description="Instagram handle (if known)")
    
    # Profile Data
    bio: Optional[str] = None
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Hashtags found in bio/content")
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    # Visual Analysis
    vibe_check_score: Optional[float] = Field(None, ge=0, le=10, description="Brand fit score 0-10")
    vibe_check_notes: Optional[str] = None
    
    # Research Data
    research_data: Optional[Dict[str, Any]] = None
    
    # Outreach Status
    status: Optional[str] = Field(
        None,
        description="Pipeline status (e.g. New, Contacted, Replied, Interested, Not Interested)"
    )
    contact_status: Optional[str] = Field(None, description="pending, contacted, responded, converted")
    outreach_method: Optional[str] = Field(None, description="email, linkedin_dm, both")
    outreach_date: Optional[datetime] = None
    contacted: Optional[bool] = Field(None, description="Whether lead/prospect has been contacted")
    contacted_date: Optional[datetime] = None
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    owner: Optional[str] = Field(None, description="Assigned team member")
    priority: Optional[str] = Field(None, description="Priority: High, Medium, Low")
    
    # Prospecting Metadata
    search_query: Optional[str] = None
    found_date: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LeadBatch(BaseModel):
    """Batch of leads for processing."""
    
    leads: List[Lead]
    batch_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    def __len__(self) -> int:
        return len(self.leads)
    
    def __iter__(self):
        return iter(self.leads)


class OutreachResult(BaseModel):
    """Result of an outreach attempt."""
    
    lead_id: str
    method: str  # "email" or "linkedin_dm"
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

