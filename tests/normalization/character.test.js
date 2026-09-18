import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { normalizeCharacter, parsePathbuilder } from "../../skill/src/index.js";

async function coverage() {
  const text = await readFile(new URL("../../fixtures/feature-coverage.json", import.meta.url), "utf8");
  return normalizeCharacter(parsePathbuilder(text));
}

test("preserves unknown fields and maps proficiency ranks", async () => {
  const character = await coverage();
  assert.equal(character.raw.exportRevision, "unknown-fields-must-survive");
  assert.deepEqual(character.raw.build.futureBuildField, { kept: true });
  assert.deepEqual(character.proficiencies.arcana, { rankBonus: 6, rank: "master" });
  assert.equal(character.lores[0].proficiency.rank, "expert");
});

test("normalizes positional feats, equipment, and item mechanics", async () => {
  const character = await coverage();
  assert.equal(character.feats[1].choiceType, "childChoice");
  assert.equal(character.feats[1].parentChoice, "Human Feat 1");
  assert.equal(character.inventory.equipment[0].containerId, "bag-1");
  assert.equal(character.inventory.equipment[1].invested, true);
  assert.equal(character.weapons[0].specificProficiency, "expert");
  assert.equal(character.weapons[0].potency, 1);
  assert.equal(character.weapons[0].striking, "striking");
  assert.deepEqual(character.weapons[0].propertyRunes, ["Flaming"]);
  assert.equal(character.shields[0].name, "Steel Shield");
});

test("keeps spellcasting modes and focus magic distinct", async () => {
  const character = await coverage();
  assert.equal(character.spellcasting[0].preparationModel, "spellbook");
  assert.deepEqual(character.spellcasting[0].prepared["4"], ["Fly"]);
  assert.deepEqual(character.spellcasting[1].repertoire["1"], ["Heal"]);
  assert.equal(character.spellcasting[2].innate, true);
  assert.equal(character.focus.entries[0].spells[0], "Hand of the Apprentice");
});

test("normalizes secondary systems without inventing detail", async () => {
  const character = await coverage();
  assert.deepEqual(character.resistances[0], { raw: "fire 4", type: "fire", value: 4 });
  assert.equal(character.resistances[1].value, null);
  assert.equal(character.rituals[0].name, "Consecrate");
  assert.equal(character.formulas[0].futureFormulaField, true);
  assert.equal(character.companions[0].data.name, "Wolf");
  assert.equal(character.familiars[0].data.name, "Moth");
  assert.equal(character.computed.pathbuilder.ac.acTotal, 23);
});
