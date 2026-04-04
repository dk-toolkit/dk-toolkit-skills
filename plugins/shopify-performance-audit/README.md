# Shopify Performance Audit

> Generates professional .docx performance audit reports for Shopify stores.

## What It Does

Shopify Performance Audit runs PageSpeed Insights tests three times per page in both mobile and desktop modes (in parallel), collects Core Web Vitals and Lighthouse metrics, and compiles the results into a formatted Word document. The report includes scores, metric breakdowns, and actionable recommendations.

## Triggers

- `/shopify-performance-audit`

## Requirements

- Python 3 with `python-docx` and `playwright`
- Google PageSpeed Insights API key

## Quick Start

Run `/shopify-performance-audit` and provide the store URL(s) you want to audit. The plugin handles test execution, data collection, and document generation, then outputs a `.docx` report file.
