---
name: js-standards
description: >
  MANDATORY JavaScript standards for Shopify themes. This skill MUST be applied automatically whenever
  Claude writes, edits, reviews, or generates ANY JavaScript code — including .js files, script tags,
  event handlers, Web Components, fetch calls, or any code that implies JS behavior. Auto-activate when:
  (1) writing or editing any .js file, (2) generating a Shopify section or page that includes JS,
  (3) the user asks to "make something interactive", "add a toggle", "build a carousel", "add JS",
  or any behavior that implies JavaScript. This skill is a hard dependency of shopify-section-generator
  and shopify-build-page — all JS output from those skills MUST comply with these rules. Covers modern
  ES syntax, defer loading, Web Components, data attributes for Liquid-to-JS, event delegation, AJAX
  cart fetch patterns, pub/sub communication, and accessibility. Enforces strict rules: NO inline
  styles via JS, NO DOM creation, NO price formatting in JS, NO inline scripts.
---

# JavaScript Standards (MANDATORY for all JS code)

## Core Rules

This theme uses **vanilla JavaScript only**. No frameworks, no jQuery, no build-step libraries.

Shopify themes run on Shopify's CDN with no build pipeline. Every byte of JavaScript is served directly to the browser, so the theme must work without compilation, bundling, or transpilation. Vanilla JS also keeps the dependency footprint at zero — no version conflicts, no supply chain risk, no build failures.

### Modern ES Syntax — Always

- **`const` by default. `let` when reassignment is needed. Never `var`.**
- **Arrow functions for callbacks and standalone functions. Use method syntax inside classes and Web Components — never arrow functions as class methods.**
- Destructuring for object/array access
- Template literals over string concatenation
- Optional chaining (`?.`) and nullish coalescing (`??`) over manual null checks
- `for...of` over `.forEach()` when no index needed

```javascript
// ✅ Correct
const gallery = document.querySelector('.product-gallery');
const { productId, imagesCount } = gallery.dataset;
const items = [...document.querySelectorAll('.item')];

const handleClick = (event) => {
  const { target } = event;
  target.classList.toggle('is-active');
};

// ✅ Correct — method syntax inside a class
class CartDrawer extends HTMLElement {
  connectedCallback() {
    this.bindEvents();
  }

  bindEvents() {
    this.addEventListener('click', this.handleClick);
  }

  handleClick(event) {
    // `this` works correctly as a class method
  }
}

// ❌ Wrong
var gallery = document.querySelector('.product-gallery');
var productId = gallery.getAttribute('data-product-id');
function handleClick(event) {
  event.target.classList.toggle('is-active');
}

// ❌ Wrong — arrow function as class method breaks `this` binding expectations
class BadComponent extends HTMLElement {
  handleClick = (event) => { ... } // avoid
}
```

## File Organization

- All JS lives in `assets/` directory as separate files
- Never create inline `<script>` tags in Liquid files
- Pass Liquid values to JS via `data-` attributes:

Data attributes create a clean boundary between Liquid (server) and JS (client). The Liquid template renders data into the DOM as attributes, and JS reads it at runtime. This avoids the security risks of interpolating Liquid variables into inline script blocks and keeps the two languages decoupled.

```liquid
<div class="product-gallery" data-product-id="{{ product.id }}" data-images-count="{{ product.images.size }}">
```

```javascript
const gallery = document.querySelector('.product-gallery');
const { productId, imagesCount } = gallery.dataset;
```

## Script Loading

Always `defer` regardless of fold position:

`defer` tells the browser to download the script in parallel with HTML parsing but execute it only after the DOM is fully parsed. This prevents JS from blocking page rendering — critical for Shopify's Core Web Vitals scores.

```liquid
<script src="{{ 'section-name.js' | asset_url }}" defer></script>
```

## Initialization Patterns

**One-off section scripts** — `DOMContentLoaded`:

```javascript
document.addEventListener('DOMContentLoaded', () => {
  // Initialize section behavior
});
```

Use `DOMContentLoaded` for one-off section scripts because it's simple and direct — the code runs once when the page loads.

**Reusable interactive components** (multiple places) — Web Components:

```javascript
class AccordionElement extends HTMLElement {
  connectedCallback() {
    // Initialize
  }

  disconnectedCallback() {
    // Cleanup event listeners
  }
}

if (!customElements.get('accordion-element')) {
  customElements.define('accordion-element', AccordionElement);
}
```

Web Components handle Theme Editor compatibility automatically — `connectedCallback` fires when a section is added or re-rendered in the editor, and `disconnectedCallback` cleans up when it's removed. This lifecycle management is essential for components that appear in multiple sections or need to survive editor re-renders.

Do NOT use Web Components for one-off section scripts.

## Event Delegation

Never bind individual listeners to repeated elements. Always delegate to the closest stable parent container.

