---
name: brief
description: Initialize and operate a Brief React/Vite report site from a bundled template, then generate standalone Brief-style HTML analysis reports and publish them into that Brief site. Use when an agent is asked to create a new Brief site, bootstrap the project template, generate a Brief-style report, add report HTML under public/reports, or update src/content/reports.ts metadata. The bundled template includes the site engineering scaffold and one sample report only.
---

# Brief Site

## Scope

Use this skill for the full Brief workflow:

- initialize a new Brief site from the bundled React + Vite + Tailwind template.
- generate one standalone Brief-style HTML analysis report.
- publish that report into the Brief site by adding HTML and metadata.

Do not use it to redesign the Brief visual system unless the user explicitly asks. The template already encodes the site style, layout, theme transition, iframe report rendering, and report archive behavior.

## Initialize A Site

Use the bundled template at `assets/brief-site-template`. This is the complete frontend project, not a scaffold stub. After copying it to a target directory, dependency installation is the only required setup before startup.

The user is not expected to run setup scripts manually. Treat the script and shell commands in this section as the agent's implementation steps after the user asks to initialize or start a Brief site.

It contains:

- React + Vite + TypeScript app.
- Tailwind/shadcn-compatible component structure.
- fixed Brief header, Edition/Archive/Tags views, detail page, iframe report renderer.
- View Transitions based light/dark theme switching.
- one sample report only: `harness-design-long-running-apps`.
- no extra report data beyond the single sample report.

When asked to create a site, the agent should:

```bash
python3 <skill-dir>/scripts/init_brief_site.py /path/to/NewBriefSite
cd /path/to/NewBriefSite
npm install
npm run dev
```

Use `--force` only when the user explicitly wants to replace the target directory.

## Generate A Report

Generate one report at a time as a standalone HTML file.

Content rules:
- Use the language requested by the user or implied by the site. If no language is specified, follow the existing site's language.
- Preserve source claims, caveats, dates, examples, and scope.
- Do not invent facts or write the user's instructions into the report body.
- Produce an independent professional brief, not a school-style article summary.
- Identify the source's central engineering/product judgment.
- Use external context only to sharpen interpretation, not to replace the source.

Report structure:
- kicker, H1, deck, source metadata.
- lead judgment block.
- 3-5 analytical sections.
- useful visual reasoning: architecture diagram, flow, matrix, lifecycle, or responsibility split.
- practical closing section: adoption criteria, risks, open variables, or design implications.

HTML rules:
- Complete standalone HTML starting with `<!doctype html>`.
- `lang="zh-CN"`.
- Light variables in `:root`.
- Dark variables in `:root[data-brief-theme="dark"]`.
- Prefer CSS diagrams and tables over external assets.
- No side rail that squeezes the main reading column unless explicitly requested.
- Report title in `<title>` and `<h1>` must match site metadata exactly.

## Publish A Report

In the Brief project, a published report has two files:

1. HTML:
   - `public/reports/<slug>.html`
   - `slug` is lowercase kebab-case.

2. Metadata:
   - `src/content/reports.ts`
   - add or update one `Report` object in `reports`.

Required `Report` fields:

```ts
{
  slug: string
  title: string
  deck: string
  publishedAt: string
  readingTime: string
  docSrc: string
  sourceUrl: string
  featured?: boolean
  tags: string[]
  summary: string
  commentary: string
  watchlist: string[]
  keyFindings: string[]
}
```

Metadata rules:
- `docSrc` must be `/reports/<slug>.html`.
- `title` must match report HTML `<title>` and `<h1>`.
- `deck` should be compact enough for the homepage lead display.
- `summary` is for the detail page left rail; keep it content-focused.
- `commentary` should be an editorial judgment, not a publishing note.
- `watchlist` should contain 2-4 short variables.
- `keyFindings` should contain 3 grounded findings.

Tags:
- Prefer existing tags in `reportTags`.
- Add a tag only when the report truly needs a new filter category.
- Tag values use lowercase kebab-case; labels should be short and match the site's language.

Featured:
- Normally only one report has `featured: true`.
- If a new report should be featured, remove `featured` from the old one.
- If the user does not specify featured placement, keep current featured unchanged.

Ordering:
- Featured report first.
- Then intended editorial order, usually reverse chronological unless the user says otherwise.

## Validation

Before finishing:

```bash
npm run build
```

Also run `npm run lint` when TypeScript/React files changed.

Check:
- no duplicate `slug`.
- no duplicate `docSrc`.
- `public/reports/<slug>.html` exists.
- report HTML starts with `<!doctype html>`.
- report has no visible publishing instructions.
- report supports dark theme.
- detail page title, metadata title, and report title agree.

## Final Response

Keep the final response practical:

- site initialized path, if applicable.
- report files created or updated.
- metadata file updated.
- build/lint result.

Do not restate the whole contract unless the user asks.
