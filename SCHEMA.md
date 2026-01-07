# 📐 APEX System - Data Schemas & Models

> Complete reference for all data structures, API payloads, and database schemas.

---

## 📋 Table of Contents

1. [Lead Model](#lead-model)
2. [API Request/Response Schemas](#api-schemas)
3. [Google Sheets Schema](#google-sheets-schema)
4. [Slack Event Schema](#slack-event-schema)
5. [Pinecone Vector Schema](#pinecone-vector-schema)
6. [Configuration Schema](#configuration-schema)

---

## 👤 Lead Model

### Python Model (`models/lead.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LeadStatus(str, Enum):
    PENDING = "pending"
    RESEARCHING = "researching"
    EMAIL_FOUND = "email_found"
    OUTREACH_SENT = "outreach_sent"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"

class Lead(BaseModel):
    """Core lead data model."""
    
    # Required fields
    id: Optional[str] = Field(default=None, description="Unique identifier")
    handle: str = Field(..., description="Social media handle (e.g., @username)")
    
    # Optional identification
    name: Optional[str] = Field(default=None, description="Full name")
    platform: str = Field(default="instagram", description="Social platform")
    
    # Contact information
    email: Optional[str] = Field(default=None, description="Verified email address")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    website: Optional[str] = Field(default=None, description="Personal website")
    
    # Research data
    bio: Optional[str] = Field(default=None, description="Bio or notes")
    follower_count: Optional[int] = Field(default=None, description="Number of followers")
    engagement_rate: Optional[float] = Field(default=None, description="Engagement rate %")
    
    # Enrichment data
    research_summary: Optional[str] = Field(default=None, description="AI research summary")
    vibe_score: Optional[int] = Field(default=None, description="Brand fit score 0-100")
    vibe_analysis: Optional[str] = Field(default=None, description="Visual analysis notes")
    
    # Outreach data
    personalized_message: Optional[str] = Field(default=None, description="Generated outreach")
    outreach_channel: Optional[str] = Field(default=None, description="email or linkedin")
    
    # Status tracking
    status: LeadStatus = Field(default=LeadStatus.PENDING)
    error_message: Optional[str] = Field(default=None, description="Error if failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    source: Optional[str] = Field(default=None, description="Where lead came from")
    tags: List[str] = Field(default_factory=list, description="Custom tags")
```

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Lead",
  "type": "object",
  "required": ["handle"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "handle": { "type": "string", "pattern": "^@?[a-zA-Z0-9_.]+$" },
    "name": { "type": "string" },
    "platform": { 
      "type": "string", 
      "enum": ["instagram", "tiktok", "youtube", "twitter", "linkedin"] 
    },
    "email": { "type": "string", "format": "email" },
    "linkedin_url": { "type": "string", "format": "uri" },
    "website": { "type": "string", "format": "uri" },
    "bio": { "type": "string" },
    "follower_count": { "type": "integer", "minimum": 0 },
    "engagement_rate": { "type": "number", "minimum": 0, "maximum": 100 },
    "research_summary": { "type": "string" },
    "vibe_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "vibe_analysis": { "type": "string" },
    "personalized_message": { "type": "string" },
    "outreach_channel": { "type": "string", "enum": ["email", "linkedin", "dm"] },
    "status": {
      "type": "string",
      "enum": ["pending", "researching", "email_found", "outreach_sent", "completed", "skipped", "error"]
    },
    "error_message": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "processed_at": { "type": "string", "format": "date-time" },
    "source": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## 🔌 API Schemas

### Perplexity Research API

**Request:**
```json
{
  "model": "sonar-pro",
  "messages": [
    {
      "role": "system",
      "content": "You are a research assistant..."
    },
    {
      "role": "user", 
      "content": "Research Instagram creator @username..."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "model": "sonar-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "## Research Summary\n\n**Name:** Jane Smith\n**Niche:** Fashion & Lifestyle..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 500,
    "total_tokens": 650
  }
}
```

### Findymail Email Discovery API

**Request:**
```json
{
  "name": "Jane Smith",
  "domain": "janesmith.com"
}
```

**Response:**
```json
{
  "email": "jane@janesmith.com",
  "confidence": 95,
  "verified": true,
  "sources": ["website", "linkedin"],
  "mx_records": true
}
```

### Smartlead Campaign API

**Add Lead to Campaign:**
```json
{
  "campaign_id": "camp_123",
  "lead": {
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "company": "Jane Smith LLC",
    "custom_fields": {
      "personalized_intro": "I loved your recent post about...",
      "instagram_handle": "@janesmith"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": "lead_456",
  "campaign_id": "camp_123",
  "status": "queued"
}
```

### Unipile LinkedIn DM API

**Send Message:**
```json
{
  "account_id": "acc_123",
  "recipient_url": "https://linkedin.com/in/janesmith",
  "message": "Hi Jane, I came across your profile..."
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "msg_789",
  "status": "sent",
  "sent_at": "2026-01-07T20:00:00Z"
}
```

### Claude Orchestration API

**Request:**
```json
{
  "model": "claude-opus-4-5-20260101",
  "max_tokens": 4096,
  "system": "You are an orchestration agent...",
  "messages": [
    {
      "role": "user",
      "content": "Process this lead: {...}"
    }
  ]
}
```

**Response:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Processing lead @janesmith...\n\n1. Research: Complete\n2. Email: Found..."
    }
  ],
  "model": "claude-opus-4-5-20260101",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 500,
    "output_tokens": 1000
  }
}
```

### Gemini Visual Analysis API

**Request:**
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Analyze this Instagram profile for brand fit..."
        },
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "base64_encoded_image..."
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.4,
    "maxOutputTokens": 1000
  }
}
```

**Response:**
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "## Visual Analysis\n\n**Aesthetic:** Minimalist, clean...\n**Brand Fit Score:** 87/100..."
          }
        ]
      },
      "finishReason": "STOP"
    }
  ]
}
```

---

## 📊 Google Sheets Schema

### Sheet Structure

**Sheet Name:** `TEST SHEET FOR CURSOR`

| Column | Header | Type | Required | Description |
|--------|--------|------|----------|-------------|
| A | `name` | String | ✅ | Creator's full name |
| B | `handle` | String | ✅ | Social handle (@username) |
| C | `platform` | String | ❌ | instagram, tiktok, youtube |
| D | `email` | String | ❌ | Known or discovered email |
| E | `linkedin` | String | ❌ | LinkedIn profile URL |
| F | `bio` | String | ❌ | Notes or bio |
| G | `follower_count` | Number | ❌ | Follower count |
| H | `status` | String | ❌ | Processing status |
| I | `vibe_score` | Number | ❌ | Brand fit 0-100 |
| J | `research_summary` | String | ❌ | AI research output |
| K | `personalized_message` | String | ❌ | Generated outreach |
| L | `processed_at` | DateTime | ❌ | When processed |
| M | `error` | String | ❌ | Error message if failed |

### Example Row

```csv
name,handle,platform,email,linkedin,bio,follower_count,status,vibe_score,research_summary,personalized_message,processed_at,error
Jane Smith,@janesmith,instagram,jane@email.com,linkedin.com/in/jane,Fashion influencer,150000,completed,87,"Fashion and lifestyle creator...",Hi Jane! I loved...,2026-01-07T20:00:00Z,
```

### API Response Format

```json
{
  "range": "'TEST SHEET FOR CURSOR'!A1:M100",
  "majorDimension": "ROWS",
  "values": [
    ["name", "handle", "platform", "email", "linkedin", "bio", "follower_count", "status", "vibe_score", "research_summary", "personalized_message", "processed_at", "error"],
    ["Jane Smith", "@janesmith", "instagram", "", "", "Fashion influencer", "150000", "pending", "", "", "", "", ""]
  ]
}
```

---

## 💬 Slack Event Schema

### URL Message Event

When a user posts an Instagram URL:

```json
{
  "token": "verification_token",
  "team_id": "T0123456",
  "event": {
    "type": "message",
    "channel": "C0123456789",
    "user": "U0123456",
    "text": "https://instagram.com/janesmith",
    "ts": "1704657600.000100",
    "event_ts": "1704657600.000100",
    "channel_type": "channel"
  },
  "type": "event_callback",
  "event_id": "Ev0123456",
  "event_time": 1704657600
}
```

### Bot Response Message

```json
{
  "channel": "C0123456789",
  "text": "✅ Lead detected: @janesmith",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "✅ *Lead detected:* `@janesmith`"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Platform:*\nInstagram"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\n⏳ Processing..."
        }
      ]
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Estimated completion: 2-3 minutes"
        }
      ]
    }
  ]
}
```

### Completion Update Message

```json
{
  "channel": "C0123456789",
  "text": "✅ Lead processed: @janesmith",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "✅ *Lead processed:* `@janesmith`"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Email:*\njane@janesmith.com"
        },
        {
          "type": "mrkdwn",
          "text": "*Vibe Score:*\n87/100 ✨"
        }
      ]
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Research:*\nFashion & lifestyle creator with 150K followers..."
        },
        {
          "type": "mrkdwn",
          "text": "*Outreach:*\n📤 Added to Smartlead campaign"
        }
      ]
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": { "type": "plain_text", "text": "View in Sheet" },
          "url": "https://docs.google.com/spreadsheets/d/..."
        }
      ]
    }
  ]
}
```

---

## 🔢 Pinecone Vector Schema

### Index Configuration

```json
{
  "name": "apex-leads",
  "dimension": 1536,
  "metric": "cosine",
  "spec": {
    "serverless": {
      "cloud": "aws",
      "region": "us-east-1"
    }
  }
}
```

### Vector Record

```json
{
  "id": "lead_janesmith_instagram",
  "values": [0.123, -0.456, 0.789, ...],  // 1536 dimensions
  "metadata": {
    "handle": "@janesmith",
    "platform": "instagram",
    "name": "Jane Smith",
    "email": "jane@janesmith.com",
    "processed_at": "2026-01-07T20:00:00Z",
    "vibe_score": 87
  }
}
```

### Query Request

```json
{
  "vector": [0.123, -0.456, 0.789, ...],
  "top_k": 5,
  "include_metadata": true,
  "filter": {
    "platform": { "$eq": "instagram" }
  }
}
```

### Query Response

```json
{
  "matches": [
    {
      "id": "lead_janesmith_instagram",
      "score": 0.95,
      "metadata": {
        "handle": "@janesmith",
        "platform": "instagram",
        "name": "Jane Smith"
      }
    }
  ],
  "namespace": ""
}
```

---

## ⚙️ Configuration Schema

### Environment Variables Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "APEX Configuration",
  "type": "object",
  "required": [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY", 
    "GOOGLE_API_KEY",
    "PERPLEXITY_API_KEY",
    "FINDYMAIL_API_KEY",
    "PINECONE_API_KEY"
  ],
  "properties": {
    "ANTHROPIC_API_KEY": {
      "type": "string",
      "pattern": "^sk-ant-.*$",
      "description": "Claude API key"
    },
    "OPENAI_API_KEY": {
      "type": "string", 
      "pattern": "^sk-proj-.*$",
      "description": "OpenAI API key"
    },
    "GOOGLE_API_KEY": {
      "type": "string",
      "pattern": "^AIzaSy.*$",
      "description": "Google Cloud API key"
    },
    "PERPLEXITY_API_KEY": {
      "type": "string",
      "pattern": "^pplx-.*$",
      "description": "Perplexity API key"
    },
    "FINDYMAIL_API_KEY": {
      "type": "string",
      "description": "Findymail API key"
    },
    "UNIPILE_API_KEY": {
      "type": "string",
      "description": "Unipile API key"
    },
    "SMARTLEAD_API_KEY": {
      "type": "string",
      "pattern": "^[a-f0-9-]+$",
      "description": "Smartlead API key"
    },
    "PINECONE_API_KEY": {
      "type": "string",
      "pattern": "^pcsk_.*$",
      "description": "Pinecone API key"
    },
    "GOOGLE_SHEET_ID": {
      "type": "string",
      "description": "Google Sheet document ID"
    },
    "GOOGLE_SHEET_TAB_NAME": {
      "type": "string",
      "default": "TEST SHEET FOR CURSOR",
      "description": "Sheet tab name to read from"
    },
    "SLACK_BOT_TOKEN": {
      "type": "string",
      "pattern": "^xoxb-.*$",
      "description": "Slack bot OAuth token"
    },
    "SLACK_SIGNING_SECRET": {
      "type": "string",
      "description": "Slack app signing secret"
    },
    "SLACK_CHANNEL_ID": {
      "type": "string",
      "pattern": "^C[A-Z0-9]+$",
      "description": "Slack channel for lead intake"
    }
  }
}
```

### Railway Configuration (`railway.json`)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🔄 State Machine

### Lead Processing States

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
              ┌─────│ RESEARCHING │─────┐
              │     └──────┬──────┘     │
              │            │            │
              │ (duplicate)│            │ (error)
              ▼            ▼            ▼
        ┌─────────┐ ┌─────────────┐ ┌─────────┐
        │ SKIPPED │ │ EMAIL_FOUND │ │  ERROR  │
        └─────────┘ └──────┬──────┘ └─────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │OUTREACH_SENT│
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  COMPLETED  │
                    └─────────────┘
```

---

*Schema version: 1.0.0 | Last updated: January 2026*

