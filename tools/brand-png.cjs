// Genera los PNG del logo a partir de los SVG de brand/.
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const fs = require('fs'), path = require('path');
const dir = path.resolve(__dirname, '../brand');
const svg = f => 'data:image/svg+xml;base64,' + fs.readFileSync(path.join(dir, f)).toString('base64');
const jobs = [
  // archivo, svg, ancho, alto, fondo, relleno
  ['kab-export-logo-color.png', 'kab-export-logo-color.svg', 3000, 0, null, 0],
  ['kab-export-logo-blanco.png', 'kab-export-logo-blanco.svg', 3000, 0, null, 0],
  ['kab-export-logo-negro.png', 'kab-export-logo-negro.svg', 3000, 0, null, 0],
  ['kab-export-logo-fondo-verde.png', 'kab-export-logo-blanco.svg', 2400, 1260, '#1F3B2D', 0.2],
  ['kab-export-logo-fondo-crema.png', 'kab-export-logo-color.svg', 2400, 1260, '#F6EFDF', 0.2],
  ['kab-export-icono-color.png', 'kab-export-icono-color.svg', 1024, 1024, null, 0],
  ['kab-export-icono-blanco.png', 'kab-export-icono-blanco.svg', 1024, 1024, null, 0],
  ['kab-export-perfil-redes.png', 'kab-export-icono-blanco.svg', 1024, 1024, '#1F3B2D', 0.2],
];
(async () => {
  const b = await chromium.launch();
  for (const [out, src, w, h, bg, pad] of jobs) {
    const vb = fs.readFileSync(path.join(dir, src), 'utf8').match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);
    const ratio = vb[3] / vb[2];
    const H = h || Math.round(w * ratio);
    const p = await b.newPage({ viewport: { width: w, height: H } });
    const iw = w * (1 - 2 * pad), ih = H * (1 - 2 * pad);
    await p.setContent(`<body style="margin:0;width:${w}px;height:${H}px;display:grid;place-items:center;background:${bg || 'transparent'}"><img src="${svg(src)}" style="max-width:${iw}px;max-height:${ih}px;width:${iw}px;height:${ih}px;object-fit:contain"></body>`);
    await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(dir, out), omitBackground: !bg });
    await p.close();
  }
  await b.close();
  console.log('PNG generados');
})();
