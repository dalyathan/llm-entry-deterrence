# LLM agents in an entry-deterrence game

Do language-model agents play strategic games the way game theory predicts?
This repo tests that with a classic two-move game: an incumbent firm decides
whether to expand capacity, then a potential entrant decides whether to enter.
It is built on Google DeepMind's
[Concordia](https://github.com/google-deepmind/concordia) library.

## The game

Payoffs (incumbent, entrant) in the baseline market scenario:

| Incumbent \ Entrant | Enter | Stay out |
|---|---|---|
| Keep capacity | (2, 1) | (4, 0) |
| Expand | (1, -1) | (3, 0) |

The subgame perfect equilibrium is for the incumbent to expand and for the
entrant to stay out after expansion but enter otherwise. A threat to start a
price war without expanding is not credible.

## What's here

- `entry_deterrence/` — the game as a Concordia simulation.
  - `game.py`: payoffs, best responses, subgame perfect and Nash equilibria,
    and non-credible threats.
  - `simulation.py`: two scenes (leader, then follower), each scored with
    Concordia's `PayoffMatrix` component.
  - `configs/`: five framings of the same game — market, reversed move order,
    costly expansion (the equilibrium flips), an abstract version with no
    story, and a security version (defender vs attacker).
  - Tests: 17, run with scripted (puppet) players, no API key needed.
- `pilot/` — a first pilot with Claude Haiku and Sonnet, the prompts used,
  and a Gambit cross-check of the equilibria. See
  [`pilot/RESULTS.md`](pilot/RESULTS.md).

## Pilot result

32 of 32 decisions matched the subgame perfect equilibrium, in every framing.
That is a ceiling effect: with an explicit payoff table and a two-move game,
the models may simply recognise a textbook problem. So the pilot shows the
setup works, not that the models reason strategically.

Next: hidden incumbent types with cheap talk, payoffs described in prose and
randomised, more model families, and comparison with human experiments.

## Running

Requires Python 3.12+.

```sh
pip install gdm-concordia pytest
python -m pytest entry_deterrence
```

`pilot/gambit_check.py` also needs `pygambit`.

## License

Apache 2.0. See [LICENSE](LICENSE).
