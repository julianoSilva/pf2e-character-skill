# PF2e Character Skill

A reusable Codex skill and small, dependency-free JavaScript library for reading current Pathbuilder 2e JSON exports without losing source data.

The first release focuses on import, normalization, explanation-ready data, and structural validation. It does **not** promise Pathbuilder-compatible export. Mechanical validation must resolve current Pathfinder Second Edition Remaster rules through [Archives of Nethys](https://2e.aonprd.com/) rather than embedding a stale rules database.

## Layout

- `skill/SKILL.md` — skill entry point
- `skill/schema.md` — observed Pathbuilder structures and normalized model
- `skill/normalization.md` — normalization and validation decisions
- `src/` — parser, normalizer, and validator library
- `fixtures/` — real and focused compatibility samples
- `tests/` — Node test-runner coverage

## Use

```js
import { parsePathbuilder, normalizeCharacter, validateCharacter } from "./src/index.js";

const parsed = parsePathbuilder(jsonText);
const character = normalizeCharacter(parsed);
const diagnostics = validateCharacter(character);
```

Run the suite with Node 20 or newer:

```sh
node --test
```

The normalized result includes a deep-cloned `raw` source document. Unknown fields remain there and are also preserved on normalized records through `source`, allowing the reader to tolerate Pathbuilder additions.
