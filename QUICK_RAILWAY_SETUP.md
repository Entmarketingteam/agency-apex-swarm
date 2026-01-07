# 🚀 Quick Railway Setup - Project ID: fdc4ef5d-702b-49e1-ab23-282b2fe90066

## Your Railway Project
**Project ID:** `fdc4ef5d-702b-49e1-ab23-282b2fe90066`  
**Dashboard:** https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

## ⚡ Fast Setup (5 minutes)

### Step 1: Add Environment Variables

Go to your Railway project → **Variables** tab → Click **"New Variable"** for each:

1. **ANTHROPIC_API_KEY**
   ```
   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
   ```

2. **OPENAI_API_KEY**
   ```
   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
   ```

3. **GOOGLE_API_KEY**
   ```
   AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s
   ```

4. **PERPLEXITY_API_KEY**
   ```
   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
   ```

5. **FINDYMAIL_API_KEY**
   ```
   2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc
   ```

6. **UNIPILE_API_KEY**
   ```
   D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo=
   ```

7. **SMARTLEAD_API_KEY**
   ```
   17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg
   ```

8. **PINECONE_API_KEY**
   ```
   pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk
   ```

### Step 2: Configure Service

1. Go to **Settings** → **Service**
2. Set **Start Command**: 
   ```
   python scripts/scheduler.py
   ```
3. Set **Restart Policy**: `On Failure`
4. **Save**

### Step 3: Deploy

**Option A: Connect GitHub Repo**
1. Go to **Settings** → **Source**
2. Connect your GitHub repository
3. Railway will auto-deploy on push

**Option B: Manual Deploy**
1. Install Railway CLI:
   ```bash
   curl -fsSL https://railway.app/install.sh | sh
   ```
2. Login and link:
   ```bash
   railway login
   railway link fdc4ef5d-702b-49e1-ab23-282b2fe90066
   railway up
   ```

## ✅ After Deployment

1. **Check Logs**: Railway dashboard → **Deployments** → **Logs**
2. **Verify**: Look for "Starting Agency Apex Swarm Scheduler"
3. **Test**: System will process leads from `leads/queue.csv`

## 📝 Adding Leads

Create `leads/queue.csv` in your repo with format:
```csv
name,handle,platform,bio
Creator Name,creator_handle,instagram,Fashion content creator
```

Or add via Railway console after deployment.

## 🆘 Troubleshooting

- **Service won't start**: Check logs, verify all 8 env vars are set
- **API errors**: Double-check API keys are correct
- **Build fails**: Ensure `requirements.txt` is committed

## 📊 Monitor Your Deployment

- **Logs**: Real-time in Railway dashboard
- **Metrics**: CPU/Memory usage
- **Status**: Green = Running, Red = Error

**Your system will process leads every hour automatically!** 🎉

