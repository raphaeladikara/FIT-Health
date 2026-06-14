export async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.json();
}

export async function loadBundle() {
  const [dashboard, cases, manifest] = await Promise.all([
    loadJson("data/dashboard.json"),
    loadJson("data/demo-cases.json"),
    loadJson("data/manifest.json"),
  ]);
  return { dashboard, cases, manifest };
}
