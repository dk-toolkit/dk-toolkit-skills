---
name: dynamic-data-flow
description: >
  Converts hardcoded Shopify Liquid templates into fully dynamic, metafield-driven pages.
  Use this skill whenever the user wants to make a Shopify page dynamic, add metafields to a
  Shopify template, replace hardcoded content with editable fields, or connect Shopify sections
  to product/collection/variant/shop metafields. Triggers on phrases like "make this page dynamic",
  "add metafields", "replace hardcoded content", "dynamic shopify template", "metafield-driven",
  "make sections editable", or any request involving Shopify content management via metafields.
  Also triggers when user wants to clean up section schemas or migrate settings to metafields.
---

# dynamic-data-flow

Converts hardcoded Shopify Liquid templates into clean, metafield-driven dynamic pages.
Follows a strict step-by-step interactive flow with user confirmation at each stage.

## Reference Files
- `references/metafield-types.md` — All Shopify metafield types, when to use each, Liquid syntax, filters
- `references/decision-rules.md` — Section setting vs Metafield vs Hardcoded decision framework
- `references/liquid-patterns.md` — Safe Liquid patterns, fallbacks, list rendering, translations
- `references/api-reference.md` — GraphQL mutations, queries, pagination, rate limiting
- `scripts/shopify_api.py` — Python script for all Shopify Admin API operations

**Read `references/metafield-types.md` and `references/decision-rules.md` before Step 5.**
**Read `references/liquid-patterns.md` before Step 8.**
**Read `references/api-reference.md` before Step 7.**

---

## STEP 1 — Theme Directory Detection & Validation

When the skill is invoked, first detect if the terminal is inside a valid Shopify theme directory.

**Auto-detect by checking for:**
```
config/settings_schema.json
templates/
sections/
snippets/
assets/
layout/theme.liquid
```

If detected → confirm: "Found Shopify theme at `[path]`. Proceeding with this theme. ✓"

If NOT detected → ask: "Please navigate to your Shopify theme root directory and run again, or provide the full path to the theme folder."

**Also detect store URL from:**
- `package.json` → look for `"store"` key (Shopify CLI config)
- `.shopifyignore` parent dir name
- `shopify.theme.toml` → `store` field
- `.env` file → `SHOPIFY_STORE_URL` or `SHOPIFY_FLAG_STORE`

Store this as `STORE_URL` for later API use.

---

## STEP 2 — Page / Template Selection

Ask the user which page they want to make dynamic:

```
Which page do you want to make dynamic?
1. Homepage (templates/index.json)
2. Collection page (templates/collection.*.json)
3. Product page (templates/product.*.json)
4. Page template (templates/page.*.json)
5. Blog / Article
6. Cart / Other
```

Parse `templates/` folder to show only what actually exists.

---

## STEP 3 — Specific Template Selection (if multiple exist)

If the chosen page type has multiple templates (e.g., `collection.json`, `collection.sale.json`, `collection.seasonal.json`), list them and ask which one(s) to work on.

Show the template name + any sections already assigned to it by reading the JSON.

---

## STEP 4 — Credentials Collection

**Store URL:** Use auto-detected value from Step 1. If not found, ask:
> "What is your store's myshopify URL? (e.g., `your-store.myshopify.com`)"

**Admin API Token:**
> "Please provide your Shopify Admin API Access Token."
> ⚠️ "This will be saved to `.env` in your theme root and will NOT be printed to terminal again."

Immediately write to `.env`:
```
SHOPIFY_ADMIN_TOKEN=your-token-here
SHOPIFY_STORE_URL=your-store.myshopify.com
```

Verify `.env` is in `.gitignore`. If not, add it automatically and inform the user.

**Verify credentials** by making a lightweight test API call (fetch shop name). Confirm success before proceeding.

---

## STEP 5 — Full Template Analysis & Dynamic Plan

**Read `references/decision-rules.md` and `references/metafield-types.md` now.**

Read all section files referenced in the selected template. For each section:

### 5a — Section-by-Section Audit

For each section found, display:

