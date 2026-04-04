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

name: tbt-improvement
description: Detect, analyze, plan, implement, and validate TBT (Total Blocking Time) improvements across Homepage, PDP, and PLP pages. Runs before/after PageSpeed reports, compares results, and auto-updates skill intelligence based on learnings.
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

# TBT (Total Blocking Time) Improvement Skill

## Purpose

Focused skill for detecting, analyzing, planning, implementing, and validating TBT improvements across Homepage, PDP, and PLP pages. The primary goal is to **improve TBT as much as possible** while minimizing unnecessary processing time.

TBT measures the **total time the main thread is blocked** by long tasks (>50ms) between FCP and Time to Interactive. It directly reflects how responsive the page feels to user input — high TBT means the page appears loaded but clicks/taps/scrolls are unresponsive.

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

### TBT-Focused Optimization

**Main goal is TBT improvement.** To save time and API usage:

1. **Primary extraction**: Focus on TBT-specific data from the API response
2. Extract TBT value from: `lighthouseResult.audits['total-blocking-time'].numericValue` (in ms)
3. Extract long tasks from: `lighthouseResult.audits['long-tasks']`
4. Extract main-thread work from: `lighthouseResult.audits['mainthread-work-breakdown']`
5. Extract JS execution time from: `lighthouseResult.audits['bootup-time']`
6. Extract third-party impact from: `lighthouseResult.audits['third-party-summary']`
7. Extract unused JS from: `lighthouseResult.audits['unused-javascript']`
8. Extract unminified JS from: `lighthouseResult.audits['unminified-javascript']`
9. Extract legacy JS from: `lighthouseResult.audits['legacy-javascript']`
10. Extract DOM size from: `lighthouseResult.audits['dom-size']`
11. **Secondary extraction** (for context only): Performance score, TTI — only if needed for TBT root cause analysis
12. Avoid processing CLS, FCP, LCP, SI metrics unless specifically needed

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

### TBT Value Extraction

| Page | Mobile TBT (Test 1) | Mobile TBT (Test 2) | Mobile Avg | Desktop TBT (Test 1) | Desktop TBT (Test 2) | Desktop Avg |
|------|---------------------|---------------------|------------|----------------------|----------------------|-------------|
| Homepage | — | — | — | — | — | — |
| PDP | — | — | — | — | — | — |
| PLP | — | — | — | — | — | — |

### TBT Severity Classification

| TBT Value (Mobile) | TBT Value (Desktop) | Severity | Status |
|---------------------|----------------------|----------|--------|
| ≤ 200ms | ≤ 150ms | Good | Pass |
| 200ms – 600ms | 150ms – 350ms | Needs Improvement | Warning |
| > 600ms | > 350ms | Poor | Fail |

### Identify:

1. **Which pages have TBT issues** (any page exceeding thresholds above)
2. **Device-specific issues** — Mobile-only, Desktop-only, or Both (Mobile is almost always worse due to CPU throttling)
3. **Severity level** per page per device
4. **Main-thread work breakdown** — categorize time spent:
   - **Script Evaluation** — JavaScript parsing and compilation
   - **Script Execution** — JavaScript runtime execution
   - **Style & Layout** — CSS recalculation and layout computation
   - **Rendering** — paint and compositing
   - **Garbage Collection** — memory management
   - **Other** — parsing HTML, etc.

5. **Root cause patterns**:
   - Large JavaScript bundles executing on load (theme.js, vendor.js)
   - Third-party scripts blocking the main thread (analytics, chat widgets, marketing pixels)
   - Synchronous script execution chains
   - Heavy DOM manipulation on page load
   - Excessive event listeners registered during initialization
   - Unoptimized loops or recursive operations
   - Large CSS recalculations triggered by JS
   - Legacy JavaScript polyfills not needed for modern browsers
   - Shopify app scripts injecting heavy initialization code
   - Cart/bundle/upsell app scripts running synchronously

6. **Top blocking scripts** — identify the specific scripts with highest execution time from `bootup-time` audit

---

## Step 4: Create TBT Improvement Plan

Create a complete, actionable plan using:

### Reference Documentation:
- https://web.dev/articles/tbt
- https://web.dev/articles/long-tasks-devtools
- https://web.dev/articles/optimize-long-tasks
- https://web.dev/articles/script-evaluation
- Best practices and technical expertise

