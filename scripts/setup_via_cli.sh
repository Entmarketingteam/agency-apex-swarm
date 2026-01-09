#!/bin/bash
# Setup Railway using CLI with token authentication
# This script uses Railway CLI with token stored in config

set -e

TOKEN="de9380b6-7634-49d1-958e-abade2d5b9ab"
PROJECT_ID="fdc4ef5d-702b-49e1-ab23-282b2fe90066"

echo "🚀 Railway Setup with Token"
echo "==========================="
echo ""

# Store token in Railway config
mkdir -p ~/.railway
echo "$TOKEN" > ~/.railway/token

# Set environment variable for Railway CLI
export RAILWAY_TOKEN="$TOKEN"

# Try to use Railway CLI
echo "🔗 Linking to project..."
railway link --project "$PROJECT_ID" 2>&1 || echo "Project may already be linked"

echo ""
echo "🔐 Setting environment variables..."
echo ""

# Set each variable
railway variables set ANTHROPIC_API_KEY="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" 2>&1
railway variables set OPENAI_API_KEY="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" 2>&1
railway variables set GOOGLE_API_KEY="AIzaSyDNRH84fdrENv2cSkk36X1xP_IOYGpen1s" 2>&1
railway variables set PERPLEXITY_API_KEY="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" 2>&1
railway variables set FINDYMAIL_API_KEY="2iPtT1d6b8dZeUW5UOr0YmRtK8VS94aFNVLGzVtR543a3bbc" 2>&1
railway variables set UNIPILE_API_KEY="D4DUla7y.8iOltN1EOrpxp2MHU3DdfjhLmKaHAEE8rZLArSkKBDo=" 2>&1
railway variables set SMARTLEAD_API_KEY="17a34ec2-b253-45a8-9f0c-707333b745ad_3eex9gg" 2>&1
railway variables set PINECONE_API_KEY="pcsk_42FJgZ_9L3myTJeW5T5dvfZcqvXTt3P7tcBBCNyHUz7M19FaNVuZkiu77xG8shSkfNnVfk" 2>&1

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next: Configure service in Railway dashboard:"
echo "  - Start Command: python scripts/scheduler.py"
echo "  - Restart Policy: On Failure"


