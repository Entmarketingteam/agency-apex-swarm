#!/bin/bash
# One-command Railway setup
# Just run: bash setup_railway.sh

echo "🚀 Railway Automated Setup"
echo "========================="
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    export PATH="$HOME/.railway/bin:$PATH"
fi

# Check login
if ! railway whoami &>/dev/null; then
    echo "🔐 Please login to Railway..."
    echo "This will open a browser for authentication"
    railway login
    echo ""
fi

echo "✅ Logged in!"
echo ""

# Run complete setup
bash scripts/complete_railway_setup.sh


