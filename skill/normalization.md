# Normalization and validation

## Lossless import

Parsing accepts JSON text or an object. It rejects invalid JSON, non-object roots, and documents without a `build` object. It never mutates the caller's object. The full import is deep-cloned into `raw`; unknown additions therefore pass through automatically.

Normalization is intentionally conservative. Missing arrays and objects become empty normalized collections, while the source stays untouched. Positional records expose named fields plus their original value.

## Preparation models

`prepared` means the spells currently prepared. It does not establish the legal preparation pool.

- `full-list`: the caster can normally prepare common spells from its full list plus other spells it has legitimately learned or accessed.
- `spellbook`: preparation is limited by a learned collection such as a spellbook.
- `unknown`: the export does not contain enough reliable information.

The normalizer respects an explicit `preparationModel`. It recognizes conservative spellbook hints such as Wizard and Magus but does not maintain a comprehensive class rules database. Mechanical validation must resolve the casting source through Archives of Nethys. Never flag a prepared spell merely because it is absent from the exported `spells` list.

## Validation levels

Local validation is structural and provenance-aware: errors identify unusable normalized data; warnings identify unexpected encodings; informational diagnostics identify uncertainty requiring a current rules lookup.

Rules validation is deliberately external. Look up current Remaster rules on Archives of Nethys for feats, spells, items, runes, proficiencies, companions, familiars, rituals, formulas, and derived-stat formulas. Record the rule URL and do not silently substitute legacy or remembered text.

## Calculations

Keep source inputs, Pathbuilder computations, and independently derived expectations distinct. When reconstructing a value, show both imported and derived values and explain differences. Do not parse `display` when a dedicated field exists. Do not assume an item name, property rune string, or resistance string has complete mechanical detail.
