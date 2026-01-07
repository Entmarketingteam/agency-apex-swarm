# 🎬 APEX System - Workflow Scenarios

> Real-world examples of how the system processes leads through different pathways.

---

## 📋 Table of Contents

1. [Scenario 1: Google Sheets Lead](#scenario-1-google-sheets-lead)
2. [Scenario 2: Slack Instagram URL](#scenario-2-slack-instagram-url)
3. [Scenario 3: Bulk CSV Import](#scenario-3-bulk-csv-import)
4. [Scenario 4: Duplicate Detection](#scenario-4-duplicate-detection)
5. [Scenario 5: Email Not Found - LinkedIn Fallback](#scenario-5-linkedin-fallback)
6. [Scenario 6: Error Recovery](#scenario-6-error-recovery)

---

## 🎯 Scenario 1: Google Sheets Lead

**Trigger:** User adds a new row to Google Sheets

### Step-by-Step Flow

#### 1. User Action
User adds row to "TEST SHEET FOR CURSOR" tab:

| name | handle | platform | status |
|------|--------|----------|--------|
| Emma Johnson | @emmastyle | instagram | |

#### 2. System Detection (Every 5 minutes)

```python
# run.py detects new lead
from api_clients.google_sheets_client import GoogleSheetsClient

client = GoogleSheetsClient()
leads = client.get_unprocessed_leads()
# Returns: [{"name": "Emma Johnson", "handle": "@emmastyle", "platform": "instagram"}]
```

#### 3. Deduplication Check

```python
from api_clients.pinecone_client import PineconeClient

pinecone = PineconeClient()
is_duplicate = pinecone.check_duplicate("emmastyle")
# Result: False (new lead)
```

#### 4. Research Phase

```python
from api_clients.perplexity_client import PerplexityClient

perplexity = PerplexityClient()
research = perplexity.research_lead(
    name="Emma Johnson",
    handle="emmastyle",
    platform="instagram"
)
```

**Perplexity Response:**
```
## Emma Johnson (@emmastyle)

**Niche:** Fashion & Sustainable Style
**Followers:** 85,000
**Engagement Rate:** 4.2%
**Location:** Los Angeles, CA

**Recent Activity:**
- Partnership with Reformation (sustainable fashion)
- Featured in Vogue's "Influencers to Watch 2026"
- Launched capsule collection with Everlane

**Brand Partnerships:**
- Reformation, Everlane, Girlfriend Collective
- Focus on sustainable/eco-friendly brands

**Content Style:**
- Minimalist aesthetic
- Earth tones and neutral palette
- Mix of lifestyle and fashion content
```

#### 5. Vibe Check (Visual Analysis)

```python
from ai_models.gemini_client import GeminiClient

gemini = GeminiClient()
vibe = gemini.analyze_creator_profile("https://instagram.com/emmastyle")
```

**Gemini Response:**
```
## Visual Analysis

**Aesthetic Score:** 92/100
**Brand Fit Score:** 87/100

**Visual Themes:**
- Clean, minimalist compositions
- Natural lighting preference
- Consistent earth-tone color palette
- High production quality

**Content Categories:**
- 60% Fashion (outfit posts)
- 25% Lifestyle (home, travel)
- 15% Sustainability education

**Recommendation:** Excellent fit for premium lifestyle brands
```

#### 6. Email Discovery

```python
from api_clients.findymail_client import FindymailClient

findymail = FindymailClient()
email = findymail.find_email(
    name="Emma Johnson",
    domain="emmastyle.com"  # Found from research
)
```

**Result:**
```json
{
  "email": "emma@emmastyle.com",
  "confidence": 98,
  "verified": true
}
```

#### 7. Content Generation

```python
from ai_models.openai_client import OpenAIClient

openai = OpenAIClient()
message = openai.generate_outreach(
    lead=lead,
    research=research,
    vibe=vibe_analysis
)
```

**Generated Email:**
```
Subject: Loved your Reformation collab 🌿

Hi Emma,

I came across your recent partnership with Reformation and was genuinely 
impressed by how authentically you integrated their sustainable message 
into your content. Your minimalist aesthetic perfectly complements the 
eco-conscious fashion space.

I'm reaching out from [Brand] - we're launching a new sustainable 
loungewear line and immediately thought of you when planning our 
creator partnerships.

Would you be open to a quick chat about a potential collaboration? 
I think your audience would genuinely love what we're building.

Best,
[Name]
```

#### 8. Campaign Addition

```python
from api_clients.smartlead_client import SmartleadClient

smartlead = SmartleadClient()
smartlead.add_to_campaign(
    email="emma@emmastyle.com",
    first_name="Emma",
    custom_fields={
        "personalized_intro": message,
        "instagram_handle": "@emmastyle"
    }
)
```

#### 9. Status Update

Google Sheets row updated:

| name | handle | platform | email | status | vibe_score | processed_at |
|------|--------|----------|-------|--------|------------|--------------|
| Emma Johnson | @emmastyle | instagram | emma@emmastyle.com | completed | 87 | 2026-01-07T20:15:00Z |

#### 10. Vector Storage

```python
pinecone.store_lead(
    handle="emmastyle",
    metadata={
        "name": "Emma Johnson",
        "email": "emma@emmastyle.com",
        "vibe_score": 87
    }
)
```

---

## 💬 Scenario 2: Slack Instagram URL

**Trigger:** User pastes Instagram URL in Slack channel

### Step-by-Step Flow

#### 1. User Action

In Slack channel `#lead-intake`:
```
User: https://instagram.com/techbro_mike
```

#### 2. Bot Detection

```python
# slack_bot/handlers.py
import re

def extract_instagram_handle(text):
    patterns = [
        r'instagram\.com/([a-zA-Z0-9_.]+)',
        r'@([a-zA-Z0-9_.]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

handle = extract_instagram_handle("https://instagram.com/techbro_mike")
# Result: "techbro_mike"
```

#### 3. Immediate Response

Bot posts in channel:
```
🤖 APEX Bot:
✅ Lead detected: @techbro_mike
📋 Added to processing queue
⏳ Estimated completion: 2-3 minutes
```

#### 4. Lead Creation

```python
from models.lead import Lead

lead = Lead(
    handle="@techbro_mike",
    platform="instagram",
    source="slack"
)
```

#### 5. Processing (Same as Scenario 1)

- Dedup check ✓
- Research via Perplexity ✓
- Vibe check via Gemini ✓
- Email discovery via Findymail ✓
- Content generation via GPT ✓
- Campaign addition via Smartlead ✓

#### 6. Completion Notification

Bot posts update:
```
🤖 APEX Bot:
✅ Lead processed: @techbro_mike

📧 Email: mike@techbromike.com
📊 Vibe Score: 72/100
🎯 Niche: Tech Reviews & Gadgets

📝 Research Summary:
Tech reviewer with 45K followers. Focus on consumer 
electronics and productivity tools. Previous partnerships 
with Anker, Logitech, and Notion.

📤 Status: Added to Smartlead campaign

[View in Sheet] [View Full Research]
```

#### 7. Sheet Updated

Row automatically added to Google Sheets:

| name | handle | platform | email | status | source |
|------|--------|----------|-------|--------|--------|
| Mike Chen | @techbro_mike | instagram | mike@techbromike.com | completed | slack |

---

## 📦 Scenario 3: Bulk CSV Import

**Trigger:** User runs import script with CSV file

### Step-by-Step Flow

#### 1. CSV File (`leads_import.csv`)

```csv
name,handle,platform,bio
Sarah Kim,@sarahkbeauty,instagram,Beauty and skincare
Alex Rivera,@alexfitness,instagram,Fitness coach
Jordan Lee,@jordancooks,instagram,Food blogger
```

#### 2. Import Command

```bash
python scripts/import_leads.py --file leads_import.csv --batch-size 10
```

#### 3. Import Script Logic

```python
# scripts/import_leads.py
import csv
from api_clients.google_sheets_client import GoogleSheetsClient

def import_csv_to_sheets(file_path, batch_size=10):
    client = GoogleSheetsClient()
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"Importing {len(leads)} leads...")
    
    for i in range(0, len(leads), batch_size):
        batch = leads[i:i+batch_size]
        client.append_leads(batch)
        print(f"Imported batch {i//batch_size + 1}")
    
    print("Import complete!")
```

#### 4. Processing Queue

All leads added to Google Sheets with `status: pending`

| name | handle | platform | bio | status |
|------|--------|----------|-----|--------|
| Sarah Kim | @sarahkbeauty | instagram | Beauty and skincare | pending |
| Alex Rivera | @alexfitness | instagram | Fitness coach | pending |
| Jordan Lee | @jordancooks | instagram | Food blogger | pending |

#### 5. Batch Processing

System processes leads sequentially:
```
[20:00:00] Processing @sarahkbeauty...
[20:02:15] ✅ @sarahkbeauty completed (vibe: 89)
[20:02:16] Processing @alexfitness...
[20:04:30] ✅ @alexfitness completed (vibe: 76)
[20:04:31] Processing @jordancooks...
[20:06:45] ✅ @jordancooks completed (vibe: 82)
```

---

## 🔄 Scenario 4: Duplicate Detection

**Trigger:** User adds lead that was already processed

### Step-by-Step Flow

#### 1. User Adds Lead

| name | handle | platform |
|------|--------|----------|
| Emma Johnson | @emmastyle | instagram |

(Same lead from Scenario 1)

#### 2. Dedup Check

```python
from api_clients.pinecone_client import PineconeClient

pinecone = PineconeClient()
result = pinecone.check_duplicate("emmastyle")
```

**Query Result:**
```json
{
  "matches": [
    {
      "id": "lead_emmastyle_instagram",
      "score": 0.99,
      "metadata": {
        "handle": "@emmastyle",
        "email": "emma@emmastyle.com",
        "processed_at": "2026-01-07T20:15:00Z"
      }
    }
  ]
}
```

#### 3. Skip Decision

```python
if result["matches"] and result["matches"][0]["score"] > 0.9:
    # High similarity = duplicate
    lead.status = "skipped"
    lead.error_message = "Duplicate: Already contacted on 2026-01-07"
```

#### 4. Status Update

| name | handle | status | error |
|------|--------|--------|-------|
| Emma Johnson | @emmastyle | skipped | Duplicate: Already contacted on 2026-01-07 |

#### 5. Notification (if Slack)

```
🤖 APEX Bot:
⚠️ Duplicate detected: @emmastyle
📅 Previously contacted: January 7, 2026
📧 Email on file: emma@emmastyle.com
❌ Skipping to avoid double outreach
```

---

## 🔀 Scenario 5: LinkedIn Fallback

**Trigger:** Email not found via Findymail

### Step-by-Step Flow

#### 1. Lead Input

| name | handle | platform | linkedin |
|------|--------|----------|----------|
| David Park | @davidparkdesign | instagram | linkedin.com/in/davidpark |

#### 2. Email Discovery Attempt

```python
from api_clients.findymail_client import FindymailClient

findymail = FindymailClient()
result = findymail.find_email(
    name="David Park",
    domain="davidparkdesign.com"
)
```

**Result:**
```json
{
  "email": null,
  "confidence": 0,
  "verified": false,
  "message": "No verified email found"
}
```

#### 3. LinkedIn Fallback

```python
# Check if LinkedIn URL available
if lead.linkedin_url and not email_found:
    from api_clients.unipile_client import UnipileClient
    
    unipile = UnipileClient()
    
    # Option A: Try to get email from LinkedIn
    linkedin_data = unipile.get_profile_data(lead.linkedin_url)
    
    # Option B: Send LinkedIn DM instead
    if not linkedin_data.get("email"):
        message = generate_linkedin_message(lead)
        unipile.send_dm(
            recipient_url=lead.linkedin_url,
            message=message
        )
        lead.outreach_channel = "linkedin"
```

#### 4. LinkedIn DM Sent

```python
dm_result = unipile.send_dm(
    recipient_url="https://linkedin.com/in/davidpark",
    message="""
Hi David,

I came across your design work and was really impressed by your 
portfolio. Your minimalist approach to UI design caught my eye.

I'm reaching out because we're looking for design collaborators 
for an upcoming project. Would you be open to connecting?

Best,
[Name]
"""
)
```

#### 5. Status Update

| name | handle | email | outreach_channel | status |
|------|--------|-------|------------------|--------|
| David Park | @davidparkdesign | | linkedin | outreach_sent |

---

## 🔧 Scenario 6: Error Recovery

**Trigger:** API failure during processing

### Step-by-Step Flow

#### 1. Processing Starts

```python
lead = Lead(handle="@newcreator", name="New Creator")
lead.status = "researching"
```

#### 2. API Error Occurs

```python
from api_clients.perplexity_client import PerplexityClient

try:
    perplexity = PerplexityClient()
    research = perplexity.research_lead(lead.handle)
except Exception as e:
    # Error: Rate limit exceeded
    logger.error(f"Perplexity API error: {e}")
```

#### 3. Exponential Backoff Retry

```python
from utils.retry import exponential_backoff_retry

@exponential_backoff_retry(max_attempts=3, exceptions=(APIError,))
def research_with_retry(handle):
    return perplexity.research_lead(handle)

# Attempt 1: Fails (wait 2s)
# Attempt 2: Fails (wait 4s)
# Attempt 3: Succeeds!
```

#### 4. If All Retries Fail

```python
if all_retries_failed:
    lead.status = "error"
    lead.error_message = "Perplexity API: Rate limit exceeded after 3 attempts"
    
    # Save partial progress
    save_lead_state(lead)
    
    # Queue for later retry
    add_to_retry_queue(lead, retry_after=300)  # 5 minutes
```

#### 5. Status Update

| name | handle | status | error |
|------|--------|--------|-------|
| New Creator | @newcreator | error | Perplexity API: Rate limit exceeded |

#### 6. Automatic Retry (Later)

```python
# Scheduler checks retry queue every 5 minutes
def process_retry_queue():
    retry_leads = get_retry_queue()
    for lead in retry_leads:
        if lead.retry_after < now():
            process_lead(lead)  # Try again
```

---

## 📊 Scenario Summary

| Scenario | Trigger | Key Steps | Outcome |
|----------|---------|-----------|---------|
| **1. Sheets Lead** | Manual row add | Full pipeline | Email campaign |
| **2. Slack URL** | Paste URL | Auto-detect + process | Campaign + notification |
| **3. Bulk Import** | CSV upload | Batch processing | Multiple campaigns |
| **4. Duplicate** | Repeat lead | Pinecone check | Skip + notify |
| **5. LinkedIn Fallback** | No email found | DM via Unipile | LinkedIn outreach |
| **6. Error Recovery** | API failure | Retry + queue | Delayed processing |

---

## 🚀 Quick Reference

### Start Processing Manually

```bash
# Process all pending leads now
python run.py

# Process specific lead
python -c "from main import process_single_lead; process_single_lead('@username')"
```

### Check Lead Status

```bash
# Via API
python -c "
from api_clients.google_sheets_client import GoogleSheetsClient
client = GoogleSheetsClient()
leads = client.get_leads_from_sheet()
for lead in leads:
    print(f\"{lead['handle']}: {lead.get('status', 'pending')}\")
"
```

### Force Reprocess Lead

```bash
# Clear from Pinecone and reprocess
python -c "
from api_clients.pinecone_client import PineconeClient
pc = PineconeClient()
pc.delete_lead('username')
"
```

---

*Scenarios version: 1.0.0 | Last updated: January 2026*

