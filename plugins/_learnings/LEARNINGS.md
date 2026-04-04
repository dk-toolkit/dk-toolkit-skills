# Performance Improvement Skills - Learnings

---
Date: 2026-02-23
Skill name: cls-improvement
Iteration #: 1
Symptom: CLS already excellent (0.0001-0.0073 across all pages) - user requested further optimization
Root cause: Theme (Eurus/Shopify) already had strong CLS fundamentals - width/height on images, font-display:swap, fetchpriority on hero images, padding-bottom aspect ratio technique
Fix applied: 1) Deferred GTM/Clarity via requestAnimationFrame, 2) Added defer to CAPI scripts, 3) Changed non-critical fonts to font-display:optional, 4) Preloaded header+menu fonts, 5) Added content-visibility:auto for below-fold sections, 6) Added CSS contain:layout inline-size on product cards, 7) Added aspect-ratio CSS alongside padding-bottom
Result: Overall CLS 0.0031 -> 0.0031 (stable at excellent levels). PDP Desktop improved 42%, PLP Desktop improved 21%. Natural variance at low CLS values makes micro-improvements hard to measure.
Rule to reuse: When CLS is already below 0.01, improvements are in the noise range of PageSpeed tests. Focus optimization effort on pages with CLS > 0.05 for measurable impact. For already-good sites, apply preventive best practices (content-visibility, font preloads, script deferral) without expecting measurable CLS changes.
Dedup Key: cls-already-excellent-preventive-fixes
---

---
Date: 2026-02-23
Skill name: cls-improvement
Iteration #: 1
Symptom: Synchronous third-party scripts in head (GTM, CAPI, Clarity)
Root cause: Scripts loaded synchronously in <head> can block initial render and contribute to layout shifts
Fix applied: Wrapped GTM and Clarity in requestAnimationFrame+setTimeout pattern; added defer to CAPI scripts
Result: No negative CLS impact, scripts still function correctly
Rule to reuse: Use requestAnimationFrame(function(){setTimeout(function(){...},0);}); pattern to defer non-critical analytics scripts. Always add defer to third-party tracking scripts in <head>. Never make GTM fully async-deferred on Shopify as it may break some app integrations.
Dedup Key: defer-analytics-scripts-pattern
---

