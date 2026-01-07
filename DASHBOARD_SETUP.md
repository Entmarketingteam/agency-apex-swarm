# 🎯 Railway Dashboard Setup (Easiest Method)

Since we're in a Codespace, use the Railway **dashboard** instead of CLI.

## Step-by-Step Dashboard Setup

### 1. Go to Your Project
**Link:** https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

### 2. Add Environment Variables
1. Click **"Variables"** tab (left sidebar)
2. Click **"New Variable"** button
3. Add each variable below (copy-paste):

**Variable 1:**
- **Name:** `ANTHROPIC_API_KEY`
- **Value:** `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`

**Variable 2:**
- **Name:** `OPENAI_API_KEY`
- **Value:** `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`

**Variable 3:**
- **Name:** `GOOGLE_API_KEY`
- **Value:** `AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s`

**Variable 4:**
- **Name:** `PERPLEXITY_API_KEY`
- **Value:** `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`

**Variable 5:**
- **Name:** `FINDYMAIL_API_KEY`
- **Value:** `2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc`

**Variable 6:**
- **Name:** `UNIPILE_API_KEY`
- **Value:** `D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo=`

**Variable 7:**
- **Name:** `SMARTLEAD_API_KEY`
- **Value:** `17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg`

**Variable 8:**
- **Name:** `PINECONE_API_KEY`
- **Value:** `pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk`

### 3. Configure Service
1. Click **"Settings"** tab (left sidebar)
2. Click **"Service"** section
3. Find **"Start Command"** field
4. Enter: `python scripts/scheduler.py`
5. Find **"Restart Policy"** dropdown
6. Select: `On Failure`
7. Click **"Save"**

### 4. Connect GitHub (Optional but Recommended)
1. Click **"Settings"** tab
2. Click **"Source"** section
3. Click **"Connect GitHub"**
4. Select your `agency-apex-swarm` repository
5. Railway will auto-deploy on every push

### 5. Deploy
If you connected GitHub:
- Just push your code: `git push origin main`
- Railway will auto-deploy

If not connected:
- Click **"Deployments"** tab
- Click **"Deploy"** button
- Or push code to trigger deployment

## ✅ That's It!

Your system will:
- ✅ Run 24/7 on Railway
- ✅ Process leads every hour
- ✅ Auto-restart on failure
- ✅ Log everything

## 📊 Monitor

- **Logs:** Click "Deployments" → Click latest deployment → "Logs"
- **Status:** Green = Running, Red = Error

## 🆘 Troubleshooting

- **Service won't start:** Check logs, verify all 8 variables are set
- **API errors:** Double-check API keys are correct
- **Build fails:** Make sure `requirements.txt` is in repo

---

**Total time: 5 minutes in the dashboard!** 🎉

