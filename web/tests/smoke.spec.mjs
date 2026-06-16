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

const baseUrl = process.env.BASE_URL || "http://localhost:4173";

await page.goto(`${baseUrl}/`, { waitUntil: "networkidle0" });
if (!(await page.$eval("h1", (node) => node.textContent)).includes("safer triage")) {
  throw new Error("Landing heading did not load");
}

await page.goto(`${baseUrl}/assessment.html`, { waitUntil: "networkidle0" });
await page.select("#case-select", "SYNTH-LOW-UNCERTAINTY");
await page.click('button[type="submit"]');
await page.waitForFunction(
  () => document.querySelector("#assessment-result")?.textContent?.trim().length > 0
);

const prototypeStates = [
  {
    route: "/prototype.html?case=SYNTH-LOW-UNCERTAINTY&stage=assessment",
    selector: "#prototype-probabilities .prototype-probability",
    text: "frozen-test positives",
  },
  {
    route: "/prototype.html?case=SYNTH-MISSING&stage=decision",
    selector: "#prototype-decision",
    text: "Clinical review required",
  },
  {
    route: "/prototype.html?case=SYNTH-OOD&stage=response",
    selector: "#prototype-response",
    text: "beyond entered capacity",
  },
];
for (const state of prototypeStates) {
  await page.goto(`${baseUrl}${state.route}`, { waitUntil: "networkidle0" });
  await page.waitForFunction(
    (selector, text) => document.querySelector(selector)?.textContent?.includes(text),
    {},
    state.selector,
    state.text,
  );
  const caption = await page.$eval("#stage-caption", (node) => node.textContent);
  if (!caption.includes("What this demonstrates")) {
    throw new Error(`Report caption missing for ${state.route}`);
  }
}

await page.goto(
  `${baseUrl}/prototype.html?case=SYNTH-LOW-UNCERTAINTY&stage=intake`,
  { waitUntil: "networkidle0" },
);
await page.keyboard.press("Tab");
const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
if (focusedTag !== "A") throw new Error("Keyboard focus did not reach the skip link");

const failurePage = await browser.newPage();
await failurePage.setRequestInterception(true);
failurePage.on("request", (request) => {
  if (request.url().endsWith("/api/assess")) {
    request.respond({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ error: "Synthetic smoke-test API failure" }),
    });
  } else {
    request.continue();
  }
});
await failurePage.goto(
  `${baseUrl}/prototype.html?case=SYNTH-LOW-UNCERTAINTY&stage=assessment`,
  { waitUntil: "networkidle0" },
);
await failurePage.waitForFunction(
  () => document.querySelector("#assessment-status")?.textContent?.includes("Assessment unavailable"),
);
await failurePage.close();

await page.goto(`${baseUrl}/dashboard.html#executive`, { waitUntil: "networkidle0" });
const routeKeys = await page.$$eval("[data-route]", (nodes) => nodes.map((node) => node.dataset.route));
for (const route of routeKeys) {
  await page.click(`[data-route="${route}"]`);
  await page.waitForFunction((expected) => location.hash === `#${expected}`, {}, route);
}
await page.goBack();
await new Promise((resolve) => setTimeout(resolve, 50));

await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
await page.goto(
  `${baseUrl}/prototype.html?case=SYNTH-MISSING&stage=decision`,
  { waitUntil: "networkidle0" },
);
const mobileOverflow = await page.evaluate(
  () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
);
if (mobileOverflow) throw new Error("Prototype has horizontal overflow on mobile");
await page.goto(`${baseUrl}/dashboard.html#executive`, { waitUntil: "networkidle0" });
await page.click("#open-menu");
if (!(await page.$eval("#sidebar", (node) => node.classList.contains("open")))) {
  throw new Error("Mobile drawer did not open");
}
await page.click("#close-menu");

await browser.close();
if (errors.length) throw new Error(`Browser console errors:\n${errors.join("\n")}`);
console.log(
  `Smoke checks passed across ${routeKeys.length} dashboard routes and ${prototypeStates.length} deterministic prototype states.`,
);