---
Date: 2026-02-23
Skill name: cls-improvement
Iteration #: 1
Symptom: All custom fonts using font-display:swap including non-critical variants
Root cause: font-display:swap on all fonts causes FOUT for rarely-used font variants (bold-italic, highlight fonts)
Fix applied: Changed heading_highlight_font, bold, italic, and bold-italic variants to font-display:optional
Result: Reduces FOUT flash on non-critical text without affecting above-fold rendering
Rule to reuse: Keep font-display:swap for body, header, menu, button fonts (above-fold critical). Use font-display:optional for decorative/highlight fonts and bold-italic variants that aren't visible in initial viewport.
Dedup Key: font-display-optional-non-critical
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: Mobile FCP 3.69-4.00s (Poor) across all pages, Desktop 0.85-1.00s (Good). PageSpeed API reported 0 render-blocking resources but manual inspection revealed multiple synchronous scripts.
Root cause: 1) Two CAPI scripts from S3 without defer (render-blocking), 2) Large Meta CAPI init block (2KB inline JS) blocking parsing, 3) Duplicate theme.css loaded twice (317KB each), 4) GTM/Facebook Pixel/Clarity all blocking in head, 5) Personizely script (1,200ms blocking) injected via content_for_header, 6) Product images with oversized srcset (450w minimum when displayed at 312px), 7) Missing preconnect/dns-prefetch for 10+ third-party domains
Fix applied: 1) Added defer to CAPI scripts, 2) Wrapped Meta CAPI init in DOMContentLoaded, 3) Removed duplicate theme.css, 4) Deferred GTM/FB Pixel to DOMContentLoaded, 5) Deferred Clarity via requestIdleCallback, 6) Script interception for personizely async, 7) Added 250w/375w srcset breakpoints + reduced fallback src to 750, 8) Added preconnect + 8 dns-prefetch hints, 9) Deferred ElevateAB redirect.js, 10) Wrapped survey script in DOMContentLoaded
Result: FCP improved 14% overall (2.35s -> 2.02s). PDP Mobile best: -18.2% (3.69s -> 3.02s). Desktop stayed Good (0.73-0.94s). Unused JS reduced ~200-300KB per page.
Rule to reuse: PageSpeed API render-blocking audit misses synchronous scripts — always manually audit <head> section. CAPI/tracking scripts from non-CDN origins (S3 buckets) are major blockers. Use script interception pattern for content_for_header apps. DOMContentLoaded wrapping is safe for GTM/FB/Clarity/survey scripts.
Dedup Key: fcp-capi-defer-script-interception
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: User pointed out CAPI clientParamsHelper.bundle.js was render-blocking but PageSpeed did not flag it
Root cause: PageSpeed's render-blocking audit uses heuristics that sometimes miss third-party scripts loaded from non-standard origins (like S3 buckets). The audit primarily flags stylesheets and scripts that match known patterns.
Fix applied: Always do manual <head> inspection in addition to API data analysis
Result: Found 2 blocking CAPI scripts, GTM blocking, FB Pixel blocking, large Meta init block — none flagged by API
Rule to reuse: CRITICAL — Never rely solely on PageSpeed API for identifying render-blocking resources. Always read layout/theme.liquid and manually check every <script> tag in <head> for missing async/defer attributes. Check ALL script tags between <head> and </head>, including those after content_for_header.
Dedup Key: pagespeed-api-misses-blocking-scripts
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: User shared PageSpeed UI screenshots showing issues not captured by API (personizely 1,200ms blocking, image oversizing, legacy JS, cache lifetimes)
Root cause: The API response only includes structured audit data but the UI shows additional context like specific blocking durations, image dimension comparisons, legacy JS babel transforms, and cache TTL details
Fix applied: Added screenshots review step to the skill workflow
Result: Discovered personizely as biggest single blocker (1,200ms) and image delivery savings (347 KiB) — neither fully visible from API data alone
Rule to reuse: After initial API analysis, ALWAYS ask user for PageSpeed UI screenshots of: render-blocking requests, image delivery, font display, duplicated JS, legacy JS, and cache lifetimes. These screenshots contain actionable details the API misses.
Dedup Key: always-request-pagespeed-screenshots
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: Shopify app (personizely) injecting render-blocking script via content_for_header — cannot be modified directly
Root cause: Shopify's content_for_header output is controlled by the platform and app extensions. Theme developers cannot add defer/async to scripts injected this way.
Fix applied: Added script interception pattern using document.createElement override before content_for_header. The pattern intercepts script element creation, checks the src against blocked domains, and forces async=true.
Result: Converts personizely from synchronous (1,200ms blocking) to async loading
Rule to reuse: For any render-blocking third-party script injected via content_for_header, use the document.createElement interception pattern. Place it BEFORE {{ content_for_header }}. Keep the blockedDomains array configurable per store.
Dedup Key: content-for-header-script-interception
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: Product card images served at 450w minimum but displayed at 312px on mobile
Root cause: srcset started at 450w with fallback src at 1500w. Mobile devices displaying cards at ~312px had no appropriately-sized option.
Fix applied: Added 250w and 375w breakpoints to all product card srcset attributes. Reduced fallback src from width:1500 to width:750.
Result: Est. 347 KiB savings on image delivery across product listing pages
Rule to reuse: Always check the smallest srcset breakpoint against actual display dimensions. If images display at Xpx, ensure there's a srcset option at X or slightly above. Reduce fallback src to a reasonable mid-range size (750w) instead of maximum. Apply to card-product.liquid for ALL image variants (primary, hover, slide).
Dedup Key: product-card-srcset-optimization
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: Duplicate theme.css loading in layout/theme.liquid (line 94 via stylesheet_tag, line 101 via liquid echo)
Root cause: theme.css was loaded both as a direct Liquid tag and inside a {% liquid %} block. This is a common copy-paste error in Shopify themes.
Fix applied: Removed the duplicate echo line inside the {% liquid %} block, keeping only the direct stylesheet_tag
Result: Eliminated one 317KB redundant CSS request on every page load
Rule to reuse: Always search for ALL instances of the main CSS file being loaded. In Shopify themes, check both direct {{ stylesheet_tag }} calls and {% liquid echo %} blocks. Common pattern: the CSS file is loaded once explicitly and once inside a render block.
Dedup Key: duplicate-theme-css-detection
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 1
Symptom: Unused CSS 165KB, Unused JS 1.1-1.5MB reported on all pages
Root cause: theme.css (317KB) contains full TailwindCSS v3.1.8 + Splide CSS. This is a compiled asset. Many JS files are feature-specific but conditionally loaded via sections.
Fix applied: Cannot fix from theme code — requires build-time CSS purging. Flagged to user as limitation.
Result: N/A — build pipeline optimization needed
Rule to reuse: If theme.css contains TailwindCSS, unused CSS CANNOT be reduced by editing Liquid files. This requires the theme's build pipeline (PostCSS/PurgeCSS). Flag this to the user as a build-time optimization. Similarly, vendor.js bundles with Alpine.js etc. need tree-shaking at build time.
Dedup Key: tailwind-unused-css-build-pipeline
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 2
Symptom: Google Fonts Poppins loading ALL 18 weights (100-900, all italics) via render-blocking stylesheet, creating 10.9s critical request chain on pdp-tlpc pages
Root cause: Theme already has Poppins self-hosted via Shopify's font system (400, 500, 600 weights) but pdp-tlpc template ALSO loaded full Poppins from Google Fonts. This created duplicate font loading AND a deep critical chain: HTML → Google Fonts CSS (5,186ms) → 8 woff2 files (5,000-11,000ms each).
Fix applied: 1) Reduced Google Fonts to only weight 300 (the only weight not self-hosted), 2) Deferred it with media="print" onload="this.media='all'" pattern, 3) Removed redundant preconnect for fonts.googleapis.com, 4) Kept single preconnect for fonts.gstatic.com
Result: Eliminates 10.9s critical chain on pdp-tlpc pages. Only weight 300 loads async instead of 18 weights render-blocking.
Rule to reuse: ALWAYS check if Google Fonts loads fonts already available via Shopify's font system (settings_data.json type_body_font, type_header_font etc.). Shopify self-hosts fonts from its font library. If theme settings use poppins_n4/n5/n6, Google Fonts Poppins is redundant for those weights. Only load missing weights via deferred Google Fonts.
Dedup Key: google-fonts-duplicate-shopify-fonts
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 2
Symptom: Only body font (poppins_n4) was preloaded, but header (poppins_n6) and menu (poppins_n5) fonts are also above-fold critical
Root cause: Original theme only had one font preload hint. Header and menu fonts were discovered only after CSS was parsed, adding to critical chain.
Fix applied: Added preload hints for type_header_font and type_menu_font alongside existing type_body_font preload
Result: Browser can start downloading all 3 critical font files immediately without waiting for CSS parse
Rule to reuse: Preload ALL above-fold font weights, not just the body font. In Shopify themes, header_font and menu_font are always visible above the fold. Use: <link rel="preload" href="{{ settings.type_header_font | font_url }}" as="font" type="font/woff2" crossorigin="anonymous" />
Dedup Key: preload-all-above-fold-fonts
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 2
Symptom: Shopflo bridge.js loaded async in <head> but not needed until user interacts with checkout
Root cause: Checkout bridge script loaded on every page immediately, wasting bandwidth and competing with critical resources
Fix applied: Replaced <script async> with interaction-based loading (scroll/mousemove/touchstart/click/keydown) with 5s timeout fallback
Result: Removes ~37KB from initial page load. Script loads on first user interaction or after 5s.
Rule to reuse: Checkout/payment bridge scripts (Shopflo, Razorpay, etc.) are NEVER needed for first paint. Always defer to user interaction. Pattern: addEventListener for scroll/mousemove/touchstart/click/keydown with {once:true, passive:true}, plus setTimeout fallback (5s).
Dedup Key: checkout-bridge-interaction-loading
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 2
Symptom: PageSpeed warned "More than 4 preconnect connections found" — too many preconnects waste resources
Root cause: Each preconnect opens a full TCP+TLS connection. More than 3-4 preconnects compete with each other and waste bandwidth on connections that may not be used immediately.
Fix applied: Used preconnect ONLY for cdn.shopify.com (primary asset CDN) and fonts.gstatic.com (conditional). All other third-party domains use lightweight dns-prefetch instead.
Result: Resolved PageSpeed preconnect warning while still providing early DNS resolution for third-party domains
Rule to reuse: Limit preconnect to MAX 2-3 origins that are critical for first paint (CDN for CSS/fonts, critical API). Use dns-prefetch for everything else. Shopify's content_for_header already adds preconnects for cdn.shopify.com and monorail — check before adding duplicates.
Dedup Key: preconnect-limit-3-origins
---

