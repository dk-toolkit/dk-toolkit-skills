# Decision Rules — Section Setting vs Metafield vs Hardcoded

## The Core Question

For every piece of content, ask:

> **"Does this value change per resource instance (product/collection/variant), or is it the same default across all instances of this page type?"**

- **Changes per resource** → Metafield on that resource
- **Same across all, but merchant wants to override** → Section Setting (theme editor)
- **Never needs to change** → Hardcode it

---

## Decision Tree

```
Is this content?
│
├── Structural / layout (spacing, grid columns, font sizes)
│   └── → HARDCODE or CSS variable. Not a setting, not a metafield.
│
├── Style preference (colors, background style, text alignment)
│   └── Is it the same across all pages of this type?
│       ├── YES, but merchant may want to change it → SECTION SETTING
│       └── NO, different per collection/product → METAFIELD (color type)
│
├── Text content
│   └── Is it the same across all pages of this type?
│       ├── YES (e.g., same tagline on every collection page) → SECTION SETTING
│       └── NO (e.g., different headline per collection) → METAFIELD
│
├── Images / media
│   └── Is it the same image on every page?
│       ├── YES (e.g., brand logo) → HARDCODE or SECTION SETTING
│       └── NO (e.g., per-collection banner) → METAFIELD (file_reference)
│
├── Toggle / feature flag
│   └── Does it vary per product/collection?
│       ├── YES (e.g., show sale badge on some products) → METAFIELD (boolean)
│       └── NO (e.g., show/hide a section entirely) → SECTION SETTING
│
└── Reference to another resource (product, collection, page)
    └── → Always METAFIELD (reference type)
```

---

## Detailed Rules with Examples

### Rule 1 — Per-Resource Uniqueness → Metafield

If the content is UNIQUE per product, collection, or variant → **always metafield**.

| Example | Metafield Owner | Type |
|---|---|---|
| Collection banner image | COLLECTION | file_reference |
| Collection banner headline | COLLECTION | single_line_text_field |
| Product "Why buy this" section text | PRODUCT | rich_text_field |
| Variant size guide image | PRODUCTVARIANT | file_reference |
| Product custom badge (e.g., "New", "Award Winner") | PRODUCT | single_line_text_field |
| Collection SEO description (custom) | COLLECTION | multi_line_text_field |
| Product video URL | PRODUCT | url |
| Featured product in a collection hero | COLLECTION | product_reference |

---

### Rule 2 — Global Store Data → Shop Metafield

If content is global and appears identically across many pages but needs to be editable without a deployment → **Shop metafield**.

| Example | Notes |
|---|---|
| Promo bar text (site-wide) | SHOP metafield, single_line_text_field |
| Free shipping threshold display | SHOP metafield, number_integer |
| Support phone number | SHOP metafield, single_line_text_field |
| Trust badge icons (global) | SHOP metafield, list.file_reference |

---

### Rule 3 — Per-Page Overrides → Section Settings

If content has a **sensible default** that applies across all instances of that page, but the merchant might want to override it **per section assignment** (not per resource) → **Section setting**.

| Example | Notes |
|---|---|
| Overlay opacity on banner | Same default fine, merchant adjusts per section instance |
| Number of product columns in grid | Layout preference |
| Text alignment (left/center/right) | Style preference |
| Background color of a section | Same across pages of this type |
| Padding/spacing | Layout, not content |
| Enable/disable lazy loading | Technical toggle |

---

### Rule 4 — Mobile vs Desktop Images → Always Separate Metafields

When an image is used responsively, always create **two separate metafields**: one for desktop, one for mobile. Do NOT use a single image and rely on CSS cropping — merchants need to control the art direction.

```
banner.image_desktop  → file_reference (COLLECTION)
banner.image_mobile   → file_reference (COLLECTION)
```

Liquid pattern:
```liquid
{% assign img_desktop = collection.metafields.banner.image_desktop.value %}
{% assign img_mobile = collection.metafields.banner.image_mobile.value %}

{% if img_mobile != blank %}
  <img class="mobile-only" src="{{ img_mobile | image_url: width: 768 }}" ...>
{% endif %}
{% if img_desktop != blank %}
  <img class="desktop-only" src="{{ img_desktop | image_url: width: 1440 }}" ...>
{% elsif img_mobile != blank %}
  <img class="desktop-only" src="{{ img_mobile | image_url: width: 1440 }}" ...>
{% endif %}
```

---

### Rule 5 — Single Entry vs List

| Scenario | Use |
|---|---|
| One image per resource | Single `file_reference` |
| Gallery of images (count unknown) | `list.file_reference` |
| One CTA button | Single `url` + Single `single_line_text_field` for label |
| Multiple USP points | `list.single_line_text_field` |
| Multiple featured products | `list.product_reference` |
| Tabs with content | `list.metaobject_reference` (if complex) or `list.single_line_text_field` + `list.multi_line_text_field` |

**When to ask user:** If you genuinely can't tell from the template whether the design intends 1 or N items, ASK before deciding.

---

### Rule 6 — Variant-Level Metafields

Use variant metafields when:
- The information changes per variant (size, color option), NOT just per product
- Examples: variant-specific size guide, variant swatch custom image, variant badge

```liquid
{% for variant in product.variants %}
  {% assign badge = variant.metafields.ns.badge.value %}
  {% if badge != blank %}
    <span class="variant-badge">{{ badge }}</span>
  {% endif %}
{% endfor %}
```

---

### Rule 7 — When NOT to Create a Metafield

Don't create a metafield if:
- It's a layout property (padding, columns, fonts)
- It's already handled by Shopify natively (product title, description, price, images array)
- It's the same across every instance with no reason to ever change per-resource
- The section already has a schema setting that covers it adequately
- It's a conditional for a section that should be toggled in the theme editor (keep as section setting)

---

### Rule 8 — Namespace Strategy

Always use **feature/section-based namespaces**, not generic ones.

| Good | Bad |
|---|---|
| `banner`, `hero`, `pdp_extras` | `custom`, `global`, `data` |
| `product_tabs`, `collection_info` | `metafields`, `content` |
| `variant_display` | `store`, `general` |

Rules:
- Never use `global` — Shopify reserves this for its own use
- Keep namespaces to 1–2 words, lowercase, underscores only
- Group related fields under one namespace (all banner fields → `banner`)
- Max namespace length: 20 characters

---

### Rule 9 — What to Keep Hardcoded

These should ALWAYS remain hardcoded — never put in a metafield:

- HTML structure and semantic tags
- CSS class names
- JavaScript behavior
- Shopify Liquid conditionals and logic
- Default Shopify object properties (`.title`, `.price`, `.url`, `.handle`)
- Icon SVG code (use assets/ or snippets/ instead)
- Schema type definitions

---

### Rule 10 — Migrating Existing Section Settings

When a section setting currently does the same job as a proposed metafield:

| Situation | Action |
|---|---|
| Setting has a value that changes per page (but shouldn't — it's been abused) | Replace with metafield, remove setting |
| Setting is genuinely page-wide with rare overrides | KEEP as setting, don't migrate |
| Setting is now redundant because metafield covers it | Remove setting, update Liquid to use metafield |
| Setting is a layout/style prop | Always KEEP |

When removing a setting, add cleanup comment in Liquid before removing:
```liquid
{% comment %} 
  Removed: [setting_id] — migrated to metafield [namespace.key] 
  Date: [today]
{% endcomment %}
```