```
📦 SECTION: hero-banner  (sections/hero-banner.liquid)
─────────────────────────────────────────────────────
STATIC (keep hardcoded — same across all pages):
  ✓ Layout structure, spacing, font sizes

SECTION SETTINGS (theme editor — same default, overrideable per assignment):
  ⚙ overlay_opacity (already in schema as range) — KEEP AS IS
  ⚙ text_alignment — KEEP AS IS

METAFIELD CANDIDATES:
  🔵 Banner headline text → per-collection unique → collection metafield
     Type: single_line_text_field | Namespace: banner | Key: headline
     Entry type: Single value
  
  🔵 Desktop banner image → per-collection unique → collection metafield
     Type: file_reference (image) | Namespace: banner | Key: image_desktop
     Entry type: Single value
  
  🔵 Mobile banner image → per-collection unique → collection metafield  
     Type: file_reference (image) | Namespace: banner | Key: image_mobile
     Entry type: Single value
     Note: Separate mobile/desktop for art direction control
  
  🔵 CTA button label → per-collection → collection metafield
     Type: single_line_text_field | Namespace: banner | Key: cta_label
     Entry type: Single value
  
  ❓ CONFIRM NEEDED: Badge label on product cards
     Is this per-product or the same label for all products in this collection?
     → If per-product: product metafield
     → If collection-level: collection metafield
```

### 5b — Classification Rules (apply automatically, ask only when ambiguous)

Apply rules from `references/decision-rules.md`. The key question for each piece of content:

> "Is this content identical across all pages of this type, OR unique per resource instance?"
> - Same for all → Section setting (or hardcoded)
> - Unique per resource → Metafield on that resource

### 5c — User Confirmation Loop

After presenting the full plan:
```
Does this plan look correct? 
- Type YES to proceed
- Type a section name to discuss changes for that section
- Type ADD to add something I missed
- Type any corrections and I'll update the plan
```

Repeat until user confirms. Do NOT proceed to Step 6 without explicit confirmation.

---

## STEP 6 — Existing Metafield Check

Before creating anything, query all existing metafield definitions from the store.
Handle pagination (see `references/api-reference.md`).

For each planned metafield, check:
1. **Exact match** (same namespace + key + owner type) → "Already exists, will reuse ✓"
2. **Purpose match** (similar name or description, different namespace) → show it and ask:
   ```
   Found existing: custom.collection_hero_image (file_reference, COLLECTION)
   Your planned:   banner.image_desktop (file_reference, COLLECTION)
   
   These appear to serve the same purpose. Reuse existing or create new?
   [R] Reuse existing  [N] Create new  [S] Skip this field
   ```
3. **No match** → mark for creation

Build final confirmed list before proceeding to Step 7.

---

## STEP 7 — Metafield Definition Creation

**Read `references/api-reference.md` now.**

For each metafield marked for creation, confirm details with user:

```
Creating metafield 1 of 6:
─────────────────────────
Owner:       COLLECTION
Namespace:   banner
Key:         headline
Name:        Banner Headline
Type:        single_line_text_field
Pin in admin: YES (merchants can fill this in collection editor)
Storefront:  YES (readable in Liquid)
Validation:  Max 120 characters? [Y/N/custom]

Confirm? [Y] Yes  [E] Edit  [S] Skip
```

**Auto-apply these defaults:**
- `pin: true` always (so merchants see it in admin)
- `access.storefront: "PUBLIC_READ"` always (readable in Liquid)
- Suggest sensible validations based on type (see `references/metafield-types.md`)

**After each creation:** show `✓ Created: banner.headline` with the returned ID.

**Rate limiting:** Add 250ms delay between mutations. Monitor `extensions.cost` in response.

**On error:** Show the exact error message and ask user how to proceed (retry / skip / edit).

---

## STEP 8 — Liquid Code Implementation

**Read `references/liquid-patterns.md` now.**

For each section being updated:

### 8a — Replace hardcoded values

Map each confirmed metafield to its location in the Liquid code. Replace with correct syntax based on type (see `references/metafield-types.md` for type → filter mapping).

### 8b — Mandatory fallback for every dynamic field

