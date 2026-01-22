# 🔒 Add Channel ID to Railway

## Your Channel ID
```
C0A7Y1UFLA0
```

## Steps to Add

1. **Go to Railway Dashboard**
   - https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

2. **Click on your service**: `agency-apex-swarm`

3. **Go to Variables tab**

4. **Click "+ New Variable"**

5. **Add the variable**:
   - **Name**: `SLACK_CHANNEL_ID`
   - **Value**: `C0A7Y1UFLA0`

6. **Click "Add"**

7. **Railway will automatically redeploy** with the new variable

---

## ✅ Verification

After adding, check Railway logs. You should see:
```
🔒 Bot restricted to channel: C0A7Y1UFLA0
```

---

## 🎯 What This Does

- ✅ Bot **only** processes messages from channel `C0A7Y1UFLA0`
- ✅ All other channels are **silently ignored**
- ✅ Slash commands from other channels show error
- ✅ @mentions from other channels are ignored

**Your bot is now locked to your dedicated lead intake channel!** 🔒