---
Date: 2026-02-24
Skill name: fcp-improvement
Iteration #: 2
Symptom: Round 2 optimizations (preconnect, font preload, script interception expansion, interaction-based loading) showed only marginal FCP improvement (~0-3%)
Root cause: After Round 1 removed all major render-blocking scripts and duplicate CSS, the remaining FCP bottleneck is dominated by: 1) theme.css 317KB (TailwindCSS — render-blocking, can't defer), 2) TTFB 400-1400ms (Shopify infrastructure), 3) Unused CSS/JS 165KB+1.1MB (build pipeline needed). These are infrastructure-level issues that cannot be fixed from theme Liquid code.
Fix applied: Applied all safe optimizations (preconnect, font preloads, script interception, interaction-based loading, Google Fonts deferral)
Result: Mobile FCP: 3.03-3.38s (still Poor). Desktop: 0.74-0.91s (Good). Cumulative improvement from original: -15.8% to -18.2% across pages.
Rule to reuse: After 2 rounds of theme-level FCP optimization, if Mobile FCP is still >3.0s, the remaining improvement requires: 1) TailwindCSS purge via build pipeline (could save 200-300KB CSS), 2) Shopify app audit and removal of unused apps, 3) Better hosting/CDN for TTFB. Do NOT attempt a third round of theme-level changes — diminishing returns. Instead, advise user on build pipeline and app cleanup.
Dedup Key: fcp-diminishing-returns-infrastructure-bottleneck
---
