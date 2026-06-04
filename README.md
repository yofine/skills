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

Use the `brief` skill to create and operate a professional research brief site. It can initialize a new Brief site, turn source material into standalone Chinese analysis reports, publish those reports into the site, and start the local preview server.

![Brief site preview](./images/brief.png)

Example requests:

- "Use the brief skill to initialize a new site in `~/Workspace/my-brief` and start it locally."
- "Use brief to analyze this article, generate a Chinese report, and publish it to my Brief site."
- "Use brief to add this codebase analysis as a new report and make it the featured report."
- "Use brief to build the site and tell me where the production output is."

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
