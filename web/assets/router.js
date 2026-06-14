export function normalizeRoute(hash, validRoutes, fallback = "overview") {
  const route = String(hash || "").replace(/^#/, "");
  return validRoutes.includes(route) ? route : fallback;
}

export function routeHref(route) {
  return `#${route}`;
}
