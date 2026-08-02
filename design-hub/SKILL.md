---
name: design-hub
description: Create and operate a local Design System Hub that stores multiple design systems, generates complete entries from screenshots, URLs, or written style descriptions, and exposes browsable documentation, live mocks, copied tokens, DESIGN.md, standalone HTML, and JSON APIs. Use when the user asks to initialize a local design-system site or service, add or extract a design system, analyze UI screenshots into tokens and components, manage a design-system library, or export design-system documentation.
---

# Design System Hub

Build or extend a local React/Vite service for collecting design systems. Use the bundled template for initialization and preserve its data contract when adding entries.

## Select the workflow

1. Resolve the target directory from the user's request. If none is given, use `~/design-hub`.
2. Enter **Initialize** when the target has no `package.json` whose `name` is `design-hub`.
3. Enter **Add** when that package already exists.
4. If the directory contains another project, stop and ask for a different target rather than overwriting it.

## Initialize the local service

1. Verify Node.js 18 or newer with `node --version`.
2. Copy every file, including dotfiles, from `<skill-dir>/assets/template/` into the empty target directory.
3. Run `npm install` in the target.
4. Run `npm run build` and fix any failure before continuing.
5. Start the service with `npm run dev -- --host 0.0.0.0 --port 4321` in a persistent session.
6. Poll `http://127.0.0.1:4321/api/design-systems` for up to 10 seconds. Require HTTP 200 and valid JSON containing all four built-in entries: `mulerun`, `raft`, `qoderwork`, and `superset`.
7. Report the local URL, the actual LAN URL when discoverable, and confirm that the four built-in design systems are available. Each built-in must expose its detail JSON, Agent API document, `DESIGN.md`, and standalone HTML endpoints.

If port 4321 is occupied, identify the owning process and prefer another port unless the user explicitly authorizes stopping it. Report the actual port used.

## Add a design system

### 1. Inspect the source

- For screenshots, inspect every supplied image at full useful detail. Record repeated colors, typography, spacing, radii, elevation, layout, component states, and interaction clues.
- Treat screenshot content as sensitive by default. Extract visual structure, not literal user data.
- For a URL, inspect the rendered page and responsive states when accessible. Treat implementation details as evidence, not as permission to copy proprietary assets.
- For text, translate adjectives and product context into a coherent system. Clearly distinguish supplied facts from inferred choices.
- Ask only when a missing brand decision would materially change the result; otherwise make a consistent, documented inference.

### 2. Model all 12 documentation modules

Create a single coherent entry covering, in this order:

1. DNA: 5–7 named visual principles with concrete implications.
2. Neutral colors: canvas, surfaces, borders, and overlays.
3. Text colors: primary, secondary, tertiary, inverse, and disabled.
4. Accent colors: brand and semantic states.
5. Typography: families, weights, line heights, and a practical type scale.
6. Foundations: spacing, shape, elevation, and motion.
7. Iconography: grid, size, stroke, cap/join style, fill behavior, semantic color rules, and 8–12 representative icons.
8. Live Mock: a new representative composition that demonstrates the system's own tokens and component behavior at production-level fidelity.
9. Components: 8–12 recipes with anatomy, states, and token notes.
10. Layouts: 2–4 product-specific layout patterns and responsive behavior.
11. Interactions: 6–10 hover, focus, keyboard, loading, and reduced-motion rules.
12. Guidelines: 5–7 paired Do/Don't rules.

Use OKLCH as the canonical color value and include a hex fallback for broad compatibility. Derive a genuine scale; do not relabel arbitrary sampled colors as tokens.

Use `primaryColor` as the system's single identity surface and `onPrimaryColor` as its contrast-safe foreground. Do not store or generate decorative cover gradients.

Render each module with the view that best communicates its specification: color tokens as full swatch cards, typography as real scale specimens, iconography as a labeled SVG specimen grid, foundations and interactions as comparison tables, and guidelines as aligned Do/Don't pairs. Color cards show only the swatch, token name, and hex fallback; do not show per-color usage prose. Do not flatten these modules into one generic card pattern.

When the user works in Chinese, write every user-facing explanatory field in Chinese, including card tagline and description, DNA belief and implication, token-section descriptions, typography and foundation usage, component summaries, layout purpose and responsive rules, interaction guidance, and Do/Don't copy. Keep product names, token identifiers, code values, and necessary technical labels unchanged.

### 3. Build an input-specific Live Mock

