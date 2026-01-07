#!/usr/bin/env python3
"""Railway setup using GraphQL API v2."""

import os
import sys
import requests
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import config

# Railway API v2 endpoint (correct endpoint per docs)
RAILWAY_API = "https://backboard.railway.com/graphql/v2"
PROJECT_ID = "fdc4ef5d-702b-49e1-ab23-282b2fe90066"

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


def graphql_request(token, query, variables=None, use_project_token=False):
    """Execute a GraphQL request."""
    headers = {
        "Content-Type": "application/json"
    }
    
    if use_project_token:
        headers["Project-Access-Token"] = token
    else:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(RAILWAY_API, json=payload, headers=headers)
    
    try:
        return response.json()
    except:
        print(f"Response: {response.text}")
        return {"errors": [{"message": response.text}]}


def get_project_info(token):
    """Get project information."""
    query = """
    query GetProject($id: String!) {
        project(id: $id) {
            id
            name
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            services {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
    }
    """
    
    result = graphql_request(token, query, {"id": PROJECT_ID})
    return result


def upsert_variables(token, project_id, environment_id, service_id, variables):
    """Upsert environment variables."""
    mutation = """
    mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
        variableCollectionUpsert(input: $input)
    }
    """
    
    input_data = {
        "projectId": project_id,
        "environmentId": environment_id,
        "variables": variables
    }
    
    if service_id:
        input_data["serviceId"] = service_id
    
    result = graphql_request(token, mutation, {"input": input_data})
    return result


def main():
    """Main setup function."""
    token = os.getenv("RAILWAY_TOKEN", "de9380b6-7634-49d1-958e-abade2d5b9ab")
    
    print("🚀 Railway API v2 Setup")
    print("=" * 50)
    print(f"Using endpoint: {RAILWAY_API}")
    print(f"Project ID: {PROJECT_ID}")
    print("")
    
    # Try to get project info
    print("📋 Getting project info...")
    result = get_project_info(token)
    
    if "errors" in result and result.get("data") is None:
        print(f"❌ Error: {result['errors']}")
        print("\n⚠️ Token may be invalid or expired.")
        print("\nTo get a valid token:")
        print("1. Go to: https://railway.com/account/tokens")
        print("2. Create a new 'Personal Token' (not Team or Project token)")
        print("3. Copy the token and try again")
        return False
    
    project = result.get("data", {}).get("project")
    if project:
        print(f"✅ Found project: {project.get('name')}")
        
        # Get environment
        environments = project.get("environments", {}).get("edges", [])
        if environments:
            env_id = environments[0]["node"]["id"]
            print(f"✅ Found environment: {environments[0]['node']['name']} ({env_id})")
        else:
            print("⚠️ No environments found")
            env_id = None
        
        # Get service
        services = project.get("services", {}).get("edges", [])
        if services:
            service_id = services[0]["node"]["id"]
            print(f"✅ Found service: {services[0]['node']['name']} ({service_id})")
        else:
            print("⚠️ No services found (will create on first deploy)")
            service_id = None
        
        # Set variables
        if env_id:
            print("\n🔐 Setting environment variables...")
            result = upsert_variables(token, PROJECT_ID, env_id, service_id, ENV_VARS)
            
            if "errors" in result:
                print(f"❌ Error setting variables: {result['errors']}")
            else:
                print("✅ All variables set!")
    else:
        print("❌ Could not access project")
    
    return True


if __name__ == "__main__":
    main()

