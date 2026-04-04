name: shopify-performance-audit
description: Generate a complete Shopify website performance audit report (.docx) by running PageSpeed Insights tests on Homepage, PDP, and PLP pages, collecting metrics, and producing a formatted document following the exact reference template.
user-invocable: true
allowed-tools:

- Read
- Write
- Bash
- WebFetch
- WebSearch
- Glob
- Grep
- AskUserQuestion

---

# Shopify Performance Audit Report Generator

## Purpose

Generate a complete, professionally formatted `.docx` performance audit report for any Shopify website. The skill:

1. Takes a Shopify website URL as input
2. Runs PageSpeed Insights tests (3 per page type) for Homepage, PDP, and PLP
3. Collects all performance metrics
4. Generates a `.docx` report following the EXACT reference template format
5. Replaces brand name, inserts metrics, and maintains strict formatting

---

## Input Required

When invoked, ask the user for:

1. **Website URL** (required) — e.g., `https://www.example.com/`
2. **PDP URL** (required) — a product detail page URL, e.g., `https://www.example.com/products/some-product`
3. **PLP URL** (required) — a product listing/collection page URL, e.g., `https://www.example.com/collections/some-collection`
4. **Brand Name** (required) — the brand name to use in the report
5. **Brand Logo** (optional) — path to a logo image file. If not provided, attempt to extract from the website. If extraction fails, ask the user.

---

## Step-by-Step Process

### Step 1: Run PageSpeed Insights Tests

For each page (Homepage, PDP, PLP), run **3 separate PageSpeed Insights API tests** for both Mobile and Desktop.

Use the Google PageSpeed Insights API:
```
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={URL}&strategy={mobile|desktop}&category=performance
```

For each test, collect:
- **Performance Score** (multiply by 100)
- **CLS** (Cumulative Layout Shift)
- **TBT** (Total Blocking Time) in ms
- **FCP** (First Contentful Paint) in seconds
- **LCP** (Largest Contentful Paint) in seconds
- **SI** (Speed Index) in seconds
- **Core Web Vitals** pass/fail status

Run **3 test rounds per page** with mobile + desktop in parallel per round = **9 parallel rounds total** (3 pages x 3 rounds). Each round fires 2 API calls simultaneously (mobile + desktop), so 18 API calls total but completes in the wall-clock time of ~9 sequential calls.

Calculate the **average** of 3 tests for each metric per page per device.

### Step 2: Analyze Metrics and Determine Scope

For each metric, compare against ideal benchmarks and assign scope:

| Scope Label | Condition |
|---|---|
| `Already good` | Value is within or better than ideal range |
| `Minor scope of improvements` | Value is slightly above ideal range |
| `Scope of improvements` | Value is moderately above ideal range |
| `Major scope of improvements` | Value is significantly above ideal range |

**Ideal Performance Benchmark Ranges:**

| Metric | Ideal Mobile Range | Ideal Desktop Range |
|---|---|---|
| PageSpeed Score | 50-65+ | 65-90+ |
| CLS | ≤ 0.1 | ≤ 0.1 |
| TBT | ≤ 800 ms | ≤ 600 ms |
| FCP | ≤ 2 sec | ≤ 1.8 sec |
| LCP | ≤ 3 sec | ≤ 2.5 sec |
| Speed Index | ≤ 4 sec | ≤ 3 sec |

