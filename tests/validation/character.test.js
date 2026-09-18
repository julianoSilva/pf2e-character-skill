import test from "node:test";
import assert from "node:assert/strict";
import { normalizeCharacter, validateCharacter } from "../../src/index.js";

test("reports unknown proficiency encodings", () => {
  const character = normalizeCharacter({ build: { name: "Odd", proficiencies: { arcana: 3 } } });
  assert.ok(validateCharacter(character).some((item) => item.code === "unknown_proficiency"));
});

test("does not treat prepared spells absent from known list as invalid", () => {
  const character = normalizeCharacter({ build: { name: "Prepared", spellCasters: [{ name: "Cleric", spellcastingType: "prepared", proficiency: 2, spells: [], prepared: [{ spellLevel: 2, list: ["Heal"] }] }] } });
  const diagnostics = validateCharacter(character);
  assert.ok(diagnostics.some((item) => item.code === "unknown_preparation_model"));
  assert.ok(!diagnostics.some((item) => item.code === "unknown_prepared_spell"));
});
