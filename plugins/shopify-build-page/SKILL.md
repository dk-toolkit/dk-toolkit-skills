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

name: shopify-build-page
description: Build a complete Shopify theme page from Figma (mobile+desktop) by splitting the design into sections, generating each section via /shopify-section-generator, wiring them into a template JSON, then running QA + repair.
allowed-tools:

- Read
- Write
- Glob
- Grep
- AskUserQuestion
- mcp__figma-desktop__get_metadata
- mcp__figma-desktop__get_design_context
- mcp__figma-desktop__get_screenshot
- mcp__shopify__get_docs
- mcp__shopify__search_docs
- mcp__shopify__introspect_admin_schema
- mcp__shopify__get_started_with_theme_app_extensions

---

# Shopify Build Page

## Inputs (ask only if missing)

1. **Template target** — which Shopify template this page belongs to. Examples:
   - `templates/index.json` (home page)
   - `templates/page.about.json` (custom page)
   - `templates/collection.json` (collection page)
   - `templates/product.json` (product page)
   - `templates/article.json` (blog article)
   - `templates/blog.json` (blog listing)
   - Or a new template: provide the handle (e.g., `landing-summer-sale`)

2. **Design source** — choose one:
   - Separate: Desktop page CSS dump + Mobile page CSS dump (All layers CSS)
   - Combined: A single CSS dump that includes both desktop + mobile layers
   - Figma URLs: Desktop page frame URL + Mobile page frame URL (optional, or when CSS is too messy)

3. **Section naming prefix** (optional) — a short prefix to namespace sections for this page, e.g., `about-`, `lp-sale-`. Helps avoid collisions in `sections/`. Reply with prefix or `none`.

4. **Confirm section file placement** — ask:
   > "All sections for this page will be created as `sections/<prefix><section-name>.liquid` files. Confirm, or provide a different naming convention."

---

## Global Shopify Rules (must enforce on every section)

- Max section content width: `1440px`; always use a `.section-<name>__container` wrapper with `max-width` + `margin: auto`.
- At `min-width: 1536px`, remove horizontal padding on containers so the full 1440px width is reached.
- Mobile-first CSS: base → `@media (min-width: 750px)` → `@media (min-width: 990px)` → `@media (min-width: 1200px)`.
- No raw hex colors in CSS — map to Dawn CSS token variables (`--color-background`, `--color-foreground`, etc.).
- Every section must expose a `color_scheme` schema setting so merchants can control it from the Customizer.
- Every section must include at least one `presets` entry in its schema — without it, merchants cannot add the section via the Customizer.
- Images: always use `image_url: width: X` with `srcset`, `sizes`, and `loading="lazy"`. Never bare `{{ image }}`.
- Buttons/CTAs: always render as `<a href="{{ section.settings.button_url }}" class="button button--primary">{{ section.settings.button_label }}</a>`.
- Icons: use `snippets/icon-<name>.liquid`; never embed raw SVG inside section files.
- **JavaScript: MANDATORY — follow `js-standards` skill.** All JS files must comply with every rule in the js-standards skill: vanilla JS only, modern ES syntax, Web Components for reusable components, `DOMContentLoaded` for one-off scripts, `defer` loading, data attributes for Liquid-to-JS, event delegation, `fetch`+`async/await` for AJAX cart, pub/sub via custom events, full accessibility (aria-expanded, keydown, focus trap). Strict rules: NO inline styles via JS, NO DOM creation via innerHTML, NO price formatting in JS, NO inline scripts. Validate every `.js` file against the js-standards checklist before finalizing.
- Reuse rule: If an existing section in `sections/` is ≥80% similar in layout and schema shape, extend it instead of creating a new one. Document the reuse decision in the plan.
- Placeholder images: use Shopify's `{{ 'image' | placeholder_svg_tag }}` by default, or canonical Unsplash URLs during dev (with `{%- # TEMP -%}` comment).
- Placeholder video (TEMP): use `https://www.youtube.com/embed/dQw4w9WgXcQ` with `{%- # TEMP: placeholder video – replace with real asset -%}`.
- Translations: wrap all hardcoded fallback strings with `{{ 'sections.<section-name>.<key>' | t }}` and add keys to `locales/en.default.json`.
- All section files must use `{{ block.shopify_attributes }}` on every block wrapper element for theme editor highlighting.
- Scoped CSS: every section must enqueue its own `assets/<section-name>.css` at the top of the section file. No global CSS edits.

---

## Process

### 1) Parse Page Structure from Design Source (primary path)

**CSS dump path:**
- If CSS is combined (desktop+mobile), split into device layers first.
- Split the full page CSS into per-section chunks using `/* Frame ... */` comment headings or `order:` property groupings to determine vertical flow.
- Extract desktop CSS snippet and mobile CSS snippet for each section independently.
- Only call Figma MCP (`mcp__figma-desktop__get_metadata` / `mcp__figma-desktop__get_screenshot`) if CSS is ambiguous about section boundaries or visual structure.

