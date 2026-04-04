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

name: fcp-improvement
description: Detect, analyze, plan, implement, and validate FCP (First Contentful Paint) improvements across Homepage, PDP, and PLP pages. Runs before/after PageSpeed reports, compares results, and auto-updates skill intelligence based on learnings.
user-invocable: true
allowed-tools:

- Read
- Write
- Edit
- Bash
- WebFetch
- WebSearch
- Glob
- Grep
- AskUserQuestion

---

# FCP (First Contentful Paint) Improvement Skill

## Purpose

Focused skill for detecting, analyzing, planning, implementing, and validating FCP improvements across Homepage, PDP, and PLP pages. The primary goal is to **improve FCP as much as possible** while minimizing unnecessary processing time.

FCP measures how long it takes for the **first visible content** (text, image, SVG, or canvas) to appear on screen. It is the user's first signal that the page is loading.

---

## Step 1: Collect Required Inputs

**First Action — Ask the user for:**

1. **Homepage Preview Link** (required)
2. **PDP (Product Detail Page) Preview Link** (required)
3. **PLP (Product Listing Page) Preview Link** (required)

**Do NOT proceed until all 3 links are provided.**

Use AskUserQuestion to collect these if not already provided.

---

## Step 2: Generate Initial "Before" Reports

Once all 3 links are received, generate reports for each page.

### Reports Per Page:
- 2 reports for **Desktop**
- 2 reports for **Mobile**

### Total Reports:
- 3 Pages × 4 Reports = **12 Reports**

### API Configuration

**Google PageSpeed Insights API**

API Key (MANDATORY — hardcoded):
```
AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674
```

API URL format:
```
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&strategy={mobile|desktop}&category=performance&key={API_KEY}
```

### FCP-Focused Optimization

**Main goal is FCP improvement.** To save time and API usage:

1. **Primary extraction**: Focus on FCP-specific data from the API response
2. Extract FCP value from: `lighthouseResult.audits['first-contentful-paint'].numericValue` (in ms)
3. Extract render-blocking resources from: `lighthouseResult.audits['render-blocking-resources']`
4. Extract unused CSS from: `lighthouseResult.audits['unused-css-rules']`
5. Extract unused JS from: `lighthouseResult.audits['unused-javascript']`
6. Extract TTFB from: `lighthouseResult.audits['server-response-time'].numericValue`
7. Extract third-party impact from: `lighthouseResult.audits['third-party-summary']`
8. Extract font display from: `lighthouseResult.audits['font-display']`
9. Extract critical request chains from: `lighthouseResult.audits['critical-request-chains']`
10. Extract minification opportunities from: `lighthouseResult.audits['unminified-css']` and `lighthouseResult.audits['unminified-javascript']`
11. **Secondary extraction** (for context only): Performance score — only if needed for FCP root cause analysis
12. Avoid processing CLS, TBT, LCP, SI metrics unless specifically needed

### Parallel Execution Strategy

- Run Mobile + Desktop in **parallel** per test round using `ThreadPoolExecutor`
- 2 test rounds per page = 2 parallel pairs = 4 API calls per page
- Total: 6 rounds across 3 pages = 12 API calls
- Add **15 seconds delay** between test rounds per page to avoid rate limits

### Cache Busting (CRITICAL)

Append unique cache-busting parameter to each URL:
```
{url}?_cb={unix_timestamp}_{test_index}
```
Or `&_cb=...` if URL already has `?`

### Error Handling

- HTTP 429 (rate limit): exponential backoff — 30s, 60s, 120s, 240s (up to 4 retries)
- HTTP 500 (server error): retry after 15s (up to 4 retries)
- Timeout per request: 180 seconds
- Always run with `PYTHONUNBUFFERED=1` for real-time output

---

## Step 2.5: Manual `<head>` Audit (CRITICAL — Do NOT Skip)

**PageSpeed API misses many render-blocking resources.** Before analyzing API data:

1. **Read `layout/theme.liquid`** from line 1 to `</head>`
2. **Flag every `<script>` tag** without `async` or `defer` — these are render-blocking
3. **Check for duplicate CSS loading** — search for the main CSS file (e.g., `theme.css`) being loaded multiple times
4. **List all third-party domains** loaded in `<head>` — check for missing preconnect/dns-prefetch
5. **Check `{{ content_for_header }}`** position — identify what Shopify injects and if any app scripts are blocking
6. **Identify large inline `<script>` blocks** — anything >1KB inline JS in `<head>` that could be deferred
7. **Check `{{ settings.additional_head }}`** — merchant-added custom scripts that may block

**After API analysis, always ask the user for PageSpeed UI screenshots** showing:
- Render-blocking requests (with blocking duration)
- Image delivery opportunities
- Font display issues
- Duplicated JavaScript
- Legacy JavaScript
- Cache lifetime warnings
- Third-party summary with sizes

These screenshots reveal critical blockers the API data misses.

---

## Step 3: Analyze Reports

After collecting all 12 reports, extract and analyze:

### FCP Value Extraction

