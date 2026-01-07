#!/usr/bin/env python3
"""Railway API setup using API token."""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config

RAILWAY_PROJECT_ID = "fdc4ef5d-702b-49e1-ab23-282b2fe90066"
RAILWAY_API_URL = "https://api.railway.app/v1"

# Environment variables to set
ENV_VARS = {
    "ANTHROPIC_API_KEY": config.ANTHROPIC_API_KEY,
    "OPENAI_API_KEY": config.OPENAI_API_KEY,
    "GOOGLE_API_KEY": config.GOOGLE_API_KEY,
    "PERPLEXITY_API_KEY": config.PERPLEXITY_API_KEY,
    "FINDYMAIL_API_KEY": config.FINDYMAIL_API_KEY,
    "UNIPILE_API_KEY": config.UNIPILE_API_KEY,
    "SMARTLEAD_API_KEY": config.SMARTLEAD_API_KEY,
    "PINECONE_API_KEY": config.PINECONE_API_KEY,
}


def set_variables_via_api(token):
    """Set environment variables using Railway API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get project
    project_url = f"{RAILWAY_API_URL}/projects/{RAILWAY_PROJECT_ID}"
    response = requests.get(project_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error accessing project: {response.text}")
        return False
    
    project = response.json()
    print(f"✅ Connected to project: {project.get('name', 'Unknown')}")
    
    # Get services
    services_url = f"{RAILWAY_API_URL}/projects/{RAILWAY_PROJECT_ID}/services"
    response = requests.get(services_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error getting services: {response.text}")
        return False
    
    services = response.json()
    if not services:
        print("⚠️ No services found. Creating service...")
        # Service will be created on first deploy
    else:
        service_id = services[0]['id']
        print(f"✅ Found service: {service_id}")
    
    # Set variables
    print("\n🔐 Setting environment variables...")
    
    for key, value in ENV_VARS.items():
        if not value:
            print(f"⚠️ Skipping {key} - no value")
            continue
        
        # Railway API endpoint for variables
        vars_url = f"{RAILWAY_API_URL}/projects/{RAILWAY_PROJECT_ID}/variables"
        
        # Check if variable exists
        response = requests.get(vars_url, headers=headers)
        existing_vars = response.json() if response.status_code == 200 else []
        
        # Update or create
        var_exists = any(v.get('key') == key for v in existing_vars)
        
        if var_exists:
            # Update existing
            var_id = next(v['id'] for v in existing_vars if v.get('key') == key)
            update_url = f"{RAILWAY_API_URL}/variables/{var_id}"
            response = requests.patch(
                update_url,
                headers=headers,
                json={"value": value}
            )
        else:
            # Create new
            response = requests.post(
                vars_url,
                headers=headers,
                json={
                    "key": key,
                    "value": value,
                    "projectId": RAILWAY_PROJECT_ID
                }
            )
        
        if response.status_code in [200, 201]:
            print(f"✅ {key} set")
        else:
            print(f"❌ Failed to set {key}: {response.text}")
    
    print("\n✅ All variables set!")
    return True


def main():
    """Main function."""
    token = os.getenv("RAILWAY_TOKEN")
    
    if not token:
        print("❌ RAILWAY_TOKEN environment variable not set")
        print("\nTo get your Railway token:")
        print("1. Go to: https://railway.app/account/tokens")
        print("2. Click 'New Token'")
        print("3. Copy the token")
        print("4. Run: RAILWAY_TOKEN=your_token python scripts/railway_api_setup.py")
        return False
    
    print("🚀 Railway API Setup")
    print("=" * 50)
    
    return set_variables_via_api(token)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

