# 🤖 Automated Railway Setup

I've created scripts to automate the Railway setup. Here's how to use them:

## Option 1: Automated Script (Easiest)

### Step 1: Login to Railway
```bash
railway login
```
This will open a browser for authentication. Complete the login.

### Step 2: Run Setup Script
```bash
bash scripts/complete_railway_setup.sh
```

This script will:
- ✅ Link to your project
- ✅ Set all 8 environment variables
- ✅ Deploy your application

**That's it!** The script does everything automatically.

## Option 2: Manual Steps (If script doesn't work)

### 1. Login
```bash
railway login
```

### 2. Link Project
```bash
railway link fdc4ef5d-702b-49e1-ab23-282b2fe90066
```

### 3. Set Environment Variables
```bash
railway variables set ANTHROPIC_API_KEY="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"
railway variables set OPENAI_API_KEY="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"
railway variables set GOOGLE_API_KEY="AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s"
railway variables set PERPLEXITY_API_KEY="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"
railway variables set FINDYMAIL_API_KEY="2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc"
railway variables set UNIPILE_API_KEY="D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo="
railway variables set SMARTLEAD_API_KEY="17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg"
railway variables set PINECONE_API_KEY="pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk"
```

### 4. Deploy
```bash
railway up
```

## Option 3: Railway Dashboard (No CLI needed)

1. Go to: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. Click **Variables** tab
3. Add each environment variable (copy from `railway_env_vars.txt`)
4. Go to **Settings** → **Service**
5. Set **Start Command**: `python scripts/scheduler.py`
6. Set **Restart Policy**: `On Failure`
7. Click **Deploy**

## What's Already Done

✅ Railway CLI installed  
✅ Configuration files created (`railway.json`, `railway.toml`, `Procfile`)  
✅ Setup scripts created  
✅ All API keys ready to deploy  

## After Setup

Once deployed, your system will:
- Run continuously on Railway
- Process leads from `leads/queue.csv` every hour
- Log all activity to Railway logs
- Auto-restart on failure

## Quick Commands

```bash
# Check status
railway status

# View logs
railway logs

# Redeploy
railway up

# Open dashboard
railway open
```

## Need Help?

If the automated script doesn't work, use Option 3 (Dashboard) - it's the most reliable method!

