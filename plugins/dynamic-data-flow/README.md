# Dynamic Data Flow

> Converts hardcoded Shopify Liquid templates into fully dynamic, metafield-driven pages.

## What It Does

Dynamic Data Flow walks you through an 11-step interactive workflow that transforms static Shopify templates into editable, metafield-powered pages. It detects the active theme, analyzes every template for hardcoded content, creates the required metafields via the Shopify GraphQL Admin API, rewrites Liquid with proper fallbacks, and runs a QC validation pass to confirm everything renders correctly.

## Triggers

- "make this page dynamic"
- "add metafields"
- "replace hardcoded content"
- "dynamic shopify template"
- "metafield-driven"
- "make sections editable"

## Requirements

- Python 3 with the `requests` library
- Shopify Admin API access token

## Quick Start

Use one of the trigger phrases above in conversation. The plugin will guide you through theme detection, template analysis, metafield creation, Liquid implementation with fallbacks, and QC validation. Reference docs for metafield types, decision rules, Liquid patterns, and the API are bundled with the plugin.