| Page | Mobile FCP (Test 1) | Mobile FCP (Test 2) | Mobile Avg | Desktop FCP (Test 1) | Desktop FCP (Test 2) | Desktop Avg |
|------|---------------------|---------------------|------------|----------------------|----------------------|-------------|
| Homepage | — | — | — | — | — | — |
| PDP | — | — | — | — | — | — |
| PLP | — | — | — | — | — | — |

### FCP Severity Classification

| FCP Value | Severity | Status |
|-----------|----------|--------|
| ≤ 1.8s | Good | Pass |
| 1.8s – 3.0s | Needs Improvement | Warning |
| > 3.0s | Poor | Fail |

### Identify:

1. **Which pages have FCP issues** (any page with FCP > 1.8s)
2. **Device-specific issues** — Mobile-only, Desktop-only, or Both
3. **Severity level** per page per device
4. **What is blocking first paint** — categorize blockers:
   - **Render-blocking CSS** — stylesheets in `<head>` that block rendering
   - **Render-blocking JS** — synchronous scripts that block parsing
   - **Slow server response (TTFB)** — server takes too long to respond
   - **Web font blocking** — fonts without `font-display: swap` block text rendering
   - **Third-party scripts** — external scripts delaying first paint
   - **Large DOM / inline styles** — excessive HTML parsing time
   - **Unused CSS/JS** — downloaded but not used for first paint
   - **Critical request chain depth** — too many sequential dependent requests
   - **Unminified CSS/JS** — larger files take longer to parse

5. **Root cause quantification**:
   - Render-blocking savings (ms)
   - Unused CSS bytes
   - Unused JS bytes
   - TTFB (ms)
   - Third-party blocking time (ms)
   - Number of critical request chains

---

## Step 4: Create FCP Improvement Plan

Create a complete, actionable plan using:

### Reference Documentation:
- https://web.dev/articles/fcp
- https://web.dev/articles/font-best-practices
- https://web.dev/articles/render-blocking-resources
- https://web.dev/articles/critical-rendering-path
- https://web.dev/articles/extract-critical-css
- Best practices and technical expertise

### Plan Structure (per page with issues):

#### 1. Root Cause Analysis
- Identify exact resources blocking first paint
- Map blockers to file paths and load order
- Quantify impact per blocker (ms saved if fixed)
- Determine critical rendering path bottlenecks

#### 2. Device-Wise Issue Mapping
- Mobile-specific issues (slower CPU, slower network simulation)
- Desktop-specific issues
- Shared issues and fixes

#### 3. Technical Fixes Required (in priority order)

**High Priority — Remove Render-Blocking Resources:**
- Defer non-critical CSS using `media="print" onload="this.media='all'"` pattern
- Inline critical above-the-fold CSS directly in `<head>`
- Add `defer` attribute to non-critical `<script>` tags
- Add `async` attribute to independent scripts (analytics, tracking)
- Move `<script>` tags to end of `<body>` where possible
- Split large CSS files — load critical CSS inline, rest deferred

**High Priority — Optimize Server Response Time (TTFB):**
- Target TTFB < 600ms (mobile) / < 200ms (desktop)
- Add `<link rel="preconnect">` for critical third-party origins:
  ```html
  <link rel="preconnect" href="https://cdn.shopify.com">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  ```
- Add `<link rel="dns-prefetch">` for secondary origins
- Enable compression (gzip/Brotli) if not already
- Leverage CDN caching

**High Priority — Font Loading Optimization:**
- Add `font-display: swap` to all `@font-face` declarations
- Preload critical fonts:
  ```html
  <link rel="preload" as="font" type="font/woff2" href="..." crossorigin>
  ```
- Self-host fonts instead of loading from Google Fonts (eliminates extra DNS + connection)
- Subset fonts to only include needed character ranges
- Limit font variants (weights/styles) to what's actually used
- Consider `font-display: optional` for non-critical fonts

**Medium Priority — Reduce Unused CSS/JS:**
- Identify and remove unused CSS rules (use coverage tools data from audit)
- Remove unused JavaScript modules
- Split CSS into critical (above-fold) and non-critical (below-fold)
- Tree-shake JavaScript bundles
- Remove legacy app code snippets left in theme files

**Medium Priority — Optimize Third-Party Scripts:**
- Audit all third-party scripts and their blocking impact
- Defer non-essential third-party scripts (chat widgets, analytics, marketing)
- Load third-party scripts on user interaction instead of page load:
  ```javascript
  // Load on first scroll/click/touch
  ['scroll', 'click', 'touchstart'].forEach(event => {
    window.addEventListener(event, loadThirdParty, { once: true });
  });
  ```
- Use `rel="preconnect"` for required third-party origins
- Remove unused third-party scripts/apps entirely

**Medium Priority — Optimize Theme App Extensions:**
- Audit Shopify theme app extensions for render-blocking behavior
- Defer app extension scripts that don't affect above-fold content
- Remove disabled/unused app extensions
- Check for duplicate functionality across apps

