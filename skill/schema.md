# Pathbuilder JSON schema notes

This is an observed, permissive schema rather than a claim of an official Pathbuilder contract. A document is expected to be an object with a `build` object. `success` is retained but is not required because saved exports may omit it.

## Source layers

The normalized result separates:

- `raw`: a deep clone of the complete import, including unknown fields;
- normalized source inputs: identity, ability scores, rank bonuses, choices, inventory, and spell lists;
- `computed.pathbuilder`: values already calculated by Pathbuilder, such as AC and weapon attack/damage;
- future independently derived values, which must not replace Pathbuilder outputs.

Every normalized positional record and rich item object includes `source`, a deep clone of its original value.

## Positional arrays

### Feats

Observed order: `[name, selection, category, level, choiceTrack, choiceType, parentChoice]`. Trailing fields are optional. Preserve parent/child, Free Archetype, Combat Flexibility, and other choice-track metadata as supplied.

### Equipment

Observed core order: `[name, quantity, containerId?, investedMarker?]`. Some exports omit the container and place `"Invested"` in the third position. Normalization identifies the marker but retains the full positional source.

### Lores

Observed order: `[name, proficiencyRankBonus]`.

## Proficiency values

| Value | Rank |
| ---: | --- |
| 0 | untrained |
| 2 | trained |
| 4 | expert |
| 6 | master |
| 8 | legendary |

Unexpected numbers are retained with rank `unknown` and reported by validation.

## Weapons, armor, and shields

Weapon and armor entries are objects. `pot` is potency; weapon `str` is the striking tier; armor `res` is the resilient tier; `runes` contains property runes. A shield may occur in `armor` with `prof: "shield"`, so normalization separates it into `shields` without losing the source record.

`display` is presentation data. Dedicated fields win when they disagree. `attack`, `damageBonus`, `extraDamage`, and `acTotal` are imported Pathbuilder computations.

Specific proficiency is supplied separately under `specificProficiencies.{trained,expert,master,legendary}`. Match names exactly and expose the matching rank on weapons without replacing their general `prof` category.

## Spellcasting

Each `spellCasters` entry is independent and may describe class, archetype, item, or innate casting. Normalize `magicTradition`, `spellcastingType`, `perDay`, `spells`, `prepared`, and `innate` independently.

For spontaneous entries, `spells` is exposed as `repertoire`. For prepared entries, it is exposed as `knownOrAvailable`; its exact meaning depends on the casting source. `preparationModel` is inferred only from explicit source metadata or conservative class/source hints and otherwise remains `unknown`.

Focus spell data is separate under `focus[tradition][ability]`, with focus cantrips, focus spells, bonuses, and proficiency. Global `focusPoints` is retained.

## Secondary systems

- `rituals`: strings; normalize to `{name, source}` without inventing checks or rank.
- `resistances`: presentation strings; retain `raw`, and parse a simple trailing integer when possible.
- `formula`: objects such as `{type, known}`; preserve unknown keys.
- `mods`: nested maps of target to modifier label/value.
- `familiars` and `pets`: permissive records. `pets` includes animal companions and other pets because the export may not label the subtype consistently.
- `equipmentContainers`: map keyed by Pathbuilder IDs; preserve IDs and all properties.
- `inventorMods`, `specials`, `money`, ability breakdowns, and all unrecognized fields remain available in `raw`.
