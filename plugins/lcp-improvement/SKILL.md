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

name: lcp-improvement
description: Detect, analyze, plan, implement, and validate LCP (Largest Contentful Paint) improvements across Homepage, PDP, and PLP pages. Runs before/after PageSpeed reports, compares results, and auto-updates skill intelligence based on learnings.
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

# LCP (Largest Contentful Paint) Improvement Skill

## Purpose

Focused skill for detecting, analyzing, planning, implementing, and validating LCP improvements across Homepage, PDP, and PLP pages. The primary goal is to **improve LCP as much as possible** while minimizing unnecessary processing time.

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

### LCP-Focused Optimization

**Main goal is LCP improvement.** To save time and API usage:

1. **Primary extraction**: Focus on LCP-specific data from the API response
2. Extract LCP value from: `lighthouseResult.audits['largest-contentful-paint'].numericValue` (in ms)
3. Extract LCP element details from: `lighthouseResult.audits['largest-contentful-paint-element']`
4. Extract render-blocking resources from: `lighthouseResult.audits['render-blocking-resources']`
5. Extract LCP sub-parts from: `lighthouseResult.audits['lcp-lazy-loaded']` and `lighthouseResult.audits['prioritize-lcp-image']`
6. Extract TTFB from: `lighthouseResult.audits['server-response-time'].numericValue`
7. **Secondary extraction** (for context only): Performance score, FCP — only if needed for LCP root cause analysis
8. Avoid processing CLS, TBT, SI, and other non-LCP metrics unless specifically needed

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

## Step 3: Analyze Reports

After collecting all 12 reports, extract and analyze:

### LCP Value Extraction

| Page | Mobile LCP (Test 1) | Mobile LCP (Test 2) | Mobile Avg | Desktop LCP (Test 1) | Desktop LCP (Test 2) | Desktop Avg |
|------|---------------------|---------------------|------------|----------------------|----------------------|-------------|
| Homepage | — | — | — | — | — | — |
| PDP | — | — | — | — | — | — |
| PLP | — | — | — | — | — | — |

### LCP Severity Classification

| LCP Value | Severity | Status |
|-----------|----------|--------|
| ≤ 2.5s | Good | Pass |
| 2.5s – 4.0s | Needs Improvement | Warning |
| > 4.0s | Poor | Fail |

### Identify:

1. **Which pages have LCP issues** (any page with LCP > 2.5s)
2. **Device-specific issues** — Mobile-only, Desktop-only, or Both
3. **Severity level** per page per device
4. **LCP element identification** — What is the LCP element on each page:
   - Hero/banner image
   - Product image
   - Background image (CSS)
   - Text block (heading/paragraph)
   - Video poster image
   - Carousel/slider first slide
5. **Root cause patterns**:
   - Large unoptimized hero/banner images
   - Images not in next-gen formats (WebP/AVIF)
   - Missing `fetchpriority="high"` on LCP image
   - LCP image being lazy-loaded (should NOT be)
   - Render-blocking CSS/JS delaying paint
   - Slow server response time (TTFB > 800ms)
   - Web fonts blocking text rendering
   - Client-side rendering delaying LCP element
   - Large DOM size slowing render
   - Excessive critical-path CSS
   - Third-party scripts blocking main thread
   - Missing image `width`/`height` attributes
   - CSS background images not preloaded

---

## Step 4: Create LCP Improvement Plan

Create a complete, actionable plan using:

### Reference Documentation:
- https://web.dev/articles/optimize-lcp
- https://web.dev/articles/font-best-practices
- https://web.dev/articles/lcp
- https://web.dev/articles/preload-critical-assets
- Best practices and technical expertise

### Plan Structure (per page with issues):

#### 1. Root Cause Analysis
- Identify the exact LCP element on each page
- Determine why it loads slowly
- Map bottlenecks to code locations
- Quantify impact (TTFB vs resource load vs render delay)

#### 2. LCP Element Identification
- Screenshot/description of the LCP element
- Element type (image, text, video poster, etc.)
- Current load behavior (preloaded? lazy-loaded? fetch priority?)
- Current file format and size

