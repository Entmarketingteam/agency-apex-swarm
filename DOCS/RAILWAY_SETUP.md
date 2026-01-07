# Railway Deployment Guide

## Quick Setup Steps

### 1. Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Verify your email

### 2. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `agency-apex-swarm` repository
4. Click "Deploy Now"

### 3. Add Environment Variables
In Railway dashboard, go to your project → Variables tab, add:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSy...
PERPLEXITY_API_KEY=pplx-...
FINDYMAIL_API_KEY=2iPtT1d6...
UNIPILE_API_KEY=D4DUla7y...
SMARTLEAD_API_KEY=17a34ec2-...
PINECONE_API_KEY=pcsk_...
```

### 4. Configure Service
1. Go to Settings → Service
2. Set **Start Command**: `python scripts/scheduler.py`
3. Set **Restart Policy**: On Failure
4. Save

### 5. Deploy
Railway will automatically deploy when you:
- Push to main branch, OR
- Click "Deploy" in dashboard

## Monitoring

- **Logs**: View in Railway dashboard → Deployments → Logs
- **Metrics**: Check CPU/Memory usage
- **Alerts**: Set up notifications for failures

## Cost Estimate

- **Free Tier**: $5 credit/month
- **Hobby Plan**: $5/month (after free tier)
- **Pro Plan**: $20/month (for production)

## Troubleshooting

### Service Won't Start
- Check logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is up to date

### API Errors
- Check API keys are correct
- Verify API quotas/limits
- Check logs for specific error messages

### Memory Issues
- Upgrade to Pro plan if needed
- Optimize batch sizes in scheduler

## Next Steps After Deployment

1. Test with one lead manually
2. Monitor logs for first 24 hours
3. Adjust scheduler frequency if needed
4. Set up alerts for failures

