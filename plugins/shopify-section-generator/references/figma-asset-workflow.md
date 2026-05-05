# Figma Asset Extraction & Shopify Files Upload

**Skip this entire workflow if the source is CSS dumps (no Figma context available).**

## 3.1 — Credential Resolution

Look for a `.env` file in the project root. Check for these keys:

- `SHOPIFY_STORE_URL` or `SHOPIFY_FLAG_STORE` or `SHOPIFY_STORE` → store `.myshopify.com` URL
- `SHOPIFY_STOREFRONT_TOKEN` or `SHOPIFY_STOREFRONT_API_TOKEN` → Storefront API token

If both are found → confirm with user once:

```
Found store credentials in .env:
Store URL:        your-store.myshopify.com
Storefront Token: ••••••••[last 4 chars]

Confirm these are correct for this project? [Y/N]
```

If either is missing → ask the user only for the missing value.

Store both as `STORE_URL` and `STOREFRONT_TOKEN` for use in upload calls below.

## 3.2 — Identify Exportable Assets

Scan the Figma design context already fetched in Step 2. Identify only:

- **Images** — raster fills, photo layers, product shots, background images, hero images, any layer with an image/bitmap fill
- **Videos** — video embed layers or any layer named or tagged as video

Exclude entirely: Icons, SVGs, vectors, shape layers, text layers, pure color/gradient fills.

## 3.3 — Present Asset List for Confirmation

Before uploading, display the full asset list:

```
FIGMA ASSETS FOUND — Please confirm before upload
──────────────────────────────────────────────────
#   Layer Name                  Type    Format   Proposed Shopify Filename
1   Hero Background Desktop     Image   PNG      {section-name}-hero-bg-desktop.png
2   Hero Background Mobile      Image   PNG      {section-name}-hero-bg-mobile.png
3   Product Lifestyle Shot      Image   WEBP     {section-name}-product-lifestyle.webp
4   Intro Video                 Video   MP4      {section-name}-intro-video.mp4

Total: 4 assets to upload to Shopify Files (/admin/content/files)

Confirm upload? Options:
  [Y]   Upload all
  [E]   Edit the list (remove, rename, or change format)
  [N]   Skip asset upload entirely
```

Naming convention: `{section-name}-{layer-name-kebab}.{ext}`

Format rules:
- Photos / hero images → WEBP (fallback PNG if export fails)
- Decorative/UI images → PNG
- Videos → MP4

Do NOT proceed to upload until user confirms.

## 3.4 — Export from Figma

For each confirmed asset:

1. Use `mcp__figma-desktop__get_design_context` to get the node ID.
2. Export via Figma REST API:
   - Images: `GET https://api.figma.com/v1/images/{file_id}?ids={node_id}&format=png&scale=2`
   - Videos: export at original resolution
3. Download the exported file bytes locally.
4. If export fails → warn the user, skip that asset, continue with rest.

## 3.5 — Upload to Shopify Files

Upload each asset to Shopify `/admin/content/files` using the Storefront API:

```graphql
mutation fileCreate($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files {
      ... on MediaImage {
        id
        image { url }
      }
      ... on Video {
        id
        sources { url }
      }
    }
    userErrors { field message }
  }
}
```

- Endpoint: `https://{STORE_URL}/api/2026-01/graphql.json`
- Header: `X-Shopify-Storefront-Access-Token: {STOREFRONT_TOKEN}`
- Upload one asset at a time. Add 300ms delay between uploads.
- On success → store CDN URL in asset map.
- On error → show error, ask user: `[Retry] [Skip] [Abort]`

## 3.6 — Asset Map Output

After all uploads, print confirmation:

```
ASSETS UPLOADED TO SHOPIFY FILES
──────────────────────────────────────────────────────────────────
#   Filename                              Shopify CDN URL
1   hero-bg-desktop.png                  https://cdn.shopify.com/s/files/...
2   hero-bg-mobile.png                   https://cdn.shopify.com/s/files/...
──────────────────────────────────────────────────────────────────
These URLs will be used as default values in schema settings and Liquid code.
```

Store this map internally — used in Steps 4 and 5.

## 3.7 — Usage in Section Code

**In schema** — use CDN URLs as preset defaults:

```json
"presets": [
  {
    "name": "Hero Banner",
    "settings": {
      "hero_image": "https://cdn.shopify.com/s/files/..."
    }
  }
]
```

**In Liquid** — for fallback images:

```liquid
{%- assign fallback_src = 'https://cdn.shopify.com/s/files/...' -%}
<img
  src="{{ section.settings.hero_image | image_url: width: 1440 | default: fallback_src }}"
  loading="lazy" width="1440" height="800"
  alt="{{ section.settings.hero_image_alt | escape }}">
```

**For videos:**

```liquid
<video autoplay muted loop playsinline>
  <source src="{{ section.settings.video_url | default: 'https://cdn.shopify.com/s/files/...' }}" type="video/mp4">
</video>
```

Icons remain unaffected — continue using `{%- render 'icon-<name>' -%}` snippets.