#### 3. Device-Wise Issue Mapping
- Mobile-specific issues and fixes (often different LCP element than desktop)
- Desktop-specific issues and fixes
- Shared issues and fixes

#### 4. Technical Fixes Required (in priority order)

**High Priority — LCP Image Optimization:**
- Set `fetchpriority="high"` on the LCP image element
- Remove `loading="lazy"` from LCP image (MUST be eager-loaded)
- Add `<link rel="preload" as="image" href="..." fetchpriority="high">` in `<head>`
- Convert LCP image to WebP/AVIF format
- Compress and resize LCP image to optimal dimensions
- Use responsive `srcset` and `sizes` for device-appropriate image delivery
- Set explicit `width` and `height` attributes on LCP image

**High Priority — Render-Blocking Elimination:**
- Defer non-critical CSS with `media="print" onload="this.media='all'"`
- Inline critical above-the-fold CSS
- Add `defer` or `async` to non-critical `<script>` tags
- Move render-blocking third-party scripts below the fold or load on interaction

**Medium Priority — Server & Network:**
- Reduce TTFB (server response time) — target < 800ms
- Add `<link rel="preconnect">` for critical third-party origins
- Add `<link rel="dns-prefetch">` for secondary origins
- Enable HTTP/2 or HTTP/3 for parallel resource loading
- Use CDN for static assets if not already

**Medium Priority — Font Optimization:**
- Add `font-display: swap` or `font-display: optional` for web fonts
- Preload critical fonts: `<link rel="preload" as="font" type="font/woff2" crossorigin>`
- Subset fonts to only include needed characters
- Self-host fonts instead of loading from Google Fonts (reduces TTFB)

**Low Priority — Advanced Optimizations:**
- Use `content-visibility: auto` for below-fold sections
- Implement priority hints for critical resources
- Optimize CSS delivery (remove unused CSS)
- Reduce JavaScript execution time blocking main thread
- Consider server-side rendering for client-rendered LCP elements

#### 5. Code-Level Implementation Guidance
- Specific HTML/CSS/JS changes needed
- File paths and line numbers where changes should be made
- Before/after code snippets
- Liquid template changes (for Shopify themes)

#### 6. Risk Assessment
- Potential visual regressions
- Browser compatibility concerns (WebP/AVIF fallbacks)
- Performance trade-offs (inlining CSS increases HTML size)
- Impact on other metrics (e.g., CLS if image dimensions change)
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
   - Test that LCP element loads correctly
4. **Key implementation patterns:**

   **Preload LCP Image (in `<head>` or theme.liquid):**
   ```html
   <link rel="preload" as="image" href="{{ lcp_image_url }}" fetchpriority="high">
   ```

   **Set fetch priority on LCP image:**
   ```html
   <img src="..." fetchpriority="high" loading="eager" decoding="async" width="..." height="...">
   ```

   **Remove lazy loading from LCP image:**
   ```html
   <!-- BEFORE (bad) -->
   <img src="..." loading="lazy">
   <!-- AFTER (good) -->
   <img src="..." loading="eager" fetchpriority="high">
   ```

   **Inline critical CSS:**
   ```html
   <style>/* critical above-fold CSS here */</style>
   <link rel="stylesheet" href="full.css" media="print" onload="this.media='all'">
   ```

   **Preconnect to critical origins:**
   ```html
   <link rel="preconnect" href="https://cdn.shopify.com">
   <link rel="preconnect" href="https://fonts.googleapis.com">
   ```

5. **Validation during execution:**
   - Ensure no breaking changes
   - Verify LCP element still renders correctly
   - Check that fixes don't introduce CLS or other regressions
   - Confirm fetchpriority and preload are correctly applied

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
- **Primary focus: LCP only** (limit to LCP metric extraction if possible)
- Use same API key, cache busting, and error handling

---

## Step 9: Compare Before vs After

Generate a comprehensive comparison:

### Comparison Table

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      LCP IMPROVEMENT REPORT                             ║
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

