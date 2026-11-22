// main.ts — bring-the-humans-03 entrypoint (Node 22, stdlib only).
// Copies VIDEO.json from the repository root into the output directory
// so the grader can read the submitted TikTok video address.

import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
} from "node:fs";
import { join } from "node:path";

// The grader runs this with the repository as the working directory and
// hands it the output directory through MAKEFUN_OUTPUT_DIR; /output is
// the default when that variable is not set.
const repoRoot = process.cwd();
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const sourcePath = join(repoRoot, "VIDEO.json");
const targetPath = join(outputDir, "VIDEO.json");

if (!existsSync(sourcePath)) {
  console.error(`VIDEO.json not found at ${sourcePath}`);
  process.exit(1);
}

const raw = readFileSync(sourcePath, "utf8");

let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch {
  console.error("VIDEO.json is not valid JSON");
  process.exit(1);
}

if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
  console.error("VIDEO.json must be a JSON object with a url field");
  process.exit(1);
}

const url = (parsed as Record<string, unknown>).url;
if (typeof url !== "string" || !url.startsWith("https://www.tiktok.com/")) {
  console.error("VIDEO.json url must start with https://www.tiktok.com/");
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourcePath, targetPath);

// Read the copy back and make sure it landed byte for byte: a silent
// failed copy would hand the grader an empty or stale /output.
const written = readFileSync(targetPath, "utf8");
if (written !== raw) {
  console.error(`Verification failed: ${targetPath} differs from VIDEO.json`);
  process.exit(1);
}

console.log(`Copied VIDEO.json to ${targetPath} (${url})`);
console.log(`Verified ${targetPath} matches VIDEO.json byte for byte`);
