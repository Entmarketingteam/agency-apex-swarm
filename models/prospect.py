"""Prospect data models for creator prospecting system."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms."""
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"


class ProspectStatus(str, Enum):
    """Prospect pipeline status."""
    NEW = "new"
    CONTACTED = "contacted"
    REPLIED = "replied"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"


class Priority(str, Enum):
    """Prospect priority level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OutreachType(str, Enum):
    """Type of outreach."""
    EMAIL = "email"
    INSTAGRAM_DM = "instagram_dm"
    LINKEDIN_DM = "linkedin_dm"
    FOLLOW_UP = "follow_up"


class Prospect(BaseModel):
    """
    Prospect model for creator prospecting.
    
    Represents a potential creator to contact for brand partnerships.
    """
    
    # Core Identification
    id: Optional[int] = None
    platform: Platform = Field(..., description="Source platform: tiktok, twitter, instagram")
    username: str = Field(..., description="Profile username (without @)")
    profile_url: str = Field(..., description="Full profile URL")
    
    # Contact Information
    email: EmailStr = Field(..., description="Contact email found in bio/profile")
    instagram_username: Optional[str] = Field(None, description="Instagram handle (may differ from main platform)")
    
    # Profile Data
    bio: Optional[str] = Field(None, description="Profile bio text")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Hashtags found in bio/content")
    follower_count: Optional[int] = Field(None, ge=0, description="Follower count if available")
    engagement_rate: Optional[float] = Field(None, ge=0, le=100, description="Engagement rate percentage")
    
    # Search Metadata
    search_query: Optional[str] = Field(None, description="Query that found this prospect")
    found_date: datetime = Field(default_factory=datetime.now, description="Date prospect was discovered")
    
    # Outreach Status
    status: ProspectStatus = Field(default=ProspectStatus.NEW, description="Pipeline status")
    priority: Priority = Field(default=Priority.MEDIUM, description="Prospect priority")
    contacted: bool = Field(default=False, description="Whether prospect has been contacted")
    contacted_date: Optional[datetime] = Field(None, description="Date of first contact")
    last_contact_date: Optional[datetime] = Field(None, description="Most recent contact date")
    next_followup_date: Optional[datetime] = Field(None, description="Scheduled follow-up date")
    
    # Team Management
    owner: Optional[str] = Field(None, description="Team member assigned to this prospect")
    notes: Optional[str] = Field(None, description="Free-form notes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_sheet_row(self) -> List[Any]:
        """Convert prospect to Google Sheets row format."""
        return [
            self.platform,
            f"@{self.username}",
            self.profile_url,
            self.email,
            f"@{self.instagram_username}" if self.instagram_username else "",
            ", ".join(self.hashtags) if self.hashtags else "",
            self.bio or "",
            self.follower_count or "",
            self.search_query or "",
            self.found_date.strftime("%Y-%m-%d") if self.found_date else "",
            self.status,
            "Yes" if self.contacted else "No",
            self.contacted_date.strftime("%Y-%m-%d") if self.contacted_date else "",
            self.owner or "",
            self.priority,
            self.notes or "",
            self.last_contact_date.strftime("%Y-%m-%d") if self.last_contact_date else "",
            self.next_followup_date.strftime("%Y-%m-%d") if self.next_followup_date else "",
        ]
    
    @classmethod
    def sheet_headers(cls) -> List[str]:
        """Get Google Sheets column headers."""
        return [
            "Platform",
            "Username", 
            "Profile URL",
            "Email",
            "Instagram",
            "Hashtags",
            "Bio",
            "Follower Count",
            "Search Query",
            "Found Date",
            "Status",
            "Contacted",
            "Contacted Date",
            "Owner",
            "Priority",
            "Notes",
            "Last Contact",
            "Next Follow-up",
        ]


class ProspectBatch(BaseModel):
    """Batch of prospects for processing."""
    
    prospects: List[Prospect]
    batch_id: Optional[str] = None
    search_query: Optional[str] = None
    platform: Optional[Platform] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    def __len__(self) -> int:
        return len(self.prospects)
    
    def __iter__(self):
        return iter(self.prospects)
    
    @property
    def emails(self) -> List[str]:
        """Get all emails from prospects."""
        return [p.email for p in self.prospects]
    
    def filter_by_status(self, status: ProspectStatus) -> List[Prospect]:
        """Filter prospects by status."""
        return [p for p in self.prospects if p.status == status]
    
    def filter_uncontacted(self) -> List[Prospect]:
        """Get uncontacted prospects."""
        return [p for p in self.prospects if not p.contacted]


class SearchQuery(BaseModel):
    """Search query parameters for prospecting."""
    
    platform: Platform = Field(default=Platform.TIKTOK, description="Platform to search")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Hashtags to search for")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Keywords to search for")
    email_domains: Optional[List[str]] = Field(
        default=["gmail.com", "yahoo.com", "outlook.com"],
        description="Email domains to look for"
    )
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results to return")
    
    def build_google_query(self) -> str:
        """
        Build Google search query string.
        
        Example output:
        site:tiktok.com "@gmail.com" ("#LTK" OR "#amazonfinds") ("wellness" OR "fitness")
        """
        parts = []
        
        # Platform site restriction
        site_map = {
            Platform.TIKTOK: "site:tiktok.com",
            Platform.TWITTER: "site:twitter.com OR site:x.com",
            Platform.INSTAGRAM: "site:instagram.com",
            Platform.YOUTUBE: "site:youtube.com",
        }
        parts.append(site_map.get(self.platform, "site:tiktok.com"))
        
        # Email domain filter
        if self.email_domains:
            email_parts = [f'"@{domain}"' for domain in self.email_domains]
            if len(email_parts) == 1:
                parts.append(email_parts[0])
            else:
                parts.append(f"({' OR '.join(email_parts)})")
        
        # Hashtag filter
        if self.hashtags:
            hashtag_parts = [f'"#{tag.lstrip("#")}"' for tag in self.hashtags]
            if len(hashtag_parts) == 1:
                parts.append(hashtag_parts[0])
            else:
                parts.append(f"({' OR '.join(hashtag_parts)})")
        
        # Keyword filter
        if self.keywords:
            keyword_parts = [f'"{kw}"' for kw in self.keywords]
            if len(keyword_parts) == 1:
                parts.append(keyword_parts[0])
            else:
                parts.append(f"({' OR '.join(keyword_parts)})")
        
        return " ".join(parts)


class SearchHistory(BaseModel):
    """Record of a search execution."""
    
    id: Optional[int] = None
    query: str
    platform: Optional[Platform] = None
    results_count: int = 0
    prospects_with_email: int = 0
    serpapi_credits_used: int = 1
    search_date: datetime = Field(default_factory=datetime.now)


class OutreachLog(BaseModel):
    """Log of an outreach attempt."""
    
    id: Optional[int] = None
    prospect_email: EmailStr
    outreach_type: OutreachType
    template_used: Optional[str] = None
    subject: Optional[str] = None  # For emails
    message_preview: Optional[str] = Field(None, max_length=500)
    send_status: str = Field(default="pending", description="pending, sent, failed, bounced")
    error_message: Optional[str] = None
    response_received: bool = False
    response_text: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class EmailTemplate(BaseModel):
    """Email template for outreach."""
    
    id: Optional[int] = None
    name: str = Field(..., description="Template name for reference")
    subject: str = Field(..., description="Email subject line (supports {placeholders})")
    body: str = Field(..., description="Email body (supports {placeholders})")
    template_type: str = Field(default="initial", description="initial, follow_up, partnership")
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Available placeholders
    PLACEHOLDERS = [
        "{name}",           # Creator name/username
        "{platform}",       # TikTok, Instagram, etc.
        "{hashtag}",        # Primary hashtag
        "{content_topic}",  # Content topic derived from bio
        "{brand}",          # Brand being pitched
        "{product}",        # Specific product
    ]
    
    def render(self, context: Dict[str, str]) -> tuple[str, str]:
        """
        Render template with context values.
        
        Args:
            context: Dictionary of placeholder -> value mappings
        
        Returns:
            Tuple of (rendered_subject, rendered_body)
        """
        subject = self.subject
        body = self.body
        
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        return subject, body


class DMTemplate(BaseModel):
    """Instagram/LinkedIn DM template."""
    
    id: Optional[int] = None
    name: str
    message: str = Field(..., max_length=1000, description="DM message (shorter than email)")
    platform: str = Field(default="instagram", description="instagram, linkedin")
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    def render(self, context: Dict[str, str]) -> str:
        """Render template with context values."""
        message = self.message
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            message = message.replace(placeholder, str(value))
        return message


# Default templates from PRD
DEFAULT_EMAIL_TEMPLATES = [
    EmailTemplate(
        name="LTK Creator Outreach",
        subject="Partnership opportunity for {hashtag} creators 🎯",
        body="""Hi {name},

