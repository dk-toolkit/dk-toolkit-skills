# Skill Updater

> Auto-propagates learnings from LEARNINGS.md into responsible skill files.

## What It Does

Skill Updater monitors the LEARNINGS.md file and pushes new entries into the appropriate skill files so that accumulated knowledge is available in future runs. It is called automatically by other plugins after they log learnings -- no manual invocation is needed.

## Triggers

- Called automatically by other skills after they log learnings.

## Requirements

- No external dependencies.

## Quick Start

No action required. When any plugin appends a new entry to LEARNINGS.md, Skill Updater picks it up and distributes the learning to the relevant skill files automatically.