**Scope Assignment Rules:**
- CLS: ≤0.1 = Already good, 0.1-0.25 = Minor scope, 0.25-0.5 = Scope of improvements, >0.5 = Major scope
- TBT Mobile: ≤800ms = Already good, 800-1500ms = Minor scope, 1500-3000ms = Scope of improvements, >3000ms = Major scope
- TBT Desktop: ≤600ms = Already good, 600-1000ms = Minor scope, 1000-2000ms = Scope of improvements, >2000ms = Major scope
- FCP Mobile: ≤2s = Already good, 2-4s = Minor scope, 4-6s = Scope of improvements, >6s = Major scope
- FCP Desktop: ≤1.8s = Already good, 1.8-3s = Minor scope, 3-5s = Scope of improvements, >5s = Major scope
- LCP Mobile: ≤3s = Already good, 3-6s = Minor scope, 6-12s = Scope of improvements, >12s = Major scope
- LCP Desktop: ≤2.5s = Already good, 2.5-4s = Minor scope, 4-8s = Scope of improvements, >8s = Major scope
- SI Mobile: ≤4s = Already good, 4-6s = Minor scope, 6-10s = Scope of improvements, >10s = Major scope
- SI Desktop: ≤3s = Already good, 3-5s = Minor scope, 5-8s = Scope of improvements, >8s = Major scope

### Step 3: Calculate Expected "After" Values

Based on current values and scope, calculate realistic expected improvement ranges:
- Performance Score Mobile: Current + 10-20 points (cap at 65)
- Performance Score Desktop: Current + 5-15 points (cap at 90)
- Core Web Vitals: If currently Failed → "Expected: Passed"; if Passed → "Passed"

### Step 4: Generate the .docx Report

Use Python with `python-docx` and `playwright` libraries to generate the report. Install if needed:
```bash
pip3 install python-docx playwright --user -q
python3 -m playwright install chromium
```

---

## Document Structure (EXACT FORMAT — Follow Reference Template)

### Cover / Title Area
- Title: **Website Performance Optimization**
- Brand: `{{BRAND_NAME}}`
- Submitted by: devx labs
- Brand logo in header (if available)

### Section 1: Executive Summary (STRICTLY SAME — Only replace brand name)

```
{{BRAND_NAME}}'s website performance has been analysed across Homepage, Product Detail Pages (PDP), and Collection Pages (PLP) to evaluate loading behaviour, visual stability, and user experience across devices. The audit highlights that while desktop performance remains relatively stable, mobile performance presents opportunities for improvement, particularly across rendering speed, loading prioritisation, and asset delivery.

The purpose of this optimisation initiative is to enhance overall performance efficiency while maintaining the existing design structure and functionality. The recommendations focus on improving Core Web Vitals stability, reducing delays during page load, and ensuring a smoother browsing experience across key customer journeys.
```

### Section 2: Website Performance Audit Report

#### Homepage Findings

**Current speed performance reports:**
- List 3 PageSpeed test URLs (mobile tab links)
- Add 1 extra link if available

**Before Data Table:**

| | Average Mobile | Average Desktop | Core Web Vitals Mobile | Core Web Vitals Desktop |
|---|---|---|---|---|
| Before | `{{HP_AVG_MOBILE}}` | `{{HP_AVG_DESKTOP}}` | `{{HP_CWV_MOBILE}}` | `{{HP_CWV_DESKTOP}}` |
| After speed opt. | `Expected: {{HP_EXPECTED_MOBILE}}` | `Expected: {{HP_EXPECTED_DESKTOP}}` | `{{HP_EXPECTED_CWV_MOBILE}}` | `{{HP_EXPECTED_CWV_DESKTOP}}` |

**What Can Be Done to Improve Website Speed:**

#### Improve CLS (Cumulative Layout Shift) — Max 4 pointers
- Goal text: "Our goal is to keep CLS close to 0 (~0) to improve load time, ensure visual stability on first view, and enhance the overall user experience."
- Show: Current CLS (Mobile): `{{VALUE}}` (`{{SCOPE}}`), Current CLS (Desktop): `{{VALUE}}` (`{{SCOPE}}`)
- **To improve CLS** (SAME pointers as reference):
  - We need to ensure that no elements move or change their size or position during the page load process.

#### Improve TBT (Total Blocking Time) — Max 4 pointers
- Show: Current TBT (Mobile): `{{VALUE}}` (`{{SCOPE}}`), Current TBT (Desktop): `{{VALUE}}` (`{{SCOPE}}`)
- "We need to reduce this blocking time to below 1000 ms, ideally around 500 ms (in optimal cases)."
- **To improve TBT** (SAME as reference):
  - This can be achieved by optimizing scripts, CSS, and managing third-party integrations that contribute to blocking the main thread.

