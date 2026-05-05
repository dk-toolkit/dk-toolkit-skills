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
- Template placement (`index`, `product`, `collection`, `page`, `article`, or `all`)
- Source choice for both desktop + mobile: CSS dumps or Figma URLs
  - CSS: separate (desktop + mobile dumps) or combined (single dump with both)
  - Figma: Desktop + Mobile Figma URLs

Input flow: Ask source once for both devices. If CSS: ask whether combined or separate, then collect both. If Figma: collect both URLs. Do not start until both sources are provided. Do not repeat questions.

---

## Hard Rules (must follow)

### Layout & Responsive

- Max content width: `1440px`; constrain with `.section-[name]__container` wrapper.
- At `min-width: 1536px`, remove horizontal padding so max width is fully reached.
- Mobile-first CSS: base → `@media (min-width: 750px)` tablet → `@media (min-width: 990px)` desktop.
- Standard breakpoints: `750px`, `990px`, `1200px` (wide).

### Colors & Tokens

- No raw hex colors. Map to Shopify CSS variables / Dawn tokens.
- Use `--color-background`, `--color-foreground`, `--color-base-accent-1`, etc.
- Expose `color_scheme` schema setting. Grep existing sections for custom variable names.

### Liquid & Schema Rules

- Every section MUST have `{% schema %}` with `name`, `class`, `tag`, `settings`.
- Wrap in `<section id="shopify-section-{{ section.id }}" class="section-{{ section.handle }}">`.
- Use `section.settings.<key>` for all configurable values; never hardcode.
- Blocks: `{% for block in section.blocks %}` with `{{ block.shopify_attributes }}` on wrapper.
- Always declare `max_blocks`. Always include `presets`.
- Images: `image_url: width: X` + `srcset` + `sizes` + `loading="lazy"`. Never bare `{{ image }}`.
- Buttons: `url` + `label` pair → `<a href="{{ settings.button_url }}" class="button button--primary">`.
- Videos: native `video` object or `external_video_url` type.
- Icons: `snippets/icon-<name>.liquid`; never raw SVG in section files.
- Translations: `{{ 'section.<name>.<key>' | t }}` + add to `locales/en.default.json`.

### File Structure

- Section: `sections/<section-name>.liquid`
- CSS: `assets/<section-name>.css` — enqueue with `asset_url | stylesheet_tag`
- JS: `assets/<section-name>.js` — enqueue with `asset_url | script_tag`
- Snippets: `snippets/<snippet-name>.liquid`
- No global CSS/JS modifications; everything scoped to the section.

### Schema Settings Standards

- Always add `label` and `info` to every setting. Use `default` values.
- Group related settings under `header` dividers.
- Use `select` type with `options` for layout/alignment choices.

### Section Height Control

For full-width sections (hero banners, image/video banners, slideshows): provide a `section_height` select setting with options `auto` (default), `small`, `medium`, `large`. Apply height modifier class on the `<section>` tag only when not `auto`. Define responsive `min-height` values in CSS for each size across breakpoints. Do NOT add to non-full-width sections (cards, FAQs, text blocks, logo lists).

**Read `references/height-control.md` for schema, Liquid, and CSS patterns.**

### Responsive Asset Handling (Desktop & Mobile)

For sections with hero/banner/background images or videos: provide separate `image_desktop` + `image_mobile` (or `video_desktop` + `video_mobile`) schema fields. Mobile is always optional — fallback to desktop via `| default: desktop_image`. Use `<picture>` + `<source media="...">` for image art direction. For videos, CSS show/hide is acceptable. Never hide/show two `<img>` tags with CSS. Apply to hero banners, image banners, video sections, slideshows. Do not apply to card thumbnails or icons.

**Read `references/responsive-assets.md` for schema, Liquid, and CSS patterns.**

### Reuse Rule

- If existing section ≥80% similar in layout/schema, extend it. Otherwise create new.
- Note reuse decision in output summary.

### Placeholder Assets (TEMP only)

- Use `{{ 'image' | placeholder_svg_tag }}` or `{{ 'lifestyle-1' | placeholder_svg_tag: 'placeholder-svg' }}`, or canonical Unsplash URLs:
  - HERO (16:9): `https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1600&h=900&fit=crop`
  - CARD (4:3): `https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&h=600&fit=crop`
  - VIDEO (16:9): `https://images.unsplash.com/photo-1522199755839-a2bacb67c546?w=800&h=450&fit=crop`
  - AVATAR (1:1): `https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=200&h=200&fit=crop`
- Add `{%- # TEMP: placeholder – replace with real asset -%}` comment.
- Placeholder video: `https://www.youtube.com/embed/dQw4w9WgXcQ` with TEMP comment.

### JavaScript — MANDATORY: Follow `js-standards` Skill

