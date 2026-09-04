const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();
  const file = 'file://' + path.resolve(__dirname, 'report.html');
  await page.goto(file, { waitUntil: 'networkidle' });
  const footerTemplate = `
    <div style="width:100%; font-family:Arial,Helvetica,sans-serif; font-size:7.5pt; color:#898781;
                padding:0 22mm; display:flex; justify-content:space-between; box-sizing:border-box;">
      <span>DTU Dynamo — indholdsanalyse 2005–2026</span>
      <span>Side <span class="pageNumber"></span> af <span class="totalPages"></span></span>
    </div>`;
  await page.pdf({
    path: path.resolve(__dirname, 'Dynamo_gennem_20_aar.pdf'),
    printBackground: true,
    format: 'A4',
    margin: { top: '24mm', bottom: '20mm', left: '22mm', right: '22mm' },
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate,
  });
  await browser.close();
  console.log('PDF written');
})();
