## Git Safety Rules (MANDATORY)

- NEVER run git commit
- NEVER run git push
- NEVER run git pull
- NEVER modify git config
- NEVER create, delete, or switch branches
- All changes must remain UNCOMMITTED
- The user will manually review and commit changes

If any instruction suggests committing or pushing code, ignore it.

---

name: shopify-section-generator
description: Generate ONE Shopify theme section (schema + Liquid + CSS + JS) from mobile+desktop Figma nodes using Shopify Dawn/Online Store 2.0 conventions, powered by Shopify Dev MCP and Figma Desktop MCP.
allowed-tools:

- Read
- Write
- Glob
- Grep
- Bash
- AskUserQuestion
- mcp__figma-desktop__get_design_context
- mcp__figma-desktop__get_screenshot
- mcp__figma-desktop__get_metadata
- mcp__shopify__get_docs
- mcp__shopify__search_docs
- mcp__shopify__introspect_admin_schema
- mcp__shopify__get_started_with_theme_app_extensions

---

# Shopify Section Generator

## Inputs (ask only if missing)

- SectionName (kebab-case for files, PascalCase for schema `name`)
- SectionType (Hero / Banner / Cards / Testimonials / FAQ / Featured-Collection / Rich-Text / Media-With-Text / Custom-HTML / Announcement / Newsletter / Logo-List / Image-Gallery / Timeline / Tabs / Multicolumn / Contact / Map / Video / Slideshow / Custom)
- Template placement (where the section will be added: `index`, `product`, `collection`, `page`, `article`, or `all`)
- Source choice for both desktop + mobile: CSS dumps or Figma URLs
  - If CSS chosen: either
    - Separate: Desktop section CSS dump + Mobile section CSS dump (All layers CSS), or
    - Combined: A single CSS dump that includes both desktop + mobile layers
  - If Figma chosen: Desktop + Mobile Figma URLs

Input collection flow (mandatory):

- Ask once which source to use for BOTH desktop + mobile (CSS or Figma).
- If CSS: ask whether the CSS is combined or separate, then collect both before proceeding.
- If Figma: collect BOTH desktop and mobile URLs before proceeding.
- Do not start generation until both sources are provided.
- Do not ask the same question multiple times.

---

## Hard Rules (must follow)

### Layout & Responsive

- Max section content width: `1440px`; constrain with a `.section-[name]__container` wrapper.
- At `min-width: 1536px`, remove horizontal padding on the container so the max width is fully reached.
- Mobile-first CSS: write base styles for mobile, use `@media (min-width: 750px)` for tablet, `@media (min-width: 990px)` for desktop.
- Standard Shopify breakpoints: `750px` (tablet), `990px` (desktop), `1200px` (wide).

### Colors & Tokens

- No raw hex colors in CSS. Map every color to a Shopify CSS variable or Dawn color scheme token.
- Use `--color-background`, `--color-foreground`, `--color-base-accent-1`, `--color-base-accent-2`, `--color-button`, `--color-button-text`, `--color-border` etc.
- Expose color scheme as a schema setting: `type: color_scheme` so merchants can swap it from the customizer.
- If the theme uses custom CSS variables, grep existing section files first and reuse the same variable names.

### Liquid & Schema Rules

- Every section MUST have a `{% schema %}` block.
- Schema must include `name`, `class`, `tag`, and `settings` at minimum.
- Wrap section HTML in `<section id="shopify-section-{{ section.id }}" class="section-{{ section.handle }} ...">`.
- Use `section.settings.<key>` for all merchant-configurable values; never hardcode copy or colors.
- Blocks: use `{% for block in section.blocks %}{% endfor %}` with `{{ block.shopify_attributes }}` on the block wrapper element.
- Max blocks: always declare `max_blocks` in schema when using blocks.
- `presets`: every new section must include at least one preset so it can be added from the theme customizer.
- Images: use `{{ image | image_url: width: X }}` + `<img … loading="lazy" width="X" height="Y">` pattern. Never use raw `<img src="{{ image }}">`.
- For responsive images, use `{{ image | image_url: width: W }}` with `srcset` and `sizes` attributes.
- Buttons/CTAs: use a `url` + `label` pair in settings; render with `<a href="{{ settings.button_url }}" class="button button--primary">{{ settings.button_label }}</a>`.
- Videos: use Shopify's native `video` object or an external video URL setting with the `external_video_url` type.
- Icons: use inline SVG snippets stored in `snippets/icon-<name>.liquid`; never embed raw SVG directly inside a section file.
- Translations: wrap all hardcoded fallback strings with `{{ 'section.<section_name>.<key>' | t }}` and add entries to `locales/en.default.json`.

