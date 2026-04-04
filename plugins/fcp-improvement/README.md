# FCP Improvement

> Detect, analyze, plan, implement, and validate First Contentful Paint improvements.

## What It Does

FCP Improvement follows the same 12-step measure-fix-verify workflow as the other Core Web Vitals plugins, but targets First Contentful Paint specifically. It includes proven patterns for script deferral, font optimization, and script interception to get visible content on screen faster.

## Triggers

- `/fcp-improvement`

## Requirements

- Google PageSpeed Insights API key

## Quick Start

Run `/fcp-improvement` and supply the URLs to optimize. The plugin will benchmark current FCP times, identify render-blocking resources, apply optimizations, and confirm the results.
