# 💬 Slack Integration Setup Guide

> Enable Instagram URL lead intake via Slack

---

## 🚀 Quick Start

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name: `APEX Lead Bot`
4. Select your workspace
5. Click **"Create App"**

### 2. Configure Bot Permissions

Go to **OAuth & Permissions** → **Scopes** → **Bot Token Scopes**

Add these scopes:
```
channels:history      - Read messages in public channels
channels:read         - View basic channel info
chat:write           - Send messages
commands             - Add slash commands
groups:history       - Read messages in private channels
im:history           - Read direct messages
users:read           - View users
```

### 3. Enable Socket Mode

1. Go to **Socket Mode** in sidebar
2. Toggle **"Enable Socket Mode"** ON
3. Create an App-Level Token:
   - Name: `apex-socket`
   - Scope: `connections:write`
4. Copy the token (starts with `xapp-`)

### 4. Subscribe to Events

Go to **Event Subscriptions**:

1. Toggle **"Enable Events"** ON
2. Under **Subscribe to bot events**, add:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `app_mention`

### 5. Create Slash Command (Optional)

Go to **Slash Commands** → **Create New Command**:

- Command: `/apex`
- Description: `Process Instagram lead`
- Usage Hint: `@username or instagram.com/username`

### 6. Install App

1. Go to **Install App**
2. Click **"Install to Workspace"**
3. Authorize the app
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

---

## 🔐 Environment Variables

Add these to Railway or your `.env`:

```bash
# Required
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_APP_TOKEN=xapp-your-app-token-here

# Optional
SLACK_CHANNEL_ID=C0123456789  # Specific channel to monitor
```

### Where to Find These

| Variable | Location |
|----------|----------|
| `SLACK_BOT_TOKEN` | OAuth & Permissions → Bot User OAuth Token |
| `SLACK_SIGNING_SECRET` | Basic Information → App Credentials → Signing Secret |
| `SLACK_APP_TOKEN` | Basic Information → App-Level Tokens |
| `SLACK_CHANNEL_ID` | Right-click channel → Copy link → Extract ID |

---

## 📱 Usage

### Method 1: Paste URL in Channel

Just paste an Instagram URL in any channel where the bot is present:

```
https://instagram.com/fashionista_jane
```

Bot responds:
```
✅ Lead detected: @fashionista_jane
📋 Added to processing queue
⏳ Estimated completion: 2-3 minutes
```

### Method 2: Use Slash Command

```
/apex @fashionista_jane
```

or

```
/apex https://instagram.com/fashionista_jane
```

### Method 3: @ Mention the Bot

```
@APEX Lead Bot check out https://instagram.com/fashionista_jane
```

---

## 🔗 Supported URL Formats

The bot recognizes these Instagram formats:

| Format | Example |
|--------|---------|
| Profile URL | `https://instagram.com/username` |
| Profile with params | `https://instagram.com/username?igsh=abc` |
| WWW URL | `https://www.instagram.com/username/` |
| Stories | `https://instagram.com/stories/username/` |
| @ Mention | `@username` |
| Raw handle | `username` (in /apex command) |

---

## 📊 Bot Responses

### Lead Detected

```
✅ Lead detected: @username
Platform: Instagram
Status: ⏳ Processing...
Estimated completion: 2-3 minutes
```

### Lead Processed

```
✅ Lead processed: @username

📧 Email: user@example.com
📊 Vibe Score: 87/100 ✨

Research: Fashion & lifestyle creator with 150K followers...
Outreach: 📤 Added to Smartlead campaign

[View in Sheet]
```

### Duplicate Detected

```
⚠️ Duplicate detected: @username
📅 Previously contacted: January 7, 2026
📧 Email on file: user@example.com
❌ Skipping to avoid double outreach
```

### Error

```
❌ Error processing: @username
`Error message here`
```

---

## 🏃 Running the Bot

### Local Development

```bash
# Install dependencies
pip install slack-bolt

# Run the bot
python -m slack_bot.app
```

### Railway Deployment

The bot runs automatically with the main application. Just ensure the Slack environment variables are set in Railway.

### Standalone Mode

To run only the Slack bot:

```bash
python slack_bot/app.py
```

---

## 🔧 Troubleshooting

### Bot Not Responding

1. Check bot is in the channel: `/invite @APEX Lead Bot`
2. Verify `SLACK_BOT_TOKEN` is correct
3. Check Railway logs for errors

### "Invalid Signing Secret"

- Regenerate signing secret in Slack app settings
- Update `SLACK_SIGNING_SECRET` in Railway

### "Socket Mode Connection Failed"

- Ensure Socket Mode is enabled in Slack app
- Verify `SLACK_APP_TOKEN` starts with `xapp-`
- Check app-level token has `connections:write` scope

### Rate Limiting

The bot processes leads sequentially to avoid API rate limits. If you're hitting limits:
- Reduce batch sizes
- Add delays between leads
- Upgrade API plans

---

## 📁 File Structure

```
slack_bot/
├── __init__.py           # Package init
├── app.py                # Main Slack app
├── handlers.py           # Message handlers
└── instagram_parser.py   # URL parsing utilities
```

---

## 🔒 Security Notes

1. **Never commit tokens** - Use environment variables
2. **Restrict channels** - Set `SLACK_CHANNEL_ID` to limit where bot responds
3. **Audit logs** - All actions are logged for review
4. **Rate limiting** - Built-in protection against abuse

---

## 📞 Support

- **Slack API Docs:** https://api.slack.com/docs
- **slack-bolt Python:** https://slack.dev/bolt-python/
- **GitHub Issues:** https://github.com/Entmarketingteam/agency-apex-swarm/issues

---

*Last updated: January 2026*


