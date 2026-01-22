# ⚠️ Google API Key Issue

The current Google API key shows "API key expired" when accessing Google Sheets.

## Quick Fix: Create a New Google API Key

### Step 1: Go to Google Cloud Console
https://console.cloud.google.com/apis/credentials

### Step 2: Create New API Key
1. Click **"+ CREATE CREDENTIALS"**
2. Select **"API key"**
3. Copy the new key

### Step 3: Enable Google Sheets API
1. Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com
2. Click **"ENABLE"**

### Step 4: Update Railway Environment Variable
1. Go to: https://railway.app/project/fdc4ef5d-702b-49e1-ab23-282b2fe90066
2. Click **Variables** tab
3. Update **GOOGLE_API_KEY** with your new key

### Step 5: Redeploy
Railway will auto-redeploy when you update the variable.

---

## Alternative: Use Service Account (More Secure)

For production, consider using a Google Service Account instead of an API key.

1. Create a Service Account in Google Cloud Console
2. Download the JSON credentials file
3. Share your Google Sheet with the service account email
4. Add credentials as environment variable

This is more secure but requires more setup.

---

## Your Sheet Configuration

- **Sheet ID:** `1R2bYx2-G7cgtkv2GuiYqSZz-A7FOgh1V`
- **Tab Name:** `TEST SHEET FOR CURSOR`
- **Status:** Configured ✅ (just needs valid API key)


