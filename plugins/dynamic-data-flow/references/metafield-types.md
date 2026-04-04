# Shopify Metafield Types — Complete Reference

## Owner Types
| Owner | Used For | Liquid Access |
|---|---|---|
| `PRODUCT` | Per-product data | `product.metafields.ns.key` |
| `COLLECTION` | Per-collection data | `collection.metafields.ns.key` |
| `PRODUCTVARIANT` | Per-variant data | `variant.metafields.ns.key` |
| `PAGE` | Per-page data | `page.metafields.ns.key` |
| `BLOG` | Per-blog data | `blog.metafields.ns.key` |
| `ARTICLE` | Per-article data | `article.metafields.ns.key` |
| `SHOP` | Global store data | `shop.metafields.ns.key` |
| `CUSTOMER` | Per-customer data | `customer.metafields.ns.key` |
| `ORDER` | Per-order data | (admin only) |
| `LOCATION` | Per-location data | `location.metafields.ns.key` |

---

## Text Types

### `single_line_text_field`
- **Use for:** Headlines, labels, short descriptions, button text, badge text, short URLs
- **Max length:** 255 characters (configurable validation)
- **Liquid output:** `{{ resource.metafields.ns.key.value }}`
- **Filter needed:** None for plain text. Use `| escape` for user-facing content
- **List version:** `list.single_line_text_field`
- **List liquid:** `{% for item in resource.metafields.ns.key.value %}{{ item }}{% endfor %}`
- **Suggested validations:** `max_length: 120` for headlines, `max_length: 255` for labels

### `multi_line_text_field`
- **Use for:** Paragraphs, descriptions, plain text blocks (no formatting needed)
- **Liquid output:** `{{ resource.metafields.ns.key.value | newline_to_br }}`
- **Filter needed:** `newline_to_br` to preserve line breaks
- **List version:** `list.multi_line_text_field`

### `rich_text_field`
- **Use for:** Formatted content — bold, italic, lists, links, headings
- **Liquid output:** `{{ resource.metafields.ns.key | metafield_tag }}`
- **⚠️ CRITICAL:** ALWAYS use `metafield_tag` filter. Raw `.value` outputs a JSON object, not HTML
- **List version:** Not available
- **Note:** Outputs sanitized HTML. No XSS risk.

---

## Number Types

### `number_integer`
- **Use for:** Counts, quantities, sort order values, IDs
- **Liquid output:** `{{ resource.metafields.ns.key.value }}`
- **List version:** `list.number_integer`
- **Suggested validations:** Set `min` and `max` where logical

### `number_decimal`
- **Use for:** Prices (custom display), ratings, measurements, percentages
- **Liquid output:** `{{ resource.metafields.ns.key.value }}`
- **Filter:** `| round: 2` for decimal display control
- **List version:** `list.number_decimal`

---

## Boolean Type

### `boolean`
- **Use for:** Show/hide toggles, feature flags, yes/no options
- **Liquid output:** `{% if resource.metafields.ns.key.value == true %}`
- **⚠️ Note:** Value is boolean `true`/`false`, NOT string "true"/"false"
- **List version:** Not available

---

## Date/Time Types

### `date`
- **Use for:** Sale start/end dates, event dates, launch dates
- **Liquid output:** `{{ resource.metafields.ns.key.value | date: "%B %d, %Y" }}`
- **List version:** `list.date`

### `date_time`
- **Use for:** Countdown timers, precise event times
- **Liquid output:** `{{ resource.metafields.ns.key.value | date: "%Y-%m-%dT%H:%M:%S" }}`
- **List version:** `list.date_time`

---

## Color Type

### `color`
- **Use for:** Theme accent colors per collection/product, badge colors, custom highlights
- **Liquid output:** `{{ resource.metafields.ns.key.value }}`
- **Returns:** Hex string e.g. `#FF5733`
- **Usage:** `style="color: {{ resource.metafields.ns.key.value }}"`
- **List version:** `list.color`

---

## URL Type

### `url`
- **Use for:** External links, CTA button URLs, video URLs (non-Shopify hosted)
- **Liquid output:** `{{ resource.metafields.ns.key.value }}`
- **Validation:** URL format enforced automatically
- **List version:** `list.url`

---

## JSON Type

### `json`
- **Use for:** Complex structured data — feature tables, spec lists, custom data structures
- **Liquid output:** Assign first, then access keys: `{% assign data = resource.metafields.ns.key.value %}{{ data.key }}`
- **⚠️ Note:** Merchants must input valid JSON. Hard for non-technical users. Prefer structured alternatives when possible.
- **List version:** Not available

---

## File Types

### `file_reference`
- **Use for:** Images, videos, PDFs uploaded via Shopify Files
- **Returns:** A Shopify file object (NOT a URL string)
- **⚠️ CRITICAL:** NEVER do `{{ metafield.value }}` directly — it outputs a file ID