### Metrics to Generate:
1. **Page-wise comparison** — LCP before/after per page
2. **Device-wise comparison** — Mobile vs Desktop improvement
3. **Percentage improvement** — `((before - after) / before) × 100`
4. **Pass/Fail status** — Based on LCP ≤ 2.5s threshold
5. **Overall LCP score** — Average across all pages/devices
6. **LCP element change** — Did the LCP element change after optimization?

---

## Step 10: If No Improvement

If results show no improvement, minimal improvement, or LCP still failing:

1. **Analyze why** — what didn't work and why
2. **Create a new alternative improvement plan** with different strategies:
   - If image optimization didn't help → investigate render-blocking resources
   - If preloading didn't help → check TTFB and server response
   - If CSS optimization didn't help → investigate JavaScript blocking
   - Check if LCP element changed after fixes (common gotcha)
   - Investigate third-party script interference
   - Consider more aggressive approaches (inline critical resources, remove non-essential scripts)
3. **Present new plan to user**
4. **Wait for approval**
5. **Execute again**
6. **Re-run reports**
7. **Compare again**
8. **Repeat until acceptable improvement is achieved** or user decides to stop

---

## Step 11: If Results Are Good

If LCP improvements are satisfactory (all pages at or below 2.5s):

1. **Present final summary** to user
2. **Ask if any more changes are needed**
3. If no → **Finalize process**
4. Generate final summary report with all before/after data

---

## Step 12: Self-Learning & Auto-Update Skill

**Final Step — The skill must auto-update itself based on:**

1. **Learnings from this improvement cycle:**
   - Which fixes had the biggest LCP impact
   - Which fixes had no effect
   - Time taken per fix type
   - Common LCP elements per page type (Homepage=hero, PDP=product image, PLP=grid image)
   - API patterns and errors encountered

2. **User feedback:**
   - Mistakes pointed out by user
   - Alternative approaches suggested by user
   - Preferences for fix strategies

3. **Errors and regressions:**
   - Errors caused by LCP fixes
   - Regression patterns discovered (e.g., fixing LCP broke CLS)
   - Performance bottlenecks found

### Auto-Update Process:

1. Append learnings to `~/.claude/skills/_learnings/LEARNINGS.md` in the format:
```
---
Date: YYYY-MM-DD
Skill name: lcp-improvement
Iteration #: X
Symptom: <what was observed>
Root cause: <what caused it>
Fix applied: <what was done>
Result: <LCP before → after, in seconds>
Rule to reuse: <actionable rule for future runs>
Dedup Key: <short unique identifier>
---
```

2. Update the `## Auto-Updated Rules` section of this skill file with validated learnings
3. This makes the skill **progressively smarter over time**

### What Gets Updated:
- LCP element detection accuracy per page type
- Image optimization strategy refinements
- Preload/fetchpriority effectiveness patterns
- Render-blocking elimination techniques
- TTFB improvement approaches
- Error avoidance rules

---

## Summary Flow

