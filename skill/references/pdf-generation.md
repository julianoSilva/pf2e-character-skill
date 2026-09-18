# Dynamic fillable PDF generation

Use `scripts/generate_sheet.py INPUT OUTPUT` after parsing and normalizing a Pathbuilder export. The input is the normalized character object, not the raw Pathbuilder document.

## Design contract

- US Letter is the default; `--paper a4` is supported.
- The visual language is inspired by Paizo's Remaster sheet: dark-green section rules, burgundy accents, compact statistic boxes, and proficiency pips. Do not copy logos or proprietary artwork.
- Core statistics always occupy page one.
- Advancement, inventory, spellcasting, companions/familiars, and crafting/ritual sections are emitted only when useful and repeat across overflow pages.
- Each spellcasting source gets its own page so prepared, spontaneous, innate, and focus data are not conflated.
- All interactive field names are stable paths into the normalized model. Repeated values are suffixed by their normalized array index.
- Imported Pathbuilder computations are labeled as imported values. The PDF generator does not independently certify their legality.

## Output modes

Interactive output is the default. Use `--flatten` only for a print/archive copy. Keep an interactive copy whenever later edits may be required.

## Verification

After generation, reopen the PDF and verify canonical fields, page widgets, appearance streams, and rendered layout. Flattened output must contain neither a field tree nor widget annotations.
