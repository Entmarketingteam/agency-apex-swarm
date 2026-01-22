# Quick Start Guide

## System Overview

The Agency Apex Swarm is a complete lead generation orchestration system that:
- Researches leads using Perplexity
- Performs visual vibe checks with Gemini 3.0 Ultra
- Discovers contact information via Findymail
- Checks for duplicates using Pinecone
- Generates persuasive content with GPT-5.2 Pro
- Executes outreach via Smartlead (email) and Unipile (LinkedIn DMs)

## Quick Start

### 1. Verify Configuration

```bash
python test_system.py
```

This will:
- Check all API keys are configured
- Test the system with a sample lead
- Show you the complete workflow

### 2. Process a Single Lead

```python
from main import LeadGenerationOrchestrator
from models.lead import Lead

# Create orchestrator
orchestrator = LeadGenerationOrchestrator()

# Create a lead
lead = Lead(
    name="Creator Name",
    handle="creator_handle",
    platform="instagram",
    bio="Creator bio here"
)

# Process the lead
result = orchestrator.process_lead(lead)
print(f"Status: {result['status']}")
```

### 3. Process a Batch of Leads

```python
from main import LeadGenerationOrchestrator
from models.lead import Lead

orchestrator = LeadGenerationOrchestrator()

leads = [
    Lead(name="Creator 1", handle="creator1", platform="instagram"),
    Lead(name="Creator 2", handle="creator2", platform="tiktok"),
    # ... more leads
]

results = orchestrator.process_batch(leads)
```

## Workflow Steps

1. **Research** - Uses Perplexity to gather information about the creator
2. **Vibe Check** - Uses Gemini 3.0 Ultra to analyze visual content (Instagram/TikTok)
3. **Contact Discovery** - Uses Findymail to find email addresses
4. **Duplicate Check** - Uses Pinecone to check if we've contacted this lead before
5. **Content Generation** - Uses GPT-5.2 Pro to write personalized emails/DMs
6. **Outreach** - Sends emails via Smartlead and LinkedIn DMs via Unipile
7. **Storage** - Stores lead in Pinecone for future deduplication

## Configuration

All API keys are loaded from `.env` file. Make sure you have:
- ✅ All keys configured (see `utils/config.py` for list)
- ✅ `.env` file in project root
- ✅ Dependencies installed (`pip install -r requirements.txt`)

## Logs

Logs are written to:
- Console (INFO level and above)
- `logs/apex_swarm_YYYYMMDD.log` (DEBUG level and above)

## Next Steps

1. Test with a real lead
2. Monitor logs for any API errors
3. Adjust vibe check thresholds if needed
4. Scale to 400 leads/day by processing batches

## Troubleshooting

### API Errors
- Check API keys in `.env`
- Verify API quotas/limits
- Check logs for specific error messages

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Pinecone Index Issues
- The system auto-creates the index on first run
- Ensure Pinecone API key has proper permissions

## Architecture

See `DOCS/IMPLEMENTATION_PLAN.md` for detailed architecture documentation.