Binding a listener to every `.item` in a list creates one listener per element — a memory leak risk, especially in dynamic lists like cart line items or search results. Delegation uses a single listener on the parent and checks `event.target` at runtime, which is also safer when items are added or removed from the DOM.

```javascript
// ❌ Wrong — one listener per element
const items = [...document.querySelectorAll('.cart-item')];
items.forEach(item => item.addEventListener('click', handleRemove));

// ✅ Correct — single delegated listener
const cartList = document.querySelector('.cart-items');
cartList.addEventListener('click', (event) => {
  const item = event.target.closest('.cart-item__remove');
  if (!item) return;
  handleRemove(item);
});
```

Use `Element.closest()` to safely walk up the DOM tree and match the intended target — it returns `null` if no match, so the early `return` guard keeps the handler clean.

## AJAX Cart / Fetch Standards

All Shopify Cart API calls use `fetch` with `async/await`. No jQuery AJAX, no XMLHttpRequest.

Shopify's Cart API (`/cart/add.js`, `/cart/update.js`, `/cart/change.js`, `/cart.js`) returns JSON. Always send requests with the correct `Content-Type` header and always handle errors explicitly — never assume success.

```javascript
// ✅ Adding to cart
const addToCart = async (variantId, quantity = 1) => {
  try {
    const response = await fetch('/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: variantId, quantity }),
    });

    if (!response.ok) throw new Error(`Cart error: ${response.status}`);

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('addToCart failed:', error);
    // Show user-facing error via UI state class, not alert()
  }
};

// ✅ Fetching cart state
const fetchCart = async () => {
  const response = await fetch('/cart.js');
  if (!response.ok) throw new Error('Failed to fetch cart');
  return response.json();
};
```

- Always `await` fetch calls — never mix `.then()` chains with `async/await`
- Never use `alert()` for errors — toggle an error state class on the relevant element
- Always return the parsed response so callers can react to it (e.g., updating cart count)

## Pub/Sub — Cross-Component Communication

Components must not reach into each other directly. Use custom events dispatched on `document` for cross-component communication.

Tight coupling between components (e.g., a cart drawer directly calling a method on a header cart count badge) breaks when either component is removed or refactored. Custom events on `document` decouple the publisher from the subscriber — the cart doesn't need to know what listens to it.

Always namespace custom event names to avoid collisions with native browser events.

```javascript
// ✅ Publishing — e.g., after a successful cart add
const publishCartUpdate = (cartData) => {
  document.dispatchEvent(new CustomEvent('theme:cart:updated', {
    detail: { cart: cartData },
    bubbles: true,
  }));
};

// ✅ Subscribing — e.g., in a cart count badge component
class CartCount extends HTMLElement {
  connectedCallback() {
    this.handleCartUpdate = this.handleCartUpdate.bind(this);
    document.addEventListener('theme:cart:updated', this.handleCartUpdate);
  }

  disconnectedCallback() {
    document.removeEventListener('theme:cart:updated', this.handleCartUpdate);
  }

  handleCartUpdate(event) {
    const { cart } = event.detail;
    this.textContent = cart.item_count;
  }
}
```

- Event names follow the pattern `theme:<noun>:<verb>` — e.g., `theme:cart:updated`, `theme:modal:opened`
- Always remove listeners in `disconnectedCallback` to prevent memory leaks
- Pass relevant data in `event.detail` — subscribers should not need to re-fetch what the publisher already has

## Accessibility

All custom interactive components must be keyboard accessible and use correct ARIA attributes. JS that adds interactivity must also manage the corresponding accessibility state.

Screen readers and keyboard users rely on ARIA attributes to understand component state. If JS toggles a panel open/closed but doesn't update `aria-expanded`, assistive technology sees a broken interface.

```javascript
// ✅ Accordion / disclosure pattern
class AccordionElement extends HTMLElement {
  connectedCallback() {
    this.trigger = this.querySelector('[data-accordion-trigger]');
    this.panel = this.querySelector('[data-accordion-panel]');

    this.trigger.addEventListener('click', this.toggle.bind(this));
    this.trigger.addEventListener('keydown', this.handleKeydown.bind(this));
  }

  toggle() {
    const isOpen = this.trigger.getAttribute('aria-expanded') === 'true';
    this.trigger.setAttribute('aria-expanded', String(!isOpen));
    this.panel.classList.toggle('is-open', !isOpen);
  }

  handleKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      this.toggle();
    }
  }
}
```

Rules:
- Toggle `aria-expanded` on triggers (accordions, dropdowns, modals)
- Use `aria-controls` to associate a trigger with the panel it controls
- Handle `Enter` and `Space` keydown events on any non-`<button>` interactive element
- Never remove focus outline via JS — use CSS `focus-visible` instead
- Modals and drawers must trap focus while open and restore focus on close