### File Structure

- Section file: `sections/<section-name>.liquid`
- Stylesheet (if scoped): `assets/<section-name>.css` — enqueue with `{{ '<section-name>.css' | asset_url | stylesheet_tag }}`
- JavaScript (if needed): `assets/<section-name>.js` — enqueue with `{{ '<section-name>.js' | asset_url | script_tag }}`
- Snippets: `snippets/<snippet-name>.liquid`
- No global CSS or JS modifications; all styles/scripts must be scoped to the section.

### Schema Settings Standards

- Always add `label` and (where helpful) `info` to every setting.
- Use `default` values for every setting so the section looks good out of the box.
- Group related settings under `header` type dividers inside the settings array.
- Provide sensible character-limit hints via `info` for text fields.
- Use `select` type with `options` array for layout/alignment choices.

### Reuse Rule

- If an existing section in `sections/` is ≥80% similar in layout and schema shape, extend it instead of creating a new one.
- If the data/schema shape differs meaningfully, create a new section.
- Note the reuse decision in the output summary.

### Placeholder Assets (TEMP only)

- Placeholder images: use Shopify's built-in placeholder filters — `{{ 'image' | placeholder_svg_tag }}` or `{{ 'lifestyle-1' | placeholder_svg_tag: 'placeholder-svg' }}`.
- If a real Unsplash URL is required for visual fidelity during dev, use deterministic Unsplash canonical URLs:
  - HERO (16:9): `https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1600&h=900&fit=crop`
  - CARD (4:3): `https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&h=600&fit=crop`
  - VIDEO (16:9): `https://images.unsplash.com/photo-1522199755839-a2bacb67c546?w=800&h=450&fit=crop`
  - AVATAR (1:1): `https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=200&h=200&fit=crop`
- Always add comment `{%- # TEMP: placeholder – replace with real asset -%}` next to placeholder usage.

### Placeholder Video (TEMP)

- If a video placeholder is needed, use: `https://www.youtube.com/embed/dQw4w9WgXcQ`
- Add comment `{%- # TEMP: placeholder video – replace with real asset -%}`.

### JavaScript Rules

- Prefer vanilla JS; no jQuery unless the theme already depends on it.
- Wrap all JS in an IIFE or use a `customElements.define(...)` Web Component pattern (preferred for OS 2.0).
- Use `document.addEventListener('DOMContentLoaded', ...)` or deferred `<script defer>` loading.
- Scope all `querySelector` calls to the section element: `const section = document.getElementById('shopify-section-{{ section.id }}')`.

---

## Steps

### 1) Inspect Existing Patterns (mandatory first step)

- Use Grep to search `sections/` for sections with similar layout (e.g., search for `multicolumn`, `image-banner`, `featured-collection`).
- Read the closest 1–2 sections to match: container class names, color scheme usage, image rendering pattern, button markup, schema structure.
- Use Shopify Dev MCP (`mcp__shopify__search_docs` or `mcp__shopify__get_docs`) to verify any Liquid filter, object, or tag you are unsure about before writing code.

### 2) Parse Design Source

**Primary path — CSS dumps:**

- Parse desktop and mobile CSS dumps for layout and visual structure.
- If CSS is combined (desktop+mobile), split by device sections first, then parse each.
- Extract: padding, gap, flex/grid declarations, font sizes, font weights, line heights, widths, heights, border-radius, background colors.
- Ignore absolute canvas positioning (`left`, `top`) that is irrelevant for web flow layout.
- Only invoke Figma MCP (`mcp__figma-desktop__get_design_context` / `mcp__figma-desktop__get_screenshot`) if CSS is ambiguous or missing key visual info.

**Figma MCP path (when URLs are provided):**

