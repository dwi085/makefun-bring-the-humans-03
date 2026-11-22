#!/usr/bin/env node
// bring-the-humans-03 entrypoint: copy VIDEO.json to the output directory.
//
// The grader runs this file as `node /bot/main.ts` from an arbitrary working
// directory, so nothing here may depend on process.cwd(). The bot directory
// comes from MAKEFUN_BOT_DIR (default "/bot") and the output directory from
// MAKEFUN_OUTPUT_DIR (default "/output").

const fs = require("node:fs");
const path = require("node:path");

function fail(message) {
  console.error("error: " + message);
  process.exit(1);
}

function main() {
  const botDir = process.env.MAKEFUN_BOT_DIR || "/bot";
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const srcPath = path.join(botDir, "VIDEO.json");
  const dstPath = path.join(outDir, "VIDEO.json");

  let raw;
  try {
    raw = fs.readFileSync(srcPath);
  } catch (err) {
    fail("cannot read " + srcPath + ": " + err.message);
  }

  let data;
  try {
    data = JSON.parse(raw.toString("utf8"));
  } catch (err) {
    fail("VIDEO.json is not valid JSON: " + err.message);
  }

  if (data === null || typeof data !== "object" || Array.isArray(data)) {
    fail("VIDEO.json must be a JSON object");
  }

  if (typeof data.url !== "string" || !data.url.startsWith("https://www.tiktok.com/") || !data.url.includes("/video/")) {
    fail("VIDEO.json must have a \"url\" string for a TikTok video starting with https://www.tiktok.com/ and containing /video/");
  }

  try {
    fs.mkdirSync(outDir, { recursive: true });
  } catch (err) {
    fail("cannot create output directory " + outDir + ": " + err.message);
  }

  try {
    fs.copyFileSync(srcPath, dstPath);
  } catch (err) {
    fail("cannot copy " + srcPath + " to " + dstPath + ": " + err.message);
  }

  let copied;
  try {
    copied = fs.readFileSync(dstPath);
  } catch (err) {
    fail("cannot read back " + dstPath + ": " + err.message);
  }

  if (!raw.equals(copied)) {
    fail("copied VIDEO.json differs from the original");
  }

  console.log("copied VIDEO.json to " + dstPath + " (" + data.url + ")");
}

main();
