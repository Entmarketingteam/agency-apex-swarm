# Railway Deployment Guide

## Quick Deploy

### Option 1: GitHub Integration (Recommended)

1. **Connect Repository:**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `agency-apex-swarm`
   - Railway will auto-detect the project

2. **Set Environment Variables:**
   - Go to Variables tab
   - Add all required API keys (see [Environment Variables](ENV_VARS.md))

3. **Deploy:**
   - Railway auto-deploys on push to `main`
   - Or click "Deploy" in dashboard

### Option 2: Railway CLI

```bash
# Install CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Link project
railway link

# Set variables
railway variables set SLACK_BOT_TOKEN="your_token"
# ... repeat for all variables

# Deploy
railway up
```

## Required Files

- `Procfile` - Defines the start command
- `requirements.txt` - Python dependencies
- `.railwayignore` - Files to exclude from deployment

## Environment Variables

See [Environment Variables Guide](ENV_VARS.md) for complete list.

**Required:**
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `SLACK_SIGNING_SECRET`
- `GOOGLE_SHEET_ID`
- `GOOGLE_API_KEY`
- All API keys (Perplexity, Findymail, etc.)

## Service Configuration

**Start Command:** `python run.py`

**Port:** Railway automatically sets `$PORT` - service must bind to it

**Restart Policy:** On Failure (default)

## Monitoring

- **Logs:** Railway dashboard → Deployments → View logs
- **Metrics:** Railway dashboard → Metrics tab
- **Health:** Service should respond to health checks

## Troubleshooting

### Service Won't Start
1. Check logs for errors
2. Verify all environment variables are set
3. Ensure `Procfile` exists and is correct
4. Check Python version compatibility

### Deployment Fails
1. Check build logs
2. Verify `requirements.txt` is valid
3. Ensure all dependencies are available
4. Check for syntax errors in code

### Service Crashes
1. Review application logs
2. Check API key validity
3. Verify external service connectivity
4. Check memory/CPU limits

---

*For environment variable details, see [ENV_VARS.md](ENV_VARS.md)*
