// Screenshot loop helper — drives system Chrome via puppeteer-core.
// Usage: node tools/shot.mjs <label> <route> [route2 ...]
//   node tools/shot.mjs baseline / /patients /resources /evidence /methodology
// Each route is captured at desktop (1440) + mobile (390) into tools/out/.
import puppeteer from "puppeteer-core";
import { mkdirSync } from "node:fs";

const CHROME =
  "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.SHOT_BASE || "http://localhost:3000";
const OUT = new URL("./out/", import.meta.url).pathname.replace(/^\//, "");

const label = process.argv[2] || "shot";
const routes = process.argv.slice(3);
if (routes.length === 0) routes.push("/");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

const slug = (r) =>
  r === "/" ? "home" : r.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "");

mkdirSync(OUT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"],
});

for (const route of routes) {
  for (const vp of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport({ width: vp.width, height: vp.height, deviceScaleFactor: 1 });
    const url = `${BASE}${route}`;
    try {
      await page.goto(url, { waitUntil: "networkidle0", timeout: 30000 });
      // settle charts / fonts
      await new Promise((r) => setTimeout(r, 600));
      const file = `${OUT}${label}__${slug(route)}__${vp.name}.png`;
      await page.screenshot({ path: file, fullPage: vp.name === "desktop" });
      console.log(`✓ ${url} (${vp.name}) -> ${file}`);
    } catch (err) {
      console.error(`✗ ${url} (${vp.name}): ${err.message}`);
    } finally {
      await page.close();
    }
  }
}

await browser.close();