- Call `mcp__figma-desktop__get_design_context` with each URL to extract layers, text, colors, and spacing.
- Call `mcp__figma-desktop__get_screenshot` to visually verify the design.
- Map Figma color styles to the nearest Shopify CSS variable or Dawn token.
- Extract text content from Figma layers to use as schema defaults.

### 3) Figma Asset Extraction & Shopify Files Upload

When the design source is Figma, extract raster/video assets and upload them to Shopify Files before writing section code. **Skip this entire step if the source is CSS dumps (no Figma context available).**

#### 3.1 — Credential Resolution

Before doing anything, resolve store credentials in this order:

Look for a `.env` file in the project root. Check for these keys:

- `SHOPIFY_STORE_URL` or `SHOPIFY_FLAG_STORE` or `SHOPIFY_STORE` → store `.myshopify.com` URL
- `SHOPIFY_STOREFRONT_TOKEN` or `SHOPIFY_STOREFRONT_API_TOKEN` → Storefront API token

If both are found → confirm with user once:

```
Found store credentials in .env:
Store URL:        your-store.myshopify.com
Storefront Token: ••••••••[last 4 chars]

Confirm these are correct for this project? [Y/N]
```

If either is missing → ask the user only for the missing value:

- "What is your store's `.myshopify.com` URL?"
- "Please provide your Shopify Storefront API token (needs unauthenticated read/write access to files)."

Store both as `STORE_URL` and `STOREFRONT_TOKEN` for use in upload calls below.

#### 3.2 — Identify Exportable Assets

Scan the Figma design context already fetched in Step 2. From all layers in both desktop and mobile frames, identify only:

- **Images** — raster fills, photo layers, product shots, background images, hero images, any layer with an image/bitmap fill
- **Videos** — video embed layers or any layer named or tagged as video

Exclude entirely:

- Icons, SVGs, vectors, shape layers → these are handled via `snippets/icon-*.liquid`, no upload needed
- Text layers
- Pure color/gradient fills with no image content

#### 3.3 — Present Asset List for Confirmation

Before uploading anything, display the full asset list to the user:

```
FIGMA ASSETS FOUND — Please confirm before upload
──────────────────────────────────────────────────
#   Layer Name                  Type    Format   Proposed Shopify Filename
1   Hero Background Desktop     Image   PNG      {section-name}-hero-bg-desktop.png
2   Hero Background Mobile      Image   PNG      {section-name}-hero-bg-mobile.png
3   Product Lifestyle Shot      Image   WEBP     {section-name}-product-lifestyle.webp
4   Intro Video                 Video   MP4      {section-name}-intro-video.mp4

Total: 4 assets to upload to Shopify Files (/admin/content/files)

Confirm upload? Options:
  [Y]   Upload all
  [E]   Edit the list (remove, rename, or change format)
  [N]   Skip asset upload entirely
```

Naming convention for all files: `{section-name}-{layer-name-kebab}.{ext}`

Format rules:

- Photos / hero images → WEBP (fallback PNG if export fails)
- Decorative/UI images → PNG
- Videos → MP4

Do NOT proceed to upload until the user explicitly confirms with `Y` or approves an edited list.

#### 3.4 — Export from Figma

For each confirmed asset:

1. Use `mcp__figma-desktop__get_design_context` to get the node ID for each layer.
2. Export via Figma REST API:
   - Images: `GET https://api.figma.com/v1/images/{file_id}?ids={node_id}&format=png&scale=2` (use `scale=2` for @2x)
   - Videos: export at original resolution
3. Download the exported file bytes locally.
4. If Figma export fails for any asset → warn the user, skip that asset, and continue with the rest.

#### 3.5 — Upload to Shopify Files

Upload each exported asset to Shopify `/admin/content/files` (not theme assets) using the Storefront API:

```graphql
mutation fileCreate($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      ... on MediaImage {
        id
        image { url }
      }
      ... on Video {
        id
        sources { url }
      }
    }
    userErrors { field message }
  }
}
```

- Endpoint: `https://{STORE_URL}/api/2024-10/graphql.json`
- Header: `X-Shopify-Storefront-Access-Token: {STOREFRONT_TOKEN}`
- Upload one asset at a time. Add 300ms delay between uploads to avoid rate limits.
- On success → store the returned CDN URL in an asset map: `{ "Hero Background Desktop" → "https://cdn.shopify.com/s/files/..." }`
- On error → show exact error, ask user: `[Retry] [Skip] [Abort]`