**Low Priority — Advanced Optimizations:**
- Minify all CSS and JavaScript files
- Enable HTTP/2 or HTTP/3 for parallel resource loading
- Implement resource hints (`modulepreload` for ES modules)
- Reduce HTML document size (remove excessive inline styles/scripts)
- Optimize critical request chain depth (reduce sequential dependencies)
- Use `content-visibility: auto` for below-fold sections
- Consider code splitting for large JavaScript bundles

#### 4. Code-Level Implementation Guidance
- Specific HTML/CSS/JS changes needed
- File paths and line numbers where changes should be made
- Before/after code snippets
- Liquid template changes (for Shopify themes)
- theme.liquid / base.css / theme.js modifications

#### 5. Risk Assessment
- Potential visual regressions (FOUC from deferred CSS)
- Flash of unstyled text (FOUT) from font-display changes
- Functionality issues from deferred scripts
- Browser compatibility concerns
- Impact on other metrics (LCP, CLS)
- Fallback strategies

---

## Step 5: Wait for User Approval

After generating the plan:

1. Present the complete plan to the user
2. **Ask for explicit approval** using AskUserQuestion
3. If user suggests changes → update plan accordingly
4. **Do NOT proceed without confirmation**

---

## Step 6: Execute Improvements

Once approved:

1. Follow the updated plan **strictly**
2. Apply fixes in priority order (High → Medium → Low)
3. For each fix:
   - Read the target file first
   - Make minimal, focused changes
   - Preserve existing functionality
   - Test that first paint behavior is correct
4. **Key implementation patterns:**

   **Inline Critical CSS (in theme.liquid `<head>`):**
   ```html
   <style>
     /* Critical above-fold styles only */
     body { margin: 0; font-family: ...; }
     .header { ... }
     .hero { ... }
   </style>
   ```

   **Defer Non-Critical CSS:**
   ```html
   <link rel="stylesheet" href="non-critical.css" media="print" onload="this.media='all'">
   <noscript><link rel="stylesheet" href="non-critical.css"></noscript>
   ```

   **Defer Non-Critical JavaScript:**
   ```html
   <!-- BEFORE (blocking) -->
   <script src="app.js"></script>
   <!-- AFTER (non-blocking) -->
   <script src="app.js" defer></script>
   ```

   **Font Display Swap:**
   ```css
   @font-face {
     font-family: 'CustomFont';
     src: url('font.woff2') format('woff2');
     font-display: swap;
   }
   ```

   **Preconnect to Critical Origins:**
   ```html
   <link rel="preconnect" href="https://cdn.shopify.com">
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link rel="dns-prefetch" href="https://www.googletagmanager.com">
   ```

   **Load Third-Party on Interaction:**
   ```javascript
   function loadDeferredScripts() {
     // Load chat widget, analytics, etc.
     var script = document.createElement('script');
     script.src = 'https://third-party.com/widget.js';
     document.body.appendChild(script);
   }
   var triggered = false;
   ['scroll', 'mousemove', 'touchstart', 'click', 'keydown'].forEach(function(evt) {
     window.addEventListener(evt, function() {
       if (!triggered) { triggered = true; loadDeferredScripts(); }
     }, { once: true, passive: true });
   });
   ```

   **Script Interception for content_for_header Apps (PROVEN):**
   Place BEFORE `{{ content_for_header }}` to force specific third-party scripts to load async:
   ```html
   <script>
   (function(){
     var blockedDomains = ['static.personizely.net','cdn.personizely.net'];
     var origCreate = document.createElement;
     document.createElement = function(tag) {
       var el = origCreate.call(document, tag);
       if (tag.toLowerCase() === 'script') {
         var origSrcDesc = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'src');
         Object.defineProperty(el, 'src', {
           set: function(v) {
             for (var i = 0; i < blockedDomains.length; i++) {
               if (v && v.indexOf(blockedDomains[i]) !== -1) { el.async = true; break; }
             }
             origSrcDesc.set.call(el, v);
           },
           get: function() { return origSrcDesc.get.call(el); }
         });
       }
       return el;
     };
   })();
   </script>
   ```

   **Defer GTM (Proven Safe for Shopify):**
   ```html
   <script>window.dataLayer=window.dataLayer||[];
   document.addEventListener('DOMContentLoaded',function(){
     (function(w,d,s,l,i){w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});
     var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
     j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;
     f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-XXXXX');
   });</script>
   ```

   **Defer Facebook Pixel (Proven Safe):**
   ```html
   <script>
   window.fbq||(window.fbq=function(){window.fbq.callMethod?
   window.fbq.callMethod.apply(window.fbq,arguments):window.fbq.queue.push(arguments)},
   window._fbq||(window._fbq=window.fbq),window.fbq.push=window.fbq,
   window.fbq.loaded=!0,window.fbq.version="2.0",window.fbq.queue=[]);
   document.addEventListener('DOMContentLoaded',function(){
     var s=document.createElement('script');s.async=!0;
     s.src="https://connect.facebook.net/en_US/fbevents.js";
     document.head.appendChild(s);
   });
   </script>
   ```

   **Defer Clarity via requestIdleCallback:**
   ```html
   <script>
   (function(){
     function loadClarity(){
       (function(c,l,a,r,i,t,y){
         c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
         t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
         y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
       })(window, document, "clarity", "script", "YOUR_ID");
     }
     if ('requestIdleCallback' in window) {
       requestIdleCallback(loadClarity, { timeout: 3000 });
     } else { setTimeout(loadClarity, 2000); }
   })();
   </script>
   ```

   **Optimized Product Card Image srcset:**
   ```liquid
   srcset="{{ image | image_url: width: 250 }} 250w,
     {{ image | image_url: width: 375 }} 375w,
     {{ image | image_url: width: 450 }} 450w,
     {{ image | image_url: width: 750 }} 750w,
     {{ image | image_url: width: 900 }} 900w,
     {{ image | image_url: width: 1100 }} 1100w,
     {{ image | image_url: width: 1500 }} 1500w"
   src="{{ image | image_url: width: 750 }}"
   ```

