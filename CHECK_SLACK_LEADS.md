# 🔍 Checking Your Slack Leads

## Leads You Pasted

1. `https://www.instagram.com/nicki.entenmann/`
2. `https://www.instagram.com/lorenmattingly/`

---

## ✅ What Should Happen

### In Slack:
1. **Bot should detect the URLs** immediately
2. **Bot should respond** with acknowledgment messages like:
   ```
   ✅ Lead detected: @nicki.entenmann
   📋 Added to processing queue
   ⏳ Estimated completion: 2-3 minutes
   ```

3. **After 2-3 minutes**, bot should send completion messages with:
   - Email found (if discovered)
   - Vibe score
   - Research summary
   - Outreach status

### In Google Sheet:
1. **If leads exist in your sheet**, they should be updated with:
   - Status: `completed` / `failed` / `skipped`
   - Email: (if found)
   - Vibe Score: (0-100)
   - Research: (summary)

---

## 🔍 How to Check

### 1. Check Slack Channel
- Look for bot responses in your channel
- Check if bot acknowledged the leads
- Look for completion messages

### 2. Check Railway Logs
1. Go to: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. Click your service: `agency-apex-swarm`
3. Click **Deployments** → **Latest** → **Logs**
4. Look for:
   - `Processing Instagram handle(s)`
   - `Processing lead: @nicki.entenmann`
   - `Processing lead: @lorenmattingly`
   - `Updated lead` messages

### 3. Check Google Sheet
1. Open your Google Sheet
2. Search for handles: `nicki.entenmann` and `lorenmattingly`
3. Check if status updated
4. Check if email, vibe score, research populated

---

## 🐛 Troubleshooting

### Bot Not Responding?

**Possible Issues:**
1. **Bot not in channel** - Invite bot: `/invite @APEX Lead Bot`
2. **Wrong channel** - Bot only works in channel `C0A7Y1UFLA0`
3. **Bot not running** - Check Railway logs for errors
4. **Tokens missing** - Verify all 3 Slack tokens in Railway

**Check:**
- Is bot online in Slack?
- Are you in the correct channel?
- Check Railway logs for errors

### Bot Responding But Not Processing?

**Check Railway Logs:**
- Look for error messages
- Check if APIs are working
- Verify API keys are set

### Processing But No Results in Sheet?

**Possible Issues:**
1. **Leads not in sheet** - Bot processes but can't update if lead doesn't exist
2. **Handle mismatch** - Handle in sheet must match exactly
3. **Column names** - Check if status/email columns exist

---

## 📋 What to Look For in Logs

### Successful Processing:
```
Processing Instagram handle(s)
Processing lead: @nicki.entenmann
Step 1: Research & Validation
Step 2: Visual Vibe Check
Step 3: Contact Discovery
Step 4: Duplicate Check
Step 5: Content Generation
Step 6: Outreach Execution
Lead processing completed: @nicki.entenmann
Updated lead nicki.entenmann: status=completed
```

### Errors to Watch For:
```
Error processing lead
API error
Could not find row for handle
Failed to update sheet
```

---

## ✅ Next Steps

1. **Check Slack** - Did bot respond?
2. **Check Railway Logs** - Are leads processing?
3. **Check Google Sheet** - Are results updating?
4. **Report back** - Let me know what you see!

---

## 🆘 If Something's Wrong

Tell me:
- ✅ Did bot respond in Slack?
- ✅ What do Railway logs show?
- ✅ Are leads in your Google Sheet?
- ✅ Any error messages?

I can help debug from there!