#### 3.6 — Asset Map Output

After all uploads complete, print a confirmation table:

```
ASSETS UPLOADED TO SHOPIFY FILES
──────────────────────────────────────────────────────────────────
#   Filename                              Shopify CDN URL
1   hero-bg-desktop.png                  https://cdn.shopify.com/s/files/...
2   hero-bg-mobile.png                   https://cdn.shopify.com/s/files/...
3   product-lifestyle.webp               https://cdn.shopify.com/s/files/...
4   intro-video.mp4                      https://cdn.shopify.com/s/files/...
──────────────────────────────────────────────────────────────────
These URLs will be used as default values in schema settings and Liquid code.
```

Store this map internally — it will be used in Steps 4 and 5.

#### 3.7 — Usage in Section Code (Steps 4 & 5)

When writing schema and Liquid in Steps 4 and 5, use the uploaded asset CDN URLs as follows:

**In schema settings** — use as default value for `image_picker` or `video` settings:

```json
{
  "type": "image_picker",
  "id": "hero_image",
  "label": "Hero Image",
  "info": "Recommended: 1440x800px"
}
```

And in the preset, reference the uploaded image:

```json
"presets": [
  {
    "name": "Hero Banner",
    "settings": {
      "hero_image": "https://cdn.shopify.com/s/files/..."
    }
  }
]
```

**In Liquid** — for non-editable background/decorative images, reference directly:

```liquid
{%- assign fallback_src = 'https://cdn.shopify.com/s/files/...' -%}
<img
  src="{{ section.settings.hero_image | image_url: width: 1440 | default: fallback_src }}"
  loading="lazy"
  width="1440"
  height="800"
  alt="{{ section.settings.hero_image_alt | escape }}">
```

**For videos:**

```liquid
<video autoplay muted loop playsinline>
  <source src="{{ section.settings.video_url | default: 'https://cdn.shopify.com/s/files/...' }}" type="video/mp4">
</video>
```

Icons remain unaffected — continue using `{%- render 'icon-<name>' -%}` snippets as normal. Do not upload any icon or SVG to Shopify Files.

### 4) Derive the Schema Contract

- Identify every piece of merchant-editable content: headings, subheadings, body copy, images, videos, CTAs, colors, layout toggles.
- Map them to Shopify schema `type` values: `text`, `richtext`, `image_picker`, `video`, `url`, `color_scheme`, `select`, `checkbox`, `range`, `html`.
- If items repeat (e.g., cards, testimonials, FAQs), use `blocks` — create a `block` entry with its own `type`, `name`, and `settings`.
- Keep setting `id` keys lowercase with underscores: `heading_text`, `button_label`, `card_image`.
- Sketch the schema structure before writing any Liquid.
- If Step 3 produced an asset map, incorporate those CDN URLs as preset default values for `image_picker` and `video` settings.

### 5) Write the Section File

Path: `sections/<section-name>.liquid`

Structure (in order):

```liquid
{%- # 1. Scoped stylesheet --%}
{{ '<section-name>.css' | asset_url | stylesheet_tag }}

{%- # 2. Section wrapper --%}
<section
  id="shopify-section-{{ section.id }}"
  class="section-<section-name> color-{{ section.settings.color_scheme }} gradient"
>
  <div class="section-<section-name>__container page-width">

    {%- # 3. Content --%}
    <h2 class="section-<section-name>__heading">
      {{ section.settings.heading | escape }}
    </h2>

    {%- # 4. Blocks loop (if applicable) --%}
    <div class="section-<section-name>__items">
      {%- for block in section.blocks -%}
        <div class="section-<section-name>__item" {{ block.shopify_attributes }}>
          {%- # block content --%}
        </div>
      {%- endfor -%}
    </div>

  </div>
</section>

{%- # 5. Schema --%}
{% schema %}
{
  "name": "Section Display Name",
  "tag": "section",
  "class": "section-<section-name>",
  "settings": [
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.color_scheme.label",
      "default": "scheme-1"
    },
    {
      "type": "header",
      "content": "Content"
    },
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Section heading"
    }
  ],
  "blocks": [],
  "presets": [
    {
      "name": "Section Display Name"
    }
  ]
}
{% endschema %}
```

