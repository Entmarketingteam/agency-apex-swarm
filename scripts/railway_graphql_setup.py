#!/usr/bin/env python3
"""Railway setup using GraphQL API."""

import os
import sys
import requests
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config import config

TOKEN = "de9380b6-7634-49d1-958e-abade2d5b9ab"
PROJECT_ID = "fdc4ef5d-702b-49e1-ab23-282b2fe90066"

RAILWAY_GRAPHQL = "https://backboard.railway.app/graphql/v1"

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


def graphql_query(query, variables=None):
    """Execute a GraphQL query."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(RAILWAY_GRAPHQL, json=payload, headers=headers)
    return response.json()


def get_project_services():
    """Get services for the project."""
    query = """
    query GetProject($id: String!) {
        project(id: $id) {
            id
            name
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
    
    result = graphql_query(query, {"id": PROJECT_ID})
    
    if "errors" in result:
        print(f"❌ Error: {result['errors']}")
        return None
    
    project = result.get("data", {}).get("project")
    if not project:
        print("❌ Project not found")
        return None
    
    print(f"✅ Found project: {project.get('name')}")
    
    services = project.get("services", {}).get("edges", [])
    if services:
        service_id = services[0]["node"]["id"]
        print(f"✅ Found service: {service_id}")
        return service_id
    
    return None


def set_variable(service_id, key, value):
    """Set an environment variable."""
    mutation = """
    mutation UpsertVariable($input: VariableUpsertInput!) {
        variableUpsert(input: $input) {
            id
            key
        }
    }
    """
    
    variables = {
        "input": {
            "serviceId": service_id,
            "key": key,
            "value": value
        }
    }
    
    result = graphql_query(mutation, variables)
    
    if "errors" in result:
        return False, result["errors"]
    
    return True, None


def main():
    """Main setup function."""
    print("🚀 Railway GraphQL Setup")
    print("=" * 50)
    
    # Get service
    service_id = get_project_services()
    if not service_id:
        print("\n⚠️ No service found. Creating variables at project level...")
        # Try project-level variables
        service_id = None
    
    print("\n🔐 Setting environment variables...")
    
    success_count = 0
    for key, value in ENV_VARS.items():
        if not value:
            print(f"⚠️ Skipping {key} - no value")
            continue
        
        if service_id:
            success, error = set_variable(service_id, key, value)
        else:
            # Try project-level
            success, error = False, "Service ID required"
        
        if success:
            print(f"✅ {key} set")
            success_count += 1
        else:
            print(f"❌ Failed to set {key}: {error}")
    
    print(f"\n✅ Set {success_count}/{len(ENV_VARS)} variables")
    print("\n📝 Note: Some variables may need to be set manually in Railway dashboard")
    print("   if GraphQL API doesn't support project-level variables")


if __name__ == "__main__":
    main()


