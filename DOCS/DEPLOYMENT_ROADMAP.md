# Deployment Roadmap: From Code to Production

## Current Status: ✅ Code Complete, ⚠️ Not Yet Deployed

### What's DONE ✅
- [x] Complete codebase structure
- [x] All API client wrappers
- [x] AI model integrations
- [x] Error handling and retry logic
- [x] Data models and schemas
- [x] Main orchestration workflow
- [x] Configuration management
- [x] Logging system
- [x] Dependencies defined

### What's NOT DONE ⚠️
- [ ] API endpoint verification (may need adjustments)
- [ ] Real API testing with actual credentials
- [ ] Lead input mechanism (how leads enter the system)
- [ ] Hosting/deployment infrastructure
- [ ] Scheduled execution (cron/job queue)
- [ ] Results storage/database
- [ ] Monitoring and alerts
- [ ] Web dashboard (optional but recommended)

---

## Step-by-Step Deployment Plan

### PHASE 1: API Verification & Testing (2-4 hours)

#### 1.1 Verify API Endpoints
**Status:** ⚠️ CRITICAL - APIs may have changed

Each API client needs verification against actual documentation:

- [ ] **Perplexity API** - Verify endpoint, headers, request format
  - Check: https://docs.perplexity.ai/
  - May need to adjust: `api_clients/perplexity_client.py`

- [ ] **Findymail API** - Verify endpoint structure
  - Check: https://docs.findymail.ai/ (or their API docs)
  - May need to adjust: `api_clients/findymail_client.py`

- [ ] **Unipile API** - Verify LinkedIn DM endpoint
  - Check: https://docs.unipile.com/ (or their API docs)
  - May need to adjust: `api_clients/unipile_client.py`

- [ ] **Smartlead API** - Verify campaign creation
  - Check: https://help.smartlead.ai/API-Documentation-a0d223bdd3154a77b3735497aad9419f
  - May need to adjust: `api_clients/smartlead_client.py`

- [ ] **Pinecone API** - Verify index creation and operations
  - Check: https://docs.pinecone.io/
  - May need to adjust: `api_clients/pinecone_client.py`

#### 1.2 Test Each API Individually
Create test scripts for each API:

```python
# test_apis.py
# Test each API client with a simple call
# Verify responses match expected format
```

#### 1.3 Fix API Integration Issues
- Update endpoints if wrong
- Fix authentication if incorrect
- Adjust request/response parsing

**Estimated Time:** 2-4 hours

---

### PHASE 2: Lead Input System (4-8 hours)

#### 2.1 Define Lead Sources
How will leads enter the system?

**Option A: CSV/JSON File Input**
- [ ] Create `scripts/import_leads.py`
- [ ] Accept CSV with columns: name, handle, platform, bio, etc.
- [ ] Validate and convert to Lead objects

**Option B: Database Input**
- [ ] Set up database (PostgreSQL/SQLite)
- [ ] Create leads table
- [ ] Create `scripts/fetch_leads.py` to pull from DB

**Option C: API Endpoint**
- [ ] Create FastAPI/Flask endpoint
- [ ] Accept POST requests with lead data
- [ ] Queue leads for processing

**Option D: Manual Entry Script**
- [ ] Create interactive script
- [ ] Prompt for lead details
- [ ] Process immediately

**Recommended:** Start with Option A (CSV), add Option C later

#### 2.2 Build Lead Import Script
```python
# scripts/import_leads.py
import csv
from models.lead import Lead
from main import LeadGenerationOrchestrator

def import_from_csv(filepath):
    leads = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            lead = Lead(
                name=row['name'],
                handle=row['handle'],
                platform=row['platform'],
                bio=row.get('bio', '')
            )
            leads.append(lead)
    return leads
```

**Estimated Time:** 2-4 hours

---

### PHASE 3: Hosting & Deployment (4-8 hours)

#### 3.1 Choose Hosting Platform

**Option A: GitHub Codespaces (Current)**
- ✅ Already set up
- ✅ Free for personal use
- ❌ Not ideal for 24/7 operation
- ❌ Limited to Codespace uptime

**Option B: AWS/GCP/Azure**
- [ ] Set up EC2/Compute Engine/VM
- [ ] Install Python 3.11
- [ ] Clone repository
- [ ] Set up environment variables
- [ ] Install dependencies
- **Cost:** ~$10-50/month

**Option C: Railway/Render/Fly.io**
- [ ] Create account
- [ ] Connect GitHub repo
- [ ] Configure environment variables
- [ ] Deploy
- **Cost:** ~$5-20/month

**Option D: Docker + Any Cloud**
- [ ] Create Dockerfile
- [ ] Build container
- [ ] Deploy to container service
- **Cost:** Varies

**Recommended:** Start with Option C (Railway/Render) for simplicity

#### 3.2 Create Deployment Configuration

**If using Railway/Render:**
```yaml
# railway.json or render.yaml
# Define how to run the application
```

**If using Docker:**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**If using traditional server:**
- [ ] Set up systemd service
- [ ] Configure auto-restart
- [ ] Set up log rotation

**Estimated Time:** 4-8 hours

---

### PHASE 4: Scheduling & Automation (2-4 hours)

#### 4.1 Choose Scheduling Method

**Option A: Cron Job (Linux/Mac)**
```bash
# Run every hour
0 * * * * cd /path/to/project && python main.py --batch
```

**Option B: Python Schedule Library**
```python
# scheduler.py
import schedule
import time
from main import LeadGenerationOrchestrator

def process_pending_leads():
    # Fetch leads from source
    # Process batch
    pass

schedule.every().hour.do(process_pending_leads)
```

**Option C: Celery + Redis (Advanced)**
- [ ] Set up Redis
- [ ] Configure Celery workers
- [ ] Create task queue
- [ ] Process leads asynchronously