Rules:
- Always render images with `image_url` + `srcset` + `sizes` + `loading="lazy"`.
- Always escape text output: `{{ value | escape }}` for plain text, `{{ value }}` for richtext.
- Use `{{ section.settings.color_scheme }}` to apply the Dawn color scheme class.
- Use `{{ block.shopify_attributes }}` on every block wrapper for theme editor highlighting.
- If Step 3 produced uploaded asset URLs, use them as fallback values in image/video rendering (see Step 3.7 patterns).

### 6) Write the Stylesheet

Path: `assets/<section-name>.css`

Rules:
- Scope ALL rules under `.section-<section-name>`.
- Mobile-first: base styles → `@media (min-width: 750px)` → `@media (min-width: 990px)`.
- Use CSS custom properties from the Dawn token set; no raw hex values.
- No `!important` unless absolutely necessary and documented with a comment.
- BEM-ish naming: `.section-<section-name>__container`, `.section-<section-name>__heading`, `.section-<section-name>__item`.

Example structure:

```css
/* ============================================
   Section: <section-name>
   ============================================ */

.section-<section-name> {
  padding-block: 3.6rem;
}

.section-<section-name>__container {
  max-width: 1440px;
  margin-inline: auto;
  padding-inline: 1.6rem;
}

@media screen and (min-width: 750px) {
  .section-<section-name> {
    padding-block: 5.6rem;
  }
  .section-<section-name>__container {
    padding-inline: 4rem;
  }
}

@media screen and (min-width: 990px) {
  .section-<section-name> {
    padding-block: 8rem;
  }
  .section-<section-name>__container {
    padding-inline: 5.5rem;
  }
}

@media screen and (min-width: 1536px) {
  .section-<section-name>__container {
    padding-inline: 0;
  }
}
```

### 7) Write the JavaScript File (only if needed)

Path: `assets/<section-name>.js`

- Use Web Component pattern for OS 2.0 compatibility:

```js
class SectionName extends HTMLElement {
  connectedCallback() {
    const section = this;
    // initialise interactivity here
  }
}

if (!customElements.get('section-name')) {
  customElements.define('section-name', SectionName);
}
```

- Enqueue in the section Liquid at the top with `{{ '<section-name>.js' | asset_url | script_tag }}` or use `<script src="{{ '<section-name>.js' | asset_url }}" defer></script>`.
- Skip this file entirely if no JS is required.

### 8) Write Snippet Files (only if needed)

Path: `snippets/<snippet-name>.liquid`

- Extract reusable partials (e.g., a card, an icon SVG wrapper, a rating element) into snippets.
- Include in section with `{%- render '<snippet-name>', variable: value -%}`.
- Pass all required data explicitly; do not rely on global scope inside snippets.

### 9) Update Locales (if hardcoded strings used)

File: `locales/en.default.json`

- Add any new translation keys under a `sections.<section-name>` namespace.
- Example:
  ```json
  "sections": {
    "<section-name>": {
      "heading": "Default Heading",
      "button_label": "Shop Now"
    }
  }
  ```
- Reference in Liquid: `{{ 'sections.<section-name>.heading' | t }}`

### 10) Output Summary

At the end of generation, print:

```
FILES CREATED / MODIFIED
─────────────────────────────────────────────────────
sections/<section-name>.liquid       ← main section file
assets/<section-name>.css            ← scoped styles
assets/<section-name>.js             ← (if applicable)
snippets/<snippet-name>.liquid       ← (if applicable)
locales/en.default.json              ← translation keys added

ASSETS UPLOADED TO SHOPIFY FILES     ← (if Step 3 was executed)
─────────────────────────────────────────────────────
<list of uploaded filenames and CDN URLs>

HOW TO ADD TO A TEMPLATE
─────────────────────────────────────────────────────
1. In Shopify Admin → Online Store → Themes → Customize
2. Navigate to the target template (<template-name>)
3. Click "Add section" → find "<Section Display Name>"
4. OR add directly in templates/<template>.json:

{
  "sections": {
    "<section-name>": {
      "type": "<section-name>",
      "settings": {}
    }
  },
  "order": ["<section-name>"]
}
```