#### Improve FCP (First Contentful Paint) — Max 5 pointers
- Show: Current FCP (Mobile): `{{VALUE}}` (`{{SCOPE}}`), Current FCP (Desktop): `{{VALUE}}` (`{{SCOPE}}`)
- "FCP measures how long it takes for the first visible element to render on page load. It depends largely on code quality, DOM size, and critical or third-party scripts."
- **To improve FCP** (SAME as reference):
  - Optimize and clean up code in the theme.liquid file.
  - Reduce and manage critical and third-party scripts as much as possible.

#### Improve LCP (Largest Contentful Paint) — Max 6 pointers
- Show: Current LCP (Mobile): `{{VALUE}}` (`{{SCOPE}}`), Current LCP (Desktop): `{{VALUE}}` (`{{SCOPE}}`)
- "LCP is one of the most impactful metrics for page load speed."
- **To improve LCP** (SAME as reference):
  - Ensure the LCP element remains consistent on every page load.
  - Set fetch priority = high for the LCP element.
  - Set fetch priority = low for all other non-critical assets.
  - Lazy load all images except the LCP element to avoid heavy asset loading on initial render.
- If large gap between FCP and LCP on mobile, add: "There is a major gap between FCP and LCP on mobile (around {{GAP}} seconds, i.e., {{LCP}} sec - {{FCP}} sec). This delay is primarily caused by slow LCP element loading and render delays, which we need to optimize."

#### Improve SI (Speed Index) — Max pointers same as reference
- Show: Current SI (Mobile): `{{VALUE}}` (`{{SCOPE}}`), Current SI (Desktop): `{{VALUE}}` (`{{SCOPE}}`)
- "Speed Index depends on the performance of all the above metrics, but is also influenced by other factors:"
- **Pointers** (SAME as reference):
  - Optimize or remove long-running JavaScript functions and network tasks.
  - Rearrange scripts in network calls based on priority and dependency.
  - Reduce inter-dependencies among scripts to eliminate waiting time.
  - Follow best coding practices to keep solutions minimal, efficient, and easy to execute.

#### Additional Optimization Points — Max 7 total (SAME as reference, may add extras)
- Remove unused or unnecessary apps from the store.
- Clean up legacy code from previously used apps that are no longer active.
- Convert images to next-generation formats (WEBP, PNG) to improve render speed.
- Resize and serve images according to actual display dimensions.
- "For example, if a product card displays an image at 300×300, avoid loading a 1000×1000 version, as it increases CPU load and slows down the page."

### Section 3: Summary / Action Plan (STRICTLY SAME — No Changes)

#### Cumulative Layout Shift (CLS)
- Set fixed width & height for images, videos, and banners.
- Predefine container sizes for all dynamic elements (reviews, icons, etc.).
- Avoid inserting new elements above existing content after load.

#### Total Blocking Time (TBT)
- Defer or async non-critical JavaScript files.
- Minimize third-party scripts (tracking, analytics, chat widgets).
- Move non-essential scripts to load on user interaction (scroll, click, etc.).
- Split large JS bundles; optimize Shopify theme.js and custom scripts.
- Remove unused CSS and JS from the theme.

#### First Contentful Paint (FCP)
- Optimize theme.liquid by cleaning up unnecessary code and inline scripts.
- Reduce critical JS/CSS and prioritize above-the-fold content.
- Use `<picture>` tags and responsive images for mobile and desktop.
- Limit the number of third-party scripts running on page load.

#### Largest Contentful Paint (LCP)
- Identify and prioritize the main LCP element (usually banner image or hero text).
- Set fetchpriority="high" for LCP element; fetchpriority="low" for others.
- Lazy load all images except the LCP one.
- Compress and serve LCP images in WEBP format.
- Avoid animations or opacity transitions on the LCP element.
- Ensure the LCP element appears within the first viewport and is consistent on reload.

