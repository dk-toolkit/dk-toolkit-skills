# Responsive Asset Handling (Desktop & Mobile) — Reference Patterns

## Image Schema Settings

```json
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
}
```

## Video Schema Settings

```json
{
  "type": "video",
  "id": "video_desktop",
  "label": "Desktop video"
},
{
  "type": "video",
  "id": "video_mobile",
  "label": "Mobile video",
  "info": "Optional. If empty, the desktop video will be used on mobile."
}
```

## Liquid — Responsive Image (`<picture>` art direction)

```liquid
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
```

## Liquid — Responsive Video

```liquid
{%- assign desktop_video = section.settings.video_desktop -%}
{%- assign mobile_video = section.settings.video_mobile | default: desktop_video -%}

{%- if desktop_video != blank -%}
  <div class="section-<section-name>__video section-<section-name>__video--desktop">
    {{ desktop_video | video_tag: autoplay: true, muted: true, loop: true, playsinline: true }}
  </div>
  <div class="section-<section-name>__video section-<section-name>__video--mobile">
    {{ mobile_video | video_tag: autoplay: true, muted: true, loop: true, playsinline: true }}
  </div>
{%- endif -%}
```

## CSS — Video Desktop/Mobile Toggle

```css
.section-<section-name>__video--mobile {
  display: block;
}
.section-<section-name>__video--desktop {
  display: none;
}

@media screen and (min-width: 750px) {
  .section-<section-name>__video--mobile {
    display: none;
  }
  .section-<section-name>__video--desktop {
    display: block;
  }
}
```
