# 🔐 Slack Tokens for Railway

## Tokens Ready to Add

All three Slack tokens have been obtained and are ready to be added to Railway:

### 1. Bot Token (xoxb-...)
```
SLACK_BOT_TOKEN=xoxb-6255452579572-10250746563831-ygNUIy78o5ex0DvjlLinG7ZY
```

### 2. Signing Secret
```
SLACK_SIGNING_SECRET=34abfce1954f64ddfa43bcc0fcdcf079
```

### 3. App Token (xapp-...) - For Socket Mode
```
SLACK_APP_TOKEN=xapp-1-A0A7XNCECBE-10269793755652-cac80fb35c7bf4046831898226769965720fae19ef7ba8df50bd104a7854a8e9
```

---

## How to Add to Railway

### Option 1: Railway Dashboard (Easiest)

1. Go to: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. Click on your service: **agency-apex-swarm**
3. Go to **Variables** tab
4. Click **+ New Variable** for each:
   - `SLACK_BOT_TOKEN` = `xoxb-6255452579572-10250746563831-ygNUIy78o5ex0DvjlLinG7ZY`
   - `SLACK_SIGNING_SECRET` = `34abfce1954f64ddfa43bcc0fcdcf079`
   - `SLACK_APP_TOKEN` = `xapp-1-A0A7XNCECBE-10269793755652-cac80fb35c7bf4046831898226769965720fae19ef7ba8df50bd104a7854a8e9`
5. Railway will automatically redeploy with the new variables

### Option 2: Railway CLI

If you have Railway CLI linked to your project:

```bash
railway variables --set "SLACK_BOT_TOKEN=xoxb-6255452579572-10250746563831-ygNUIy78o5ex0DvjlLinG7ZY"
railway variables --set "SLACK_SIGNING_SECRET=34abfce1954f64ddfa43bcc0fcdcf079"
railway variables --set "SLACK_APP_TOKEN=xapp-1-A0A7XNCECBE-10269793755652-cac80fb35c7bf4046831898226769965720fae19ef7ba8df50bd104a7854a8e9"
```

---

## Verification

After adding the tokens, the Slack bot should:
1. Connect via Socket Mode
2. Listen for Instagram URLs in Slack channels
3. Process leads when URLs are detected

---

## Next Steps

1. ✅ Add tokens to Railway (see above)
2. ✅ Deploy/restart the service
3. ✅ Test by pasting an Instagram URL in Slack
4. ✅ Bot should respond and process the lead

---

## Code Status

The Slack bot code is already implemented in:
- `slack_bot/app.py` - Main bot application
- `slack_bot/handlers.py` - Message handlers
- `slack_bot/instagram_parser.py` - URL extraction

The bot will automatically start when:
- All three tokens are set in Railway
- The service is running
- Socket Mode is enabled (✅ already done in Slack app config)