#### Speed Index (SI)
- Optimize overall code execution order (critical first).
- Reorder scripts based on dependency and importance.
- Remove long-running JS tasks and optimize loops or event listeners.
- Keep DOM structure lightweight.
- Follow clean, modular code practices.

#### Additional Optimizations
- Remove unused or disabled apps from Shopify.
- Clean up old app code snippets left in theme.liquid or assets.
- Convert images to next-gen formats (WEBP/PNG).
- Serve images in exact required sizes (no oversized assets).

### Section 4: PDP (Product Detail Page) Findings

**Current speed performance reports:**
- List 3 PageSpeed test URLs

**Table:** (Same format as Homepage table with PDP values)

**What Can Be Done to Improve Website Speed:**
- For each metric (CLS, TBT, FCP, LCP, SI): show current values + scope
- NO extra detailed explanation like homepage — just values and scope

### Section 5: PLP (Product Listing Page) Findings

**Current speed performance reports:**
- List 3 PageSpeed test URLs

**Table:** (Same format as Homepage table with PLP values)

**What Can Be Done to Improve Website Speed:**
- For each metric (CLS, TBT, FCP, LCP, SI): show current values + scope
- NO extra detailed explanation like homepage — just values and scope

### Section 6: Common Performance Improvements (Dynamic based on findings)

#### Total Blocking Time (TBT)
- Optimizing JS files: swiper and animations.
- Cart and bundle-related scripts (including third-party apps)
- Ensuring scripts load only when needed and do not block the main page.

#### First Contentful Paint (FCP)
- Third-party apps or plugins: Marketing and tracking scripts
- Improving image loading and delivery.
- The first visible image loads immediately when the page opens.
- Reviewing framework usage (e.g., React) to minimize its impact on initial load time.

#### Largest Contentful Paint (LCP)
- Render-blocking resources.
- Fixing image loading priorities so key visuals load first.
- Optimizing image sizes and delivery for different devices.

**Note:** "Core Web Vitals data on Google updates approximately 28 days after the site goes live, so we'll need to wait for that period after go-live to see the actual impact from real user data."

### Section 7: Ideal Performance Benchmark Range (SAME unless major need to change)

| Metric | Ideal Mobile Range | Ideal Desktop Range |
|---|---|---|
| PageSpeed Score | 50-65+ | 65-90+ |
| CLS | ≤ 0.1 | ≤ 0.1 |
| TBT | ≤ 800 ms | ≤ 600 ms |
| FCP | ≤ 2 sec | ≤ 1.8 sec |
| LCP | ≤ 3 sec | ≤ 2.5 sec |
| Speed Index | ≤ 4 sec | ≤ 3 sec |

### Section 8: Performance Metrics Glossary (STRICTLY SAME)

| Metric | Definition |
|---|---|
| LCP (Largest Contentful Paint) | Measures how long it takes for the main visible content (largest image or text block) to load on the screen. |
| FCP (First Contentful Paint) | Indicates when the first visual element appears, showing that the page has started loading. |
| TBT (Total Blocking Time) | Calculates how long the page stays unresponsive due to heavy scripts blocking user interaction. |
| CLS (Cumulative Layout Shift) | Tracks unexpected layout movements while the page loads, affecting visual stability. |
| Speed Index | Shows how quickly the visible parts of the page are populated during loading. |

### Section 9: Expected Performance Outcomes (STRICTLY SAME — Only replace brand name)

```
Based on the current analysis and optimisation scope, the following outcomes are expected:

- Faster and more responsive mobile browsing across Homepage, PDP, and PLP pages
- Improved loading priority for key visual elements, allowing important content to appear sooner
- Reduced layout shifts, resulting in a more stable and consistent page experience
- Smoother interaction readiness with fewer delays caused by heavy scripts and background processes
- Better sequencing of scripts and assets, creating a more efficient overall loading flow
- Improved Core Web Vitals stability aligned with modern performance benchmarks

Overall, these improvements are expected to create a smoother and more reliable browsing journey, helping users explore products with less friction and enhancing their overall experience on the website.
```

