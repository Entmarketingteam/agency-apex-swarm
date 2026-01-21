# 🔧 Next Fixes Needed

## Issue 1: Google Sheet URL in Slack Messages

**Problem:** URL showing as broken `/edit/edit` instead of correct URL

**Root Cause:** 
- Code has fallback, but `GOOGLE_SHEET_ID` might not be set in Railway
- Need to verify environment variable is correctly set

**Fix:**
1. Verify `GOOGLE_SHEET_ID` is set in Railway environment variables
2. Add better logging to see what value is being used
3. Ensure fallback works correctly

**Location:** `slack_bot/handlers.py` line 307-308

---

## Issue 2: Research/Vibe Score Not Showing

**Problem:** Completion messages showing "No research available" and "N/A" for vibe score

**Root Cause:**
- Research data structure: `result["steps"]["research"]` contains `{"content": ..., "citations": ...}` not `{"summary": ...}`
- Handler is looking for `summary` but should look for `content`
- Vibe score extraction looks correct, but may need better error handling

**Fix:**
1. Update handler to extract `content` instead of `summary` for research
2. Add better error handling and logging
3. Ensure data is being passed correctly from orchestrator

**Location:** `slack_bot/handlers.py` line 279-280

---

## Issue 3: Missing `find_from_handle` Method

**Problem:** `FindymailClient` doesn't have `find_from_handle()` method that's being called

**Root Cause:**
- `main.py` calls `self.findymail.find_from_handle()` but method doesn't exist
- Need to implement this method or use existing method

**Fix:**
1. Implement `find_from_handle()` in `FindymailClient`
2. Or update `main.py` to use existing method

**Location:** `api_clients/findymail_client.py` and `main.py` line 169

---

## Testing Plan

1. **Verify Environment Variables:**
   - Check Railway dashboard for `GOOGLE_SHEET_ID`
   - Should be: `1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew`

2. **Test with Real Instagram URL:**
   - Paste URL in Slack channel
   - Verify completion message shows:
     - ✅ Correct Google Sheet URL
     - ✅ Email address (or "Not found")
     - ✅ Vibe score (0-100)
     - ✅ Research summary (first 200 chars)

3. **Check Railway Logs:**
   - Look for any errors during processing
   - Verify all steps complete successfully

---

## Priority Order

1. **HIGH:** Fix `find_from_handle` method (blocks processing)
2. **HIGH:** Fix research data extraction (shows wrong data)
3. **MEDIUM:** Fix Google Sheet URL (cosmetic but important)
4. **LOW:** Add better logging for debugging
