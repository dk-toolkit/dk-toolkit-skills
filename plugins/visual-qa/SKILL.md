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

name: visual-qa
description: Automated Shopify theme visual QA across breakpoints using Playwright MCP (if available) or manual checklist. Tests sections built by /shopify-build-page and /shopify-section-generator against the local Shopify CLI dev server.
allowed-tools:

- Read
- Write
- Glob
- Grep
- AskUserQuestion

---

# Visual QA (Shopify)

## Overview

Run visual QA on Shopify theme sections at multiple breakpoints using the local Shopify CLI dev server (`shopify theme dev`). Detects overflow, clipping, spacing issues, and Shopify-specific problems like unscoped CSS and missing container resets.

Works globally across any Shopify project.

---

## Breakpoints

| Group    | Widths (px)                |
|----------|----------------------------|
| Mobile   | 320, 375, 390, 414         |
| Tablet   | 768, 820                   |
| Laptop   | 1024, 1280                 |
| Desktop  | 1440, 1920, 2560           |

Full list: `320, 375, 390, 414, 768, 820, 1024, 1280, 1440, 1920, 2560`

---

## Inputs (ask only if missing)

1. **Base URL** — default: `http://127.0.0.1:9292`
   - This is the Shopify CLI local dev server (`shopify theme dev`).
   - Ask user to confirm or provide a different URL if their dev server runs elsewhere.

2. **Template / Route** — which page to test. Ask user to pick or provide:

   | Template type | Example route                        |
   |---------------|--------------------------------------|
   | Home          | `/`                                  |
   | Collection    | `/collections/all` or `/collections/<handle>` |
   | Product       | `/products/<handle>`                 |
   | Page          | `/pages/<handle>`                    |
   | Blog          | `/blogs/<handle>`                    |
   | Article       | `/blogs/<handle>/<article-handle>`   |
   | Cart          | `/cart`                              |
   | Search        | `/search?q=<term>`                   |

   If the user says "collection page", ask for the collection handle or use `/collections/all`.
   If the user says "product page", ask for a product handle.

3. **Section focus** (optional) — specific section name or CSS selector to scroll to before screenshots.
   - Example: `.section-hero-banner`, `#shopify-section-hero-banner`
   - If not provided, test the full page.

4. **Breakpoint group** (optional) — `mobile`, `tablet`, `laptop`, `desktop`, or `all` (default: `all`).
   - If provided, only test breakpoints in that group.

---

## Checks (per breakpoint)

### Layout Checks
- **Horizontal overflow**: `scrollWidth > clientWidth` on `<html>` or `<body>`
- **Section container max-width**: every `.section-*__container` must not exceed `1440px` computed width
- **1536px+ gutter reset**: at viewports `>= 1536px`, section containers with `max-width: 1440px` must have `padding-inline: 0` (content should fill the full 1440px, not be 1328px or smaller)
- **Clipped/disappearing elements**: elements with `overflow: hidden` cutting off content unexpectedly
- **Full-bleed exceptions**: sections intentionally designed to be full-width (e.g., hero banners) are allowed to exceed 1440px — do not flag these

### Visual Checks
- **Spacing mismatches**: padding/margin inconsistencies between mobile and desktop
- **Typography**: font sizes, line heights, and weights should scale appropriately across breakpoints
- **Aspect ratio**: media/video blocks (e.g., 16:9) should not appear stretched or squished
- **Color scheme**: `color-{{ section.settings.color_scheme }}` classes should render correctly (no unstyled/white sections)

### Shopify-Specific Checks
- **Scoped CSS**: section styles should not leak into other sections (check for unscoped selectors like `.container`, `.heading` without `.section-*` prefix)
- **Image rendering**: images should use `srcset` and `loading="lazy"` — no broken images or missing placeholders
- **Block rendering**: if sections use blocks, verify they render and are not empty/collapsed

---

## Symptom Categories

Use these fixed categories when reporting issues:

| Symptom        | Description                                                  |
|----------------|--------------------------------------------------------------|
| `overflow`     | Horizontal scrollbar or content exceeding viewport width     |
| `clipping`     | Elements cut off or hidden unexpectedly                      |
| `misalignment` | Elements not aligned as expected (centering, flex issues)    |
| `typography`   | Font size, weight, or line-height wrong at this breakpoint   |
| `aspect-ratio` | Media/video blocks stretched or squished                     |
| `spacing`      | Padding/margin too large, too small, or missing              |
| `gutter`       | Container not reaching 1440px at wide screens (padding not removed) |
| `color`        | Color scheme not applied or wrong colors showing             |
| `css-leak`     | Section CSS affecting other sections or global Dawn styles   |
| `image`        | Broken image, missing srcset, or no lazy loading             |
| `blocks`       | Section blocks not rendering or collapsed                    |

---

## Process

### Step 1: Identify the Template and Sections

