# DK Toolkit Skills

> A marketplace-ready collection of Claude Code plugins for Shopify theme development and performance optimization.

## Overview

This repository contains **10 production-tested plugins** that extend Claude Code with specialized Shopify capabilities:

- **Theme Development** - Build pages and sections from Figma designs
- **Dynamic Content** - Convert hardcoded templates to metafield-driven pages
- **Performance Optimization** - Analyze and improve Core Web Vitals (CLS, FCP, LCP, TBT)
- **Quality Assurance** - Visual QA across 11 responsive breakpoints
- **Self-Learning** - Skills improve automatically with each use

## Installation

```bash
git clone https://github.com/dk-toolkit/dk-toolkit-skills.git
cd dk-toolkit-skills/plugins
./install.sh
```

See [plugins/README.md](./plugins/README.md) for detailed documentation.

## Repository Structure

```
dk-toolkit-skills/
  plugins/
    registry.json                   # Master plugin registry
    install.sh                      # One-command installer
    README.md                       # Full documentation
    dynamic-data-flow/              # Metafield-driven dynamic pages
    shopify-build-page/             # Full page builder from Figma
    shopify-section-generator/      # Section generator from Figma
    shopify-performance-audit/      # .docx performance reports
    cls-improvement/                # CLS optimization
    fcp-improvement/                # FCP optimization
    lcp-improvement/                # LCP optimization
    tbt-improvement/                # TBT optimization
    visual-qa/                      # Visual QA testing
    skill-updater/                  # Self-learning automation
    _learnings/                     # Shared knowledge base
  agents/                           # (reserved for future agent configs)
  skills -> ~/.claude/skills        # Local development symlink
```

## License

MIT

---

Built by [DevX Labs](https://www.devxlabs.ai/)
