import puppeteer from "puppeteer-core";

const browser = await puppeteer.launch({
  executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  headless: "new",
  args: ["--no-sandbox", "--disable-gpu"],
});

const errors = [];
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
page.on("console", (message) => {
  if (message.type() === "error") errors.push(message.text());
});
page.on("pageerror", (error) => errors.push(error.message));

await page.goto("http://localhost:3000/", { waitUntil: "networkidle0" });
if (!(await page.$eval("h1", (node) => node.textContent)).includes("safer triage")) {
  throw new Error("Landing heading did not load");
}

await page.goto("http://localhost:3000/demo.html", { waitUntil: "networkidle0" });
await page.click("#demo-next");
if (!(await page.$eval("#demo-counter", (node) => node.textContent)).includes("2 of 5")) {
  throw new Error("Guided demo did not advance");
}
await page.click("#demo-back");

await page.goto("http://localhost:3000/dashboard.html#overview", { waitUntil: "networkidle0" });
const routeKeys = await page.$$eval("[data-route]", (nodes) => nodes.map((node) => node.dataset.route));
for (const route of routeKeys) {
  await page.click(`[data-route="${route}"]`);
  await page.waitForFunction((expected) => location.hash === `#${expected}`, {}, route);
}
await page.goBack();
await new Promise((resolve) => setTimeout(resolve, 50));

await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await page.reload({ waitUntil: "networkidle0" });
await page.click("#open-menu");
if (!(await page.$eval("#sidebar", (node) => node.classList.contains("open")))) {
  throw new Error("Mobile drawer did not open");
}
await page.click("#close-menu");

await browser.close();
if (errors.length) throw new Error(`Browser console errors:\n${errors.join("\n")}`);
console.log(`Smoke checks passed across ${routeKeys.length} dashboard routes.`);
