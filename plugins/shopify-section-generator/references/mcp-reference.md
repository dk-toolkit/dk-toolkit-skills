# MCP Usage Reference

## Shopify Dev MCP (`@shopify/dev-mcp@latest`)

Use at any step where you need to verify Liquid syntax, object properties, schema types, or theme architecture.

| When to use | Tool |
|---|---|
| Verify a Liquid filter or tag | `mcp__shopify__get_docs` |
| Find docs on a Shopify object (product, collection, section…) | `mcp__shopify__search_docs` |
| Check Admin API schema for metafields / metaobjects | `mcp__shopify__introspect_admin_schema` |
| Understand theme app extension structure | `mcp__shopify__get_started_with_theme_app_extensions` |

**Rule:** Always verify any Shopify Liquid object, filter, or schema `type` you are unsure of via the MCP before writing code. Do not rely on memory — they change across versions.

## Figma Desktop MCP

| When to use | Tool |
|---|---|
| Extract layers, spacing, typography, colors | `mcp__figma-desktop__get_design_context` |
| Get a visual screenshot of the design frame | `mcp__figma-desktop__get_screenshot` |
| Read component/frame metadata (name, size) | `mcp__figma-desktop__get_metadata` |

**Rule:** Only invoke Figma MCP if the CSS dump is ambiguous, missing, or the user provides Figma URLs directly. Do not call Figma MCP unnecessarily.