### Plan Structure (per page with issues):

#### 1. Root Cause Analysis
- Identify exact scripts causing long tasks (>50ms)
- Map blocking scripts to file paths and origins
- Quantify blocking time per script
- Determine main-thread work distribution

#### 2. Device-Wise Issue Mapping
- Mobile-specific issues (4x CPU throttling makes TBT much worse)
- Desktop-specific issues
- Shared issues and fixes

#### 3. Technical Fixes Required (in priority order)

**High Priority — Defer & Async Non-Critical JavaScript:**
- Add `defer` to all non-critical `<script>` tags
- Add `async` to independent scripts (analytics, tracking)
- Move scripts to end of `<body>` where possible
- Load non-essential scripts on user interaction:
  ```javascript
  function loadDeferred() {
    // chat widgets, analytics, marketing scripts
  }
  var done = false;
  ['scroll', 'mousemove', 'touchstart', 'click', 'keydown'].forEach(function(e) {
    window.addEventListener(e, function() {
      if (!done) { done = true; loadDeferred(); }
    }, { once: true, passive: true });
  });
  ```

**High Priority — Break Up Long Tasks:**
- Use `requestIdleCallback()` for non-urgent work
- Use `setTimeout(fn, 0)` to yield to the main thread between chunks
- Use `scheduler.yield()` (where supported) to explicitly yield
- Split large initialization functions into smaller async chunks:
  ```javascript
  // BEFORE: one long task
  function initAll() {
    initSlider();
    initCart();
    initReviews();
    initTracking();
  }

  // AFTER: yielding between tasks
  async function initAll() {
    initSlider();
    await new Promise(r => setTimeout(r, 0)); // yield
    initCart();
    await new Promise(r => setTimeout(r, 0)); // yield
    initReviews();
    await new Promise(r => setTimeout(r, 0)); // yield
    initTracking();
  }
  ```

**High Priority — Reduce Third-Party Script Impact:**
- Audit all third-party scripts and their main-thread blocking time
- Remove unused third-party scripts/apps entirely
- Defer non-essential third-party scripts to user interaction
- Use `loading="lazy"` for third-party iframes (chat widgets)
- Replace heavy third-party libraries with lighter alternatives
- Use web workers for heavy third-party computations where possible

**Medium Priority — Optimize JavaScript Bundles:**
- Remove unused JavaScript (use `unused-javascript` audit data)
- Tree-shake JavaScript bundles
- Code-split large bundles — load route-specific code only
- Minify all JavaScript files
- Remove legacy JavaScript polyfills (`legacy-javascript` audit):
  - Remove polyfills for features supported by target browsers
  - Use `<script type="module">` / `<script nomodule>` pattern
- Compress JavaScript with gzip/Brotli

**Medium Priority — Optimize Shopify Theme Scripts:**
- Audit `theme.js` — split into critical and non-critical parts
- Defer Swiper/slider initialization until element is in viewport:
  ```javascript
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        initSlider(entry.target);
        observer.unobserve(entry.target);
      }
    });
  });
  document.querySelectorAll('.slider').forEach(el => observer.observe(el));
  ```
- Defer cart drawer / quick-add / bundle scripts until interaction
- Lazy-initialize product recommendation sections
- Optimize section rendering JavaScript

**Medium Priority — Optimize Shopify App Scripts:**
- Identify Shopify apps injecting heavy scripts (reviews, upsells, bundles, loyalty)
- Defer app scripts that don't affect above-fold content
- Remove disabled/unused apps and clean up leftover code snippets
- Check for duplicate functionality across apps
- Contact app developers about performance if scripts are excessive

**Low Priority — Reduce DOM Complexity:**
- Reduce DOM size (target < 1500 elements)
- Simplify deeply nested DOM structures
- Use `content-visibility: auto` for off-screen sections (reduces style/layout work)
- Minimize CSS complexity that triggers expensive recalculations
- Avoid `querySelectorAll` on large selectors during initialization
- Use event delegation instead of many individual event listeners

