const VALID_RANK_BONUSES = new Set([0, 2, 4, 6, 8]);

const diagnostic = (severity, code, path, message) => ({ severity, code, path, message });

export function validateCharacter(character) {
  const diagnostics = [];
  if (!character || typeof character !== "object") {
    return [diagnostic("error", "invalid_character", "$", "Normalized character must be an object")];
  }
  if (!character.raw?.build) diagnostics.push(diagnostic("error", "missing_raw", "raw.build", "Lossless raw Pathbuilder build is required"));
  if (!character.identity?.name) diagnostics.push(diagnostic("warning", "missing_name", "identity.name", "Character name is missing"));

  for (const [name, proficiency] of Object.entries(character.proficiencies ?? {})) {
    if (!VALID_RANK_BONUSES.has(proficiency.rankBonus)) {
      diagnostics.push(diagnostic("warning", "unknown_proficiency", `proficiencies.${name}`, `Unexpected rank bonus ${String(proficiency.rankBonus)}`));
    }
  }
  for (const [index, feat] of (character.feats ?? []).entries()) {
    if (!feat.name) diagnostics.push(diagnostic("warning", "malformed_feat", `feats.${index}`, "Feat positional record has no name"));
  }
  for (const [index, caster] of (character.spellcasting ?? []).entries()) {
    if (caster.castingType === "prepared" && !caster.innate && caster.preparationModel === "unknown") {
      diagnostics.push(diagnostic("info", "unknown_preparation_model", `spellcasting.${index}`, "Resolve full-list versus learned-collection preparation from the casting source before validating spell legality"));
    }
  }
  return diagnostics;
}
