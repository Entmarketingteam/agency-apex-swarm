#!/bin/bash
# Complete Railway setup script
# Run this after: railway login

set -e

RAILWAY_PROJECT_ID="fdc4ef5d-702b-49e1-ab23-282b2fe90066"

echo "🚀 Railway Complete Setup"
echo "========================"
echo ""

# Check if logged in
if ! railway whoami &>/dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Please run: railway login"
    exit 1
fi

echo "✅ Logged in to Railway"
echo ""

# Link to project
echo "🔗 Linking to project..."
railway link "$RAILWAY_PROJECT_ID" || echo "Project may already be linked"
echo ""

# Set environment variables
echo "🔐 Setting environment variables..."
echo ""

railway variables set ANTHROPIC_API_KEY="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"
railway variables set OPENAI_API_KEY="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"
railway variables set GOOGLE_API_KEY="AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s"
railway variables set PERPLEXITY_API_KEY="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"
railway variables set FINDYMAIL_API_KEY="2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc"
railway variables set UNIPILE_API_KEY="D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo="
railway variables set SMARTLEAD_API_KEY="17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg"
railway variables set PINECONE_API_KEY="pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk"

echo ""
echo "✅ All environment variables set!"
echo ""

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Check your deployment at:"
echo "https://railway.app/project/$RAILWAY_PROJECT_ID"
echo ""
echo "📝 Next: Configure service settings in Railway dashboard:"
echo "   - Start Command: python scripts/scheduler.py"
echo "   - Restart Policy: On Failure"