**For images:**
```liquid
{% assign img = resource.metafields.ns.key.value %}
{% if img != blank %}
  <img src="{{ img | image_url: width: 1200 }}" 
       alt="{{ img.alt | default: resource.title }}"
       width="{{ img.width }}"
       height="{{ img.height }}"
       loading="lazy">
{% endif %}
```

**For responsive images:**
```liquid
{% assign img = resource.metafields.ns.key.value %}
{% if img != blank %}
  <img src="{{ img | image_url: width: 800 }}"
       srcset="{{ img | image_url: width: 400 }} 400w,
               {{ img | image_url: width: 800 }} 800w,
               {{ img | image_url: width: 1200 }} 1200w"
       sizes="(max-width: 768px) 100vw, 50vw"
       alt="{{ img.alt | default: resource.title }}"
       loading="lazy">
{% endif %}
```

**For video:**
```liquid
{{ resource.metafields.ns.key | metafield_tag }}
```

**For any file (auto-renders correctly):**
```liquid
{{ resource.metafields.ns.key | metafield_tag }}
```

**Validation options:** `allowed_file_types: ["Image", "Video", "Document"]`
- `list.file_reference` → gallery of multiple images/files

---

## Reference Types (Link to Shopify Resources)

### `product_reference`
- **Use for:** Featured product, recommended product, linked product
- **Returns:** A full Shopify product object
- **Liquid output:**
```liquid
{% assign featured = resource.metafields.ns.key.value %}
{% if featured != blank %}
  <a href="{{ featured.url }}">{{ featured.title }}</a>
  <img src="{{ featured.featured_image | image_url: width: 400 }}" alt="{{ featured.title }}">
{% endif %}
```
- **List version:** `list.product_reference` (up to 10 products)

### `collection_reference`
- **Use for:** Featured collection, related collection links
- **Returns:** A full Shopify collection object
- **Liquid output:**
```liquid
{% assign col = resource.metafields.ns.key.value %}
{% if col != blank %}
  <a href="{{ col.url }}">{{ col.title }}</a>
{% endif %}
```
- **List version:** `list.collection_reference`

### `variant_reference`
- **Use for:** Default selected variant, featured variant
- **Returns:** A full variant object
- **List version:** `list.variant_reference`

### `page_reference`
- **Use for:** Linked page, terms & conditions page, about page reference
- **List version:** `list.page_reference`

### `metaobject_reference`
- **Use for:** Complex reusable structured content (team members, testimonials, FAQs)
- **Requires:** Metaobject definition to exist first
- **List version:** `list.metaobject_reference`
- **Note:** For highly structured repeating data, metaobjects are better than JSON type

---

## Dimension / Weight / Volume / Rating Types

### `dimension`
- **Use for:** Product dimensions (width, height, depth) with units
- **Returns:** Object with `value` and `unit`
- **Liquid output:** `{{ resource.metafields.ns.key.value.value }} {{ resource.metafields.ns.key.value.unit }}`
- **List version:** `list.dimension`

### `weight`
- **Use for:** Shipping weight display, product specs
- **List version:** `list.weight`

### `volume`
- **Use for:** Liquid products, capacity specs
- **List version:** `list.volume`

### `rating`
- **Use for:** Custom rating display (not Shopify reviews)
- **Returns:** Object with `value` (number) and `scale_max` (number)
- **Liquid output:** `{{ resource.metafields.ns.key.value.value }} / {{ resource.metafields.ns.key.value.scale_max }}`
- **List version:** `list.rating`

---

## Money Type

### `money`
- **Use for:** Custom pricing display, original price before discount
- **Returns:** Object with `amount` (string) and `currency_code`
- **Liquid output:** `{{ resource.metafields.ns.key.value | money }}`
- **List version:** Not available

---

## Quick Decision Guide

| Content | Recommended Type |
|---|---|
| Short headline / label | `single_line_text_field` |
| Paragraph / description | `multi_line_text_field` |
| Formatted HTML content | `rich_text_field` |
| Image (desktop/mobile) | `file_reference` |
| Gallery of images | `list.file_reference` |
| CTA button URL | `url` |
| Toggle (show/hide) | `boolean` |
| Sale end date | `date_time` |
| Accent color | `color` |
| Count / sort order | `number_integer` |
| Multiple text items (USPs, tabs) | `list.single_line_text_field` |
| Featured product | `product_reference` |
| Multiple products | `list.product_reference` |
| Related collection | `collection_reference` |
| Complex spec table | `json` or metaobject |
| Reusable structured data | `metaobject_reference` |
| Badge/tag label on variant | `single_line_text_field` on `PRODUCTVARIANT` |
| Global promo text | `single_line_text_field` on `SHOP` |
