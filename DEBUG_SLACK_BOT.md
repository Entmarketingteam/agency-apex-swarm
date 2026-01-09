# 🐛 Debugging Slack Bot - No Response

## Issue: Bot Not Responding in Slack

### Possible Causes:

1. **Bot Not Running**
   - Bot process crashed
   - Socket Mode not connected
   - Railway deployment issue

2. **Bot Not in Channel**
   - Bot needs to be invited to channel
   - Bot doesn't have permission

3. **Channel ID Mismatch**
   - Bot restricted to wrong channel
   - Channel ID in config doesn't match

4. **Message Handler Issue**
   - Event not being received
   - Handler error preventing response
   - URL parsing failing

5. **Socket Mode Connection**
   - App token invalid
   - Socket Mode not enabled
   - Connection dropped

---

## 🔍 Debugging Steps

### Step 1: Check Railway Logs

1. Go to Railway Dashboard
2. Click your service
3. Click **Deployments** → **Latest** → **Logs**
4. Look for:
   - `Starting Slack bot in Socket Mode...`
   - `Slack app configured successfully`
   - `Processing Instagram handle(s)`
   - Any error messages

**What to look for:**
- ✅ Bot started successfully
- ✅ Socket Mode connected
- ❌ Errors or crashes
- ❌ Connection failures

### Step 2: Verify Bot is in Channel

1. In Slack, go to your channel
2. Type: `/invite @APEX Lead Bot`
3. Or manually add bot to channel
4. Check if bot appears in member list

### Step 3: Check Channel ID

1. Verify channel ID in Railway:
   - Variable: `SLACK_CHANNEL_ID`
   - Should be: `C0A7Y1UFLA0`
2. Get current channel ID:
   - Right-click channel → Copy link
   - Extract ID from URL

### Step 4: Test Bot Connection

1. Try mentioning bot: `@APEX Lead Bot hello`
2. Bot should respond even without Instagram URL
3. If no response, bot isn't connected

### Step 5: Check Socket Mode

1. Go to Slack App Settings
2. Check **Socket Mode** is enabled
3. Verify App Token exists and is valid
4. Check token in Railway: `SLACK_APP_TOKEN`

---

## 🛠️ Quick Fixes

### Fix 1: Restart Bot

1. Go to Railway
2. Click **Deployments**
3. Click **Redeploy** or **Restart**

### Fix 2: Re-invite Bot

1. In Slack channel
2. Type: `/invite @APEX Lead Bot`
3. Or: `/kick @APEX Lead Bot` then re-invite

### Fix 3: Check Channel ID

1. Verify `SLACK_CHANNEL_ID` in Railway
2. Should match your channel exactly
3. Update if wrong

### Fix 4: Verify Tokens

1. Check all 3 tokens in Railway:
   - `SLACK_BOT_TOKEN` (xoxb-...)
   - `SLACK_SIGNING_SECRET`
   - `SLACK_APP_TOKEN` (xapp-...)
2. Verify they're correct and not expired

---

## 📋 What to Check in Railway Logs

### Good Signs:
```
✅ Starting Slack bot in Socket Mode...
✅ Slack app configured successfully
✅ 🔒 Bot restricted to channel: C0A7Y1UFLA0
✅ Processing Instagram handle(s)
```

### Bad Signs:
```
❌ Failed to start Slack bot
❌ SLACK_BOT_TOKEN required
❌ SLACK_APP_TOKEN required for Socket Mode
❌ Error connecting to Slack
❌ Socket Mode connection failed
```

---

## 🆘 Next Steps

1. **Check Railway Logs** - What do you see?
2. **Verify Bot in Channel** - Is bot invited?
3. **Check Channel ID** - Is it correct?
4. **Test Mention** - Does `@APEX Lead Bot` work?

**Share what you find and I'll help fix it!**