5. **Validation during execution:**
   - Ensure no breaking changes
   - Verify first paint still shows meaningful content
   - Check that deferred CSS doesn't cause visible FOUC
   - Confirm font-display changes don't cause layout shifts
   - Verify deferred scripts still function correctly

---

## Step 7: Post-Improvement Check

After improvements are completed:

1. **Ask the user:** "Do you want any additional fixes or adjustments?"
2. If user provides additional fixes:
   - Implement them
   - Then proceed to Step 8 (after-report generation)
3. If no additional fixes:
   - Proceed directly to Step 8

---

## Step 8: Generate "After" Reports

Run the same report process as Step 2:

- For each page: 2 reports for Desktop + 2 reports for Mobile
- Total: **12 reports**
- **Primary focus: FCP only** (limit to FCP metric extraction if possible)
- Use same API key, cache busting, and error handling

---

## Step 9: Compare Before vs After

Generate a comprehensive comparison:

### Comparison Table

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      FCP IMPROVEMENT REPORT                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Page      │ Device  │ Before   │ After    │ Change   │ Status          ║
╠═══════════╪═════════╪══════════╪══════════╪══════════╪═════════════════╣
║ Homepage  │ Mobile  │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
║ Homepage  │ Desktop │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
║ PDP       │ Mobile  │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
║ PDP       │ Desktop │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
║ PLP       │ Mobile  │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
║ PLP       │ Desktop │ X.XXs    │ X.XXs    │ -XX%     │ Pass/Fail       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Blocker Resolution Summary

```
╔══════════════════════════════════════════════════════════════════════════╗
║                   FCP BLOCKER RESOLUTION                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Blocker Type           │ Before (ms)  │ After (ms)  │ Resolved?        ║
╠════════════════════════╪══════════════╪═════════════╪══════════════════╣
║ Render-blocking CSS    │ XXX          │ XXX         │ Yes/No           ║
║ Render-blocking JS     │ XXX          │ XXX         │ Yes/No           ║
║ TTFB                   │ XXX          │ XXX         │ Yes/No           ║
║ Font blocking          │ XXX          │ XXX         │ Yes/No           ║
║ Third-party scripts    │ XXX          │ XXX         │ Yes/No           ║
║ Unused CSS             │ XXX KB       │ XXX KB      │ Yes/No           ║
║ Unused JS              │ XXX KB       │ XXX KB      │ Yes/No           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Metrics to Generate:
1. **Page-wise comparison** — FCP before/after per page
2. **Device-wise comparison** — Mobile vs Desktop improvement
3. **Percentage improvement** — `((before - after) / before) × 100`
4. **Pass/Fail status** — Based on FCP ≤ 1.8s threshold
5. **Overall FCP score** — Average across all pages/devices
6. **Blocker resolution** — Which blockers were eliminated

---

## Step 10: If No Improvement

If results show no improvement, minimal improvement, or FCP still failing:

1. **Analyze why** — what didn't work and why
2. **Create a new alternative improvement plan** with different strategies:
   - If CSS deferral didn't help → investigate TTFB and server response
   - If font optimization didn't help → check for other render-blocking resources
   - If script deferral didn't help → investigate critical request chain depth
   - Check for new render-blocking resources introduced
   - Investigate Shopify app extensions that may inject blocking scripts
   - Consider more aggressive approaches (remove non-essential apps, inline more CSS)
3. **Present new plan to user**
4. **Wait for approval**
5. **Execute again**
6. **Re-run reports**
7. **Compare again**
8. **Repeat until acceptable improvement is achieved** or user decides to stop

---

## Step 11: If Results Are Good

If FCP improvements are satisfactory (all pages at or below 1.8s):

1. **Present final summary** to user
2. **Ask if any more changes are needed**
3. If no → **Finalize process**
4. Generate final summary report with all before/after data

---

## Step 12: Self-Learning & Auto-Update Skill

**Final Step — The skill must auto-update itself based on:**

1. **Learnings from this improvement cycle:**
   - Which fixes had the biggest FCP impact
   - Which fixes had no effect
   - Time taken per fix type
   - Common blocking patterns per page type
   - API patterns and errors encountered

2. **User feedback:**
   - Mistakes pointed out by user
   - Alternative approaches suggested by user
   - Preferences for fix strategies

3. **Errors and regressions:**
   - Errors caused by FCP fixes (e.g., FOUC from CSS deferral)
   - Regression patterns discovered (e.g., fixing FCP broke CLS from font-display)
   - Performance bottlenecks found

### Auto-Update Process:

1. Append learnings to `~/.claude/skills/_learnings/LEARNINGS.md` in the format:
```
---
Date: YYYY-MM-DD
Skill name: fcp-improvement
Iteration #: X
Symptom: <what was observed>
Root cause: <what caused it>
Fix applied: <what was done>
Result: <FCP before → after, in seconds>
Rule to reuse: <actionable rule for future runs>
Dedup Key: <short unique identifier>
---
```

2. Update the `## Auto-Updated Rules` section of this skill file with validated learnings
3. This makes the skill **progressively smarter over time**

