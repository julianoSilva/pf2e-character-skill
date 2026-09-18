#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { parsePathbuilder, normalizeCharacter } from "../src/index.js";

const [input, output] = process.argv.slice(2);
if (!input || !output) {
  console.error("Usage: node normalize.mjs PATHBUILDER.json NORMALIZED.json");
  process.exit(2);
}

const raw = await readFile(input, "utf8");
const normalized = normalizeCharacter(parsePathbuilder(raw));
await writeFile(output, `${JSON.stringify(normalized, null, 2)}\n`, "utf8");
