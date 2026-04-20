# DK Toolkit Skills - Claude Code Plugin Marketplace

A comprehensive suite of **11 Claude Code plugins** for Shopify theme development, performance optimization, and dynamic content management.

## Quick Install

```bash
# Clone the repository
git clone https://github.com/dk-toolkit/dk-toolkit-skills.git

# Install all plugins (symlink to Claude skills directory)
cd dk-toolkit-skills
./install.sh

# Or install a single plugin
./install.sh --plugin dynamic-data-flow
```

## Available Plugins

### Shopify Content Management

| Plugin | Description | Invocable |
|--------|-------------|-----------|
| [dynamic-data-flow](./dynamic-data-flow/) | Convert hardcoded Shopify templates into metafield-driven dynamic pages | No (auto-triggered) |

### Shopify Theme Development

| Plugin | Description | Invocable |
|--------|-------------|-----------|
| [shopify-build-page](./shopify-build-page/) | Build complete Shopify pages from Figma designs | No (auto-triggered) |
| [shopify-section-generator](./shopify-section-generator/) | Generate individual Shopify sections from Figma | No (auto-triggered) |
| [js-standards](./js-standards/) | Vanilla JS standards — modern ES, Web Components, event delegation, accessibility | No (auto-triggered) |

### Performance Optimization

| Plugin | Description | Invocable |
|--------|-------------|-----------|
| [shopify-performance-audit](./shopify-performance-audit/) | Generate .docx performance audit reports | Yes |
| [cls-improvement](./cls-improvement/) | Detect and fix Cumulative Layout Shift issues | Yes |
| [fcp-improvement](./fcp-improvement/) | Detect and fix First Contentful Paint issues | Yes |
| [lcp-improvement](./lcp-improvement/) | Detect and fix Largest Contentful Paint issues | Yes |
| [tbt-improvement](./tbt-improvement/) | Detect and fix Total Blocking Time issues | Yes |

### Quality Assurance

| Plugin | Description | Invocable |
|--------|-------------|-----------|
| [visual-qa](./visual-qa/) | Visual QA across 11 breakpoints (320px-2560px) | No (auto-triggered) |

### Utilities

| Plugin | Description | Invocable |
|--------|-------------|-----------|
| [skill-updater](./skill-updater/) | Auto-propagate learnings into skill files | No (auto-triggered) |

## Plugin Structure

Each plugin follows a standardized structure:

```
plugin-name/
  plugin.json       # Manifest with metadata, triggers, dependencies
  SKILL.md           # The skill definition (Claude Code reads this)
  references/        # Reference documentation (if any)
  scripts/           # Python/JS helper scripts (if any)
```

### plugin.json Schema

```json
{
  "name": "plugin-id",
  "displayName": "Human Readable Name",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": { "name": "...", "organization": "...", "website": "..." },
  "category": "shopify-content | shopify-development | performance | quality-assurance | utility",
  "tags": ["shopify", "performance", ...],
  "triggers": ["phrases that activate this skill"],
  "userInvocable": true,
  "tools": ["Read", "Write", "Edit", ...],
  "dependencies": {
    "python": ["python-docx"],
    "mcp": ["@anthropic-ai/mcp-shopify"]
  },
  "files": {
    "skill": "SKILL.md",
    "references": ["references/file.md"],
    "scripts": ["scripts/helper.py"]
  }
}
```

## How It Works

### Trigger-Based Activation

Plugins activate automatically when you mention relevant phrases:

- "make this page dynamic" -> **dynamic-data-flow**
- "build page from figma" -> **shopify-build-page**
- "improve cls" -> **cls-improvement**
- "performance audit" -> **shopify-performance-audit**

### User-Invocable Plugins

Some plugins can be called directly:

- `/shopify-performance-audit` - Generate a performance report
- `/cls-improvement` - Start CLS optimization
- `/fcp-improvement` - Start FCP optimization
- `/lcp-improvement` - Start LCP optimization
- `/tbt-improvement` - Start TBT optimization

### Self-Learning System

The toolkit includes a built-in learning loop:

1. Skills log learnings to `_learnings/LEARNINGS.md` after each run
2. The **skill-updater** plugin propagates validated rules back into skill files
3. Skills get progressively smarter with each use

## Dependencies

### Required for All Plugins

- [Claude Code CLI](https://claude.ai/claude-code)

### Optional (per plugin)

| Dependency | Required By | Install |
|------------|-------------|---------|
| `python-docx` | shopify-performance-audit | `pip3 install python-docx` |
| `playwright` | shopify-performance-audit | `pip3 install playwright && python3 -m playwright install chromium` |
| `requests` | dynamic-data-flow | `pip3 install requests` |
| Figma Desktop MCP | shopify-build-page, shopify-section-generator | MCP server config |
| Shopify Dev MCP | shopify-build-page, shopify-section-generator | MCP server config |

## Configuration

### Google PageSpeed Insights API Key

The performance plugins use a PageSpeed Insights API key. To use your own:

1. Get a key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the PageSpeed Insights API
3. Set the environment variable:
   ```bash
   export GOOGLE_PSI_API_KEY="your-api-key-here"
   ```

### Shopify Admin API (for dynamic-data-flow)

The dynamic-data-flow plugin needs Shopify Admin API access:

1. Create a custom app in Shopify Admin
2. Grant scopes: `write_metafield_definitions`, `read_metafield_definitions`, `read_products`, `read_collections`
3. The plugin will prompt for credentials and save them securely to `.env`

## Contributing

1. Fork the repository
2. Create a new plugin directory under `plugins/`
3. Add `plugin.json` and `SKILL.md` following the schema above
4. Update `registry.json` to include your plugin
5. Submit a pull request

## License

MIT License - see individual plugin directories for details.

---

Built with Claude Code by [DevX Labs](https://www.devxlabs.ai/)