### Section 10: Timeline (STRICTLY SAME)

| Phase | Duration | Focus |
|---|---|---|
| Phase 1: Cleanup & Script Optimization | Week 1 | Remove unused apps, defer JS, clean CSS |
| Phase 2: Image & Media Optimization | Week 2 | Convert → WEBP, lazy-load, define aspect ratios |
| Phase 3: Server & CDN Setup | Week 3 | Configure Cloudflare, gzip/Brotli, preconnect |
| Phase 4: QA & Validation | Week 3 | Lighthouse testing & regression fixes |

### Section 11: Deliverables (STRICTLY SAME)

- Homepage, PDP & PLP performance optimisation
- Script and asset refinement
- Media and loading optimisation
- Pre- and post-performance validation
- Technical optimisation implementation
- Technical documentation for maintenance

### Section 12: Assumption (STRICTLY SAME)

- Optimisation will be carried out within the existing Shopify theme and current website structure.
- Third-party apps, marketing scripts, and platform behaviour may influence performance results.
- Improvements will aim for the highest feasible optimisation within the current setup.
- New features, integrations, or design changes during the optimisation phase may affect performance outcomes.
- Core Web Vitals field data take up to 28 days to reflect post-deployment improvements.
- Scope is limited to performance optimisation; UI/UX redesign or functional changes are not included unless discussed separately.
- Required access to theme files, apps, and tools will be provided for implementation.

### Section 13: Cost Estimate (STRICTLY SAME)

| Total Cost Estimate | INR 1,70,000 + GST |

### Section 14: Conclusion (STRICTLY SAME — Only replace brand name)

```
{{BRAND_NAME}}'s website demonstrates a strong desktop foundation, with the primary opportunity centred around improving mobile performance. Through structured optimisation across scripts, assets, and loading behaviour, the website can become more faster with faster load times while maintaining its existing design and user experience.
```

### Footer (EXACT SAME in every report — every page)

```
Devxconsultancy Private Limited
https://www.devxlabs.ai/

U-56, Sandhya Darshan Apartment,
Surat, Gujarat, India - 395009

GSTIN:24AAKCD0230A1ZJ | PAN:AAKCD0230A
```

---

## Scope of Improvements — Allowed Values ONLY

You must ONLY use the following exact wording for scope labels:
- `Already good`
- `Minor scope of improvements`
- `Scope of improvements`
- `Major scope of improvements`

No other wording is allowed. Ever.

---

## Document Formatting Rules

1. Use consistent font: Calibri or Arial, 11pt body text
2. Headings: Bold, larger font size (14pt for H1, 12pt for H2)
3. Tables: Bordered, header row shaded
4. Bullet points: Use standard list formatting
5. PageSpeed links: Include as clickable hyperlinks
6. Brand logo: Insert in document header if available
7. Footer: Must appear on every page
8. Page breaks: Between major sections

---

## Python Script Execution

When generating the report, create and execute a Python script that:

1. Uses `python-docx` to build the document
2. Makes API calls to PageSpeed Insights using `urllib.request` for metrics collection
3. Uses `playwright` (headless Chromium) to get shareable analysis URLs with unique analysis IDs
4. Parses JSON responses to extract metrics
5. Calculates averages across 3 tests
6. Determines scope labels
7. Builds the complete document with all sections, including shareable report links
8. Saves as `{{BRAND_NAME}} Performance Audit Report.docx`

**API Key (MANDATORY — hardcoded in script):**
```
AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674
```
- This key is hardcoded in `generate_report.py` and used automatically
- Can be overridden via `--api-key` argument or `GOOGLE_PSI_API_KEY` env variable
- **NEVER call the API without a key** — the free/unauthenticated quota is effectively 0 and will instantly return 429 errors

**API URL format:**
```
https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&strategy={mobile|desktop}&category=performance&key={API_KEY}
```