**Figma URL path:**
- Call `mcp__figma-desktop__get_metadata` on the page frame URL to list top-level frames/sections in order.
- Call `mcp__figma-desktop__get_design_context` on each section frame to extract layer structure, text content, spacing, and colors.
- Use `mcp__figma-desktop__get_screenshot` to visually confirm section boundaries.
- Map Figma colors to Dawn CSS token variables.

**Escalate to agent (only if needed):**
- If section boundaries remain unclear after both CSS parsing and Figma MCP metadata, escalate to an agent-reasoning step to propose a clean split.
- Ask the user minimal clarifying questions before escalating.
- Always ask for user confirmation before escalating.
- Agent output naming rule (only when escalation is used):
  - Append `-agent` suffix to section file names (e.g., `sections/<prefix>hero-agent.liquid`).
  - Use `Agent` suffix in schema `name` and CSS class (e.g., `section-hero-agent`).

---

### 2) Plan-First (do this before writing any code)

Print the full plan in page/vertical order before generating anything. For each section:

| Field | Description |
|---|---|
| **SectionName** | kebab-case (e.g., `hero-banner`, `product-grid`, `testimonials`) |
| **Schema display name** | Human-readable label shown in Customizer (e.g., "Hero Banner") |
| **Template placement** | Which template JSON this section belongs to |
| **Desktop CSS snippet** | Extracted from the full CSS dump |
| **Mobile CSS snippet** | Extracted from the full CSS dump |
| **Interactivity notes** | Slider / Accordion / Video / Marquee / Tabs / JS required? |
| **Blocks needed?** | Yes/No — if yes, list block types and their settings |
| **Files to create** | `sections/`, `assets/` CSS, `assets/` JS (if needed), `snippets/` (if needed) |
| **Reuse decision** | Existing section name + why ≥80% similar, or "new section" with reason |

> Print the plan and **wait for user confirmation** before proceeding to generation. Allow the user to adjust section order, names, or split decisions.

---

### 3) Generate Each Section

For each section in the confirmed plan, run `/shopify-section-generator` with:

- `SectionName` (kebab-case)
- `SectionType` (Hero / Cards / FAQ / etc.)
- `Template placement`
- Desktop CSS snippet for this section
- Mobile CSS snippet for this section

**Parallel generation mode (preferred when 3+ sections):**
- Spawn `/shopify-section-generator` tasks for all sections in parallel.
- Wait for all to finish before proceeding to template integration.

**Sequential mode:**
- If parallel execution is not supported, run sections one-by-one in plan order.

---

### 4) Integrate into the Template JSON

After all sections are generated, wire them into the Shopify template JSON file.

**For an existing template** (e.g., `templates/index.json`):
- Read the current file.
- Insert new sections into the `"sections"` object.
- Append section keys to the `"order"` array in the correct vertical order.
- Preserve all existing sections and their settings.

**For a new template** (e.g., `templates/page.landing-summer-sale.json`):
- Create the file from scratch with the correct structure.

Template JSON structure:

```json
{
  "sections": {
    "<section-name-1>": {
      "type": "<section-name-1>",
      "settings": {}
    },
    "<section-name-2>": {
      "type": "<section-name-2>",
      "settings": {}
    }
  },
  "order": [
    "<section-name-1>",
    "<section-name-2>"
  ]
}
```

Rules:
- Section keys in `"sections"` must be unique strings (use the section file handle, e.g., `"hero-banner"`).
- `"type"` must exactly match the section's filename without `.liquid` extension.
- `"order"` controls render order — match the Figma vertical flow.
- If a section has default block content, populate `"blocks"` under the section object:

```json
"<section-name>": {
  "type": "<section-name>",
  "settings": {},
  "blocks": {
    "block-1": {
      "type": "card",
      "settings": {
        "heading": "Default Heading"
      }
    }
  },
  "blocks_order": ["block-1"]
}
```

**Verify via Shopify MCP:**
- Use `mcp__shopify__get_docs` or `mcp__shopify__search_docs` if unsure about template JSON structure for a specific template type (e.g., product vs. collection differences).

---

### 5) Update Locales

After all sections are generated:
- Merge all new translation keys from individual sections into `locales/en.default.json`.
- Ensure no duplicate keys.
- Structure: `"sections" > "<section-name>" > "<key>"`.

---

### 6) Output Summary

Print a complete summary after template integration:

