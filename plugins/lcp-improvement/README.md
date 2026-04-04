# LCP Improvement

> Detect, analyze, plan, implement, and validate Largest Contentful Paint improvements.

## What It Does

LCP Improvement follows the same 12-step measure-fix-verify workflow as the other Core Web Vitals plugins, but targets Largest Contentful Paint specifically. It specializes in image optimization, resource preloading, and fetch-priority tuning to ensure the largest visible element renders as quickly as possible.

## Triggers

- `/lcp-improvement`

## Requirements

- Google PageSpeed Insights API key

## Quick Start

Run `/lcp-improvement` and supply the URLs to optimize. The plugin will benchmark current LCP times, identify the LCP element and bottlenecks, apply optimizations, and confirm the results.
