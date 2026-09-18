export const PROFICIENCY_RANKS = Object.freeze({
  0: "untrained",
  2: "trained",
  4: "expert",
  6: "master",
  8: "legendary",
});

export function normalizeProficiency(value) {
  return {
    rankBonus: value,
    rank: Object.hasOwn(PROFICIENCY_RANKS, value)
      ? PROFICIENCY_RANKS[value]
      : "unknown",
  };
}