**Low Priority — Advanced Optimizations:**
- Use Web Workers for heavy computations (data processing, filtering)
- Implement `requestAnimationFrame` for visual updates instead of synchronous DOM writes
- Use `will-change` CSS property sparingly to promote elements to GPU layers
- Implement virtual scrolling for long product lists (PLP)
- Consider using `scheduler.postTask()` API for priority-based task scheduling
- Profile and optimize hot code paths with Chrome DevTools Performance panel

#### 4. Code-Level Implementation Guidance
- Specific JS/HTML changes needed
- File paths and line numbers where changes should be made
- Before/after code snippets
- Liquid template changes (for Shopify themes)
- theme.js / vendor.js / app script modifications

#### 5. Risk Assessment
- Potential functionality regressions from deferred scripts
- Race conditions from async initialization
- Third-party script dependency chains
- Browser compatibility for modern APIs (requestIdleCallback, scheduler.yield)
- Impact on other metrics (unlikely — TBT fixes rarely hurt other metrics)
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
   - Ensure deferred scripts still execute correctly
4. **Key implementation patterns:**

   **Defer Non-Critical Script:**
   ```html
   <!-- BEFORE (blocking) -->
   <script src="heavy-script.js"></script>
   <!-- AFTER (non-blocking) -->
   <script src="heavy-script.js" defer></script>
   ```

   **Load on User Interaction:**
   ```html
   <script>
     var _loaded = false;
     function _loadDeferred() {
       if (_loaded) return;
       _loaded = true;
       // Load chat widget
       var s1 = document.createElement('script');
       s1.src = 'https://chat-widget.com/loader.js';
       document.body.appendChild(s1);
       // Load reviews
       var s2 = document.createElement('script');
       s2.src = 'https://reviews-app.com/widget.js';
       document.body.appendChild(s2);
     }
     ['scroll', 'mousemove', 'touchstart', 'click', 'keydown'].forEach(function(e) {
       window.addEventListener(e, _loadDeferred, { once: true, passive: true });
     });
     // Fallback: load after 5 seconds if no interaction
     setTimeout(_loadDeferred, 5000);
   </script>
   ```

   **Break Up Long Task with Yielding:**
   ```javascript
   function yieldToMain() {
     return new Promise(resolve => setTimeout(resolve, 0));
   }

   async function processItems(items) {
     for (let i = 0; i < items.length; i++) {
       processItem(items[i]);
       // Yield every 5 items to keep main thread responsive
       if (i % 5 === 4) await yieldToMain();
     }
   }
   ```

   **Lazy-Initialize with IntersectionObserver:**
   ```javascript
   const lazyObserver = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
       if (entry.isIntersecting) {
         const section = entry.target;
         const initFn = section.dataset.init;
         if (typeof window[initFn] === 'function') {
           window[initFn](section);
         }
         lazyObserver.unobserve(section);
       }
     });
   }, { rootMargin: '200px' });

   document.querySelectorAll('[data-lazy-init]').forEach(el => {
     lazyObserver.observe(el);
   });
   ```

   **Replace Heavy Library with Lighter Alternative:**
   ```javascript
   // BEFORE: Full jQuery for simple DOM operations
   // <script src="jquery-3.7.1.min.js"></script> (87KB gzipped)

   // AFTER: Vanilla JS (0KB)
   document.querySelectorAll('.accordion-toggle').forEach(btn => {
     btn.addEventListener('click', () => {
       btn.nextElementSibling.classList.toggle('active');
     });
   });
   ```

   **Use Web Worker for Heavy Computation:**
   ```javascript
   // main.js
   const worker = new Worker('filter-worker.js');
   worker.postMessage({ products: productData, filters: activeFilters });
   worker.onmessage = (e) => renderProducts(e.data.filtered);

   // filter-worker.js
   self.onmessage = (e) => {
     const { products, filters } = e.data;
     const filtered = products.filter(p => matchesFilters(p, filters));
     self.postMessage({ filtered });
   };
   ```

5. **Validation during execution:**
   - Ensure no breaking changes
   - Verify all interactive elements still work (cart, search, menus, filters)
   - Check that deferred scripts fire correctly on interaction
   - Confirm no race conditions between async-loaded scripts
   - Test on mobile (where TBT impact is most felt)

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
- **Primary focus: TBT only** (limit to TBT metric extraction if possible)
- Use same API key, cache busting, and error handling

---

## Step 9: Compare Before vs After

