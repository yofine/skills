import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { registry, findDesignSystem } from './src/data/registry.ts'
import { toAgentApiMarkdown, toDesignMarkdown, toStandaloneHtml } from './src/lib/serialize.ts'

function respond(response: import('node:http').ServerResponse, status: number, body: string, type: string, filename?: string) {
  response.statusCode = status
  response.setHeader('Content-Type', `${type}; charset=utf-8`)
  response.setHeader('Cache-Control', 'no-store')
  if (filename) response.setHeader('Content-Disposition', `attachment; filename="${filename}"`)
  response.end(body)
}

function designSystemApi(): Plugin {
  return {
    name: 'design-system-api',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        if (request.method !== 'GET' || !request.url) return next()
        const pathname = new URL(request.url, 'http://localhost').pathname
        if (pathname === '/api/design-systems') {
          const data = registry.map(({ tokenExport: _tokenExport, ...entry }) => ({ ...entry, tokens: undefined, dna: undefined, components: undefined, layoutPatterns: undefined, interactions: undefined, guidelines: undefined, conventions: undefined, presetMappings: undefined }))
          return respond(response, 200, JSON.stringify({ data }), 'application/json')
        }
        if (/^\/api\/design-systems\/[a-z0-9-]+\/tokens\.json$/.test(pathname)) {
          return respond(response, 404, JSON.stringify({ error: 'Token JSON downloads are not available' }), 'application/json')
        }
        const match = pathname.match(/^\/api\/design-systems\/([a-z0-9-]+)(?:\/(API\.md|DESIGN\.md|design-system\.html))?$/)
        if (!match) return next()
        const entry = findDesignSystem(match[1])
        if (!entry) return respond(response, 404, JSON.stringify({ error: 'Design system not found' }), 'application/json')
        const format = match[2]
        if (format === 'API.md') return respond(response, 200, toAgentApiMarkdown(entry), 'text/markdown')
        if (format === 'DESIGN.md') return respond(response, 200, toDesignMarkdown(entry), 'text/markdown', 'DESIGN.md')
        if (format === 'design-system.html') return respond(response, 200, toStandaloneHtml(entry), 'text/html', `${entry.slug}-design-system.html`)
        return respond(response, 200, JSON.stringify({ data: entry }), 'application/json')
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), designSystemApi()],
  server: { host: '0.0.0.0', port: 4321 },
})
