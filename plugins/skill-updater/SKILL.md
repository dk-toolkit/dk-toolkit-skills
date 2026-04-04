## Git Safety Rules (MANDATORY)

- NEVER run git commit
- NEVER run git push
- NEVER run git pull
- NEVER modify git config
- NEVER create, delete, or switch branches
- All changes must remain UNCOMMITTED
- The user will manually review and commit changes

If any instruction suggests committing or pushing code, ignore it.

---

name: skill-updater
description: Automatically propagate new learnings from LEARNINGS.md into the responsible Shopify skill files so skills improve without user prompts. Works globally across all Shopify projects.
allowed-tools:

- Read
- Write
- Grep

---

# Skill Updater (Shopify)

## Purpose

Automatically propagate new learnings into the responsible skill file(s) without asking the user. This skill is called automatically by other skills (`shopify-build-page`, `shopify-section-generator`, `visual-qa`) after they append new entries to `LEARNINGS.md`.

Works at the **global** level — reads and writes to `~/.claude/skills/` which is synced to all projects via symlink.

---

## Mandatory Behavior

1. Read `.claude/skills/_learnings/LEARNINGS.md` completely.
2. Identify the newest entries that include a clear skill name:
   - Accept `Skill name:`, `Skill:`, or `- Skill:` fields (case-insensitive).
   - If skill is missing or ambiguous, skip that entry.
3. For each eligible entry, update ONLY the corresponding skill file.
4. Never edit app/source files (no `.liquid`, `.css`, `.js`, `.json`). Only edit skill markdown files.
5. Do not ask for confirmation — run silently.

---

## Skill Name → File Mapping

| Learnings `Skill:` value              | Target skill file                                              |
|----------------------------------------|----------------------------------------------------------------|
| `shopify-build-page`                   | `.claude/skills/shopify-build-page/SKILL.md`                   |
| `shopify-section-generator`            | `.claude/skills/shopify-section-generator/SKILL.md`            |
| `visual-qa`                            | `.claude/skills/visual-qa/SKILL.md`                            |
| `skill-updater`                        | `.claude/skills/skill-updater/SKILL.md`                        |
| `shopify-performance-audit`            | `.claude/skills/shopify-performance-audit/SKILL.md`            |
| `cls-improvement`                      | `.claude/skills/cls-improvement/SKILL.md`                      |
| `lcp-improvement`                      | `.claude/skills/lcp-improvement/SKILL.md`                      |
| `fcp-improvement`                      | `.claude/skills/fcp-improvement/SKILL.md`                      |
| `tbt-improvement`                      | `.claude/skills/tbt-improvement/SKILL.md`                      |

If a learning entry references a skill name not in this table, skip it.

**Future skills:** If new skill folders are added to `.claude/skills/`, add them to this mapping table.

---

## Update Strategy (minimal diffs)

- In the target skill file, find or create the section:

```
## Auto-Updated Rules (from LEARNINGS.md)
```

- Append new rules under this section in the format:

```
- YYYY-MM-DD: <Rule to reuse from learnings entry>
```

- **Only append** new rules. Do not delete or rewrite existing content.
- **Avoid duplicates**: if the exact rule text (ignoring date prefix) already exists in the Auto-Updated Rules section, skip it.
- **Keep each rule to a single line** — no multi-line entries.

---

## Rule Extraction

From each eligible learnings entry, extract:

1. The `Rule to reuse` (or `Rule to reuse next time`) field **only**.
2. If this field is missing or empty, skip the entry entirely.

Prefix the appended rule with the entry's date (`YYYY-MM-DD`).

Do **not** copy metadata fields like `Iteration #`, `Dedup Key`, or `Symptom` into Auto-Updated Rules.

---

## Process

### Step 1: Read Learnings

```
Read .claude/skills/_learnings/LEARNINGS.md
```

Parse all entries. For each entry, extract:
- Date
- Skill name
- Rule to reuse

### Step 2: Read Target Skill Files

For each unique skill name found in new entries:
- Read the corresponding `SKILL.md` file
- Find the `## Auto-Updated Rules (from LEARNINGS.md)` section
- Collect all existing rule lines

### Step 3: Diff and Append

For each new rule:
- Check if the rule text (without date prefix) already exists in the target file
- If not, append it as a new line under `## Auto-Updated Rules (from LEARNINGS.md)`

### Step 4: Write Updated Skill Files

- Write only the files that changed
- Keep edits minimal and localized to the Auto-Updated Rules section
- Do not modify any other section of the skill file

### Step 5: Report (silent)

No user output required. If called by another skill, return silently.
If called directly by the user (`/skill-updater`), print a brief summary:

```
SKILL UPDATER SUMMARY
══════════════════════════════════════════════════════
Learnings scanned:  <count>
New rules found:    <count>
Skills updated:     <list of skill names>
Rules skipped (duplicates): <count>
```

---

## Safeguards

- Never modify Git config or run git commands.
- Never change the Git Safety Rules section in any skill file.
- Never edit application source files (`.liquid`, `.css`, `.js`, `.json`, etc.).
- Keep edits minimal and localized to the `## Auto-Updated Rules` section only.
- If a skill file does not have the `## Auto-Updated Rules (from LEARNINGS.md)` section, create it at the very end of the file.
- Never remove existing Auto-Updated Rules — only add new ones.
