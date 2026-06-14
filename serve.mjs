import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const root = join(import.meta.dirname, "web");
const port = Number(process.env.PORT || 3000);
const types = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

createServer((request, response) => {
  const urlPath = new URL(request.url, `http://${request.headers.host}`).pathname;
  if (urlPath === "/favicon.ico") {
    response.writeHead(204);
    response.end();
    return;
  }
  const relative = urlPath === "/" ? "index.html" : urlPath.replace(/^\/+/, "");
  let target = normalize(join(root, relative));
  if (!target.startsWith(root) || !existsSync(target)) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }
  if (statSync(target).isDirectory()) target = join(target, "index.html");
  response.writeHead(200, {
    "Content-Type": types[extname(target)] || "application/octet-stream",
    "Cache-Control": "no-store",
  });
  createReadStream(target).pipe(response);
}).listen(port, "127.0.0.1", () => {
  console.log(`VECTRA-X web server listening on http://localhost:${port}`);
});