### What Gets Updated:
- Render-blocking resource detection accuracy
- CSS critical path optimization techniques
- Font loading strategy refinements
- Third-party script management patterns
- TTFB optimization approaches
- Error avoidance rules (e.g., FOUC prevention)

---

## Summary Flow

```
1. Ask for 3 preview links
2. Generate 12 initial "before" reports (FCP-focused)
3. Extract and analyze FCP values + identify blockers
4. Create actionable improvement plan
5. Wait for user approval
6. Execute FCP improvements
7. Ask for additional fixes
8. Generate 12 "after" reports
9. Compare before vs after
10. Re-optimize if needed (loop)
11. Final validation
12. Auto-update skill intelligence
```

---

## Python Script Template for Reports

When generating reports, use this pattern:

```python
#!/usr/bin/env python3
"""FCP-focused PageSpeed Insights Report Generator"""

import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

API_KEY = "AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674"
BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def fetch_fcp_report(url, strategy, test_index):
    """Fetch FCP-specific data from PageSpeed Insights API."""
    ts = int(time.time())
    separator = '&' if '?' in url else '?'
    busted_url = f'{url}{separator}_cb={ts}_{test_index}'
    encoded_url = urllib.parse.quote(busted_url, safe='')

    api_url = f"{BASE_URL}?url={encoded_url}&strategy={strategy}&category=performance&key={API_KEY}"

    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    last_error = "Unknown error"
    for attempt in range(4):
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as response:
                data = json.loads(response.read().decode())

            # Extract FCP-specific data
            audits = data.get('lighthouseResult', {}).get('audits', {})
            fcp_audit = audits.get('first-contentful-paint', {})
            render_blocking = audits.get('render-blocking-resources', {})
            unused_css = audits.get('unused-css-rules', {})
            unused_js = audits.get('unused-javascript', {})
            ttfb_audit = audits.get('server-response-time', {})
            third_party = audits.get('third-party-summary', {})
            font_display = audits.get('font-display', {})
            critical_chains = audits.get('critical-request-chains', {})
            unminified_css = audits.get('unminified-css', {})
            unminified_js = audits.get('unminified-javascript', {})

            return {
                'fcp_value_ms': fcp_audit.get('numericValue', 0),
                'fcp_value_sec': round(fcp_audit.get('numericValue', 0) / 1000, 2),
                'fcp_display': fcp_audit.get('displayValue', 'N/A'),
                'fcp_score': fcp_audit.get('score', 0),
                'render_blocking_items': render_blocking.get('details', {}).get('items', []),
                'render_blocking_savings_ms': render_blocking.get('numericValue', 0),
                'unused_css_items': unused_css.get('details', {}).get('items', []),
                'unused_css_bytes': sum(item.get('wastedBytes', 0) for item in unused_css.get('details', {}).get('items', [])),
                'unused_js_items': unused_js.get('details', {}).get('items', []),
                'unused_js_bytes': sum(item.get('wastedBytes', 0) for item in unused_js.get('details', {}).get('items', [])),
                'ttfb_ms': ttfb_audit.get('numericValue', 0),
                'third_party_items': third_party.get('details', {}).get('items', []),
                'third_party_blocking_ms': sum(
                    item.get('blockingTime', 0)
                    for item in third_party.get('details', {}).get('items', [])
                ),
                'font_display_issues': font_display.get('details', {}).get('items', []),
                'font_display_score': font_display.get('score', 1),
                'critical_chain_depth': len(critical_chains.get('details', {}).get('chains', {})),
                'unminified_css_bytes': unminified_css.get('numericValue', 0),
                'unminified_js_bytes': unminified_js.get('numericValue', 0),
                'performance_score': data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100,
                'strategy': strategy,
                'url': url
            }
        except urllib.error.HTTPError as e:
            last_error = str(e)
            if e.code == 429:
                delay = 30 * (2 ** attempt)
                print(f"Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
            elif e.code == 500:
                print(f"Server error. Retrying in 15s...")
                time.sleep(15)
            else:
                time.sleep(15)
        except Exception as e:
            last_error = str(e)
            time.sleep(15)

    raise Exception(f"Failed after 4 attempts: {last_error}")

def run_fcp_reports(pages, tests_per_page=2):
    """Run FCP reports for all pages."""
    results = {}

    for page_name, url in pages.items():
        print(f"\n--- Testing {page_name}: {url} ---")
        results[page_name] = {'mobile': [], 'desktop': []}

        for test_idx in range(tests_per_page):
            print(f"  Round {test_idx + 1}/{tests_per_page}...")

            with ThreadPoolExecutor(max_workers=2) as executor:
                mobile_future = executor.submit(fetch_fcp_report, url, 'mobile', test_idx)
                desktop_future = executor.submit(fetch_fcp_report, url, 'desktop', test_idx)

                results[page_name]['mobile'].append(mobile_future.result())
                results[page_name]['desktop'].append(desktop_future.result())

            if test_idx < tests_per_page - 1:
                print("  Waiting 15s before next round...")
                time.sleep(15)

    return results

def analyze_fcp(results):
    """Analyze FCP results and generate summary."""
    summary = {}

    for page_name, data in results.items():
        mobile_fcp = [r['fcp_value_sec'] for r in data['mobile']]
        desktop_fcp = [r['fcp_value_sec'] for r in data['desktop']]

        mobile_avg = round(sum(mobile_fcp) / len(mobile_fcp), 2)
        desktop_avg = round(sum(desktop_fcp) / len(desktop_fcp), 2)

        mobile_ttfb = round(sum(r['ttfb_ms'] for r in data['mobile']) / len(data['mobile']), 0)
        desktop_ttfb = round(sum(r['ttfb_ms'] for r in data['desktop']) / len(data['desktop']), 0)

        mobile_blocking = round(sum(r['render_blocking_savings_ms'] for r in data['mobile']) / len(data['mobile']), 0)
        desktop_blocking = round(sum(r['render_blocking_savings_ms'] for r in data['desktop']) / len(data['desktop']), 0)

        summary[page_name] = {
            'mobile_avg_sec': mobile_avg,
            'desktop_avg_sec': desktop_avg,
            'mobile_status': 'Good' if mobile_avg <= 1.8 else ('Needs Improvement' if mobile_avg <= 3.0 else 'Poor'),
            'desktop_status': 'Good' if desktop_avg <= 1.8 else ('Needs Improvement' if desktop_avg <= 3.0 else 'Poor'),
            'mobile_ttfb_ms': mobile_ttfb,
            'desktop_ttfb_ms': desktop_ttfb,
            'mobile_render_blocking_ms': mobile_blocking,
            'desktop_render_blocking_ms': desktop_blocking,
            'mobile_unused_css_bytes': round(sum(r['unused_css_bytes'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_unused_css_bytes': round(sum(r['unused_css_bytes'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_unused_js_bytes': round(sum(r['unused_js_bytes'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_unused_js_bytes': round(sum(r['unused_js_bytes'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_third_party_ms': round(sum(r['third_party_blocking_ms'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_third_party_ms': round(sum(r['third_party_blocking_ms'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_font_issues': data['mobile'][0].get('font_display_issues', []),
            'desktop_font_issues': data['desktop'][0].get('font_display_issues', []),
            'render_blocking_resources': data['mobile'][0].get('render_blocking_items', []),
        }

    return summary
```