**Optimized Test Execution (Parallel Mobile + Desktop):**
- For each test round, mobile and desktop API calls run **in parallel** using `ThreadPoolExecutor`
- This means 3 test rounds per page = 3 parallel pairs = 6 API calls but in the wall-clock time of 3
- Total: 9 rounds across 3 pages, completing in ~half the time vs sequential
- Add **15 seconds delay** between test rounds per page to avoid rate limits

**PageSpeed Report Links (CRITICAL — must be direct shareable links with analysis IDs):**

The report MUST include direct shareable links that point to already-generated analysis results, NOT links that trigger a new test.

**Required URL format:**
```
https://pagespeed.web.dev/analysis/{url-slug}/{analysis-id}?form_factor=mobile
```
Example: `https://pagespeed.web.dev/analysis/https-beardo-in/mp00q2r4jd?form_factor=mobile`

**How to get these links — Use Playwright browser automation:**

The PageSpeed Insights API (googleapis.com) does NOT return shareable analysis IDs. The analysis ID is generated only by pagespeed.web.dev's web UI. To get shareable links, use Playwright to automate the web UI:

1. Install Playwright if needed: `pip3 install playwright --user -q && python3 -m playwright install chromium`
2. For each page URL, open `https://pagespeed.web.dev/analysis?url={encoded_url}&form_factor=mobile` in headless Chromium
3. **CRITICAL — Cache busting:** Append a unique cache-busting query parameter (`?_cb=timestamp_index` or `&_cb=timestamp_index`) to the URL passed to pagespeed.web.dev. This forces a fresh Lighthouse test each time instead of returning cached results.
4. Wait for the URL to change to the pattern `**/analysis/*/*?**` (this means the analysis completed and an ID was assigned)
5. Capture the final URL — this is the shareable link with the analysis ID
6. **Add 20-second delay between Playwright sessions** for the same page to ensure fresh tests
7. Timeout: 180 seconds per page (Lighthouse analysis takes 30-90 seconds)

**CRITICAL — Cache Busting for Playwright Sessions:**

pagespeed.web.dev caches Lighthouse results for the same URL. If you run 3 tests for the same URL in quick succession, all 3 will return identical cached data even though different analysis IDs are generated. To get truly unique test results:

1. **Append a unique cache-busting query parameter** to the URL BEFORE passing it to pagespeed.web.dev:
   - Format: `{url}?_cb={unix_timestamp}_{test_index}` (or `&_cb=...` if URL already has `?`)
   - Example: `https://beardo.in/?_cb=1708123456_1`, `https://beardo.in/?_cb=1708123456_2`
   - This makes pagespeed.web.dev treat each request as a different URL, forcing a fresh Lighthouse run

2. **Add 20-second delay between sessions** for the same page

3. **Use a fresh browser context per session** — create a new `browser.new_context()` with no cookies/cache for each test to prevent any browser-level caching

4. **Validate uniqueness**: After collecting 3 links, the analysis IDs must be different AND the underlying data should differ (scores will naturally vary between fresh Lighthouse runs)

**Implementation pattern (Python):**
```python
from playwright.sync_api import sync_playwright
import urllib.parse
import time

def get_shareable_psi_links(url, num_links=3, form_factor='mobile'):
    links = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for i in range(num_links):
            # Cache-busting: append unique param to force fresh Lighthouse test
            ts = int(time.time())
            separator = '&' if '?' in url else '?'
            busted_url = f'{url}{separator}_cb={ts}_{i}'
            encoded = urllib.parse.quote(busted_url, safe='')
            psi_url = f'https://pagespeed.web.dev/analysis?url={encoded}&form_factor={form_factor}'

            # Fresh browser context per test (no cookies/cache)
            context = browser.new_context()
            page = context.new_page()
            page.goto(psi_url, timeout=30000)
            page.wait_for_url('**/analysis/*/*?**', timeout=180000)
            links.append(page.url)
            context.close()

            if i < num_links - 1:
                time.sleep(20)  # Delay between sessions
        browser.close()
    return links
```

