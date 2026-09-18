import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { parsePathbuilder, PathbuilderParseError } from "../../src/index.js";

test("parses a real Pathbuilder export", async () => {
  const input = await readFile(new URL("../../fixtures/faeldraen.json", import.meta.url), "utf8");
  const result = parsePathbuilder(input);
  assert.equal(result.success, true);
  assert.ok(result.build.name);
});

test("clones object input and rejects unusable documents", () => {
  const input = { build: { name: "Clone" } };
  const parsed = parsePathbuilder(input);
  parsed.build.name = "Changed";
  assert.equal(input.build.name, "Clone");
  assert.throws(() => parsePathbuilder("{"), PathbuilderParseError);
  assert.throws(() => parsePathbuilder({ success: true }), /build object/);
});