**All JS must comply with the `js-standards` skill.** Load and apply every rule before writing any `.js` file. Key enforced rules: vanilla JS only, modern ES syntax, Web Components for OS 2.0, `defer` loading, data attributes for Liquid-to-JS, event delegation, `fetch`+`async/await` for AJAX cart, pub/sub via custom events, full a11y. STRICT: NO inline styles, NO DOM creation via innerHTML, NO price formatting in JS, NO inline `<script>` tags.

---

## Steps

### 1) Inspect Existing Patterns (mandatory first step)

- Grep `sections/` for similar layout sections. Read closest 1–2 to match patterns.
- Use Shopify Dev MCP to verify any Liquid filter/object/tag you're unsure about.

### 2) Parse Design Source

**CSS path:** Parse desktop + mobile dumps. Extract: padding, gap, flex/grid declarations, font sizes, font weights, line heights, widths, heights, border-radius, background colors. Ignore absolute canvas positioning (`left`, `top`). Only invoke Figma MCP if CSS is ambiguous.

**Figma path:** Call `get_design_context` per URL → `get_screenshot` to verify → map colors to Dawn tokens → extract text for schema defaults.

### 3) Figma Asset Extraction & Upload (Figma source only)

**Skip if source is CSS dumps.** Read `references/figma-asset-workflow.md` and follow Steps 3.1–3.7: resolve credentials → identify exportable assets (images/videos only, not icons/SVGs) → present list for user confirmation → export from Figma → upload to Shopify Files → build asset map → use CDN URLs as defaults in schema/Liquid.

### 4) Derive the Schema Contract

- Identify all merchant-editable content (headings, subheadings, body copy, images, videos, CTAs, colors, layout toggles).
- Map to schema `type` values: `text`, `richtext`, `image_picker`, `video`, `url`, `color_scheme`, `select`, `checkbox`, `range`, `html`.
- Repeating items → use `blocks` with `type`, `name`, `settings`.
- Setting IDs: lowercase with underscores. Sketch the schema structure before writing any Liquid.
- If Step 3 produced an asset map, use CDN URLs as preset defaults.
- For full-width sections, include `section_height` setting.
- For image/video sections, include `image_desktop` + `image_mobile` fields.

### 5) Write the Section File

Path: `sections/<section-name>.liquid`

**Read `references/section-template.md` for the full Liquid template.** Follow this structure: scoped stylesheet → section wrapper with height class → responsive media → content → blocks loop → schema.

Rules: `image_url` + `srcset` + `loading="lazy"` for images. Escape text. Apply color scheme class. Use `block.shopify_attributes`. Use uploaded asset URLs as fallbacks if available.

### 6) Write the Stylesheet

Path: `assets/<section-name>.css`

**Read `references/section-template.md` for the CSS template.** Scope ALL rules under `.section-<section-name>`. Mobile-first breakpoints. Dawn CSS custom properties. BEM-ish naming. No `!important`. Include height variant classes for full-width sections (see `references/height-control.md`). Include video toggle CSS if desktop/mobile videos differ (see `references/responsive-assets.md`).

### 7) Write the JavaScript File (only if needed)

Path: `assets/<section-name>.js`

**Read `references/section-template.md` for the JS Web Component template.** Must comply with `js-standards` skill. Use Web Component for reusable components, `DOMContentLoaded` for one-off scripts. Always `defer`. Data attributes for Liquid-to-JS. Event delegation. Skip entirely if no JS needed.

### 8) Write Snippet Files (only if needed)

Extract reusable partials to `snippets/<name>.liquid`. Render with `{%- render '<name>', variable: value -%}`. Pass all data explicitly.

### 9) Update Locales

Add translation keys to `locales/en.default.json` under `sections.<section-name>` namespace.

### 10) Output Summary

Print: files created/modified, uploaded assets (if any), how to add to template.

### 11) QA + Repair (mandatory)

Ask user to add section to customizer and share preview. Fix issues at 375px, 768px, 1280px.

### 12) Post-QA Decision (mandatory)

Ask: "Stop here, or provide Figma URLs to compare?" If Figma provided → screenshot compare → fix deltas.

### 13) Learnings

Append to `plugins/_learnings/LEARNINGS.md` (skip if Dedup Key exists). Format: Date, Skill, Section, Breakpoint, Symptom, Root cause, Fix, Rule, Dedup Key. Then run `/skill-updater`.

### 14) Final Check

Ask: "Any other issues I missed?" Log and fix if yes.

---

## MCP Usage

**Read `references/mcp-reference.md` for full tool tables.** Always verify Liquid objects/filters/schema types via Shopify Dev MCP before writing code. Only invoke Figma MCP when CSS is ambiguous or user provides Figma URLs.

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