I came across your {platform} and loved your content! Your audience clearly trusts your recommendations.

I run ENT Agency - we help creators like you add brand partnerships with wellness companies like Thorne, LMNT, and ARMRA.

We're currently helping brands launch new products and think your audience would love it. Interested in a quick 15-min call to explore?

Best,
Emily
ENT Agency""",
        template_type="initial"
    ),
    EmailTemplate(
        name="Amazon Storefront Creator",
        subject="Loved your Amazon finds - partnership opportunity",
        body="""Hi {name},

Your Amazon storefront is amazing! I especially loved your recommendations.

I help Amazon creators add sponsored brand partnerships that complement their affiliate earnings. We work with supplement and wellness brands who want to work with trusted voices like you.

Would you be open to a quick call this week to discuss some opportunities?

Best,
Emily
ENT Agency""",
        template_type="initial"
    ),
    EmailTemplate(
        name="Follow-up",
        subject="Re: Partnership opportunity",
        body="""Hi {name},

Just following up on my last email. Still interested in discussing brand partnership opportunities?

Let me know!

Best,
Emily
ENT Agency""",
        template_type="follow_up"
    ),
]

DEFAULT_DM_TEMPLATES = [
    DMTemplate(
        name="Instagram Initial",
        message="""Hey {name}! 👋 

Just saw your content and had to reach out. We work with wellness creators on brand partnerships - would love to chat about some opportunities.

Quick call this week? 🎯""",
        platform="instagram"
    ),
    DMTemplate(
        name="Instagram Follow-up",
        message="""Hey again! Just following up - still interested in chatting about brand partnerships? Let me know! 😊""",
        platform="instagram"
    ),
]
