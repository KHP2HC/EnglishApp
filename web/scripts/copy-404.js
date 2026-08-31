/**
 * Copy index.html → 404.html so GitHub Pages serves the SPA
 * for any unknown path (SPA fallback routing).
 *
 * GitHub Pages returns 404.html for paths that don't match a static file,
 * which lets react-router handle client-side routes like /EnglishApp/app/vocabulary
 */
import { copyFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distDir = join(__dirname, '..', 'dist')
const indexHtml = join(distDir, 'index.html')
const notFoundHtml = join(distDir, '404.html')

if (existsSync(indexHtml)) {
  copyFileSync(indexHtml, notFoundHtml)
  console.log('✓ Copied index.html → 404.html for SPA routing')
} else {
  console.error('✗ index.html not found in dist/ — did the build run?')
  process.exit(1)
}
