#!/bin/bash
# Script to deploy to Railway

echo "🚀 Railway Deployment Script"
echo "============================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    export PATH="$HOME/.railway/bin:$PATH"
fi

echo "✅ Railway CLI ready"
echo ""

# Link to existing project
echo "🔗 Linking to Railway project..."
railway link fdc4ef5d-702b-49e1-ab23-282b2fe90066

echo ""
echo "📝 Next steps:"
echo "1. Set environment variables: railway variables set KEY=value"
echo "2. Deploy: railway up"
echo ""

