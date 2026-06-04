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

Initialize a new Brief site:

```bash
python3 ./brief/scripts/init_brief_site.py /path/to/NewBriefSite
cd /path/to/NewBriefSite
npm install
npm run dev
```

Use it when an agent needs to create a Brief site, generate a standalone Chinese HTML analysis report, or publish a report by adding `public/reports/<slug>.html` and updating `src/content/reports.ts`.

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