```
1. Ask for 3 preview links
2. Generate 12 initial "before" reports (LCP-focused)
3. Extract and analyze LCP values + identify LCP elements
4. Create actionable improvement plan
5. Wait for user approval
6. Execute LCP improvements
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
"""LCP-focused PageSpeed Insights Report Generator"""

import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

API_KEY = "AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674"
BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def fetch_lcp_report(url, strategy, test_index):
    """Fetch LCP-specific data from PageSpeed Insights API."""
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

            # Extract LCP-specific data
            audits = data.get('lighthouseResult', {}).get('audits', {})
            lcp_audit = audits.get('largest-contentful-paint', {})
            lcp_element = audits.get('largest-contentful-paint-element', {})
            render_blocking = audits.get('render-blocking-resources', {})
            ttfb_audit = audits.get('server-response-time', {})
            lcp_lazy = audits.get('lcp-lazy-loaded', {})
            prioritize_lcp = audits.get('prioritize-lcp-image', {})

            return {
                'lcp_value_ms': lcp_audit.get('numericValue', 0),
                'lcp_value_sec': round(lcp_audit.get('numericValue', 0) / 1000, 2),
                'lcp_display': lcp_audit.get('displayValue', 'N/A'),
                'lcp_score': lcp_audit.get('score', 0),
                'lcp_element': lcp_element.get('details', {}).get('items', []),
                'render_blocking': render_blocking.get('details', {}).get('items', []),
                'render_blocking_savings_ms': render_blocking.get('numericValue', 0),
                'ttfb_ms': ttfb_audit.get('numericValue', 0),
                'lcp_lazy_loaded': lcp_lazy.get('score', 1),  # 1 = not lazy loaded (good), 0 = lazy loaded (bad)
                'prioritize_lcp_score': prioritize_lcp.get('score', 1),
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

def run_lcp_reports(pages, tests_per_page=2):
    """Run LCP reports for all pages."""
    results = {}

    for page_name, url in pages.items():
        print(f"\n--- Testing {page_name}: {url} ---")
        results[page_name] = {'mobile': [], 'desktop': []}

        for test_idx in range(tests_per_page):
            print(f"  Round {test_idx + 1}/{tests_per_page}...")

            with ThreadPoolExecutor(max_workers=2) as executor:
                mobile_future = executor.submit(fetch_lcp_report, url, 'mobile', test_idx)
                desktop_future = executor.submit(fetch_lcp_report, url, 'desktop', test_idx)

                results[page_name]['mobile'].append(mobile_future.result())
                results[page_name]['desktop'].append(desktop_future.result())

            if test_idx < tests_per_page - 1:
                print("  Waiting 15s before next round...")
                time.sleep(15)

    return results

def analyze_lcp(results):
    """Analyze LCP results and generate summary."""
    summary = {}

    for page_name, data in results.items():
        mobile_lcp = [r['lcp_value_sec'] for r in data['mobile']]
        desktop_lcp = [r['lcp_value_sec'] for r in data['desktop']]

        mobile_avg = round(sum(mobile_lcp) / len(mobile_lcp), 2)
        desktop_avg = round(sum(desktop_lcp) / len(desktop_lcp), 2)

        mobile_ttfb = round(sum(r['ttfb_ms'] for r in data['mobile']) / len(data['mobile']), 0)
        desktop_ttfb = round(sum(r['ttfb_ms'] for r in data['desktop']) / len(data['desktop']), 0)

        summary[page_name] = {
            'mobile_avg_sec': mobile_avg,
            'desktop_avg_sec': desktop_avg,
            'mobile_status': 'Good' if mobile_avg <= 2.5 else ('Needs Improvement' if mobile_avg <= 4.0 else 'Poor'),
            'desktop_status': 'Good' if desktop_avg <= 2.5 else ('Needs Improvement' if desktop_avg <= 4.0 else 'Poor'),
            'mobile_lcp_element': data['mobile'][0].get('lcp_element', []),
            'desktop_lcp_element': data['desktop'][0].get('lcp_element', []),
            'mobile_ttfb_ms': mobile_ttfb,
            'desktop_ttfb_ms': desktop_ttfb,
            'mobile_render_blocking_ms': round(sum(r['render_blocking_savings_ms'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_render_blocking_ms': round(sum(r['render_blocking_savings_ms'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_lcp_lazy': any(r['lcp_lazy_loaded'] == 0 for r in data['mobile']),
            'desktop_lcp_lazy': any(r['lcp_lazy_loaded'] == 0 for r in data['desktop']),
        }

    return summary
```

---

## Safeguards

- Never edit files unrelated to LCP improvements
- Always read files before editing
- Make minimal, focused changes
- Preserve existing functionality
- Do not upload or share data externally
- Keep all API calls read-only (PageSpeed Insights only)
- Always run Python scripts with `PYTHONUNBUFFERED=1`
- Never proceed without user approval on the improvement plan
- Verify LCP fixes don't regress CLS or other metrics

---

## Auto-Updated Rules (from LEARNINGS.md)

<!-- New rules will be appended here automatically by the skill-updater -->