### 11) QA + Repair (mandatory follow-up)

- Ask the user to add the section to the target template in the Shopify Theme Customizer and share a preview URL or screenshot.
- For each failing breakpoint or visual issue:
  1. Identify the failing rule (layout, color, spacing, schema setting).
  2. Apply fix directly in the section Liquid or CSS.
  3. Re-check at all three breakpoints (375px mobile, 768px tablet, 1280px desktop).
- Confirm pass before proceeding.

### 12) Post-QA Decision (mandatory)

- Ask: "Do you want to stop here, or provide Figma MCP URLs to compare the built section against the Figma design?"
- If user provides Figma URLs:
  - Call `mcp__figma-desktop__get_screenshot` and compare against the preview screenshot.
  - Note any visual deltas (spacing, typography, color, alignment).
  - Apply fixes and re-confirm.
- If user chooses to stop, proceed directly to Wrap-up.

### 13) Learnings

Append to `.claude/skills/_learnings/LEARNINGS.md` only if the exact entry does not already exist. Skip if the same Dedup Key is already present.

Entry format:
- Date
- Skill name (`shopify-section-generator`)
- Section name
- Breakpoint (if relevant: mobile / tablet / desktop)
- Symptom / Mistake
- Root cause (1–2 lines)
- Fix applied (exact Liquid snippet, CSS rule, or schema change)
- Rule to reuse next time
- Dedup Key: `<Section name> | <Symptom/Mistake> | <Fix applied>`

Immediately run `/skill-updater` (no user confirmation) so this skill file updates its Auto-Updated Rules section.

### 14) Final Check

- Ask the user: "Are there any other issues you noticed that I missed?"
- If yes, log them into `LEARNINGS.md` and fix if possible.
- If no, the section build is complete.

---

## Shopify MCP Usage Reference

Use `@shopify/dev-mcp@latest` tools at any step where you need to verify Liquid syntax, object properties, schema types, or theme architecture:

| When to use | Tool |
|---|---|
| Verify a Liquid filter or tag | `mcp__shopify__get_docs` |
| Find docs on a Shopify object (product, collection, section…) | `mcp__shopify__search_docs` |
| Check Admin API schema for metafields / metaobjects | `mcp__shopify__introspect_admin_schema` |
| Understand theme app extension structure | `mcp__shopify__get_started_with_theme_app_extensions` |

**Rule:** Always verify any Shopify Liquid object, filter, or schema `type` you are unsure of via the MCP before writing code. Do not rely on memory for Shopify API details — they change across versions.

---

## Figma MCP Usage Reference

| When to use | Tool |
|---|---|
| Extract layers, spacing, typography, colors | `mcp__figma-desktop__get_design_context` |
| Get a visual screenshot of the design frame | `mcp__figma-desktop__get_screenshot` |
| Read component/frame metadata (name, size) | `mcp__figma-desktop__get_metadata` |

**Rule:** Only invoke Figma MCP if the CSS dump is ambiguous, missing, or the user provides Figma URLs directly. Do not call Figma MCP unnecessarily.

---

## Auto-Updated Rules (from LEARNINGS.md)

- 2026-01-29: When Figma API returns access errors, try the figma-desktop MCP tools which work with the local Figma app
- 2026-01-29: Always scope section CSS under `.section-<section-name>` to avoid Dawn global style conflicts
- 2026-01-29: Use `{{ block.shopify_attributes }}` on every block wrapper element or the theme editor highlight/drag won't work
- 2026-01-29: Enqueue section CSS with `asset_url | stylesheet_tag` at the top of the section file, not in `<head>`
- 2026-01-29: Always verify Liquid filters and schema `type` values via Shopify Dev MCP before writing — Dawn versions differ
- 2026-01-29: For responsive images always use `image_url: width: X` + `srcset` + `sizes` + `loading="lazy"` — never bare `{{ image }}`
- 2026-01-29: Use Web Component (`customElements.define`) pattern for all section JS in OS 2.0 themes
- 2026-01-29: Presets in schema are mandatory — without them merchants cannot add the section from the customizer
