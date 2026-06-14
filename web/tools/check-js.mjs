import { readdir } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import path from "node:path";


const root = path.resolve(import.meta.dirname, "..");
const directories = ["assets", "tests", "tools"];
const files = [];
for (const directory of directories) {
  for (const entry of await readdir(path.join(root, directory), { withFileTypes: true })) {
    if (entry.isFile() && (entry.name.endsWith(".js") || entry.name.endsWith(".mjs"))) {
      files.push(path.join(root, directory, entry.name));
    }
  }
}
for (const file of files) {
  const result = spawnSync(process.execPath, ["--check", file], { stdio: "inherit" });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
console.log(`Checked ${files.length} JavaScript files.`);