**Option D: GitHub Actions (Free)**
```yaml
# .github/workflows/process-leads.yml
# Run on schedule
```

**Recommended:** Start with Option B (Python schedule), upgrade to Celery later

#### 4.2 Build Scheduler Script
```python
# scheduler.py
import schedule
import time
from scripts.import_leads import import_from_csv
from main import LeadGenerationOrchestrator

def job():
    # Import leads from CSV
    leads = import_from_csv('leads/queue.csv')
    
    # Process batch (max 10 at a time for rate limiting)
    orchestrator = LeadGenerationOrchestrator()
    results = orchestrator.process_batch(leads[:10])
    
    # Log results
    # Move processed leads to archive

# Schedule: Process 10 leads every hour = 240 leads/day
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Estimated Time:** 2-4 hours

---

### PHASE 5: Results Storage (4-8 hours)

#### 5.1 Choose Storage Method

**Option A: JSON Files**
- [ ] Create `results/` directory
- [ ] Save results as JSON
- [ ] Simple but not scalable

**Option B: SQLite Database**
- [ ] Create `database.py`
- [ ] Define schema
- [ ] Store leads, results, outreach history
- **Recommended for start**

**Option C: PostgreSQL/MySQL**
- [ ] Set up database
- [ ] Create tables
- [ ] Store all data
- **Recommended for scale**

**Option D: Supabase (You have API key)**
- [ ] Use Supabase for storage
- [ ] Leverage existing API key
- [ ] Built-in API access

**Recommended:** Start with Option B (SQLite), migrate to Supabase later

#### 5.2 Build Storage Module
```python
# storage/database.py
import sqlite3
from datetime import datetime

class LeadDatabase:
    def __init__(self, db_path='leads.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        # Create leads, results, outreach_history tables
        pass
    
    def save_lead_result(self, lead, result):
        # Store processing result
        pass
    
    def get_processed_leads(self):
        # Get list of processed leads
        pass
```

**Estimated Time:** 4-8 hours

---

### PHASE 6: Monitoring & Alerts (2-4 hours)

#### 6.1 Set Up Monitoring

- [ ] Error tracking (Sentry or similar)
- [ ] Success/failure metrics
- [ ] API usage tracking
- [ ] Cost monitoring

#### 6.2 Create Dashboard (Optional)

- [ ] Simple web dashboard
- [ ] Show processing stats
- [ ] Display recent results
- [ ] Manual trigger for processing

**Estimated Time:** 2-4 hours

---

### PHASE 7: Testing & Optimization (Ongoing)

#### 7.1 End-to-End Testing

- [ ] Test with 1 real lead
- [ ] Test with 10 leads
- [ ] Test with 100 leads
- [ ] Monitor for errors
- [ ] Optimize API calls
- [ ] Adjust rate limiting

#### 7.2 Scale to 400 Leads/Day

- [ ] Calculate processing time per lead
- [ ] Determine batch size
- [ ] Set appropriate schedule
- [ ] Monitor API rate limits
- [ ] Optimize for cost

**Estimated Time:** Ongoing

---

## Quick Start: Minimum Viable Deployment

### Fastest Path to Working System (8-12 hours)

1. **Verify APIs** (2 hours)
   - Test each API client with real credentials
   - Fix any endpoint/auth issues

2. **Create CSV Import** (1 hour)
   - Build simple CSV import script
   - Test with sample leads

3. **Deploy to Railway/Render** (2 hours)
   - Sign up for account
   - Connect GitHub repo
   - Set environment variables
   - Deploy

4. **Add Scheduler** (2 hours)
   - Create scheduler script
   - Process leads from CSV
   - Run continuously

5. **Add SQLite Storage** (2 hours)
   - Create database module
   - Store results
   - Query processed leads

6. **Test End-to-End** (1 hour)
   - Process 5-10 real leads
   - Verify all steps work
   - Check logs for errors

**Total: 8-12 hours to working system**

---

## Critical Next Steps (Do These First)

### 1. API Verification Script
Create a script to test each API:

```python
# scripts/verify_apis.py
# Test each API with a simple call
# Print success/failure for each
```

### 2. Real Lead Test
Process one real lead end-to-end to find issues

### 3. Choose Hosting
Decide on hosting platform and set it up

### 4. Build Lead Input
Create mechanism to get leads into the system

---

## Cost Estimates

### Monthly Costs (400 leads/day)

- **Hosting:** $5-20/month (Railway/Render)
- **API Costs:**
  - Perplexity: ~$20-50/month
  - OpenAI (GPT-4): ~$50-100/month
  - Anthropic (Claude): ~$50-100/month
  - Google (Gemini): ~$20-50/month
  - Findymail: Check pricing
  - Unipile: Check pricing
  - Smartlead: Check pricing
  - Pinecone: Free tier or ~$10/month

**Total Estimated:** $200-400/month

---

## Questions to Answer

1. **Where will leads come from?** (CSV, database, API, manual?)
2. **Where will this run?** (Codespace, cloud server, local?)
3. **How often to process?** (Continuous, hourly, daily?)
4. **Where to store results?** (Files, database, Supabase?)
5. **Need a dashboard?** (Yes/No - affects complexity)

---

## Summary

**What's Done:** ✅ Complete codebase, all integrations, workflow logic

**What's Needed:**
1. ⚠️ Verify API endpoints (may need adjustments)
2. ⚠️ Build lead input mechanism
3. ⚠️ Deploy to hosting platform
4. ⚠️ Set up scheduling
5. ⚠️ Add results storage
6. ⚠️ Test with real leads

**Time to Working System:** 8-12 hours of focused work

**Time to Production-Ready:** 20-30 hours total