```
PAGE BUILD SUMMARY
══════════════════════════════════════════════════════
Template file:   templates/<template-name>.json
Sections built:  <count>

FILES CREATED / MODIFIED
──────────────────────────────────────────────────────
templates/<template-name>.json          ← wired & ordered
sections/<prefix>hero-banner.liquid     ← new
assets/<prefix>hero-banner.css          ← new
sections/<prefix>product-grid.liquid    ← new
assets/<prefix>product-grid.css         ← new
sections/<prefix>testimonials.liquid    ← reused (extended from testimonials.liquid)
locales/en.default.json                 ← translation keys merged

HOW TO PREVIEW
──────────────────────────────────────────────────────
1. Push theme to Shopify (or use Shopify CLI: `shopify theme dev`)
2. In Admin → Online Store → Themes → Customize
3. Navigate to the target template: <template-name>
4. All new sections are visible in the section panel

SECTION ORDER (top → bottom)
──────────────────────────────────────────────────────
1. <prefix>hero-banner
2. <prefix>product-grid
3. <prefix>testimonials
```

---

### 7) QA + Repair

- Ask the user to preview the page via `shopify theme dev` or the Shopify Theme Customizer preview URL.
- For each failing breakpoint or visual issue:
  1. Identify which section is failing (layout, color, spacing, schema, JS).
  2. Fix the issue directly in the `.liquid` and/or `.css` file.
  3. Re-check at all three breakpoints: `375px` (mobile), `768px` (tablet), `1280px` (desktop).
- Confirm all sections pass before proceeding.

**Success criteria:**
- All sections render correctly at 375px, 768px, and 1280px.
- No Liquid render errors in the Shopify preview.
- No console JS errors in the browser.
- All schema settings are editable from the Shopify Theme Customizer without breaking layout.
- Sections appear in the Customizer panel and can be reordered/removed safely.

---

### 8) Post-QA Decision (mandatory)

Ask:
> "Do you want to stop here, or provide Figma MCP URLs to compare the built page against the Figma design?"

- If user provides Figma URLs:
  - Call `mcp__figma-desktop__get_screenshot` for each section frame.
  - Compare against the live preview screenshot section-by-section.
  - Note any visual deltas: spacing, typography, color, alignment, missing elements.
  - Apply fixes directly on the affected sections.
  - Re-confirm pass before completing.
- If user chooses to stop, proceed directly to Learnings.

---

### 9) Learnings

Append to `.claude/skills/_learnings/LEARNINGS.md` only if the exact entry does not already exist. Skip if the same Dedup Key is already present.

Entry format:
- Date
- Skill name (`shopify-build-page`)
- Section/Page name
- Breakpoint (if relevant: mobile / tablet / desktop)
- Symptom / Mistake
- Root cause (1–2 lines)
- Fix applied (exact Liquid snippet, CSS rule, schema change, or template JSON fix)
- Rule to reuse next time
- Dedup Key: `<Section/Page name> | <Symptom/Mistake> | <Fix applied>`

Immediately run `/skill-updater` (no user confirmation) so this skill file updates its Auto-Updated Rules section.

---

### 10) Final Check

- Ask the user: "Are there any other issues you noticed that I missed?"
- If yes, log them into `LEARNINGS.md` and fix if possible.
- If no, the page build is complete.

---

## Success Criteria (full page)

- All section `.liquid` files render without Liquid errors.
- Template JSON is valid and all section `"type"` values match existing section filenames.
- Page is stable from `320px` to `2560px` across all sections.
- Every section is editable and reorderable in the Shopify Theme Customizer.
- No unscoped CSS leaking into other sections or global Dawn styles.
- All images use `image_url` + `srcset` + `loading="lazy"`.
- Translation keys exist in `locales/en.default.json` for all `| t` filter calls.

---

## Auto-Updated Rules (from LEARNINGS.md)

- 2026-01-29: When Figma API returns access errors, try the figma-desktop MCP tools which work with the local Figma app
- 2026-01-29: Always use `{{ block.shopify_attributes }}` on every block wrapper — missing it breaks theme editor drag/highlight
- 2026-01-29: Template JSON `"type"` must exactly match the section filename (no `.liquid` extension) — a mismatch causes a silent render failure
- 2026-01-29: Always include a `presets` entry in every section schema — sections without presets cannot be added via the Customizer
- 2026-01-29: Scope all section CSS under `.section-<name>` — unscoped rules bleed into Dawn global styles and break other sections
- 2026-01-29: Enqueue section CSS at the top of the section file with `asset_url | stylesheet_tag`, not in `layout/theme.liquid`
- 2026-02-09: At `min-width: 1536px`, set `padding-inline: 0` on the container so content reaches full 1440px — missing this leaves unwanted gutters at wide viewports
- 2026-02-09: Always verify Liquid object properties and schema `type` values via Shopify Dev MCP before writing — Dawn versions differ and memory is unreliable
