# Section Height Control — Reference Patterns

## Schema Setting

```json
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
  "info": "Controls the overall height of this section."
}
```

## Liquid Class Binding

On the outer `<section>` tag:

```liquid
<section
  id="shopify-section-{{ section.id }}"
  class="section-<section-name> color-{{ section.settings.color_scheme }} gradient{% if section.settings.section_height != 'auto' %} section-<section-name>--height-{{ section.settings.section_height }}{% endif %}"
>
```

## CSS Implementation

Add to every applicable section stylesheet:

```css
/* Height variants */
.section-<section-name>--height-small {
  min-height: 25rem;
}
.section-<section-name>--height-medium {
  min-height: 40rem;
}
.section-<section-name>--height-large {
  min-height: 60rem;
}

@media screen and (min-width: 750px) {
  .section-<section-name>--height-small {
    min-height: 30rem;
  }
  .section-<section-name>--height-medium {
    min-height: 50rem;
  }
  .section-<section-name>--height-large {
    min-height: 70rem;
  }
}

@media screen and (min-width: 990px) {
  .section-<section-name>--height-small {
    min-height: 35rem;
  }
  .section-<section-name>--height-medium {
    min-height: 55rem;
  }
  .section-<section-name>--height-large {
    min-height: 80rem;
  }
}
```
