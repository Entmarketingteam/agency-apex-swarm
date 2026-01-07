#!/bin/bash
# Script to set all environment variables in Railway

echo "🔐 Setting Railway Environment Variables"
echo "========================================"
echo ""

# Read from .env file and set in Railway
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "📋 Reading API keys from .env..."
echo ""

# Set each variable
railway variables set ANTHROPIC_API_KEY="$(grep ANTHROPIC_API_KEY .env | cut -d '=' -f2)"
railway variables set OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d '=' -f2)"
railway variables set GOOGLE_API_KEY="$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)"
railway variables set PERPLEXITY_API_KEY="$(grep PERPLEXITY_API_KEY .env | cut -d '=' -f2)"
railway variables set FINDYMAIL_API_KEY="$(grep FINDYMAIL_API_KEY .env | cut -d '=' -f2)"
railway variables set UNIPILE_API_KEY="$(grep UNIPILE_API_KEY .env | cut -d '=' -f2)"
railway variables set SMARTLEAD_API_KEY="$(grep SMARTLEAD_API_KEY .env | cut -d '=' -f2)"
railway variables set PINECONE_API_KEY="$(grep PINECONE_API_KEY .env | cut -d '=' -f2)"

echo ""
echo "✅ All environment variables set!"
echo ""
echo "🚀 Ready to deploy with: railway up"

