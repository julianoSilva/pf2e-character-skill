---
name: pf2e-character
description: Read, normalize, explain, and validate Pathfinder 2e characters from Pathbuilder JSON. Use for PF2e character-sheet questions, audits, or controlled edits; do not claim Pathbuilder re-import compatibility.
---

# PF2e Character

Treat the supplied Pathbuilder export as source evidence. Preserve it unchanged, normalize only fields whose observed meaning is documented, and retain unknown data rather than rejecting it.

## Workflow

1. Parse the entire export with `src/parser/pathbuilder.js`.
2. Normalize it with `src/normalize/character.js` before explaining or comparing sections.
3. Read [schema.md](schema.md) when interpreting Pathbuilder fields or extending coverage.
4. Read [normalization.md](normalization.md) before calculating values, validating mechanics, or editing normalized data.
5. Run structural validation locally. For mechanical legality or current rules text, consult the current Pathfinder Second Edition Remaster entry on [Archives of Nethys](https://2e.aonprd.com/). Distinguish imported facts, independently derived values, and rules-source findings.

## Constraints

- Never overwrite or discard raw Pathbuilder values.
- Treat proficiency integers as rank bonuses: `0` untrained, `2` trained, `4` expert, `6` master, `8` legendary.
- Prefer dedicated structured fields over presentation strings such as `display`.
- Do not infer that a character lacks magic from class alone; inspect every spellcasting entry.
- Do not infer signature spells when the export does not identify them.
- Do not validate a prepared spell solely by membership in `spellCasters[].spells`. Resolve whether the source uses full-list access, a spellbook/learned collection, or an unknown preparation model.
- Treat `attack`, `damageBonus`, and `acTotal` as Pathbuilder-computed outputs, not independently proven values.
- Do not invent missing ritual statistics, companion mechanics, familiar abilities, or resistance exceptions.
- Report uncertainty when an observed field is incomplete or ambiguous.
- Do not emit Pathbuilder-compatible JSON unless compatibility has been separately tested.

## Editing

Make controlled edits to a copy of normalized data. Keep the raw import available for provenance and show what changed. Validate the result structurally and, when the change depends on game legality, against Archives of Nethys. Do not silently write changes back to Pathbuilder.