---

## Safeguards

- Never edit files unrelated to FCP improvements
- Always read files before editing
- Make minimal, focused changes
- Preserve existing functionality
- Do not upload or share data externally
- Keep all API calls read-only (PageSpeed Insights only)
- Always run Python scripts with `PYTHONUNBUFFERED=1`
- Never proceed without user approval on the improvement plan
- Verify FCP fixes don't cause FOUC (Flash of Unstyled Content)
- Verify FCP fixes don't regress CLS or LCP metrics
- Test that deferred scripts still function correctly

---

## Auto-Updated Rules (from LEARNINGS.md)

<!-- Auto-updated on 2026-02-24 from Iteration #1 -->

### Rule 1: ALWAYS Check for Synchronous Third-Party Scripts in `<head>` (HIGH IMPACT)
**PageSpeed's render-blocking audit does NOT catch all blocking scripts.** Manually inspect `layout/theme.liquid` for `<script src="...">` tags without `async` or `defer`. Common offenders in Shopify themes:
- **CAPI/Meta tracking scripts** from S3 buckets (e.g., `capi-automation.s3.us-east-2.amazonaws.com`) — add `defer`
- **A/B testing scripts** (e.g., personizely, ElevateAB) — add `defer` or use script interception
- **Analytics inline blocks** (GTM, Facebook Pixel, Clarity) — wrap in `DOMContentLoaded`
- The user specifically pointed out that `clientParamsHelper.bundle.js` was render-blocking but not flagged by PageSpeed. Always do a manual `<head>` audit in addition to API analysis.