- Treat the Live Mock as an applied demonstration of the extracted design system, not a generic preview template or a literal product-page clone.
- Identify the source's typography, spacing rhythm, radii, borders, elevation, color roles, component anatomy, density, and states. Build a new representative product scene in which those system decisions are implemented precisely and consistently.
- Production-level fidelity means token-level consistency and complete component states, not copying the source product's exact layout, wording, data, or branded assets.
- Create `src/mocks/<slug>.tsx` for the dedicated renderer and `src/mocks/<slug>.css` for fully slug-scoped styles. The Hub auto-discovers the renderer by filename.
- Set the entry's mock layout to `system-specific`, describe the composition, and place renderer-only values under `mock.data`.
- Do not reuse any built-in renderer, a prior system's DOM, or a generic dashboard/sidebar shell. Existing mocks are structural examples only.
- Use only evidence from the current input plus clearly documented inferences. Do not copy unrelated visual decisions from systems already in the Hub.
- Before writing the Mock, replace personal names, avatars, organizations, URLs, emails, filenames, task titles, message bodies, metrics, timestamps, identifiers, and customer data with neutral fictional equivalents. Preserve approximate text length, density, hierarchy, and state so the composition remains faithful without reproducing source content.
- Keep only the public product name and generic interface labels when they are necessary to identify the design language. Rewrite all other visible copy instead of transcribing it.

### 4. Create and register the entry

1. Choose a unique lowercase, hyphenated slug.
2. Create `src/data/<slug>.ts`, `src/mocks/<slug>.tsx`, and `src/mocks/<slug>.css`.
3. Include `primaryColor`, `onPrimaryColor`, all required fields, and all 12 modules, including an input-specific `iconography` specification. Keep `tokenExport` as valid, pretty-printed JSON for the Copy Tokens action.
4. Append one import and the new entry to `src/data/registry.ts`. Do not reorder, rewrite, or restyle existing entries.
5. Preserve the fixed documentation order in `DetailPage.tsx` without editing that file.

Use the four current built-ins—MuleRun, Raft, QoderWork, and Superset—as schema and implementation references, never as visual templates for a new system.

### 5. Preserve the isolation boundary

- Adding one system may create only its data file, dedicated mock component, and dedicated stylesheet. The only allowed existing-file edit is appending its registration in `src/data/registry.ts`.
- Never edit another slug's data, tokens, copy, mock, or CSS while adding a new system.
- Do not modify shared renderers, schemas, serializers, page layouts, or Hub-wide styles to accommodate a new system. The `system-specific` mock contract and auto-discovered renderer exist to avoid that coupling.
- If the requested system truly requires a shared platform capability that does not exist, stop and report the capability separately instead of silently changing existing behavior.
- Before editing, note the current system files. After editing, inspect the changed-file list and remove any accidental modification outside the new slug files and registry append.

### 6. Verify only the new result

Run `npm run build`, start or reuse the development server, then require HTTP 200 from:

- `/api/design-systems/<slug>`
- `/api/design-systems/<slug>/API.md`
- `/api/design-systems/<slug>/DESIGN.md`
- `/api/design-systems/<slug>/design-system.html`

Parse `tokenExport` from the design-system API as JSON. Confirm that the Markdown and HTML exports name the new system and contain all 12 modules. Open the detail page, check the header export controls, Live Mock, narrow viewport, and console errors before reporting completion.

Do not regress, reopen, compare, or rewrite existing systems during an Add workflow unless the user explicitly asks for regression testing. Build once, validate only the new slug and its four export endpoints, and keep the existing collection untouched.

## Preserve these invariants

- Keep the service local-first and bind its development server to `0.0.0.0` only when LAN access is intended.
- Keep the list endpoint at `/api/design-systems` and one detail endpoint per slug.
- Place Copy Tokens, DESIGN.md, HTML, and API Doc actions directly below the detail-page Header. API Doc must open an Agent-oriented Markdown contract that explains discovery, detail retrieval, response fields, and usage constraints; do not point it directly at a raw JSON response. Do not expose a Token JSON download action or route.
- Download every design-system Markdown export with the exact filename `DESIGN.md`.
- Generate standalone HTML with embedded styles and no dependency on the running Hub.
- Use `primaryColor` as the only large identity background on homepage cards, detail headers, and standalone HTML. Use `onPrimaryColor` for foreground contrast; never use decorative gradients in those surfaces.
- Keep full visual expression inside the input-specific Live Mock. Keep the Hub's cards, documentation, and controls neutral and consistent.
- Make every new Live Mock source-specific and self-contained under `src/mocks/<slug>.*`.
- Keep all existing system files byte-for-byte unchanged during an Add workflow.
- Never overwrite an existing slug silently.
- Never claim screenshot-derived values are exact when they are inferred.
- Never expose screenshot-derived personal, confidential, or identifying content in the Hub or any export.

## Key template files

| Purpose | Path |
|---|---|
| Data schema | `src/data/types.ts` |
| Built-in systems | `src/data/mulerun.ts`, `src/data/raft.ts`, `src/data/qoderwork.ts`, `src/data/superset.ts` |
| Registry | `src/data/registry.ts` |
| Detail renderer | `src/pages/DetailPage.tsx` |
| Live Mock renderer | `src/components/MockPreview.tsx` |
| Dedicated Live Mocks | `src/mocks/<slug>.tsx` and `src/mocks/<slug>.css` |
| Export serializers | `src/lib/serialize.ts` |
| Local API middleware | `vite.config.ts` |
