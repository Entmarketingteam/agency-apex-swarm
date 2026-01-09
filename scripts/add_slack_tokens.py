#!/usr/bin/env python3
"""Add Slack tokens to Railway via GraphQL API v2."""

import requests
import json

TOKEN = "de9380b6-7634-49d1-958e-abade2d5b9ab"
PROJECT_ID = "fdc4ef5d-702b-49e1-ab23-282b2fe90066"
RAILWAY_API = "https://backboard.railway.com/graphql/v2"

SLACK_TOKENS = {
    "SLACK_BOT_TOKEN": "xoxb-6255452579572-10250746563831-ygNUIy78o5ex0DvjlLinG7ZY",
    "SLACK_SIGNING_SECRET": "34abfce1954f64ddfa43bcc0fcdcf079",
    "SLACK_APP_TOKEN": "xapp-1-A0A7XNCECBE-10269793755652-cac80fb35c7bf4046831898226769965720fae19ef7ba8df50bd104a7854a8e9"
}


def graphql_request(query, variables=None):
    """Execute a GraphQL request."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(RAILWAY_API, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        return {"errors": [{"message": f"HTTP {response.status_code}"}]}
    
    try:
        return response.json()
    except Exception as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Response text: {response.text[:200]}")
        return {"errors": [{"message": str(e)}]}


def get_project_info():
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
    
    result = graphql_request(query, {"id": PROJECT_ID})
    return result


def upsert_variables(project_id, environment_id, service_id, variables):
    """Upsert environment variables."""
    mutation = """
    mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
        variableCollectionUpsert(input: $input)
    }
    """
    
    # Convert dict to list of {key, value} objects
    var_list = [{"key": k, "value": v} for k, v in variables.items()]
    
    input_data = {
        "projectId": project_id,
        "environmentId": environment_id,
        "variables": var_list
    }
    
    if service_id:
        input_data["serviceId"] = service_id
    
    result = graphql_request(mutation, {"input": input_data})
    return result


def main():
    """Main function."""
    print("🔐 Adding Slack Tokens to Railway")
    print("=" * 50)
    print(f"Using endpoint: {RAILWAY_API}")
    print(f"Project ID: {PROJECT_ID}\n")
    
    # Get project info
    print("📋 Getting project info...")
    result = get_project_info()
    
    if "errors" in result and result.get("data") is None:
        print(f"❌ Error: {result['errors']}")
        return
    
    project = result.get("data", {}).get("project")
    if not project:
        print("❌ Could not access project")
        return
    
    print(f"✅ Found project: {project.get('name')}")
    
    # Get environment
    environments = project.get("environments", {}).get("edges", [])
    if not environments:
        print("❌ No environments found")
        return
    
    env_id = environments[0]["node"]["id"]
    print(f"✅ Found environment: {environments[0]['node']['name']} ({env_id})")
    
    # Get service
    services = project.get("services", {}).get("edges", [])
    service_id = None
    if services:
        service_id = services[0]["node"]["id"]
        print(f"✅ Found service: {services[0]['node']['name']} ({service_id})")
    else:
        print("⚠️ No services found (will set at project level)")
    
    # Set variables
    print("\n🔐 Setting Slack environment variables...")
    result = upsert_variables(PROJECT_ID, env_id, service_id, SLACK_TOKENS)
    
    if "errors" in result:
        print(f"❌ Error setting variables: {result['errors']}")
    else:
        print("✅ All Slack tokens set!")
        print("\n🚀 Slack integration ready!")


if __name__ == "__main__":
    main()
