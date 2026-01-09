#!/bin/bash
# Railway setup using API token
# Usage: RAILWAY_TOKEN=your_token bash scripts/setup_with_token.sh

set -e

RAILWAY_PROJECT_ID="fdc4ef5d-702b-49e1-ab23-282b2fe90066"

if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ RAILWAY_TOKEN environment variable not set"
    echo ""
    echo "To get your Railway token:"
    echo "1. Go to: https://railway.app/account/tokens"
    echo "2. Click 'New Token'"
    echo "3. Copy the token"
    echo "4. Run: RAILWAY_TOKEN=your_token bash scripts/setup_with_token.sh"
    exit 1
fi

echo "🔐 Using Railway API token..."
export RAILWAY_TOKEN

# Set environment variables using Railway API
echo "🔐 Setting environment variables via API..."

# Read from .env file
source .env 2>/dev/null || true

railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set OPENAI_API_KEY="$OPENAI_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set GOOGLE_API_KEY="$GOOGLE_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set PERPLEXITY_API_KEY="$PERPLEXITY_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set FINDYMAIL_API_KEY="$FINDYMAIL_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set UNIPILE_API_KEY="$UNIPILE_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set SMARTLEAD_API_KEY="$SMARTLEAD_API_KEY" --project "$RAILWAY_PROJECT_ID"
railway variables set PINECONE_API_KEY="$PINECONE_API_KEY" --project "$RAILWAY_PROJECT_ID"

echo "✅ All variables set!"
echo ""
echo "Next: Configure service in Railway dashboard:"
echo "  - Start Command: python scripts/scheduler.py"
echo "  - Restart Policy: On Failure"