### Rule 2: Script Interception Pattern for `content_for_header` Apps
Shopify's `{{ content_for_header }}` injects third-party app scripts that you cannot directly modify. Use this **script interception pattern** placed BEFORE `content_for_header` to force specific domains to load async:
```javascript
<script>
(function(){
  var blockedDomains = ['static.personizely.net','cdn.personizely.net'];
  var origCreate = document.createElement;
  document.createElement = function(tag) {
    var el = origCreate.call(document, tag);
    if (tag.toLowerCase() === 'script') {
      var origSrcDesc = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'src');
      Object.defineProperty(el, 'src', {
        set: function(v) {
          for (var i = 0; i < blockedDomains.length; i++) {
            if (v && v.indexOf(blockedDomains[i]) !== -1) { el.async = true; break; }
          }
          origSrcDesc.set.call(el, v);
        },
        get: function() { return origSrcDesc.get.call(el); }
      });
    }
    return el;
  };
})();
</script>
```
**Result**: Personizely was blocking for 1,200ms. This pattern converts it to async.

### Rule 3: Check for Duplicate CSS Loading in Shopify Themes
Shopify themes often load `theme.css` twice — once via `{{ 'theme.css' | asset_url | stylesheet_tag }}` and again via a `{% liquid %}` block using `echo`. Search for ALL instances of the main CSS file being loaded. A 317KB CSS file loaded twice wastes significant bandwidth.

### Rule 4: Defer Meta/Facebook CAPI Initialization Block
The Meta CAPI initialization pattern (checking `window.clientParamBuilder`, processing fbclid, setting cookies) does NOT need to run before first paint. Wrap the entire CAPI init block in `DOMContentLoaded`. The CAPI scripts themselves should have `defer` attribute, and since `defer` scripts execute in order after DOM parsing, the init block in `DOMContentLoaded` will run after them.

### Rule 5: Analytics Script Deferral Patterns (Proven Safe)
These patterns are verified safe for Shopify themes:
- **GTM**: Wrap in `DOMContentLoaded` — still captures all dataLayer events since `dataLayer` array is initialized immediately
- **Facebook Pixel**: Initialize `fbq` queue immediately (synchronous), but defer `fbevents.js` script load to `DOMContentLoaded`
- **Microsoft Clarity**: Wrap in `requestIdleCallback` with 3s timeout fallback — analytics-only, no visual impact
- **ElevateAB**: Add `defer` to redirect.js — inline data object can stay synchronous
- **Survey/tracking scripts**: Wrap in `DOMContentLoaded` — event listeners still attach before user interaction

### Rule 6: Image Delivery — Add Smaller srcset Breakpoints
Product card images often display at 312px on mobile but the smallest srcset starts at 450w. Always add **250w and 375w** breakpoints to product card srcset. Also reduce the fallback `src` from `width: 1500` to `width: 750` — mobile browsers that don't support srcset will download the fallback.
```liquid
srcset="{{ image | image_url: width: 250 }} 250w,
  {{ image | image_url: width: 375 }} 375w,
  {{ image | image_url: width: 450 }} 450w,
  {{ image | image_url: width: 750 }} 750w,
  {{ image | image_url: width: 900 }} 900w,
  {{ image | image_url: width: 1100 }} 1100w,
  {{ image | image_url: width: 1500 }} 1500w"
src="{{ image | image_url: width: 750 }}"
```

### Rule 7: Resource Hints — Preconnect vs dns-prefetch Strategy
**Limit preconnect to MAX 2-3 origins** — PageSpeed warns when >4 preconnects are found. Each preconnect opens a full TCP+TLS connection, competing with critical resources. Use `preconnect` ONLY for:
- `cdn.shopify.com` (primary asset CDN — CSS, JS, fonts, images)
- `fonts.gstatic.com` (only if Google Fonts are needed and deferred)

Use lightweight `dns-prefetch` for all other third-party domains:
```html
<link rel="preconnect" href="https://cdn.shopify.com" crossorigin>
<link rel="dns-prefetch" href="https://capi-automation.s3.us-east-2.amazonaws.com">
<link rel="dns-prefetch" href="https://www.clarity.ms">
<link rel="dns-prefetch" href="https://connect.facebook.net">
<link rel="dns-prefetch" href="https://www.googletagmanager.com">
<link rel="dns-prefetch" href="https://bridge.shopflo.com">
<link rel="dns-prefetch" href="https://static.personizely.net">
```
Note: Shopify's `content_for_header` already adds preconnect for cdn.shopify.com and monorail — check before adding duplicates.

### Rule 8: Things You CANNOT Fix from Theme Code
Do not waste time trying to fix these — flag them to the user instead:
- **Legacy JavaScript** (Babel transforms in third-party bundles) — CAPI, Facebook, alia, customerlabs use legacy JS patterns. We don't control their bundles.
- **Cache lifetimes** — Third-party resources set their own cache headers (e.g., Facebook 20m, Shopify apps 1h-4h). Cannot be changed from theme code.
- **Unused CSS from Tailwind** — A monolithic 317KB theme.css containing full TailwindCSS requires build-time CSS purging with the theme's build pipeline. Cannot be fixed by editing Liquid.
- **Duplicated video.js / preview-color-swatches.js** — These are loaded per-section in Shopify themes because sections can be rendered independently via AJAX. They have built-in dedup protection (`window.Eurus.loadedScript`). The ~6KB duplication cost is acceptable.
- **TTFB** — Server response time is a Shopify infrastructure issue. Preconnect/dns-prefetch helps but can't fix slow server response.

