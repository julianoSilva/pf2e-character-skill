import { clone } from "../parser/pathbuilder.js";
import { normalizeProficiency } from "../rules/proficiency.js";

const array = (value) => Array.isArray(value) ? value : [];
const object = (value) => value && typeof value === "object" && !Array.isArray(value) ? value : {};

function rankMap(source) {
  return Object.fromEntries(Object.entries(object(source)).map(([key, value]) => [key, normalizeProficiency(value)]));
}

function normalizeFeat(value) {
  const row = array(value);
  return {
    name: row[0] ?? null,
    selection: row[1] ?? null,
    category: row[2] ?? null,
    level: row[3] ?? null,
    choiceTrack: row[4] ?? null,
    choiceType: row[5] ?? null,
    parentChoice: row[6] ?? null,
    source: clone(value),
  };
}

function normalizeEquipment(value) {
  const row = array(value);
  const thirdIsInvested = row[2] === "Invested";
  return {
    name: row[0] ?? null,
    quantity: row[1] ?? 1,
    containerId: thirdIsInvested ? null : row[2] ?? null,
    invested: thirdIsInvested || row[3] === "Invested",
    source: clone(value),
  };
}

function normalizeLore(value) {
  const row = array(value);
  return { name: row[0] ?? null, proficiency: normalizeProficiency(row[1]), source: clone(value) };
}

function specificRank(name, specific) {
  for (const rank of ["legendary", "master", "expert", "trained"]) {
    if (array(specific?.[rank]).includes(name)) return rank;
  }
  return null;
}

function normalizeWeapon(value, specific) {
  const item = object(value);
  return {
    name: item.name ?? null,
    quantity: item.qty ?? 1,
    proficiencyCategory: item.prof ?? null,
    specificProficiency: specificRank(item.name, specific),
    damageDie: item.die ?? null,
    damageType: item.damageType ?? null,
    potency: item.pot ?? null,
    striking: item.str ?? null,
    material: item.mat ?? null,
    propertyRunes: clone(array(item.runes)),
    grade: item.grade ?? null,
    computed: {
      attack: item.attack ?? null,
      damageBonus: item.damageBonus ?? null,
      extraDamage: clone(array(item.extraDamage)),
      increasedDice: item.increasedDice ?? null,
    },
    display: item.display ?? null,
    source: clone(value),
  };
}

function normalizeArmor(value) {
  const item = object(value);
  return {
    name: item.name ?? null,
    quantity: item.qty ?? 1,
    proficiencyCategory: item.prof ?? null,
    potency: item.pot ?? null,
    resilient: item.res ?? null,
    material: item.mat ?? null,
    propertyRunes: clone(array(item.runes)),
    worn: item.worn ?? null,
    grade: item.grade ?? null,
    display: item.display ?? null,
    source: clone(value),
  };
}

function spellsByRank(value) {
  return Object.fromEntries(array(value).map((entry) => [String(entry.spellLevel), clone(array(entry.list))]));
}

function preparationModel(caster) {
  if (caster.preparationModel) return caster.preparationModel;
  if (caster.spellcastingType !== "prepared" || caster.innate) return null;
  if (/wizard|magus/i.test(caster.name ?? "")) return "spellbook";
  return "unknown";
}

function normalizeCaster(value) {
  const caster = object(value);
  const spellLists = spellsByRank(caster.spells);
  const castingType = caster.spellcastingType ?? null;
  return {
    name: caster.name ?? null,
    tradition: caster.magicTradition ?? null,
    castingType,
    preparationModel: preparationModel(caster),
    ability: caster.ability ?? null,
    proficiency: normalizeProficiency(caster.proficiency),
    innate: Boolean(caster.innate),
    focusPoints: caster.focusPoints ?? 0,
    slotsPerDay: Object.fromEntries(array(caster.perDay).map((count, rank) => [String(rank), count])),
    repertoire: castingType === "spontaneous" ? spellLists : {},
    knownOrAvailable: castingType === "spontaneous" ? {} : spellLists,
    prepared: spellsByRank(caster.prepared),
    blendedSpells: clone(array(caster.blendedSpells)),
    source: clone(value),
  };
}

function normalizeFocus(value) {
  const result = [];
  for (const [tradition, abilities] of Object.entries(object(value))) {
    for (const [ability, record] of Object.entries(object(abilities))) {
      result.push({
        tradition,
        ability,
        abilityBonus: record.abilityBonus ?? null,
        proficiency: normalizeProficiency(record.proficiency),
        itemBonus: record.itemBonus ?? null,
        cantrips: clone(array(record.focusCantrips)),
        spells: clone(array(record.focusSpells)),
        source: clone(record),
      });
    }
  }
  return result;
}

function normalizeResistance(value) {
  const raw = String(value);
  const match = raw.match(/^(.+?)\s+(\d+)$/);
  return { raw, type: match?.[1] ?? null, value: match ? Number(match[2]) : null };
}

function normalizeContainers(value) {
  return Object.fromEntries(Object.entries(object(value)).map(([id, record]) => [id, { id, ...clone(record), source: clone(record) }]));
}

export function normalizeCharacter(document) {
  const raw = clone(document);
  const build = object(document.build);
  const specific = object(build.specificProficiencies);
  const armorRecords = array(build.armor).map(normalizeArmor);

  return {
    format: "pathbuilder-2e",
    raw,
    identity: {
      name: build.name ?? null, class: build.class ?? null, dualClass: build.dualClass ?? null,
      level: build.level ?? null, xp: build.xp ?? null, ancestry: build.ancestry ?? null,
      heritage: build.heritage ?? null, background: build.background ?? null,
      alignment: build.alignment ?? null, gender: build.gender ?? null, age: build.age ?? null,
      deity: build.deity ?? null, size: build.size ?? null, sizeName: build.sizeName ?? null,
      keyAbility: build.keyability ?? null, languages: clone(array(build.languages)),
    },
    abilities: clone(object(build.abilities)),
    attributes: clone(object(build.attributes)),
    proficiencies: rankMap(build.proficiencies),
    specificProficiencies: clone(specific),
    feats: array(build.feats).map(normalizeFeat),
    specials: clone(array(build.specials)),
    lores: array(build.lores).map(normalizeLore),
    inventory: {
      containers: normalizeContainers(build.equipmentContainers),
      equipment: array(build.equipment).map(normalizeEquipment),
      money: clone(object(build.money)),
    },
    weapons: array(build.weapons).map((weapon) => normalizeWeapon(weapon, specific)),
    armor: armorRecords.filter((item) => item.proficiencyCategory !== "shield"),
    shields: armorRecords.filter((item) => item.proficiencyCategory === "shield"),
    spellcasting: array(build.spellCasters).map(normalizeCaster),
    focus: { points: build.focusPoints ?? 0, entries: normalizeFocus(build.focus) },
    rituals: array(build.rituals).map((name) => ({ name, source: clone(name) })),
    resistances: array(build.resistances).map(normalizeResistance),
    formulas: array(build.formula).map((formula) => ({ ...clone(object(formula)), source: clone(formula) })),
    modifiers: clone(object(build.mods)),
    familiars: array(build.familiars).map((entry) => ({ data: clone(entry), source: clone(entry) })),
    companions: array(build.pets).map((entry) => ({ data: clone(entry), source: clone(entry) })),
    inventorMods: clone(array(build.inventorMods)),
    computed: { pathbuilder: { ac: clone(build.acTotal ?? null) } },
  };
}
