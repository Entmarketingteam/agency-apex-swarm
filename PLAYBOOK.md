# 🚀 APEX Lead Generation System - Complete Playbook

> **Last Updated:** January 2026  
> **Version:** 1.0.0  
> **Status:** Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [API Integrations](#api-integrations)
4. [Workflow Pipeline](#workflow-pipeline)
5. [Google Sheets Integration](#google-sheets-integration)
6. [Slack Integration](#slack-integration)
7. [Environment Variables](#environment-variables)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

APEX is an AI-powered lead generation and outreach automation system designed for creator/influencer outreach campaigns.

### Core Capabilities

| Feature | Description | AI Model |
|---------|-------------|----------|
| **Research** | Deep research on leads using web search | Perplexity Pro |
| **Vibe Check** | Visual analysis of creator content | Gemini 3.0 Ultra |
| **Email Discovery** | Find verified email addresses | Findymail API |
| **Personalization** | Generate custom outreach messages | GPT-5.2 Pro |
| **Orchestration** | Coordinate all workflows | Claude Opus 4.5 |
| **Deduplication** | Prevent duplicate outreach | Pinecone Vector DB |
| **Email Campaigns** | Automated email sequences | Smartlead |
| **LinkedIn DMs** | Direct message automation | Unipile |

### Input Methods

1. **Google Sheets** - Drop leads into a spreadsheet
2. **Slack** - Paste Instagram URL in a channel (coming soon)
3. **CSV Import** - Bulk import via script
4. **API** - Direct programmatic access

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT SOURCES                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Google Sheets  │     Slack       │         CSV/API             │
│  (Primary)      │  (Instagram URL)│       (Bulk Import)         │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APEX ORCHESTRATOR                            │
│                   (Claude Opus 4.5)                             │
├─────────────────────────────────────────────────────────────────┤
│  • Coordinates all API calls                                    │
│  • Manages workflow state                                       │
│  • Handles errors and retries                                   │
│  • Logs all actions                                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                          │
├─────────┬─────────┬─────────┬─────────┬─────────┬───────────────┤
│ Dedup   │Research │  Vibe   │  Email  │ Content │   Outreach    │
│ Check   │         │  Check  │  Find   │  Gen    │               │
├─────────┼─────────┼─────────┼─────────┼─────────┼───────────────┤
│Pinecone │Perplexity│ Gemini │Findymail│ GPT-5.2 │Smartlead/     │
│         │         │  Ultra  │         │  Pro    │Unipile        │
└─────────┴─────────┴─────────┴─────────┴─────────┴───────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT / STORAGE                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Google Sheets  │   Smartlead     │        Pinecone             │
│  (Status Update)│   (Campaigns)   │     (Vector Store)          │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## 🔌 API Integrations

### AI Models

| Service | Purpose | Model | Endpoint |
|---------|---------|-------|----------|
| **Anthropic** | Orchestration & Planning | Claude Opus 4.5 | `api.anthropic.com` |
| **OpenAI** | Persuasive Writing | GPT-5.2 Pro | `api.openai.com` |
| **Google** | Visual Analysis | Gemini 3.0 Ultra | `generativelanguage.googleapis.com` |
| **Perplexity** | Web Research | Sonar Pro | `api.perplexity.ai` |

### Lead Generation APIs

| Service | Purpose | Rate Limit | Docs |
|---------|---------|------------|------|
| **Findymail** | Email Discovery | 100/min | [docs](https://findymail.com/docs) |
| **Unipile** | LinkedIn Automation | 50/day | [docs](https://unipile.com/docs) |
| **Smartlead** | Email Campaigns | Unlimited | [docs](https://help.smartlead.ai) |
| **Pinecone** | Vector Deduplication | 100/sec | [docs](https://docs.pinecone.io) |

### Data Sources

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| **Google Sheets** | Lead Input/Output | API Key |
| **Slack** | Instagram URL Trigger | Bot Token |

---

## 🔄 Workflow Pipeline

### Stage 1: Lead Ingestion

```python
# From Google Sheets
from api_clients.google_sheets_client import GoogleSheetsClient

client = GoogleSheetsClient()
leads = client.get_unprocessed_leads()  # Gets leads where status != "completed"
```

### Stage 2: Deduplication Check

```python
# Check if lead was already contacted
from api_clients.pinecone_client import PineconeClient

pinecone = PineconeClient()
is_duplicate = pinecone.check_duplicate(lead.handle)
if is_duplicate:
    skip_lead()
```

### Stage 3: Research

```python
# Deep research on the lead
from api_clients.perplexity_client import PerplexityClient

perplexity = PerplexityClient()
research = perplexity.research_lead(
    name=lead.name,
    handle=lead.handle,
    platform=lead.platform
)
# Returns: bio, recent posts, engagement, brand deals, etc.
```

### Stage 4: Vibe Check (Visual Analysis)

```python
# Analyze creator's visual content
from ai_models.gemini_client import GeminiClient

gemini = GeminiClient()
vibe_analysis = gemini.analyze_creator_profile(
    profile_url=f"https://instagram.com/{lead.handle}"
)
# Returns: aesthetic, brand fit score, content themes
```

### Stage 5: Email Discovery

```python
# Find verified email
from api_clients.findymail_client import FindymailClient

findymail = FindymailClient()
email_result = findymail.find_email(
    name=lead.name,
    domain=lead.website  # or inferred from LinkedIn
)
```

### Stage 6: Content Generation

```python
# Generate personalized outreach
from ai_models.openai_client import OpenAIClient

openai = OpenAIClient()
email_content = openai.generate_outreach(
    lead=lead,
    research=research,
    vibe=vibe_analysis,
    template="partnership_intro"
)
```

### Stage 7: Outreach Execution

```python
# Send via Smartlead (email) or Unipile (LinkedIn)
from api_clients.smartlead_client import SmartleadClient

smartlead = SmartleadClient()
smartlead.add_to_campaign(
    email=lead.email,
    first_name=lead.name.split()[0],
    custom_fields={"personalized_intro": email_content}
)
```

---

## 📊 Google Sheets Integration

### Sheet URL
```
https://docs.google.com/spreadsheets/d/1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew/edit
```

### Tab Name
```
TEST SHEET FOR CURSOR
```

### Required Columns

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `name` | ✅ | Creator's full name | "Jane Smith" |
| `handle` | ✅ | Social media handle | "@janesmith" |
| `platform` | ❌ | Platform (default: instagram) | "instagram" |
| `email` | ❌ | Known email (optional) | "jane@email.com" |
| `linkedin` | ❌ | LinkedIn URL | "linkedin.com/in/jane" |
| `bio` | ❌ | Notes about creator | "Fashion influencer" |
| `status` | ❌ | Processing status | "pending" |

### Status Values

| Status | Meaning |
|--------|---------|
| *(empty)* | Not yet processed |
| `pending` | Queued for processing |
| `researching` | Currently being researched |
| `email_found` | Email discovered |
| `outreach_sent` | Email/DM sent |
| `completed` | Fully processed |
| `skipped` | Duplicate or invalid |
| `error` | Processing failed |

---

## 💬 Slack Integration (Instagram URL Workflow)

### How It Works

1. **User pastes Instagram URL** in designated Slack channel
2. **Slack bot detects URL** and extracts handle
3. **System creates lead** and starts processing
4. **Bot posts updates** as lead progresses through pipeline

### Slack Channel Setup

```
Channel: #lead-intake
Bot Name: APEX Lead Bot
```

### Supported URL Formats

```
https://instagram.com/username
https://www.instagram.com/username/
https://instagram.com/p/POST_ID  (extracts from post)
@username (just the handle)
```

### Example Slack Interaction

```
👤 User: https://instagram.com/fashionista_jane

🤖 APEX Bot: 
   ✅ Lead detected: @fashionista_jane
   📋 Added to processing queue
   ⏳ Estimated completion: 2-3 minutes

🤖 APEX Bot (2 min later):
   ✅ Lead processed: @fashionista_jane
   📧 Email found: jane@fashionista.com
   📊 Vibe Score: 87/100 (Great fit!)
   📤 Added to Smartlead campaign
```

### Environment Variables for Slack

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CHANNEL_ID=C0123456789
```

---

## 🔐 Environment Variables

### Required API Keys

```bash
# AI Models
ANTHROPIC_API_KEY=sk-ant-...      # Claude Opus 4.5
OPENAI_API_KEY=sk-proj-...        # GPT-5.2 Pro
GOOGLE_API_KEY=AIzaSy...          # Gemini + Sheets

# Lead Generation
PERPLEXITY_API_KEY=pplx-...       # Research
FINDYMAIL_API_KEY=...             # Email discovery
UNIPILE_API_KEY=...               # LinkedIn DMs
SMARTLEAD_API_KEY=...             # Email campaigns
PINECONE_API_KEY=pcsk_...         # Deduplication

# Google Sheets
GOOGLE_SHEET_ID=1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew
GOOGLE_SHEET_TAB_NAME=TEST SHEET FOR CURSOR

# Slack (Optional)
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_CHANNEL_ID=...
```

### Setting in Railway

All environment variables are configured in Railway:
- Dashboard: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

---

## 🚀 Deployment

### Railway (Production)

```bash
# Automatic deployment on git push
git push origin main

# Manual redeploy via API
python scripts/railway_v2_setup.py
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python run.py

# Or run scheduler
python scripts/scheduler.py
```

### Health Check

```bash
# Test all APIs
python scripts/verify_apis.py

# Test Google Sheets connection
python -c "from api_clients.google_sheets_client import GoogleSheetsClient; print(GoogleSheetsClient().get_leads_from_sheet())"
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "API key expired" | Google API key invalid | Generate new key in Cloud Console |
| "Rate limit exceeded" | Too many API calls | Wait or upgrade plan |
| "No leads found" | Sheet empty or wrong tab | Check sheet has data in correct tab |
| "Duplicate detected" | Lead already in Pinecone | Skip or clear Pinecone index |
| "Email not found" | Findymail couldn't verify | Try LinkedIn lookup instead |

### Logs

```bash
# View Railway logs
railway logs

# Local logs are in stdout with timestamps
2026-01-07 20:47:03 - api_clients.google_sheets_client - INFO - Fetched 5 leads
```

### Reset Pinecone Index

```python
from api_clients.pinecone_client import PineconeClient
client = PineconeClient()
client.index.delete(delete_all=True)
```

---

## 📁 File Structure

```
agency-apex-swarm/
├── api_clients/
│   ├── findymail_client.py      # Email discovery
│   ├── google_sheets_client.py  # Sheet integration
│   ├── perplexity_client.py     # Web research
│   ├── pinecone_client.py       # Deduplication
│   ├── smartlead_client.py      # Email campaigns
│   └── unipile_client.py        # LinkedIn DMs
├── ai_models/
│   ├── claude_client.py         # Orchestration
│   ├── gemini_client.py         # Visual analysis
│   └── openai_client.py         # Content generation
├── models/
│   └── lead.py                  # Lead data model
├── utils/
│   ├── config.py                # Environment config
│   ├── logger.py                # Structured logging
│   └── retry.py                 # Exponential backoff
├── scripts/
│   ├── scheduler.py             # Cron-like scheduler
│   ├── verify_apis.py           # API health check
│   └── import_leads.py          # CSV import
├── slack_bot/                   # Slack integration (new)
│   ├── app.py                   # Bot application
│   ├── handlers.py              # Message handlers
│   └── instagram_parser.py      # URL parsing
├── run.py                       # Main entry point
├── main.py                      # Core orchestration
├── requirements.txt             # Dependencies
├── railway.json                 # Railway config
└── .env                         # API keys (gitignored)
```

---

## 🎯 Quick Start

### 1. Add a Lead to Google Sheets

Open: https://docs.google.com/spreadsheets/d/1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew/edit

Add row in "TEST SHEET FOR CURSOR" tab:
```
| name        | handle      | platform  | status  |
|-------------|-------------|-----------|---------|
| Jane Smith  | @janesmith  | instagram | pending |
```

### 2. System Processes Automatically

Railway runs every 5 minutes and:
- Reads unprocessed leads
- Researches each lead
- Finds emails
- Generates personalized content
- Sends outreach
- Updates status to "completed"

### 3. Monitor Progress

Check the `status` column in Google Sheets or view Railway logs.

---

## 📞 Support

- **GitHub Repo:** https://github.com/Entmarketingteam/agency-apex-swarm
- **Railway Dashboard:** https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

---

*Built with ❤️ by APEX System*

