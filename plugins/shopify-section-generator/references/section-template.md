# Section File Templates — Reference

## Liquid Section Template

Path: `sections/<section-name>.liquid`

```liquid
{%- # 1. Scoped stylesheet --%}
{{ '<section-name>.css' | asset_url | stylesheet_tag }}

{%- # 2. Section wrapper (include height class for full-width sections) --%}
<section
  id="shopify-section-{{ section.id }}"
  class="section-<section-name> color-{{ section.settings.color_scheme }} gradient{% if section.settings.section_height != 'auto' %} section-<section-name>--height-{{ section.settings.section_height }}{% endif %}"
>
  <div class="section-<section-name>__container page-width">

    {%- # 3. Responsive media (for sections with hero/banner images) --%}
    {%- assign desktop_image = section.settings.image_desktop -%}
    {%- assign mobile_image = section.settings.image_mobile | default: desktop_image -%}
    {%- if desktop_image != blank -%}
      <picture>
        {%- if mobile_image != desktop_image -%}
          <source
            media="(max-width: 749px)"
            srcset="{{ mobile_image | image_url: width: 750 }},
                   {{ mobile_image | image_url: width: 1500 }} 2x"
          >
        {%- endif -%}
        <source
          media="(min-width: 750px)"
          srcset="{{ desktop_image | image_url: width: 1100 }},
                 {{ desktop_image | image_url: width: 1500 }} 1.5x,
                 {{ desktop_image | image_url: width: 2200 }} 2x"
        >
        <img
          src="{{ desktop_image | image_url: width: 1500 }}"
          alt="{{ desktop_image.alt | escape }}"
          loading="lazy"
          width="{{ desktop_image.width }}"
          height="{{ desktop_image.height }}"
        >
      </picture>
    {%- endif -%}

    {%- # 4. Content --%}
    <h2 class="section-<section-name>__heading">
      {{ section.settings.heading | escape }}
    </h2>

    {%- # 5. Blocks loop (if applicable) --%}
    <div class="section-<section-name>__items">
      {%- for block in section.blocks -%}
        <div class="section-<section-name>__item" {{ block.shopify_attributes }}>
          {%- # block content --%}
        </div>
      {%- endfor -%}
    </div>

  </div>
</section>

{%- # 6. Schema --%}
{% schema %}
{
  "name": "Section Display Name",
  "tag": "section",
  "class": "section-<section-name>",
  "settings": [
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.color_scheme.label",
      "default": "scheme-1"
    },
    {
      "type": "header",
      "content": "Layout"
    },
    {
      "type": "select",
      "id": "section_height",
      "label": "Section height",
      "default": "auto",
      "options": [
        { "value": "auto", "label": "Auto" },
        { "value": "small", "label": "Small" },
        { "value": "medium", "label": "Medium" },
        { "value": "large", "label": "Large" }
      ],
      "info": "Controls the overall height of this section. Applies to full-width sections only."
    },
    {
      "type": "header",
      "content": "Media"
    },
    {
      "type": "image_picker",
      "id": "image_desktop",
      "label": "Desktop image"
    },
    {
      "type": "image_picker",
      "id": "image_mobile",
      "label": "Mobile image",
      "info": "Optional. If empty, the desktop image will be used on mobile."
    },
    {
      "type": "header",
      "content": "Content"
    },
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Section heading"
    }
  ],
  "blocks": [],
  "presets": [
    {
      "name": "Section Display Name"
    }
  ]
}
{% endschema %}
```

## CSS Stylesheet Template

Path: `assets/<section-name>.css`

Rules:
- Scope ALL rules under `.section-<section-name>`.
- Mobile-first: base → `@media (min-width: 750px)` → `@media (min-width: 990px)`.
- Use Dawn CSS custom properties; no raw hex values.
- No `!important` unless documented with a comment.
- BEM-ish naming: `__container`, `__heading`, `__item`.

```css
/* ============================================
   Section: <section-name>
   ============================================ */

.section-<section-name> {
  padding-block: 3.6rem;
}

.section-<section-name>__container {
  max-width: 1440px;
  margin-inline: auto;
  padding-inline: 1.6rem;
}

@media screen and (min-width: 750px) {
  .section-<section-name> {
    padding-block: 5.6rem;
  }
  .section-<section-name>__container {
    padding-inline: 4rem;
  }
}

@media screen and (min-width: 990px) {
  .section-<section-name> {
    padding-block: 8rem;
  }
  .section-<section-name>__container {
    padding-inline: 5.5rem;
  }
}

@media screen and (min-width: 1536px) {
  .section-<section-name>__container {
    padding-inline: 0;
  }
}
```

## JavaScript Template (only if needed)

Path: `assets/<section-name>.js`

**Must comply with `js-standards` skill.** Use Web Component pattern:

```js
class SectionName extends HTMLElement {
  connectedCallback() {
    this.bindEvents();
  }

  disconnectedCallback() {
    // Cleanup event listeners
  }

  bindEvents() {
    this.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      this.handleAction(target);
    });
  }

  handleAction(target) {
    const { action } = target.dataset;
    // handle action
  }
}

if (!customElements.get('section-name')) {
  customElements.define('section-name', SectionName);
}
```

Enqueue: `<script src="{{ '<section-name>.js' | asset_url }}" defer></script>`