### Rule 9: Always Ask User for Screenshots from PageSpeed
The PageSpeed API response does NOT include all insights shown in the PageSpeed UI. After initial API-based analysis, **always ask the user to share screenshots** of:
- Render-blocking requests
- Font display issues
- Image delivery opportunities
- Duplicated JavaScript
- Legacy JavaScript
- Cache lifetime warnings
- Third-party summary
These screenshots often reveal blockers the API data missed (like the CAPI render-blocking scripts).

### Rule 10: Order of Implementation (Proven Priority)
Apply fixes in this exact order for maximum FCP impact:
1. **Defer synchronous third-party scripts** in `<head>` (CAPI, analytics) — BIGGEST impact
2. **Script interception** for `content_for_header` apps (personizely, etc.)
3. **Remove duplicate CSS** loading
4. **Add preconnect/dns-prefetch** hints
5. **Defer GTM/Facebook/Clarity** init to DOMContentLoaded
6. **Optimize image srcset** (add smaller breakpoints, reduce fallback src)
7. **Defer large inline scripts** (survey, tracking) to DOMContentLoaded
8. **Defer non-critical app scripts** (ElevateAB, etc.)

### Rule 11: Google Fonts Duplicate with Shopify Font System (HIGH IMPACT)
Shopify themes configure fonts via `settings_data.json` (e.g., `type_body_font: "poppins_n4"`). Shopify self-hosts these fonts from its CDN. If the theme ALSO loads Google Fonts for the same font family, this creates:
- **Duplicate font downloads** (8+ woff2 files from Google + self-hosted versions)
- **Deep critical request chains** (10,000ms+ latency chains)
- **Redundant preconnect hints** (fonts.googleapis.com + fonts.gstatic.com)

**Fix**: Check `config/settings_data.json` for font settings. If the same font is in both Shopify settings AND a Google Fonts `<link>`, remove/defer the Google Fonts version. Only load missing weights via deferred Google Fonts:
```html
<!-- BEFORE: Render-blocking, ALL weights -->
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100..900&display=swap" rel="stylesheet">

<!-- AFTER: Deferred, ONLY missing weight 300 -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap" media="print" onload="this.media='all'">
```

### Rule 12: Preload ALL Above-Fold Font Weights
Don't just preload the body font — header and menu fonts are also above-fold critical. Preloading them eliminates the wait for CSS to be parsed before font download starts:
```html
<link rel="preload" href="{{ settings.type_body_font | font_url }}" as="font" type="font/woff2" crossorigin="anonymous" />
<link rel="preload" href="{{ settings.type_header_font | font_url }}" as="font" type="font/woff2" crossorigin="anonymous" />
<link rel="preload" href="{{ settings.type_menu_font | font_url }}" as="font" type="font/woff2" crossorigin="anonymous" />
```

### Rule 13: Interaction-Based Loading for Checkout/Payment Scripts
Checkout bridge scripts (Shopflo, Razorpay, etc.) are NEVER needed for first paint. Load them on first user interaction:
```javascript
(function(){
  var loaded=false;
  function load(){
    if(loaded)return;loaded=true;
    var s=document.createElement('script');s.src='https://bridge.shopflo.com/js/shopflo.bundle.js';s.async=true;document.head.appendChild(s);
  }
  ['scroll','mousemove','touchstart','click','keydown'].forEach(function(e){
    window.addEventListener(e,load,{once:true,passive:true});
  });
  setTimeout(load,5000);
})();
```

### Rule 14: Expand Script Interception to All Known App Domains
The `content_for_header` script interception should include ALL known Shopify app domains that may inject blocking scripts:
```javascript
var blockedDomains = ['static.personizely.net','cdn.personizely.net','app.wigzo.com','cdn.nector.io','x.nitrocommerce.ai','sr-cdn.shiprocket.in'];
```

### Rule 15: Diminishing Returns After 2 Rounds
After 2 rounds of theme-level FCP optimization, if Mobile FCP is still >3.0s, the remaining improvement requires infrastructure changes:
1. **TailwindCSS purge** via build pipeline (could save 200-300KB CSS → 300-500ms on mobile)
2. **Shopify app audit** — remove unused apps to reduce third-party scripts
3. **Better hosting/CDN** for TTFB improvement
Do NOT attempt a third round of theme-level changes — diminishing returns. Advise user on build pipeline and app cleanup instead.

### Performance Baseline (Solved Skin Theme — 2026-02-24)
- **Original**: Mobile FCP 3.69-4.00s (Poor), Desktop 0.85-1.00s (Good)
- **After Round 1**: Mobile FCP 3.02-3.56s (-14%), Desktop 0.73-0.94s (Good)
- **After Round 2**: Mobile FCP 3.02-3.37s (-16-18% cumulative), Desktop 0.74-0.91s (Good)
- **Remaining bottleneck**: Unused CSS (165KB Tailwind), TTFB (400-1400ms), 46+ third-party app resources
