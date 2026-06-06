import { existsSync, mkdirSync, copyFileSync, rmSync, readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));
const requiredFiles = ["index.html", "src/main.js", "src/styles.css"];
const checkOnly = process.argv.includes("--check-only");

for (const file of requiredFiles) {
  const path = join(projectRoot, file);
  if (!existsSync(path)) {
    throw new Error(`Missing required web file: ${file}`);
  }
}

if (checkOnly) {
  console.log("Signbridge web files are present.");
  process.exit(0);
}

const distDir = join(projectRoot, "dist");
rmSync(distDir, { recursive: true, force: true });
mkdirSync(distDir, { recursive: true });
copyRecursive(join(projectRoot, "index.html"), join(distDir, "index.html"));
copyRecursive(join(projectRoot, "src"), join(distDir, "src"));

console.log(`Built Signbridge web app to ${distDir}`);

function copyRecursive(from, to) {
  const stat = statSync(from);
  if (stat.isDirectory()) {
    mkdirSync(to, { recursive: true });
    for (const entry of readdirSync(from)) {
      copyRecursive(join(from, entry), join(to, entry));
    }
    return;
  }

  mkdirSync(dirname(to), { recursive: true });
  copyFileSync(from, to);
}
