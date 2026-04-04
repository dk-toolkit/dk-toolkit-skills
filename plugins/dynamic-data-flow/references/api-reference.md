# Shopify Admin API Reference

## Endpoint
```
POST https://{store}.myshopify.com/admin/api/2025-01/graphql.json
```

Headers:
```
Content-Type: application/json
X-Shopify-Access-Token: {token}
```

API Version: Use `2025-01` (update to latest stable annually)

---

## 1. Verify Credentials (Test Call)

```graphql
query {
  shop {
    name
    myshopifyDomain
    primaryDomain { url }
  }
}
```

Expected: Returns shop name. If 401 → bad token. If 403 → missing scopes.

---

## 2. Fetch All Existing Metafield Definitions (with pagination)

```graphql
query GetMetafieldDefinitions($ownerType: MetafieldOwnerType!, $cursor: String) {
  metafieldDefinitions(
    ownerType: $ownerType
    first: 50
    after: $cursor
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      name
      namespace
      key
      type { name }
      description
      pinnedPosition
      access {
        storefront
      }
      validations {
        name
        value
      }
    }
  }
}
```

Variables: `{ "ownerType": "COLLECTION" }` (or PRODUCT, PRODUCTVARIANT, SHOP, etc.)

**Pagination loop:** Keep fetching with `after: endCursor` until `hasNextPage == false`.

Run this for EACH owner type relevant to the template being processed.

---

## 3. Create Metafield Definition

```graphql
mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition {
      id
      name
      namespace
      key
      type { name }
      pinnedPosition
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Variables Structure

**Minimal (text field):**
```json
{
  "definition": {
    "name": "Banner Headline",
    "namespace": "banner",
    "key": "headline",
    "type": "single_line_text_field",
    "ownerType": "COLLECTION",
    "pin": true,
    "access": {
      "storefront": "PUBLIC_READ"
    }
  }
}
```

**With description:**
```json
{
  "definition": {
    "name": "Banner Headline",
    "namespace": "banner",
    "key": "headline",
    "description": "Main headline text shown in the collection banner section",
    "type": "single_line_text_field",
    "ownerType": "COLLECTION",
    "pin": true,
    "access": {
      "storefront": "PUBLIC_READ"
    }
  }
}
```

**With validations (text length):**
```json
{
  "definition": {
    "name": "Banner Headline",
    "namespace": "banner",
    "key": "headline",
    "type": "single_line_text_field",
    "ownerType": "COLLECTION",
    "pin": true,
    "access": { "storefront": "PUBLIC_READ" },
    "validations": [
      { "name": "max", "value": "120" }
    ]
  }
}
```

### Validation Names by Type

| Type | Validation name | Value example |
|---|---|---|
| `single_line_text_field` | `min`, `max` | `"5"`, `"120"` (character count) |
| `multi_line_text_field` | `min`, `max` | `"10"`, `"2000"` |
| `number_integer` | `min`, `max` | `"0"`, `"100"` |
| `number_decimal` | `min`, `max` | `"0.0"`, `"999.99"` |
| `file_reference` | `file_type_options` | `["Image"]`, `["Image", "Video"]` |
| `url` | `allowed_domains` | `["example.com", "cdn.example.com"]` |
| `date`, `date_time` | `min`, `max` | ISO date strings |
| `rating` | `scale_min`, `scale_max` | `"1"`, `"5"` |

### Access Values

| Value | Meaning |
|---|---|
| `"PUBLIC_READ"` | Readable in Liquid and Storefront API (recommended default) |
| `"PRIVATE"` | Only readable via Admin API (use for sensitive data) |

### Owner Type Values (for GraphQL)

```
COLLECTION
PRODUCT
PRODUCTVARIANT
PAGE
BLOG
ARTICLE
SHOP
CUSTOMER
ORDER
LOCATION
```

---

## 4. Delete Metafield Definition (if needed)

```graphql
mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
  metafieldDefinitionDelete(
    id: $id
    deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields
  ) {
    deletedDefinitionId
    userErrors {
      field
      message
    }
  }
}
```

Variables:
```json
{
  "id": "gid://shopify/MetafieldDefinition/123456",
  "deleteAllAssociatedMetafields": false
}
```

⚠️ Set `deleteAllAssociatedMetafields: false` by default. Only set `true` if explicitly asked.

---

## 5. Update Metafield Definition

```graphql
mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!, $id: ID!) {
  metafieldDefinitionUpdate(definition: $definition, id: $id) {
    updatedDefinition {
      id
      name
    }
    userErrors {
      field
      message
    }
  }
}
```

---

## Error Codes

| Code | Meaning | Action |
|---|---|---|
| `TAKEN` | namespace+key already exists for this owner | Reuse or pick new key |
| `INVALID` | Invalid type or value | Check type spelling |
| `TOO_LONG` | Name/key too long | Shorten |
| `BLANK` | Required field empty | Add value |
| `RESERVED` | Namespace is reserved (e.g., `global`) | Change namespace |
| `UNSTRUCTURED_ALREADY_EXISTS` | Unstructured metafield with same key exists on a resource | Warn user: existing data may conflict |

---

## Rate Limiting

Shopify uses a **query cost** system (not simple request count).

- Budget: 1000 points/second, refills at 50 points/second
- Each mutation costs ~10 points
- Check `extensions.cost.actualQueryCost` in every response

**Safe defaults:**
- Add `250ms` delay between each mutation (conservative, avoids all throttling)
- If response includes `Throttled` error: back off 2 seconds and retry once
- For bulk creation (>20 fields): add `500ms` delay

**Python snippet for rate-limit-safe loop:**
```python
import time

def create_with_retry(session, url, headers, mutation, variables, delay=0.25):
    time.sleep(delay)
    response = session.post(url, json={"query": mutation, "variables": variables}, headers=headers)
    data = response.json()
    
    if "errors" in data:
        # Check for throttling
        for err in data["errors"]:
            if err.get("extensions", {}).get("code") == "THROTTLED":
                print("Rate limited — waiting 2s...")
                time.sleep(2)
                return create_with_retry(session, url, headers, mutation, variables, delay)
    
    return data
```

---

## Required API Scopes

For this skill, ensure the Shopify app has these Admin API scopes:
- `write_metafield_definitions` — Create/update/delete metafield definitions
- `read_metafield_definitions` — Query existing definitions
- `write_metafields` — Write metafield values (if needed)
- `read_products` — For product metafield work
- `read_collections` — For collection metafield work
- `read_product_listings` — For variant access

Grant scopes in: Shopify Admin → Settings → Apps → Develop apps → [Your App] → Configuration → Admin API access scopes
