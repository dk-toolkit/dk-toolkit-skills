# Liquid Patterns — Safe Metafield Output Reference

## Golden Rules

1. **Never output a metafield without a nil/blank check OR a `| default:` fallback**
2. **Never use `.value` on complex types (file_reference, rich_text, reference types) without the correct filter**
3. **Always assign metafields to a variable first** — cleaner, easier to debug
4. **Always provide a meaningful fallback** — use native Shopify properties as fallback when possible

---

## Pattern 1 — Simple Text Field

```liquid
{% assign mf = resource.metafields.namespace.key.value %}
{% if mf != blank %}
  <h2>{{ mf | escape }}</h2>
{% else %}
  <h2>{{ resource.title | escape }}</h2>
{% endif %}
```

**Short form with `| default:`:**
```liquid
<h2>{{ resource.metafields.namespace.key.value | default: resource.title | escape }}</h2>
```

---

## Pattern 2 — Rich Text Field

```liquid
{% assign mf = resource.metafields.namespace.key %}
{% if mf != blank %}
  <div class="rte">{{ mf | metafield_tag }}</div>
{% else %}
  <div class="rte">{{ resource.description }}</div>
{% endif %}
```

⚠️ Use `metafield_tag` on the metafield object (NOT `.value`). This outputs sanitized HTML.

---

## Pattern 3 — File Reference (Single Image)

```liquid
{% assign img = resource.metafields.namespace.key.value %}
{% if img != blank %}
  <img 
    src="{{ img | image_url: width: 1200 }}" 
    srcset="
      {{ img | image_url: width: 400 }} 400w,
      {{ img | image_url: width: 800 }} 800w,
      {{ img | image_url: width: 1200 }} 1200w
    "
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 1200px"
    alt="{{ img.alt | default: resource.title | escape }}"
    width="{{ img.width }}"
    height="{{ img.height }}"
    loading="lazy">
{% endif %}
```

---

## Pattern 4 — Mobile + Desktop Images

```liquid
{% assign img_desk = collection.metafields.banner.image_desktop.value %}
{% assign img_mob = collection.metafields.banner.image_mobile.value %}
{% assign img_fallback = collection.image %}

{%- comment -%} Desktop image {%- endcomment -%}
{% assign show_desk = img_desk | default: img_mob | default: img_fallback %}
{% if show_desk != blank %}
  <picture>
    {% if img_mob != blank %}
      <source media="(max-width: 767px)" srcset="{{ img_mob | image_url: width: 768 }}">
    {% endif %}
    <img 
      src="{{ img_desk | default: img_mob | default: img_fallback | image_url: width: 1440 }}"
      alt="{{ collection.title | escape }}"
      loading="eager"
      fetchpriority="high">
  </picture>
{% endif %}
```

---

## Pattern 5 — List of Strings

```liquid
{% assign items = resource.metafields.namespace.key.value %}
{% if items != blank and items.size > 0 %}
  <ul class="feature-list">
    {% for item in items %}
      {% if item != blank %}
        <li>{{ item | escape }}</li>
      {% endif %}
    {% endfor %}
  </ul>
{% endif %}
```

---

## Pattern 6 — List of File References (Gallery)

```liquid
{% assign images = resource.metafields.namespace.gallery.value %}
{% if images != blank and images.size > 0 %}
  <div class="gallery">
    {% for img in images %}
      {% if img != blank %}
        <div class="gallery__item">
          <img 
            src="{{ img | image_url: width: 600 }}" 
            alt="{{ img.alt | default: resource.title | escape }}"
            loading="lazy">
        </div>
      {% endif %}
    {% endfor %}
  </div>
{% endif %}
```

---

## Pattern 7 — Boolean Toggle

```liquid
{% assign show_badge = resource.metafields.namespace.show_badge.value %}
{% if show_badge == true %}
  <span class="badge">{{ resource.metafields.namespace.badge_label.value | default: 'New' }}</span>
{% endif %}
```

⚠️ Compare with `== true` (boolean), NOT `== 'true'` (string).

---

## Pattern 8 — Product Reference

```liquid
{% assign featured = collection.metafields.namespace.featured_product.value %}
{% if featured != blank %}
  <div class="featured-product">
    <a href="{{ featured.url }}">
      <img src="{{ featured.featured_image | image_url: width: 500 }}" alt="{{ featured.title | escape }}">
      <h3>{{ featured.title | escape }}</h3>
      <span>{{ featured.price | money }}</span>
    </a>
  </div>
{% endif %}
```

---

## Pattern 9 — List of Product References

```liquid
{% assign products = collection.metafields.namespace.related_products.value %}
{% if products != blank and products.size > 0 %}
  <div class="product-row">
    {% for prod in products %}
      {% if prod != blank %}
        <div class="product-card">
          <a href="{{ prod.url }}">{{ prod.title | escape }}</a>
        </div>
      {% endif %}
    {% endfor %}
  </div>
{% endif %}
```

