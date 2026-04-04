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

name: cls-improvement
description: Detect, analyze, plan, implement, and validate CLS (Cumulative Layout Shift) improvements across Homepage, PDP, and PLP pages. Runs before/after PageSpeed reports, compares results, and auto-updates skill intelligence based on learnings.
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

# CLS (Cumulative Layout Shift) Improvement Skill

## Purpose

Focused skill for detecting, analyzing, planning, implementing, and validating CLS improvements across Homepage, PDP, and PLP pages. The primary goal is to **improve CLS as much as possible** while minimizing unnecessary processing time.

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

### CLS-Focused Optimization

**Main goal is CLS improvement.** To save time and API usage:

1. **Primary extraction**: Focus on CLS-specific data from the API response
2. Extract CLS from: `lighthouseResult.audits['cumulative-layout-shift'].numericValue`
3. Also extract CLS element details from: `lighthouseResult.audits['layout-shift-elements']`
4. Extract CLS-contributing sources from: `lighthouseResult.audits['layout-shift-elements'].details.items`
5. **Secondary extraction** (for context only): Performance score, LCP, FCP — only if needed for CLS root cause analysis
6. Avoid processing TBT, SI, and other non-CLS metrics unless specifically needed

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

### CLS Value Extraction

| Page | Mobile CLS (Test 1) | Mobile CLS (Test 2) | Mobile Avg | Desktop CLS (Test 1) | Desktop CLS (Test 2) | Desktop Avg |
|------|---------------------|---------------------|------------|----------------------|----------------------|-------------|
| Homepage | — | — | — | — | — | — |
| PDP | — | — | — | — | — | — |
| PLP | — | — | — | — | — | — |

### CLS Severity Classification

| CLS Value | Severity | Status |
|-----------|----------|--------|
| ≤ 0.1 | Good | Pass |
| 0.1 – 0.25 | Needs Improvement | Warning |
| > 0.25 | Poor | Fail |

### Identify:

1. **Which pages have CLS issues** (any page with CLS > 0.1)
2. **Device-specific issues** — Mobile-only, Desktop-only, or Both
3. **Severity level** per page per device
4. **CLS-contributing elements** — from `layout-shift-elements` audit
5. **Root cause patterns**:
   - Images without dimensions
   - Dynamically injected content
   - Web fonts causing FOIT/FOUT
   - Late-loading ads or embeds
   - CSS animations triggering layout shifts
   - Lazy-loaded content above the fold

---

## Step 4: Create CLS Improvement Plan

Create a complete, actionable plan using:

### Reference Documentation:
- https://web.dev/articles/optimize-cls
- https://web.dev/articles/font-best-practices
- https://web.dev/articles/cls
- Best practices and technical expertise

### Plan Structure (per page with issues):

#### 1. Root Cause Analysis
- Identify exact elements causing layout shifts
- Map shift sources to code locations
- Quantify impact per element

#### 2. Device-Wise Issue Mapping
- Mobile-specific issues and fixes
- Desktop-specific issues and fixes
- Shared issues and fixes

#### 3. Technical Fixes Required (in priority order)

**High Priority (biggest CLS impact):**
- Set explicit `width` and `height` on all `<img>` and `<video>` elements
- Use `aspect-ratio` CSS property for responsive containers
- Reserve space for dynamic content (reviews, badges, prices)
- Add `font-display: swap` or `font-display: optional` for web fonts
- Preload critical fonts with `<link rel="preload">`

**Medium Priority:**
- Add CSS `contain: layout` on containers that resize
- Use `transform` animations instead of properties that trigger layout (top, left, width, height)
- Set `min-height` on sections that load dynamic content
- Use `content-visibility: auto` for below-fold content

**Low Priority:**
- Optimize third-party embed loading (lazy load below fold)
- Add placeholder/skeleton UI for async content
- Use `will-change` property sparingly for animated elements

#### 4. Code-Level Approach
- Specific CSS/HTML/JS changes needed
- File paths and line numbers where changes should be made
- Before/after code snippets

#### 5. Risk Assessment
- Potential visual regressions
- Browser compatibility concerns
- Performance trade-offs (if any)
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
   - Add explicit dimensions/sizing where missing
4. **Validation during execution:**
   - Ensure no breaking changes
   - Verify no visual regressions in the code logic
   - Check that fixes don't introduce new layout shifts
5. Apply best practices:
   - Always set `width` and `height` attributes on images
   - Use `aspect-ratio` for responsive sizing
   - Preload critical fonts
   - Reserve space for dynamic content
   - Use CSS `contain` where appropriate

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
- **Primary focus: CLS only** (limit to CLS metric extraction if possible)
- Use same API key, cache busting, and error handling

---

## Step 9: Compare Before vs After

Generate a comprehensive comparison:

### Comparison Table

```
╔══════════════════════════════════════════════════════════════════╗
║                    CLS IMPROVEMENT REPORT                       ║
╠══════════════════════════════════════════════════════════════════╣
║ Page      │ Device  │ Before  │ After   │ Change  │ Status     ║
╠═══════════╪═════════╪═════════╪═════════╪═════════╪════════════╣
║ Homepage  │ Mobile  │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
║ Homepage  │ Desktop │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
║ PDP       │ Mobile  │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
║ PDP       │ Desktop │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
║ PLP       │ Mobile  │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
║ PLP       │ Desktop │ 0.XXX   │ 0.XXX   │ -XX%    │ ✓/✗        ║
╚══════════════════════════════════════════════════════════════════╝
```

