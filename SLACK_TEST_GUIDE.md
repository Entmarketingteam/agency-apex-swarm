# 🧪 Slack Bot Testing Guide

## ✅ Deployment Status

Your Slack bot has been successfully deployed to Railway with all tokens configured!

---

## 🚀 What's Running Now

The application is now running **two services simultaneously**:

1. **Slack Bot** 🤖
   - Listening for Instagram URLs in Slack channels
   - Processing leads in real-time
   - Running via Socket Mode

2. **Google Sheets Scheduler** 📊
   - Processing leads from Google Sheets every hour
   - Running automatically in the background

---

## 🧪 How to Test the Slack Bot

### Test 1: Paste Instagram URL

1. Go to any Slack channel where the bot is present
2. Paste an Instagram URL:
   ```
   https://instagram.com/username
   ```
3. The bot should:
   - Detect the URL
   - Respond with a confirmation message
   - Start processing the lead

### Test 2: Use Slash Command

1. In any channel, type:
   ```
   /apex https://instagram.com/username
   ```
2. The bot should process the lead

### Test 3: @ Mention the Bot

1. Type:
   ```
   @APEX Lead Bot check out https://instagram.com/username
   ```
2. The bot should respond and process the lead

---

## 📋 Expected Bot Responses

### When Lead is Detected:
```
✅ Lead detected: @username
📋 Added to processing queue
⏳ Estimated completion: 2-3 minutes
```

### When Lead is Processed:
```
✅ Lead processed: @username

📧 Email: user@example.com
📊 Vibe Score: 87/100 ✨

Research: Fashion & lifestyle creator with 150K followers...
Outreach: 📤 Added to Smartlead campaign
```

### If Duplicate:
```
⚠️ Duplicate detected: @username
📅 Previously contacted: January 7, 2026
❌ Skipping to avoid double outreach
```

---

## 🔍 Checking Railway Logs

To verify the bot is running correctly:

1. Go to Railway Dashboard
2. Click on your service: **agency-apex-swarm**
3. Click **Deployments** tab
4. Click on the latest deployment
5. View **Logs**

You should see:
```
🚀 Agency Apex Swarm - Starting
✅ All API keys configured
✅ Slack tokens configured - starting Slack bot
🤖 Slack bot thread started
Starting Slack bot in Socket Mode...
Slack app configured successfully
```

---

## 🐛 Troubleshooting

### Bot Not Responding?

1. **Check Railway Logs** - Look for errors
2. **Verify Tokens** - Ensure all 3 tokens are set in Railway
3. **Check Socket Mode** - Verify Socket Mode is enabled in Slack app settings
4. **Bot Installation** - Ensure bot is installed to your workspace

### Common Errors:

**"SLACK_BOT_TOKEN required"**
- Token not set in Railway environment variables
- Fix: Add `SLACK_BOT_TOKEN` to Railway Variables

**"SLACK_APP_TOKEN required for Socket Mode"**
- App token missing
- Fix: Add `SLACK_APP_TOKEN` to Railway Variables

**"Failed to start Slack bot"**
- Check Railway logs for detailed error
- Verify all tokens are correct

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Railway logs show "Starting Slack bot in Socket Mode..."
2. ✅ Railway logs show "Slack app configured successfully"
3. ✅ Bot appears online in Slack
4. ✅ Bot responds to test messages
5. ✅ Leads are processed and added to Google Sheets

---

## 📝 Next Steps

1. **Test the bot** with a real Instagram URL
2. **Monitor Railway logs** to see processing
3. **Check Google Sheets** to see processed leads
4. **Invite bot to channels** where you want lead intake

---

## 🎉 You're All Set!

The Slack bot is now live and ready to process Instagram leads. Just paste URLs in Slack and watch the magic happen! ✨
