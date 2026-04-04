# TBT Improvement

> Detect, analyze, plan, implement, and validate Total Blocking Time improvements.

## What It Does

TBT Improvement follows the same 12-step measure-fix-verify workflow as the other Core Web Vitals plugins, but targets Total Blocking Time specifically. It specializes in script deferral, long-task breaking, and offloading work to Web Workers to keep the main thread responsive.

## Triggers

- `/tbt-improvement`

## Requirements

- Google PageSpeed Insights API key

## Quick Start

Run `/tbt-improvement` and supply the URLs to optimize. The plugin will benchmark current TBT, identify long tasks and heavy scripts, apply optimizations, and confirm the results.
