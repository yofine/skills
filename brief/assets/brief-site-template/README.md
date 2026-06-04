# The Brief Ledger

React + Tailwind + shadcn/ui + Vite site for publishing AI-generated HTML reports.

The site has two main surfaces:

- `/` lists every report in a restrained newspaper and magazine-style archive.
- `/reports/:slug` shows report metadata and summary on the left, then injects the standalone HTML report into an iframe on the right.

## Run

```bash
npm install
npm run dev
```

## Publish A Report

This project is intentionally Agent-friendly. To publish a new report, an Agent only needs to:

1. Generate a standalone HTML file.
2. Save it under `public/reports/<slug>.html`.
3. Add one object to `src/content/reports.ts`.

Example registry object:

```ts
{
  slug: 'new-research-brief',
  title: 'New Research Brief',
  deck: 'One sentence that describes the report.',
  publishedAt: '2026-06-04',
  readingTime: '8 min read',
  author: 'Brief Research Desk',
  docSrc: '/reports/new-research-brief.html',
  summary: 'Short detail-page summary.',
  keyFindings: ['Finding one.', 'Finding two.', 'Finding three.'],
}
```

## HTML Report Contract

Reports in `public/reports/` should be complete HTML documents with their own `<style>` block and responsive layout. They must be useful when opened directly in the browser.

The React detail page fetches `docSrc`, injects a `<base>` element for relative assets, and renders the result with `iframe srcDoc`. The iframe also receives a `doc-src` attribute so automation can inspect which source document was injected.

## Structure

```text
src/content/reports.ts          Report registry and metadata contract
src/pages/home-page.tsx         Magazine-style archive
src/pages/report-page.tsx       Summary + iframe detail page
src/components/reports/         Report cards, covers, and iframe loader
src/components/ui/              shadcn-style primitives
public/reports/                 Standalone HTML report files
```

## Build

```bash
npm run build
```