Every metafield output MUST have a fallback. Never render a raw metafield without checking blank state.

Pattern:
```liquid
{% assign mf_headline = collection.metafields.banner.headline.value %}
<h1>{{ mf_headline | default: collection.title }}</h1>
```

For images:
```liquid
{% assign mf_img = collection.metafields.banner.image_desktop.value %}
{% if mf_img != blank %}
  <img src="{{ mf_img | image_url: width: 1440 }}" alt="{{ collection.title }}">
{% elsif collection.image != blank %}
  <img src="{{ collection.image | image_url: width: 1440 }}" alt="{{ collection.title }}">
{% endif %}
```

### 8c — Schema cleanup

Remove from `{% schema %}`:
- Any settings that have been fully replaced by metafields
- Keep settings that are page-wide defaults (not per-resource)
- Keep all layout/style settings (spacing, colors, typography)

Add a comment above removed settings:
```liquid
{% comment %} Migrated to metafields: banner.headline, banner.image_desktop {% endcomment %}
```

### 8d — Multilingual awareness

If store has multiple locales (check `locales/` folder for non-default locale files):
- Wrap metafield output in translation-aware comment
- Add note: "These metafields are not automatically translated. Use Shopify Translate & Adapt app to add translations per metafield."

### 8e — Write updated files

Save all modified section files. Show a diff summary:
```
Updated: sections/hero-banner.liquid
  - Removed 3 hardcoded strings
  - Removed 2 schema settings
  - Added 4 metafield bindings with fallbacks
```

---

## STEP 9 — QC & Validation Pass

Automatically check all modified files for:

**Liquid syntax errors:**
- Unclosed `{% if %}` / `{% for %}` / `{% schema %}` tags
- Missing `{% endunless %}`, `{% endcapture %}` etc.
- Invalid filter chains

**Metafield safety checks:**
- Every metafield read has a blank/nil check or `| default:` fallback
- file_reference fields use `image_url` or `metafield_tag` filter (NOT plain `{{ value }}`)
- rich_text_field uses `metafield_tag` filter
- List fields use `{% for %}` loop
- No raw `.value` output without filter for complex types

**Schema integrity:**
- `{% schema %}` block is valid JSON
- No orphaned settings (referenced in Liquid but removed from schema)
- No duplicate setting IDs

**Report:**
```
QC Results:
✓ Liquid syntax: PASS
✓ Fallback coverage: PASS (8/8 fields covered)
⚠ Warning: sections/product-tabs.liquid — rich_text field missing metafield_tag filter
  → Auto-fixing...
✓ Schema integrity: PASS
```

Auto-fix any critical issues found. For warnings, show the fix and apply.

---

## STEP 10 — Output Artifacts

Generate these output files in `dynamic-data-flow-output/` inside the theme root:

**`metafields_created.json`** — Full log of all metafield definitions created:
```json
[
  {
    "id": "gid://shopify/MetafieldDefinition/123",
    "owner": "COLLECTION",
    "namespace": "banner",
    "key": "headline",
    "type": "single_line_text_field",
    "name": "Banner Headline",
    "pinned": true,
    "storefront_access": "PUBLIC_READ"
  }
]
```

**`merchant-guide.md`** — How to fill in the metafields:
```markdown
# How to Fill In Your New Dynamic Fields

## Collection Pages

### Banner Headline (banner.headline)
Where: Shopify Admin → Collections → [your collection] → Metafields section
What to enter: The main headline shown in the collection banner
Example: "Summer Sale — Up to 50% Off"
Required: No (falls back to collection title if empty)
Max length: 120 characters
...
```

**`changes-summary.md`** — What was changed, section by section.

---

## STEP 11 — Final Review & Handoff

```
✅ All done! Here's what was completed:

Metafields created: 6
Sections updated: 3  
Files modified: sections/hero-banner.liquid, sections/product-grid.liquid, ...
Output files: dynamic-data-flow-output/

Please review the changes and test in your development theme before committing.

Anything look wrong or need adjustment?
```

Wait for user response. If they report issues, diagnose and fix. If all good, close out.
