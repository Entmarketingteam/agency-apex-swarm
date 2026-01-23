# Common Issues & Solutions

## Instagram Bio Extraction

### Problem
Instagram bio text, emails, and contact information are not being extracted from creator profiles.

### Solution
The system now uses Perplexity to extract Instagram bio data. The `get_instagram_bio()` method:
- Queries Perplexity for the exact bio text with improved query format
- Uses multiple regex patterns to extract bio text reliably
- Extracts email addresses mentioned in the bio
- Gets follower count and profile information
- Populates the `bio` field in the Lead model
- **Email found in bio is now prioritized** over Findymail results

**How it works:**
1. When a lead is processed, if platform is "instagram", the system calls `perplexity.get_instagram_bio(handle)`
2. Bio data is extracted using improved regex patterns (handles multiple formats)
3. The lead's `bio` field is updated automatically
4. **Email found in bio is used directly** (no need for Findymail if email is in bio)
5. Bio is saved to Google Sheets during processing
6. Research data includes bio_data for reference

**Recent Improvements (Jan 2026):**
- ✅ Enhanced Perplexity query for better bio extraction
- ✅ Multiple regex patterns for robust parsing
- ✅ Bio field now saved to Google Sheets
- ✅ Email from bio prioritized in contact discovery
- ✅ Better logging for debugging extraction issues

**Status:** ✅ Fixed and improved in latest version

---

## Slack Leads Not Appearing in Google Sheet

### Problem
Leads submitted via Slack were not being added to the Google Sheet.

### Solution
The `append_lead()` method was commented out. It's now enabled and working.

**What was fixed:**
1. ✅ `append_lead()` method added to `GoogleSheetsClient`
2. ✅ Enabled in `slack_bot/handlers.py` 
3. ✅ Leads now added immediately with status "pending"
4. ✅ Sheet updated after processing completes

**Status:** ✅ Fixed

---

## Google Sheets API Errors

### Error: "API key expired"
**Solution:** Get a new Google Cloud API key and enable Google Sheets API

### Error: "Google Sheets API has not been used"
**Solution:** Enable the API at: https://console.cloud.google.com/apis/library/sheets.googleapis.com

### Error: "This operation is not supported for this document"
**Solution:** The sheet must be a native Google Sheet, not an uploaded Excel file. Convert it to Google Sheets format.

---

## Slack Bot Not Responding

### Problem
Bot doesn't respond to messages in Slack channel.

### Solutions
1. **Check channel restriction:** Bot only responds in `SLACK_CHANNEL_ID` if set
2. **Verify tokens:** Ensure `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are correct
3. **Check Socket Mode:** App must have Socket Mode enabled with `connections:write` scope
4. **Event subscriptions:** Ensure `message.channels` and `app_mention` are subscribed

---

## Pinecone Embedding Errors

### Error: "vector: invalid value for type TYPE_FLOAT"
**Problem:** Passing string instead of embedding vector to Pinecone.

**Solution:** Always generate embedding first:
```python
embedding = openai.generate_embedding(lead_text)
duplicate_id = pinecone.check_duplicate(embedding, threshold=0.95)
```

**Status:** ✅ Fixed

---

## Missing Research Data in Slack

### Problem
Slack completion message shows "Not found" for email, "N/A" for vibe score, "No research available".

### Solution
Data extraction was looking in wrong place. Fixed to extract from nested `result["steps"]` structure:
- `result["steps"]["contact_discovery"]["email"]`
- `result["steps"]["vibe_check"]["score"]`
- `result["steps"]["research"]["content"]`

**Status:** ✅ Fixed

---

## Railway Deployment Issues

### Problem
Deployment fails or service doesn't start.

### Solutions
1. **Check Procfile:** Must have `web: python run.py`
2. **Verify environment variables:** All required keys must be set
3. **Check logs:** Railway dashboard → Deployments → View logs
4. **Port binding:** Service must bind to `$PORT` environment variable

---

## Email Discovery Not Working

### Problem
Findymail not finding emails for Instagram handles.

### Solutions
1. **Check API key:** Verify `FINDYMAIL_API_KEY` is set correctly
2. **Rate limits:** Findymail has 100 requests/minute limit
3. **Handle format:** Ensure handle is clean (no @, no URL)
4. **Try bio extraction:** System now also checks bio for email addresses

---

*For more help, check the [Debug Guide](DEBUG.md) or review logs in `logs/` directory.*
