import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const here = dirname(fileURLToPath(import.meta.url))
const styleOut = resolve(here, '../../../OUT/style.json')

function saveStylePlugin() {
  return {
    name: 'save-style',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const path = (req.url || '').split('?')[0]
        if (path !== '/api/save-style' || req.method !== 'POST') {
          next()
          return
        }
        const chunks = []
        req.on('data', (chunk) => chunks.push(chunk))
        req.on('end', () => {
          try {
            const raw = Buffer.concat(chunks).toString('utf8')
            JSON.parse(raw)
            mkdirSync(dirname(styleOut), { recursive: true })
            writeFileSync(styleOut, raw.endsWith('\n') ? raw : `${raw}\n`, 'utf8')
            res.statusCode = 200
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ ok: true, path: 'F07_CAPTION/OUT/style.json' }))
          } catch (err) {
            res.statusCode = 400
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ ok: false, error: String(err.message || err) }))
          }
        })
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), saveStylePlugin()],
  base: './',
  server: {
    host: true,
    allowedHosts: ['.monkeycode-ai.live'],
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