### Metrics to Generate:
1. **Page-wise comparison** — CLS before/after per page
2. **Device-wise comparison** — Mobile vs Desktop improvement
3. **Percentage improvement** — `((before - after) / before) × 100`
4. **Pass/Fail status** — Based on CLS ≤ 0.1 threshold
5. **Overall CLS score** — Average across all pages/devices

---

## Step 10: If No Improvement

If results show no improvement, minimal improvement, or CLS still failing:

1. **Analyze why** — what didn't work and why
2. **Create a new alternative improvement plan** with different strategies:
   - Try different approaches (e.g., if CSS fix didn't help, try JS-based solutions)
   - Investigate deeper root causes
   - Consider third-party script interference
   - Check for dynamic content injection patterns
3. **Present new plan to user**
4. **Wait for approval**
5. **Execute again**
6. **Re-run reports**
7. **Compare again**
8. **Repeat until acceptable improvement is achieved** or user decides to stop

---

## Step 11: If Results Are Good

If CLS improvements are satisfactory (all pages at or below 0.1):

1. **Present final summary** to user
2. **Ask if any more changes are needed**
3. If no → **Finalize process**
4. Generate final summary report with all before/after data

---

## Step 12: Self-Learning & Auto-Update Skill

**Final Step — The skill must auto-update itself based on:**

1. **Learnings from this improvement cycle:**
   - Which fixes had the biggest CLS impact
   - Which fixes had no effect
   - Time taken per fix type
   - API patterns and errors encountered

2. **User feedback:**
   - Mistakes pointed out by user
   - Alternative approaches suggested by user
   - Preferences for fix strategies

3. **Errors and regressions:**
   - Errors caused by CLS fixes
   - Regression patterns discovered
   - Performance bottlenecks found

### Auto-Update Process:

1. Append learnings to `~/.claude/skills/_learnings/LEARNINGS.md` in the format:
```
---
Date: YYYY-MM-DD
Skill name: cls-improvement
Iteration #: X
Symptom: <what was observed>
Root cause: <what caused it>
Fix applied: <what was done>
Result: <CLS before → after>
Rule to reuse: <actionable rule for future runs>
Dedup Key: <short unique identifier>
---
```

2. Update the `## Auto-Updated Rules` section of this skill file with validated learnings
3. This makes the skill **progressively smarter over time**

### What Gets Updated:
- Detection accuracy improvements
- Solution quality improvements
- Priority ordering refinements
- New fix patterns discovered
- Error avoidance rules

---

## Summary Flow

```
1. Ask for 3 preview links
2. Generate 12 initial "before" reports (CLS-focused)
3. Extract and analyze CLS values
4. Create actionable improvement plan
5. Wait for user approval
6. Execute CLS improvements
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
"""CLS-focused PageSpeed Insights Report Generator"""

import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

API_KEY = "AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674"
BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def fetch_cls_report(url, strategy, test_index):
    """Fetch CLS-specific data from PageSpeed Insights API."""
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

            # Extract CLS-specific data
            audits = data.get('lighthouseResult', {}).get('audits', {})
            cls_audit = audits.get('cumulative-layout-shift', {})
            cls_elements = audits.get('layout-shift-elements', {})

            return {
                'cls_value': cls_audit.get('numericValue', 0),
                'cls_display': cls_audit.get('displayValue', 'N/A'),
                'cls_score': cls_audit.get('score', 0),
                'cls_elements': cls_elements.get('details', {}).get('items', []),
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

def run_cls_reports(pages, tests_per_page=2):
    """Run CLS reports for all pages."""
    results = {}

    for page_name, url in pages.items():
        print(f"\n--- Testing {page_name}: {url} ---")
        results[page_name] = {'mobile': [], 'desktop': []}

        for test_idx in range(tests_per_page):
            print(f"  Round {test_idx + 1}/{tests_per_page}...")

            with ThreadPoolExecutor(max_workers=2) as executor:
                mobile_future = executor.submit(fetch_cls_report, url, 'mobile', test_idx)
                desktop_future = executor.submit(fetch_cls_report, url, 'desktop', test_idx)

                results[page_name]['mobile'].append(mobile_future.result())
                results[page_name]['desktop'].append(desktop_future.result())

            if test_idx < tests_per_page - 1:
                print("  Waiting 15s before next round...")
                time.sleep(15)

    return results

def analyze_cls(results):
    """Analyze CLS results and generate summary."""
    summary = {}

    for page_name, data in results.items():
        mobile_cls = [r['cls_value'] for r in data['mobile']]
        desktop_cls = [r['cls_value'] for r in data['desktop']]

        mobile_avg = sum(mobile_cls) / len(mobile_cls)
        desktop_avg = sum(desktop_cls) / len(desktop_cls)

        summary[page_name] = {
            'mobile_avg': round(mobile_avg, 4),
            'desktop_avg': round(desktop_avg, 4),
            'mobile_status': 'Good' if mobile_avg <= 0.1 else ('Needs Improvement' if mobile_avg <= 0.25 else 'Poor'),
            'desktop_status': 'Good' if desktop_avg <= 0.1 else ('Needs Improvement' if desktop_avg <= 0.25 else 'Poor'),
            'mobile_elements': data['mobile'][0].get('cls_elements', []),
            'desktop_elements': data['desktop'][0].get('cls_elements', []),
        }

    return summary
```

---

## Safeguards

- Never edit files unrelated to CLS improvements
- Always read files before editing
- Make minimal, focused changes
- Preserve existing functionality
- Do not upload or share data externally
- Keep all API calls read-only (PageSpeed Insights only)
- Always run Python scripts with `PYTHONUNBUFFERED=1`
- Never proceed without user approval on the improvement plan

---

## Auto-Updated Rules (from LEARNINGS.md)

<!-- New rules will be appended here automatically by the skill-updater -->
