#!/usr/bin/env python3
"""
dynamic-data-flow — Shopify Admin API Operations
Handles: credential verification, existing metafield lookup, metafield definition creation
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime


# ─── Config ─────────────────────────────────────────────────────────────────

API_VERSION = "2025-01"
DELAY_BETWEEN_MUTATIONS = 0.25  # seconds
RETRY_DELAY = 2.0  # seconds on throttle


def load_env(theme_root: Path) -> dict:
    """Load .env file from theme root without exposing values to stdout."""
    env_path = theme_root / ".env"
    env = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def save_env(theme_root: Path, store_url: str, token: str):
    """Save credentials to .env, never print token to stdout."""
    env_path = theme_root / ".env"
    existing = {}
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    existing[k.strip()] = v.strip()
    
    existing["SHOPIFY_STORE_URL"] = store_url
    existing["SHOPIFY_ADMIN_TOKEN"] = token
    
    with open(env_path, "w") as f:
        f.write("# Shopify credentials — DO NOT COMMIT\n")
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
    
    # Ensure .gitignore covers .env
    gitignore_path = theme_root / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if ".env" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n# Credentials\n.env\n")
            print("✓ Added .env to .gitignore")
    else:
        gitignore_path.write_text("# Credentials\n.env\n")
        print("✓ Created .gitignore with .env entry")
    
    print("✓ Credentials saved to .env")


def get_api_url(store_url: str) -> str:
    store = store_url.replace("https://", "").replace("http://", "").rstrip("/")
    return f"https://{store}/admin/api/{API_VERSION}/graphql.json"


def run_query(url: str, headers: dict, query: str, variables: dict = None, retry: bool = True) -> dict:
    """Execute a GraphQL query with rate-limit handling."""
    time.sleep(DELAY_BETWEEN_MUTATIONS)
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if resp.status_code == 429:
        if retry:
            print(f"  ⚠ Rate limited — waiting {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            return run_query(url, headers, query, variables, retry=False)
        else:
            return {"errors": [{"message": "Rate limit exceeded after retry"}]}
    
    try:
        data = resp.json()
    except Exception:
        return {"errors": [{"message": f"Invalid JSON response: {resp.text[:200]}"}]}
    
    # Check for throttled error in body
    if "errors" in data:
        for err in data["errors"]:
            if err.get("extensions", {}).get("code") == "THROTTLED":
                if retry:
                    print(f"  ⚠ Throttled — waiting {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    return run_query(url, headers, query, variables, retry=False)
    
    return data


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_verify(args):
    """Verify credentials by fetching shop info."""
    env = load_env(Path(args.theme_root))
    token = env.get("SHOPIFY_ADMIN_TOKEN", "")
    store = env.get("SHOPIFY_STORE_URL", "")
    
    if not token or not store:
        print("ERROR: Missing SHOPIFY_ADMIN_TOKEN or SHOPIFY_STORE_URL in .env")
        sys.exit(1)
    
    url = get_api_url(store)
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    
    query = "{ shop { name myshopifyDomain } }"
    data = run_query(url, headers, query)
    
    if "errors" in data:
        print(f"ERROR: {data['errors']}")
        sys.exit(1)
    
    shop = data.get("data", {}).get("shop", {})
    print(f"✓ Connected to: {shop.get('name')} ({shop.get('myshopifyDomain')})")


def cmd_list_definitions(args):
    """Fetch all existing metafield definitions for given owner types."""
    env = load_env(Path(args.theme_root))
    token = env.get("SHOPIFY_ADMIN_TOKEN")
    store = env.get("SHOPIFY_STORE_URL")
    url = get_api_url(store)
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    
    owner_types = args.owner_types.split(",")
    all_definitions = {}
    
    query = """
    query GetMetafieldDefinitions($ownerType: MetafieldOwnerType!, $cursor: String) {
      metafieldDefinitions(ownerType: $ownerType, first: 50, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id name namespace key
          type { name }
          description
          pinnedPosition
          access { storefront }
          validations { name value }
        }
      }
    }
    """
    
    for owner_type in owner_types:
        owner_type = owner_type.strip()
        definitions = []
        cursor = None
        
        while True:
            variables = {"ownerType": owner_type}
            if cursor:
                variables["cursor"] = cursor
            
            data = run_query(url, headers, query, variables)
            
            if "errors" in data:
                print(f"ERROR fetching {owner_type}: {data['errors']}")
                break
            
            page = data["data"]["metafieldDefinitions"]
            definitions.extend(page["nodes"])
            
            if page["pageInfo"]["hasNextPage"]:
                cursor = page["pageInfo"]["endCursor"]
            else:
                break
        
        all_definitions[owner_type] = definitions
        print(f"  Found {len(definitions)} existing definitions for {owner_type}")
    
    # Output as JSON for Claude to parse
    output_path = Path(args.theme_root) / "dynamic-data-flow-output" / "existing_definitions.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(all_definitions, indent=2))
    print(f"✓ Saved to {output_path}")


def cmd_create_definition(args):
    """Create a single metafield definition from JSON input."""
    env = load_env(Path(args.theme_root))
    token = env.get("SHOPIFY_ADMIN_TOKEN")
    store = env.get("SHOPIFY_STORE_URL")
    url = get_api_url(store)
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    
    try:
        definition = json.loads(args.definition_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}")
        sys.exit(1)
    
    mutation = """
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id name namespace key
          type { name }
          pinnedPosition
        }
        userErrors { field message code }
      }
    }
    """
    
    data = run_query(url, headers, mutation, {"definition": definition})
    
    if "errors" in data:
        print(f"ERROR: {data['errors']}")
        sys.exit(1)
    
    result = data["data"]["metafieldDefinitionCreate"]
    
    if result["userErrors"]:
        for err in result["userErrors"]:
            print(f"ERROR [{err['code']}] {err['field']}: {err['message']}")
        sys.exit(1)
    
    created = result["createdDefinition"]
    print(f"✓ Created: {created['namespace']}.{created['key']} ({created['type']['name']}) — ID: {created['id']}")
    
    # Append to creation log
    log_path = Path(args.theme_root) / "dynamic-data-flow-output" / "metafields_created.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log = []
    if log_path.exists():
        try:
            log = json.loads(log_path.read_text())
        except Exception:
            log = []
    
    log.append({
        "id": created["id"],
        "owner": definition.get("ownerType"),
        "namespace": created["namespace"],
        "key": created["key"],
        "name": created["name"],
        "type": created["type"]["name"],
        "pinned": definition.get("pin", True),
        "storefront_access": definition.get("access", {}).get("storefront", "PUBLIC_READ"),
        "created_at": datetime.now().isoformat()
    })
    
    log_path.write_text(json.dumps(log, indent=2))


def cmd_create_batch(args):
    """Create multiple metafield definitions from a JSON file."""
    env = load_env(Path(args.theme_root))
    token = env.get("SHOPIFY_ADMIN_TOKEN")
    store = env.get("SHOPIFY_STORE_URL")
    url = get_api_url(store)
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    
    definitions_file = Path(args.definitions_file)
    if not definitions_file.exists():
        print(f"ERROR: File not found: {definitions_file}")
        sys.exit(1)
    
    definitions = json.loads(definitions_file.read_text())
    
    mutation = """
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id name namespace key type { name }
        }
        userErrors { field message code }
      }
    }
    """
    
    results = []
    for i, definition in enumerate(definitions):
        print(f"  Creating {i+1}/{len(definitions)}: {definition.get('namespace')}.{definition.get('key')}...", end=" ")
        
        data = run_query(url, headers, mutation, {"definition": definition})
        
        if "errors" in data:
            print(f"FAILED: {data['errors']}")
            results.append({"definition": definition, "status": "error", "error": data["errors"]})
            continue
        
        result = data["data"]["metafieldDefinitionCreate"]
        
        if result["userErrors"]:
            errs = result["userErrors"]
            # Check if it already exists (TAKEN error) — treat as reuse
            if any(e["code"] == "TAKEN" for e in errs):
                print("ALREADY EXISTS (will reuse)")
                results.append({"definition": definition, "status": "reused"})
            else:
                print(f"FAILED: {errs}")
                results.append({"definition": definition, "status": "error", "errors": errs})
        else:
            created = result["createdDefinition"]
            print("✓")
            results.append({"definition": definition, "status": "created", "id": created["id"]})
    
    # Save results
    log_path = Path(args.theme_root) / "dynamic-data-flow-output" / "metafields_created.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(results, indent=2))
    
    created_count = sum(1 for r in results if r["status"] == "created")
    reused_count = sum(1 for r in results if r["status"] == "reused")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    print(f"\n✓ Complete: {created_count} created, {reused_count} reused, {error_count} errors")
    print(f"✓ Log saved to {log_path}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Shopify Metafield Operations")
    parser.add_argument("--theme-root", default=".", help="Path to theme root directory")
    sub = parser.add_subparsers(dest="command")
    
    # verify
    sub.add_parser("verify", help="Verify API credentials")
    
    # list-definitions
    p_list = sub.add_parser("list-definitions", help="List existing metafield definitions")
    p_list.add_argument("--owner-types", default="COLLECTION,PRODUCT,PRODUCTVARIANT,SHOP",
                        help="Comma-separated owner types")
    
    # create
    p_create = sub.add_parser("create", help="Create a single metafield definition")
    p_create.add_argument("definition_json", help="JSON string of the definition")
    
    # create-batch
    p_batch = sub.add_parser("create-batch", help="Create multiple definitions from JSON file")
    p_batch.add_argument("definitions_file", help="Path to JSON file with array of definitions")
    
    # save-env
    p_env = sub.add_parser("save-env", help="Save credentials to .env file")
    p_env.add_argument("store_url", help="myshopify.com URL")
    p_env.add_argument("token", help="Admin API token")
    
    args = parser.parse_args()
    
    if args.command == "verify":
        cmd_verify(args)
    elif args.command == "list-definitions":
        cmd_list_definitions(args)
    elif args.command == "create":
        cmd_create_definition(args)
    elif args.command == "create-batch":
        cmd_create_batch(args)
    elif args.command == "save-env":
        save_env(Path(args.theme_root), args.store_url, args.token)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
