import fs from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'

const baseUrl = process.env.SCREENSHOT_BASE_URL || 'http://localhost:5173'
const outDir = process.env.SCREENSHOT_OUT_DIR || path.resolve('screenshots')
const routes = [
  { name: 'dashboard', path: '/' },
  { name: 'mailbox-list', path: '/mailboxes' },
  { name: 'template-list', path: '/templates' },
  { name: 'blocked-rules', path: '/blocked-rules' },
]

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true })
}

async function takeShots() {
  await ensureDir(outDir)
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } })

  for (const route of routes) {
    const page = await context.newPage()
    const target = `${baseUrl}${route.path}`
    console.log(`capturing: ${target}`)
    await page.goto(target, { waitUntil: 'networkidle' })
    await page.waitForTimeout(1200)
    await page.screenshot({ path: path.join(outDir, `${route.name}.png`), fullPage: true })
    await page.close()
  }

  await browser.close()
}

takeShots().catch((error) => {
  console.error('screenshot generation failed', error)
  process.exit(1)
})