## Strict Rules

### 1. NO Styling via JavaScript

Never inline styles. Toggle CSS classes instead:

```javascript
// ❌ element.style.display = 'block';
// ✅ element.classList.add('is-open');
// ✅ element.classList.remove('is-closed');
```

Never use Tailwind classes as query selectors.

Styling through JS bypasses the CSS cascade and makes styles impossible to override with CSS specificity. It also scatters visual logic across two languages — CSS for some styles, JS for others — making the theme harder to maintain and debug. CSS classes are declarative, cacheable, and visible in browser dev tools' Styles panel.

### 2. NO DOM Creation via JavaScript

Never build HTML strings in JS. Never use `innerHTML` with templates for components. Liquid handles all markup.

The Shopify theme editor needs to see and manage all markup server-side. DOM created by JS is invisible to the editor's section rendering pipeline. Additionally, `innerHTML` with interpolated data is an XSS vector, and server-rendered markup is indexed by search engines while JS-created DOM may not be.

If a feature requires dynamic rendering (e.g., predictive search results, AJAX cart line items), prefer cloning a Liquid-rendered `<template>` element over building HTML strings in JS.

### 3. NO Price Formatting in JavaScript

Always use Liquid money filters. Never format prices in JS.

```javascript
// ❌ const price = `$${(cents / 100).toFixed(2)}`;
```
```liquid
// ✅ {{ product.price | money }}
```

Shopify handles currency formatting, locale-specific number formats, and multi-currency conversion at the server level through Liquid money filters. Recreating this logic in JS is error-prone (different currencies have different decimal rules, symbol positions, and thousands separators) and will break when the store changes currency settings.

### 4. NO Inline Scripts

All JS lives in asset files. No `<script>` blocks in Liquid.

External JS files are cached by the browser — a script loaded on the homepage is already cached when the user navigates to a product page. Inline scripts are re-parsed on every page load. Keeping all JS in asset files also makes the theme's JavaScript surface area auditable from a single directory.

## Checklist

Validate every `.js` file against these before committing.

### Modern ES Syntax
- [ ] `const` used by default — `let` only when reassignment needed
- [ ] No `var` anywhere
- [ ] Arrow functions used for callbacks and standalone functions
- [ ] Method syntax used inside classes and Web Components — no arrow function class methods
- [ ] Function declarations only for named hoisting cases
- [ ] Destructuring used for object/array access
- [ ] Template literals over string concatenation
- [ ] Optional chaining (`?.`) and nullish coalescing (`??`) over manual null checks
- [ ] `for...of` used over `.forEach()` when no index needed

### File & Loading
- [ ] JS lives in `assets/` directory — not inline in Liquid
- [ ] Script tag uses `defer`
- [ ] Liquid values passed via `data-` attributes — no inline `<script>` for data

### Initialization
- [ ] One-off sections use `DOMContentLoaded`
- [ ] Reusable components use Web Components with `connectedCallback`/`disconnectedCallback`
- [ ] Custom element registration guarded: `if (!customElements.get('name'))`

### Event Delegation
- [ ] No per-element listeners on repeated/list elements
- [ ] Single listener on stable parent container
- [ ] `event.target.closest()` used to match intended target
- [ ] Early `return` guard if target doesn't match

### AJAX Cart / Fetch
- [ ] All cart API calls use `fetch` with `async/await`
- [ ] `Content-Type: application/json` header included on POST requests
- [ ] `response.ok` checked — errors thrown and caught explicitly
- [ ] No `alert()` for errors — UI state class toggled instead
- [ ] No mixing of `.then()` chains and `async/await`

### Pub/Sub
- [ ] Components do not call methods on other components directly
- [ ] Cross-component communication uses `document.dispatchEvent` with custom events
- [ ] Event names follow `theme:<noun>:<verb>` naming convention
- [ ] Subscribers remove listeners in `disconnectedCallback`

### Accessibility
- [ ] `aria-expanded` toggled on all disclosure triggers
- [ ] `aria-controls` associates trigger with its panel
- [ ] `keydown` handled for `Enter` and `Space` on non-`<button>` interactive elements
- [ ] Focus not removed via JS — `focus-visible` handled in CSS
- [ ] Modals/drawers trap focus while open and restore on close

### Strict Rules
- [ ] No `element.style.*` — CSS classes toggled instead
- [ ] No Tailwind classes used as query selectors
- [ ] No `innerHTML` with template strings for component rendering
- [ ] No price formatting in JS — Liquid `| money` handles prices
- [ ] No inline `<script>` tags in Liquid files

### Naming
- [ ] Files: `kebab-case.js`
- [ ] Variables/functions: `camelCase`
- [ ] Constants: `UPPER_SNAKE_CASE`
- [ ] Web Component classes: `PascalCase`
- [ ] Custom element tags: `kebab-case`