---

## Pattern 10 — Color Metafield

```liquid
{% assign accent = resource.metafields.namespace.accent_color.value %}
{% if accent != blank %}
  <div class="hero" style="--section-accent: {{ accent | escape }};">
{% else %}
  <div class="hero">
{% endif %}
```

Use CSS custom properties to inject colors. Never put raw metafield values directly in style attributes without escape.

---

## Pattern 11 — Date Display

```liquid
{% assign sale_end = resource.metafields.namespace.sale_end_date.value %}
{% if sale_end != blank %}
  <p class="sale-end">
    Sale ends: {{ sale_end | date: "%B %d, %Y" }}
  </p>
{% endif %}
```

---

## Pattern 12 — URL / CTA Button

```liquid
{% assign cta_url = resource.metafields.namespace.cta_url.value %}
{% assign cta_label = resource.metafields.namespace.cta_label.value %}
{% if cta_url != blank %}
  <a href="{{ cta_url | escape }}" class="btn">
    {{ cta_label | default: 'Shop Now' | escape }}
  </a>
{% endif %}
```

---

## Pattern 13 — JSON Metafield

```liquid
{% assign spec_data = resource.metafields.namespace.specs.value %}
{% if spec_data != blank %}
  <table class="specs">
    {% for pair in spec_data %}
      <tr>
        <td>{{ pair[0] | escape }}</td>
        <td>{{ pair[1] | escape }}</td>
      </tr>
    {% endfor %}
  </table>
{% endif %}
```

---

## Pattern 14 — Variant Metafield

```liquid
{% for variant in product.variants %}
  {% assign v_badge = variant.metafields.namespace.badge.value %}
  <div class="variant-option" data-variant-id="{{ variant.id }}">
    {{ variant.title }}
    {% if v_badge != blank %}
      <span class="variant-badge">{{ v_badge | escape }}</span>
    {% endif %}
  </div>
{% endfor %}
```

For currently selected variant in JS-driven themes:
```liquid
{% assign selected_variant = product.selected_or_first_available_variant %}
{% assign v_badge = selected_variant.metafields.namespace.badge.value %}
```

---

## Pattern 15 — Multilingual Awareness

When the store has multiple locales, metafields are NOT automatically translated. Add this comment above every metafield output in a multilingual store:

```liquid
{%- comment -%}
  TRANSLATION NOTE: {{ namespace }}.{{ key }} requires manual translation via
  Shopify Translate & Adapt app. Falls back to [fallback_value] if empty.
{%- endcomment -%}
```

To check if the store has locales configured:
```liquid
{% if shop.published_locales.size > 1 %}
  {%- comment -%} Multilingual store — metafields may need translation {%- endcomment -%}
{% endif %}
```

---

## Schema Cleanup Rules

### When removing a setting from `{% schema %}`:

1. Find all places in the Liquid where `section.settings.setting_id` is referenced
2. Replace EACH with the metafield equivalent
3. THEN remove the setting block from schema JSON
4. Never remove a schema setting before replacing all its usages

### Settings to ALWAYS keep:

```json
// Keep these even when migrating to metafields:
{ "type": "header", ... }           // Visual grouping — not referenced in Liquid
{ "type": "paragraph", ... }        // Informational — not referenced in Liquid
{ "type": "color_scheme", ... }     // Theme-level styling
{ "type": "range", "id": "padding_top", ... }    // Layout props
{ "type": "select", "id": "text_alignment", ... } // Style props
{ "type": "checkbox", "id": "show_section", ... } // Section-level visibility toggle
```

### Settings that are safe to remove after metafield migration:

```json
// Safe to remove after metafield replacement:
{ "type": "text", "id": "heading", ... }           // Text content → metafield
{ "type": "richtext", "id": "description", ... }   // Rich content → metafield
{ "type": "image_picker", "id": "image", ... }     // Image → file_reference metafield
{ "type": "url", "id": "button_link", ... }        // URL → url metafield
{ "type": "product", "id": "featured", ... }       // Reference → product_reference metafield
```

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| `{{ variant.metafields.ns.key }}` | Add `.value` → `{{ variant.metafields.ns.key.value }}` |
| `{{ mf.value }}` for rich_text | Use `{{ mf | metafield_tag }}` — no `.value` |
| `{{ img.value }}` for file_reference | Use `{{ img | image_url: width: 800 }}` |
| `{% if mf.value %}` | Use `{% if mf != blank %}` or `{% if mf.value != blank %}` |
| Comparing boolean to string: `mf.value == 'true'` | Use `mf.value == true` |
| Output without escape: `{{ mf.value }}` for user content | Use `{{ mf.value | escape }}` for text |
| Missing alt text on images | Always `alt="{{ img.alt | default: resource.title }}"` |
