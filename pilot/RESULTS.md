# Entry-deterrence pilot — 14 Nov 2026

Run on 14 Nov 2026.

## Setup
- Game: `entry_deterrence/` (incumbent M/C, then entrant E/N).
  Payoffs (incumbent, entrant): M,E (2,1); M,N (4,0); C,E (1,-1); C,N (3,0).
- Benchmarks verified with pygambit 16.7 (logit/QRE-limit selection): SPE
  matches in all three payoff scenarios; Nash-equilibrium counts match (2, 3, 2).
  Note: Gambit's `lcp_solve` returned a non-credible-threat NE in the reversed
  game — "any Nash solver" is not a valid SPE benchmark.
- Scripted (puppet) players reproduce {C,[E,N]} end to end in Concordia; 17 tests.
- LLM pilot: each decision by a separate fresh Claude agent (Haiku, Sonnet), using
  the same text Concordia gives players; option order and payoff-line order
  shuffled; game never named. Follower plan elicited with the strategy method
  (separate agent asked the off-path counterfactual).
- NOT run through Concordia's own entity/LLM loop (no Claude adapter here).

## Results (SPE-consistent / total)
| Condition | Leader | Follower (on path) | Follower (off path) |
|---|---|---|---|
| market | 2/2 expand | 2/2 stay out | 2/2 enter after keep |
| reversed order | 2/2 enter | 2/2 keep | 2/2 keep after stay-out |
| costly expansion (SPE flips) | 2/2 keep | 2/2 enter | 2/2 stay out after expand |
| abstract (no story) | 2/2 F | 2/2 Q | 2/2 P after J |
| security (defender/attacker) | 2/2 harden | 2/2 no attack | 2/2 attack after keep |
| cheap-talk threat (no expansion) | — | 2/2 enter (threat ignored) | — |

Total: 32/32 match the subgame perfect equilibrium; 0 non-credible plans.
Every leader reasoned explicitly by backward induction.

## Interpretation
- Ceiling effect: with an explicit payoff table and a 2-move tree, Claude models
  behave as textbook-rational players. The pilot cannot distinguish reasoning
  from recognition. This is a design limitation, not a finding about deterrence.
- Framing: no effect on choices. One Haiku attacker broke role and added a
  disclaimer ("not an endorsement of ransomware") before answering — a framing
  effect on *behaviour style*, worth logging.
- n = 1 per cell per model; one model family. No statistics possible.

## Next steps to make it informative
1. Run through Concordia itself (needs a model API key): other model families
   (Gemini/GPT/open models), many seeds, temperature > 0.
2. Remove the explicit payoff table: describe costs/demand in prose so players
   must compute payoffs.
3. Free-form threat scene (conversation) instead of a scripted line.
4. Deeper tree: chain-store game (one incumbent, several entrants, memory).
5. Compare with human data on entry/chain-store experiments.