**When to collect shareable links:**
- Run 3 Playwright sessions per page (one per test round) to get 3 unique shareable links with unique data
- These can run in parallel with the API-based metric collection, OR sequentially after API tests
- The Playwright sessions also run Lighthouse internally, so metrics could be extracted from the web UI too — but the API is more reliable for structured data
- If Playwright fails (timeout, browser crash), fall back to the non-shareable format: `https://pagespeed.web.dev/analysis?url={encoded_url}&form_factor=mobile`

**IMPORTANT:** Do NOT use the old format `https://pagespeed.web.dev/analysis?url=...` as the primary link — this triggers a NEW test instead of showing existing results. Only use it as a fallback if Playwright fails.

**Cookie / Cache Bypass — Preventing Duplicate Results (for BOTH API calls and Playwright):**

1. **Append a unique cache-busting query parameter** to each test URL:
   - Use current Unix timestamp + test index so every run is unique
   - If URL already has query params, use `&_cb=...` instead of `?_cb=...`
   - Apply to BOTH the API calls (urllib) AND the Playwright sessions

2. **Add delays between test rounds** for the same page:
   - API calls: 15-second delay between rounds
   - Playwright sessions: 20-second delay between sessions

3. **Use fresh browser contexts** in Playwright — `browser.new_context()` per test, then `context.close()`

4. **Validate results are unique**: After collecting 3 results, compare scores. If all identical:
   - Wait 30 seconds, re-run one test with fresh cache-buster, replace middle result

4. **Set request headers**: `Cache-Control: no-cache`, `Pragma: no-cache`

**Error Handling for API calls:**
- On HTTP 429 (rate limit): exponential backoff — 30s, 60s, 120s, 240s (up to 4 retries)
- On HTTP 500 (server error): retry after 15 seconds (up to 4 retries)
- On other errors: retry after 15 seconds (up to 4 retries)
- Timeout per request: 180 seconds (Lighthouse can be slow)

---

## Output

The final output file will be saved at:
```
/Users/dharmikkakadiya/Desktop/{{BRAND_NAME}} Performance Audit Report.docx
```

After generation, inform the user:
- File location
- Summary of all collected metrics (Mobile & Desktop averages for each page)
- Any issues encountered during PageSpeed testing

---

## Error Handling

- If PageSpeed API returns 429: exponential backoff with retries (key is mandatory to avoid this)
- If PageSpeed API returns 500: retry up to 4 times with 15s delay
- If python-docx is not installed, install it automatically with `pip3 install python-docx --user -q`
- If playwright is not installed, install it automatically with `pip3 install playwright --user -q && python3 -m playwright install chromium`
- If Playwright fails to get a shareable link (timeout, crash), fall back to non-shareable format
- If brand logo cannot be extracted from website, ask the user to provide it manually.
- If PDP or PLP URLs are not provided, ask the user before proceeding.
- Always run with `PYTHONUNBUFFERED=1` so progress output is visible in real-time

---

## Safeguards

- Never edit application source files.
- Only create the output .docx file.
- Do not upload or share the document externally.
- Keep all API calls read-only (PageSpeed Insights only).

---

## Learnings (from production runs)

### 2026-02-18: First Run Learnings

**1. API Key is MANDATORY — never run without it**
- The free/unauthenticated PageSpeed Insights API has a daily quota of effectively 0 requests
- Without an API key, ALL requests return `HTTP 429: Quota exceeded` immediately
- The error message says: `"quota_limit_value": "0"` for the shared consumer project
- **Fix**: API key `AIzaSyBIjNlne770dB5IiTzHOGM1A2NxNBd8674` is hardcoded in the script
- Always append `&key={API_KEY}` to every API request

**2. Python output buffering hides progress**
- When running via background tasks, Python buffers stdout so no output is visible for minutes
- **Fix**: Always run with `PYTHONUNBUFFERED=1` environment variable