- Read the relevant template JSON file to know which sections are on the page:
  - Home → `templates/index.json`
  - Collection → `templates/collection.json` or `templates/collection.<handle>.json`
  - Product → `templates/product.json` or `templates/product.<handle>.json`
  - Page → `templates/page.<handle>.json`
  - Blog → `templates/blog.json`
  - Article → `templates/article.json`
- List all sections in the `"order"` array — these are the sections to QA.
- If the user specified a section focus, identify just that section.

### Step 2: Pre-QA Code Review (quick scan)

Before running visual tests, do a fast code review of the sections being tested:

- **Grep** for unscoped CSS selectors in `assets/<section-name>.css` files (selectors without `.section-` prefix)
- **Check** that each section file enqueues its own CSS at the top (`asset_url | stylesheet_tag`)
- **Verify** `max-width: 1440px` and `padding-inline: 0` at `1536px` exists in each section CSS
- **Check** images use `image_url` + `srcset` + `loading="lazy"` pattern
- **Check** blocks have `{{ block.shopify_attributes }}`

Report any code-level issues found before proceeding to visual testing.

### Step 3: Visual Testing (Playwright MCP)

**If Playwright MCP is available:**

1. Navigate to `<base-url><route>` (e.g., `http://127.0.0.1:9292/collections/all`)
2. For each breakpoint in the selected group:
   a. Set viewport width to the breakpoint
   b. If section focus is provided, scroll to that section/selector
   c. Take a screenshot — save to `.claude/QA-logs/screenshots/<template>_<breakpoint>px.png`
   d. Check for horizontal overflow: evaluate `document.documentElement.scrollWidth > document.documentElement.clientWidth`
   e. Check section container widths: evaluate computed width of all `.section-*__container` elements
   f. At `>= 1536px`: verify containers reach `1440px` width (no leftover padding)
   g. Record PASS or FAIL with symptom categories

**If Playwright MCP is NOT available:**

Print a manual checklist:

```
MANUAL QA CHECKLIST — <template> (<route>)
══════════════════════════════════════════════════════

For each breakpoint: 320, 375, 390, 414, 768, 820, 1024, 1280, 1440, 1920, 2560

1. Open DevTools → Toggle Device Toolbar
2. Set viewport to <width>px
3. Check:
   [ ] No horizontal scrollbar
   [ ] No clipped/hidden elements
   [ ] Section containers do not exceed 1440px
   [ ] At 1536px+: containers reach full 1440px (no padding gutters)
   [ ] Spacing and typography look correct
   [ ] Images load with proper sizing
   [ ] Video/media aspect ratios are correct
   [ ] Color schemes are applied
   [ ] No CSS leaking between sections
```

### Step 4: QA Report

Generate a QA log file at `.claude/QA-logs/<YYYY-MM-DD>_<template-name>_qa.md`:

```markdown
# Visual QA Report

- Date: <YYYY-MM-DD>
- Project: <project folder name>
- Template: <template file>
- Route: <tested URL>
- Sections tested: <list>
- Method: Playwright / Manual

## Results

### 320px — PASS / FAIL
- Symptoms: <list or "none">
- Notes: <details>
- Suspected section: <section name>

### 375px — PASS / FAIL
...

## Code Review Issues
- <any issues found in Step 2>

## Summary
- Total breakpoints: <count>
- Passed: <count>
- Failed: <count>
- Failing sections: <list>
```

Save all screenshots under `.claude/QA-logs/screenshots/` — no screenshots outside this folder.

### Step 5: Fix Failing Sections

After reporting, ask:

> "Do you want me to fix the failing breakpoints now?"

If yes:
- For each failing section + breakpoint, identify the root cause (layout, spacing, overflow, CSS)
- Apply fixes directly in the section `.liquid` and/or `.css` files
- Re-run visual tests on the fixed breakpoints to confirm the fix
- Repeat until all breakpoints pass or user says to stop

If no:
- Proceed to Learnings.

### Step 6: Learnings

Append to `.claude/skills/_learnings/LEARNINGS.md` only if the exact entry does not already exist. Skip if the same Dedup Key is present.

Entry format:
- Date
- Skill name (`visual-qa`)
- Section/Page name
- Breakpoint
- Symptom / Mistake
- Root cause (1–2 lines)
- Fix applied
- Rule to reuse next time
- Dedup Key: `<Section/Page> | <Symptom> | <Fix>`

### Step 7: Final Check

- Ask the user: "Are there any other issues you noticed that I missed?"
- If yes, log them into `LEARNINGS.md` and fix if possible.
- If no, QA is complete.

---

## Rules

- Do NOT close the browser, tabs, or the Shopify dev server after testing.
- Do NOT add new random placeholder images during fixes — reuse the canonical placeholders from the skill rules.
- Do NOT modify template JSON files during QA — only fix section `.liquid` and `.css` files.
- Always test the **related template only** — if the user built a collection page, test the collection route, not the home page.
- QA log files and screenshots go in the **project-level** `.claude/QA-logs/` directory (not global).

---

## Auto-Updated Rules (from LEARNINGS.md)

<!-- Rules will be appended here by /skill-updater -->
