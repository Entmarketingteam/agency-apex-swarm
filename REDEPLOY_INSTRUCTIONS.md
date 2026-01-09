# 🔄 Redeploy on Railway - Fix Pinecone Error

## The Issue

The error `vector: invalid value "nicki.entenmann" for type TYPE_FLOAT` happens because the code was passing a handle string to Pinecone instead of an embedding vector.

## The Fix

I've fixed two things:
1. ✅ **Slack handler** - Now generates embedding before checking duplicates
2. ✅ **Pinecone client** - Added validation to ensure embeddings are floats

## How to Redeploy

### Option 1: Manual Redeploy (Recommended)

1. Go to Railway Dashboard:
   - https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066

2. Click your service: `agency-apex-swarm`

3. Click **Deployments** tab

4. Click **Redeploy** button (or **Deploy** if it's the latest)

5. Wait for deployment to complete (2-3 minutes)

### Option 2: Auto-Deploy (If Enabled)

If you have auto-deploy enabled, Railway should automatically deploy the latest code from GitHub. Check the deployments tab to see if a new deployment is in progress.

### Option 3: Trigger via Git Push

If auto-deploy is enabled, you can trigger a redeploy by making a small change and pushing:

```bash
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

## Verify Fix

After redeploying:

1. **Check Railway Logs**
   - Look for: `Starting Slack bot in Socket Mode...`
   - No errors about Pinecone

2. **Test in Slack**
   - Paste Instagram URL again
   - Bot should process without the 400 error

3. **Check for Success**
   - Bot should respond with completion message
   - No more "Bad Request" errors

## What Was Fixed

### Before (Broken):
```python
# ❌ Passing handle string directly
is_duplicate = pinecone.check_duplicate(handle)
```

### After (Fixed):
```python
# ✅ Generate embedding first
embedding = openai.generate_embedding(f"{handle} instagram")
duplicate_id = pinecone.check_duplicate(embedding, threshold=0.95)
```

## If Error Persists

If you still see the error after redeploying:

1. **Check Railway Logs** - Look for the exact error message
2. **Verify Deployment** - Make sure latest code is deployed
3. **Check Embedding Generation** - Verify OpenAI API is working
4. **Share Logs** - Send me the error details

---

**The fix is in the code. You just need to redeploy on Railway!** 🚀