Generate a comprehensive comparison:

### Comparison Table

```
╔══════════════════════════════════════════════════════════════════════════╗
║                      TBT IMPROVEMENT REPORT                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Page      │ Device  │ Before   │ After    │ Change   │ Status          ║
╠═══════════╪═════════╪══════════╪══════════╪══════════╪═════════════════╣
║ Homepage  │ Mobile  │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
║ Homepage  │ Desktop │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
║ PDP       │ Mobile  │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
║ PDP       │ Desktop │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
║ PLP       │ Mobile  │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
║ PLP       │ Desktop │ XXXXms   │ XXXXms   │ -XX%     │ Pass/Fail       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Main-Thread Work Breakdown Comparison

```
╔══════════════════════════════════════════════════════════════════════════╗
║               MAIN-THREAD WORK BREAKDOWN (Mobile Avg)                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Category              │ Before (ms) │ After (ms)  │ Reduction          ║
╠═══════════════════════╪═════════════╪═════════════╪════════════════════╣
║ Script Evaluation     │ XXXX        │ XXXX        │ -XX%               ║
║ Script Execution      │ XXXX        │ XXXX        │ -XX%               ║
║ Style & Layout        │ XXXX        │ XXXX        │ -XX%               ║
║ Rendering             │ XXXX        │ XXXX        │ -XX%               ║
║ Garbage Collection    │ XXXX        │ XXXX        │ -XX%               ║
║ Other                 │ XXXX        │ XXXX        │ -XX%               ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Top Blocking Scripts Comparison

```
╔══════════════════════════════════════════════════════════════════════════╗
║                  TOP BLOCKING SCRIPTS                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Script                        │ Before (ms) │ After (ms) │ Status      ║
╠═══════════════════════════════╪═════════════╪════════════╪═════════════╣
║ theme.js                      │ XXX         │ XXX        │ Improved    ║
║ vendor.js                     │ XXX         │ XXX        │ Improved    ║
║ analytics.js (3rd party)      │ XXX         │ XXX        │ Deferred    ║
║ chat-widget.js (3rd party)    │ XXX         │ XXX        │ Deferred    ║
║ reviews-app.js (3rd party)    │ XXX         │ XXX        │ Deferred    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Metrics to Generate:
1. **Page-wise comparison** — TBT before/after per page
2. **Device-wise comparison** — Mobile vs Desktop improvement
3. **Percentage improvement** — `((before - after) / before) × 100`
4. **Pass/Fail status** — Based on TBT ≤ 200ms (mobile) / ≤ 150ms (desktop) threshold
5. **Overall TBT score** — Average across all pages/devices
6. **Main-thread work reduction** — breakdown by category
7. **Top blocking scripts resolution** — which scripts were optimized/deferred

---

## Step 10: If No Improvement

If results show no improvement, minimal improvement, or TBT still failing:

1. **Analyze why** — what didn't work and why
2. **Create a new alternative improvement plan** with different strategies:
   - If script deferral didn't help → investigate first-party script optimization
   - If third-party removal didn't help → check for heavy theme.js / vendor.js
   - If code splitting didn't help → investigate DOM complexity and CSS recalculation
   - Profile specific long tasks using `mainthread-work-breakdown` data
   - Check if new blocking scripts were introduced
   - Consider more aggressive approaches (remove apps, rewrite heavy functions, use Web Workers)
3. **Present new plan to user**
4. **Wait for approval**
5. **Execute again**
6. **Re-run reports**
7. **Compare again**
8. **Repeat until acceptable improvement is achieved** or user decides to stop

---

## Step 11: If Results Are Good

If TBT improvements are satisfactory (Mobile ≤ 200ms, Desktop ≤ 150ms):

1. **Present final summary** to user
2. **Ask if any more changes are needed**
3. If no → **Finalize process**
4. Generate final summary report with all before/after data

---

## Step 12: Self-Learning & Auto-Update Skill

**Final Step — The skill must auto-update itself based on:**

1. **Learnings from this improvement cycle:**
   - Which fixes had the biggest TBT impact
   - Which fixes had no effect
   - Which scripts were the biggest offenders
   - Common Shopify app scripts that block the main thread
   - Effective yielding strategies
   - API patterns and errors encountered

2. **User feedback:**
   - Mistakes pointed out by user
   - Alternative approaches suggested by user
   - Preferences for fix strategies

3. **Errors and regressions:**
   - Errors caused by TBT fixes (e.g., deferred script broke cart functionality)
   - Race conditions from async loading
   - Regression patterns discovered
   - Performance bottlenecks found

### Auto-Update Process:

1. Append learnings to `~/.claude/skills/_learnings/LEARNINGS.md` in the format:
```
---
Date: YYYY-MM-DD
Skill name: tbt-improvement
Iteration #: X
Symptom: <what was observed>
Root cause: <what caused it>
Fix applied: <what was done>
Result: <TBT before → after, in ms>
Rule to reuse: <actionable rule for future runs>
Dedup Key: <short unique identifier>
---
```

2. Update the `## Auto-Updated Rules` section of this skill file with validated learnings
3. This makes the skill **progressively smarter over time**