**3. Unbound variable bug in error handling**
- Original code had `except Exception as e:` inside a for loop but referenced `e` after the loop
- If the exception was caught on last attempt, `e` existed; but if caught and retried, it could be unbound
- **Fix**: Use `last_error = "Unknown error"` before the loop and `last_error = str(e)` inside each except

**4. HTTP 500 errors are common from PageSpeed API**
- The Lighthouse backend occasionally returns 500 Internal Server Error
- This is normal — the test just needs to be retried
- **Fix**: Retry up to 4 times with 15-second delay for 500 errors

**5. Rate limiting (429) requires exponential backoff**
- Even with an API key, rapid consecutive requests can trigger rate limits
- **Fix**: Exponential backoff: 30s → 60s → 120s → 240s between retries on 429

**6. Sequential mobile+desktop tests waste time**
- Running Mobile 1 → Desktop 1 → Mobile 2 → etc. sequentially doubles the total time
- Mobile and desktop tests are completely independent
- **Fix**: Use `ThreadPoolExecutor` to run mobile + desktop in parallel per test round
- This cuts wall-clock time nearly in half (3 rounds instead of 6 sequential calls per page)

**7. Report links must be direct shareable URLs with analysis IDs**
- The PageSpeed API (googleapis.com) does NOT return pagespeed.web.dev analysis IDs
- The `id` field in the API response is just the tested URL, not an analysis identifier
- The format `https://pagespeed.web.dev/analysis?url={encoded_url}&form_factor=mobile` triggers a NEW test — not useful for sharing existing results
- The correct shareable format is: `https://pagespeed.web.dev/analysis/{url-slug}/{analysis-id}?form_factor=mobile`
- The analysis ID is generated only by pagespeed.web.dev's web UI backend
- **Fix**: Use Playwright (headless Chromium) to open pagespeed.web.dev, wait for the analysis to complete, and capture the final URL which contains the unique analysis ID
- Install: `pip3 install playwright --user -q && python3 -m playwright install chromium`
- The URL changes from `?url=...` to `/analysis/{slug}/{id}?form_factor=...` when the test completes
- Use `page.wait_for_url('**/analysis/*/*?**', timeout=180000)` to detect completion
- Each Playwright session takes 30-90 seconds (same as the Lighthouse test duration)
- Run 3 sessions per page to get 3 unique shareable links for the report

**8. Playwright shareable links return cached/identical data without cache-busting**
- pagespeed.web.dev caches Lighthouse results for the same URL
- Running 3 Playwright sessions for the same URL in quick succession returns 3 different analysis IDs but with IDENTICAL data/scores
- The analysis IDs are unique but the underlying Lighthouse test is not re-run — it serves the cached result
- **Fix**: Append a unique cache-busting query parameter to the URL BEFORE passing it to pagespeed.web.dev
  - Format: `{url}?_cb={unix_timestamp}_{test_index}` (or `&_cb=...` if URL already has `?`)
  - This makes pagespeed.web.dev treat each request as a different URL, forcing a fresh Lighthouse run
- **Fix**: Use `browser.new_context()` per session and `context.close()` after — ensures no browser-level cookie/cache sharing
- **Fix**: Add 20-second delay between Playwright sessions for the same page
- **Fix**: The `qn('w:r:id')` call in python-docx fails for hyperlinks — use the full namespace URI instead: `'{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'`

**9. Brand logo extraction from Shopify sites**
- Shopify sites render dynamically; the HTML source may not contain obvious `<img>` logo tags
- **Fix**: Search for CDN URLs containing "logo" or "brand" in the page source using regex
- Pattern: `//www.{domain}/cdn/shop/files/*logo*` or `//cdn.shopify.com/s/files/*logo*`
- If not found, ask user to provide logo manually

**10. Each PageSpeed test takes 30-60 seconds**
- The Lighthouse audit runs remotely and takes significant time per request
- With 3 parallel rounds per page + 15s delays = ~3-4 minutes per page
- Total for 3 pages: ~10-12 minutes (down from ~20 minutes with sequential approach)
- Always run as background task and inform user about expected wait time
