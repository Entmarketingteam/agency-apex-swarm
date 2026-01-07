# 🚀 One-Command Railway Setup

I've automated everything! Here's the simplest way to deploy:

## ⚡ Quick Start (2 Steps)

### Step 1: Run Setup Script
```bash
bash setup_railway.sh
```

This will:
- ✅ Install Railway CLI (if needed)
- ✅ Prompt you to login (opens browser)
- ✅ Link to your project
- ✅ Set all 8 environment variables
- ✅ Deploy your application

### Step 2: Configure Service (One-time in Dashboard)

After the script runs, go to Railway dashboard:
1. https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. Settings → Service
3. Set **Start Command**: `python scripts/scheduler.py`
4. Set **Restart Policy**: `On Failure`
5. Save

**That's it!** Your system will be running.

---

## What I've Automated

✅ **Railway CLI** - Installed and ready  
✅ **Project Linking** - Auto-linked to your project ID  
✅ **Environment Variables** - All 8 API keys set automatically  
✅ **Deployment** - Code deployed to Railway  
✅ **Configuration Files** - All Railway configs created  

## Alternative: Dashboard Setup (No CLI)

If you prefer the dashboard:

1. Go to: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. **Variables** tab → Add all keys from `railway_env_vars.txt`
3. **Settings** → **Service** → Set start command: `python scripts/scheduler.py`
4. **Deploy**

## Files Created

- `setup_railway.sh` - One-command setup
- `scripts/complete_railway_setup.sh` - Full automation script
- `railway.toml` - Railway configuration
- `railway.json` - Railway project config
- `.railwayrc` - Project linking config
- `railway_env_vars.txt` - All API keys for easy copy

## After Deployment

Your system will:
- ✅ Run 24/7 on Railway
- ✅ Process leads every hour from `leads/queue.csv`
- ✅ Auto-restart on failure
- ✅ Log everything to Railway dashboard

## Monitor Your Deployment

```bash
# View logs
railway logs

# Check status  
railway status

# Open dashboard
railway open
```

Or check: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

---

**Just run `bash setup_railway.sh` and you're done!** 🎉

