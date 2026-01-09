# Railway Deployment - Project Linked

## Your Railway Project
**Project ID:** `fdc4ef5d-702b-49e1-ab23-282b2fe90066`

## Quick Deploy Steps

### Option 1: Using Railway CLI (Recommended)

1. **Install Railway CLI** (if not installed):
   ```bash
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link fdc4ef5d-702b-49e1-ab23-282b2fe90066
   ```

4. **Set environment variables** (run this script):
   ```bash
   bash scripts/set_railway_env.sh
   ```
   
   Or manually set each:
   ```bash
   railway variables set ANTHROPIC_API_KEY="your_key"
   railway variables set OPENAI_API_KEY="your_key"
   # ... etc for all 8 keys
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

### Option 2: Using Railway Dashboard

1. **Go to your project**: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

2. **Add Environment Variables**:
   - Go to Variables tab
   - Add each API key from your `.env` file:
     - `ANTHROPIC_API_KEY`
     - `OPENAI_API_KEY`
     - `GOOGLE_API_KEY`
     - `PERPLEXITY_API_KEY`
     - `FINDYMAIL_API_KEY`
     - `UNIPILE_API_KEY`
     - `SMARTLEAD_API_KEY`
     - `PINECONE_API_KEY`

3. **Configure Service**:
   - Go to Settings → Service
   - **Start Command**: `python scripts/scheduler.py`
   - **Restart Policy**: On Failure

4. **Deploy**:
   - Push to GitHub (if connected), OR
   - Click "Deploy" in dashboard

## Environment Variables to Set

Copy these from your `.env` file:

```
ANTHROPIC_API_KEY=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
OPENAI_API_KEY=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
GOOGLE_API_KEY=AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s
PERPLEXITY_API_KEY=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
FINDYMAIL_API_KEY=2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc
UNIPILE_API_KEY=D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo=
SMARTLEAD_API_KEY=17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg
PINECONE_API_KEY=pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk
```

## After Deployment

1. **Check Logs**: Railway dashboard → Deployments → Logs
2. **Monitor**: Watch for any errors
3. **Test**: Add a lead to `leads/queue.csv` and watch it process

## Troubleshooting

- **Service won't start**: Check logs, verify all env vars are set
- **API errors**: Verify API keys are correct
- **Build fails**: Check `requirements.txt` is up to date

## Project URL

Your Railway project: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066


