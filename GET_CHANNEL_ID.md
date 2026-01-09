# 📍 How to Get Your Slack Channel ID

To restrict the bot to a specific channel, you need the **Channel ID**.

## Method 1: From Slack URL (Easiest)

1. Open your Slack channel in a web browser
2. Look at the URL - it will look like:
   ```
   https://growthpartner.slack.com/archives/C0123456789
   ```
3. The Channel ID is the part after `/archives/` - in this example: `C0123456789`

## Method 2: Right-Click Channel

1. In Slack desktop app, **right-click** on your channel name
2. Select **"Copy link"**
3. The link will look like:
   ```
   https://growthpartner.slack.com/archives/C0123456789
   ```
4. Extract the Channel ID: `C0123456789`

## Method 3: Using Slack API

1. Go to: https://api.slack.com/methods/conversations.list/test
2. Enter your Bot Token
3. Call the API
4. Find your channel in the list and copy its `id`

---

## ✅ Once You Have the Channel ID

1. Add it to Railway as an environment variable:
   - Variable name: `SLACK_CHANNEL_ID`
   - Variable value: `C0123456789` (your actual channel ID)

2. The bot will **only** process messages from that channel

3. Messages from other channels will be silently ignored

---

## 🔒 Security Note

With `SLACK_CHANNEL_ID` set:
- ✅ Bot only processes leads from the specified channel
- ✅ All other channels are ignored
- ✅ Slash commands from other channels show an error
- ✅ @mentions from other channels are ignored

**This ensures your bot only processes leads from your dedicated intake channel!**
