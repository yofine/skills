# Skills

My personal collection of AI agent skills.

## Overview

This repository contains reusable skills that extend AI agent capabilities. Each skill is a self-contained module that teaches an agent how to perform specific tasks.

## Project Structure

```
skills/
├── blueprinter/      # Technical diagram generation skill
├── brief/            # Brief site template and report publishing skill
└── README.md
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [blueprinter](./blueprinter/) | Generate technical diagrams in Flat Engineering Blueprint style using HTML/CSS |
| [brief](./brief/) | Initialize a Brief React/Vite report site, generate Chinese analysis reports, and publish them into the site |

### Example: Blueprinter Output

![Claude Code Architecture Blueprint](./images/claudecodesource.png)

### Brief

The `brief` skill includes a complete Brief frontend template under `assets/brief-site-template`, with React, Vite, Tailwind-compatible styling, report archive pages, detail pages, iframe-based standalone HTML report rendering, and one sample report.

Users do not need to run the template script manually. The intended workflow is to invoke the skill in an agent session and describe the desired outcome in natural language, for example:

- initialize a new Brief site in a target directory.
- generate a Brief-style Chinese HTML analysis report from a source article, topic, or codebase.
- publish the generated report into the Brief site.
- install dependencies and start the local dev server.

When invoked, the agent uses the bundled template and helper script internally, then runs the necessary project commands such as dependency installation, build validation, or dev-server startup. Publishing a report means adding `public/reports/<slug>.html` and updating `src/content/reports.ts`.

## Skill Structure

Each skill contains:

```
skill-name/
└── SKILL.md    # Skill definition with instructions for the agent
```

### SKILL.md Format

```yaml
---
name: skill-name
description: When and how to use this skill
---

# Skill content and instructions...
```

## License

MIT
## Star History

[![Star History Chart](https://api.star-history.com/image?repos=yofine/skills&type=date&legend=top-left)](https://www.star-history.com/?repos=yofine%2Fskills&type=date&legend=top-left)

<br/>
