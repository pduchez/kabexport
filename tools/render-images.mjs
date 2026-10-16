// Genera las imágenes PNG (og-image, logo, iconos) con Chromium.
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_PATH || 'playwright');
import { fileURLToPath } from 'url';
import path from 'path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const img = path.join(root, 'docs/assets/img');
const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
const browser = await chromium.launch({ proxy, args: ['--ignore-certificate-errors'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.goto('file://' + path.join(root, 'tools/og.html'));
await page.waitForTimeout(2500);
await page.screenshot({ path: path.join(img, 'og-image.png') });
for (const [file, size, src] of [['apple-touch-icon.png', 180, 'favicon.svg'], ['favicon-32.png', 32, 'favicon.svg'], ['logo.png', 512, 'logo-mark.svg']]) {
  const p = await browser.newPage({ viewport: { width: size, height: size } });
  await p.setContent(`<body style="margin:0;background:${file==='logo.png'?'#F6EFDF':'transparent'}"><img src="file://${path.join(img, src)}" style="width:${size}px;height:${size}px;display:block${file==='logo.png'?';padding:48px;box-sizing:border-box':''}"></body>`);
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(img, file), omitBackground: file !== 'logo.png' });
}
await browser.close();
console.log('ok');