### What Gets Updated:
- Script blocking detection accuracy
- Main-thread optimization techniques
- Third-party script management patterns
- Shopify app script deferral strategies
- Task-breaking / yielding best practices
- Error avoidance rules (e.g., deferred script dependency chains)

---

## Summary Flow

```
1. Ask for 3 preview links
2. Generate 12 initial "before" reports (TBT-focused)
3. Extract and analyze TBT values + identify blocking scripts
4. Create actionable improvement plan
5. Wait for user approval
6. Execute TBT improvements
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
"""TBT-focused PageSpeed Insights Report Generator"""

import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

API_KEY = "AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674"
BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def fetch_tbt_report(url, strategy, test_index):
    """Fetch TBT-specific data from PageSpeed Insights API."""
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

            # Extract TBT-specific data
            audits = data.get('lighthouseResult', {}).get('audits', {})
            tbt_audit = audits.get('total-blocking-time', {})
            mainthread = audits.get('mainthread-work-breakdown', {})
            bootup = audits.get('bootup-time', {})
            third_party = audits.get('third-party-summary', {})
            unused_js = audits.get('unused-javascript', {})
            unminified_js = audits.get('unminified-javascript', {})
            legacy_js = audits.get('legacy-javascript', {})
            dom_size = audits.get('dom-size', {})
            long_tasks = audits.get('long-tasks', {})

            # Parse main-thread work breakdown
            mainthread_items = mainthread.get('details', {}).get('items', [])
            mainthread_breakdown = {}
            for item in mainthread_items:
                group = item.get('group', 'other')
                duration = item.get('duration', 0)
                mainthread_breakdown[group] = round(duration, 1)

            # Parse top blocking scripts from bootup-time
            bootup_items = bootup.get('details', {}).get('items', [])
            top_scripts = []
            for item in sorted(bootup_items, key=lambda x: x.get('total', 0), reverse=True)[:10]:
                top_scripts.append({
                    'url': item.get('url', 'unknown'),
                    'total_ms': round(item.get('total', 0), 1),
                    'scripting_ms': round(item.get('scripting', 0), 1),
                    'script_parse_ms': round(item.get('scriptParseCompile', 0), 1),
                })

            # Parse third-party blocking
            third_party_items = third_party.get('details', {}).get('items', [])
            third_party_scripts = []
            for item in third_party_items:
                third_party_scripts.append({
                    'entity': item.get('entity', 'unknown'),
                    'blocking_time_ms': round(item.get('blockingTime', 0), 1),
                    'transfer_size': item.get('transferSize', 0),
                    'main_thread_time': round(item.get('mainThreadTime', 0), 1),
                })

            return {
                'tbt_value_ms': round(tbt_audit.get('numericValue', 0), 0),
                'tbt_display': tbt_audit.get('displayValue', 'N/A'),
                'tbt_score': tbt_audit.get('score', 0),
                'mainthread_breakdown': mainthread_breakdown,
                'mainthread_total_ms': round(sum(mainthread_breakdown.values()), 0),
                'top_scripts': top_scripts,
                'third_party_scripts': third_party_scripts,
                'third_party_blocking_ms': round(sum(
                    item.get('blockingTime', 0)
                    for item in third_party_items
                ), 0),
                'unused_js_items': unused_js.get('details', {}).get('items', []),
                'unused_js_bytes': sum(
                    item.get('wastedBytes', 0)
                    for item in unused_js.get('details', {}).get('items', [])
                ),
                'unminified_js_bytes': unminified_js.get('numericValue', 0),
                'legacy_js_bytes': sum(
                    item.get('wastedBytes', 0)
                    for item in legacy_js.get('details', {}).get('items', [])
                ),
                'dom_elements': dom_size.get('numericValue', 0),
                'long_tasks_count': len(long_tasks.get('details', {}).get('items', [])),
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

def run_tbt_reports(pages, tests_per_page=2):
    """Run TBT reports for all pages."""
    results = {}

    for page_name, url in pages.items():
        print(f"\n--- Testing {page_name}: {url} ---")
        results[page_name] = {'mobile': [], 'desktop': []}

        for test_idx in range(tests_per_page):
            print(f"  Round {test_idx + 1}/{tests_per_page}...")

            with ThreadPoolExecutor(max_workers=2) as executor:
                mobile_future = executor.submit(fetch_tbt_report, url, 'mobile', test_idx)
                desktop_future = executor.submit(fetch_tbt_report, url, 'desktop', test_idx)

                results[page_name]['mobile'].append(mobile_future.result())
                results[page_name]['desktop'].append(desktop_future.result())

            if test_idx < tests_per_page - 1:
                print("  Waiting 15s before next round...")
                time.sleep(15)

    return results

def analyze_tbt(results):
    """Analyze TBT results and generate summary."""
    summary = {}

    for page_name, data in results.items():
        mobile_tbt = [r['tbt_value_ms'] for r in data['mobile']]
        desktop_tbt = [r['tbt_value_ms'] for r in data['desktop']]

        mobile_avg = round(sum(mobile_tbt) / len(mobile_tbt), 0)
        desktop_avg = round(sum(desktop_tbt) / len(desktop_tbt), 0)

        # Aggregate main-thread breakdown (mobile)
        mobile_breakdown = {}
        for r in data['mobile']:
            for k, v in r['mainthread_breakdown'].items():
                mobile_breakdown[k] = mobile_breakdown.get(k, 0) + v
        for k in mobile_breakdown:
            mobile_breakdown[k] = round(mobile_breakdown[k] / len(data['mobile']), 1)

        summary[page_name] = {
            'mobile_avg_ms': mobile_avg,
            'desktop_avg_ms': desktop_avg,
            'mobile_status': 'Good' if mobile_avg <= 200 else ('Needs Improvement' if mobile_avg <= 600 else 'Poor'),
            'desktop_status': 'Good' if desktop_avg <= 150 else ('Needs Improvement' if desktop_avg <= 350 else 'Poor'),
            'mobile_mainthread_breakdown': mobile_breakdown,
            'mobile_top_scripts': data['mobile'][0].get('top_scripts', []),
            'desktop_top_scripts': data['desktop'][0].get('top_scripts', []),
            'mobile_third_party_ms': round(sum(r['third_party_blocking_ms'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_third_party_ms': round(sum(r['third_party_blocking_ms'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_unused_js_bytes': round(sum(r['unused_js_bytes'] for r in data['mobile']) / len(data['mobile']), 0),
            'desktop_unused_js_bytes': round(sum(r['unused_js_bytes'] for r in data['desktop']) / len(data['desktop']), 0),
            'mobile_dom_elements': round(sum(r['dom_elements'] for r in data['mobile']) / len(data['mobile']), 0),
            'mobile_long_tasks': round(sum(r['long_tasks_count'] for r in data['mobile']) / len(data['mobile']), 0),
        }

    return summary
```

---

## Safeguards

- Never edit files unrelated to TBT improvements
- Always read files before editing
- Make minimal, focused changes
- Preserve existing functionality
- Do not upload or share data externally
- Keep all API calls read-only (PageSpeed Insights only)
- Always run Python scripts with `PYTHONUNBUFFERED=1`
- Never proceed without user approval on the improvement plan
- Verify deferred scripts still execute and function correctly
- Test interactive elements (cart, menus, search, filters) after changes
- Verify TBT fixes don't regress other metrics
- Ensure no race conditions from async script loading

---

## Auto-Updated Rules (from LEARNINGS.md)

<!-- New rules will be appended here automatically by the skill-updater -->
