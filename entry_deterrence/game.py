# Copyright 2026 Surafel Tariku.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Payoffs and the game-theoretic benchmark for a two-move sequential game.

A leader chooses one of its options and the follower, having seen that choice,
chooses one of its own. This module holds the payoff table and computes what
fully rational players would do, so that simulated play can be compared with
theory:

  * the subgame perfect equilibrium, found by backward induction, and
  * every pure-strategy Nash equilibrium of the strategic form, in which a
    follower strategy is a plan saying what it does after each leader move.

A Nash equilibrium that is not subgame perfect relies on a non-credible
threat: a planned response the follower would not want to carry out if the
leader called its bluff.
"""

from collections.abc import Mapping, Sequence
import dataclasses
import itertools

# A follower plan maps each leader option to the follower's response.
Plan = Mapping[str, str]


@dataclasses.dataclass(frozen=True)
class Equilibrium:
  """A pure-strategy equilibrium of the strategic form.

  Attributes:
    leader_choice: The option the leader chooses.
    follower_plan: The follower's response to each leader option.
    payoffs: The payoffs on the path played, keyed by player name.
  """

  leader_choice: str
  follower_plan: Plan
  payoffs: Mapping[str, float]


@dataclasses.dataclass(frozen=True)
class SequentialGame:
  """A two-player game in which the leader moves first and is observed.

  Attributes:
    leader: Name of the player who moves first.
    follower: Name of the player who moves second.
    leader_options: The leader's options.
    follower_options: The follower's options.
    payoffs: Payoffs for every pair of choices, keyed by (leader option,
      follower option), as (leader payoff, follower payoff).
  """

  leader: str
  follower: str
  leader_options: Sequence[str]
  follower_options: Sequence[str]
  payoffs: Mapping[tuple[str, str], tuple[float, float]]

  def __post_init__(self):
    expected = set(
        itertools.product(self.leader_options, self.follower_options)
    )
    if set(self.payoffs) != expected:
      raise ValueError(
          'Payoffs must cover every (leader option, follower option) pair.'
      )

  def score(self, leader_choice: str, follower_choice: str) -> dict[str, float]:
    """Returns each player's payoff for a pair of choices."""
    leader_payoff, follower_payoff = self.payoffs[
        (leader_choice, follower_choice)
    ]
    return {self.leader: leader_payoff, self.follower: follower_payoff}

  def best_response(self, leader_choice: str) -> str:
    """Returns the follower's payoff-maximizing reply to a leader choice.

    Raises:
      ValueError: If two replies tie, since the benchmark is then ambiguous.
    """
    values = {
        option: self.payoffs[(leader_choice, option)][1]
        for option in self.follower_options
    }
    return _unique_argmax(values, f'follower after {leader_choice!r}')

  def subgame_perfect(self) -> Equilibrium:
    """Returns the subgame perfect equilibrium, by backward induction."""
    plan = {
        choice: self.best_response(choice) for choice in self.leader_options
    }
    leader_values = {
        choice: self.payoffs[(choice, plan[choice])][0]
        for choice in self.leader_options
    }
    leader_choice = _unique_argmax(leader_values, 'leader')
    return Equilibrium(
        leader_choice=leader_choice,
        follower_plan=plan,
        payoffs=self.score(leader_choice, plan[leader_choice]),
    )

  def nash_equilibria(self) -> list[Equilibrium]:
    """Returns every pure-strategy Nash equilibrium of the strategic form."""
    plans = [
        dict(zip(self.leader_options, responses))
        for responses in itertools.product(
            self.follower_options, repeat=len(self.leader_options)
        )
    ]
    found = []
    for leader_choice, plan in itertools.product(self.leader_options, plans):
      leader_value = self.payoffs[(leader_choice, plan[leader_choice])][0]
      leader_ok = all(
          self.payoffs[(other, plan[other])][0] <= leader_value
          for other in self.leader_options
      )
      follower_value = self.payoffs[(leader_choice, plan[leader_choice])][1]
      follower_ok = all(
          self.payoffs[(leader_choice, other[leader_choice])][1]
          <= follower_value
          for other in plans
      )
      if leader_ok and follower_ok:
        found.append(
            Equilibrium(
                leader_choice=leader_choice,
                follower_plan=plan,
                payoffs=self.score(leader_choice, plan[leader_choice]),
            )
        )
    return found

  def non_credible_threats(self) -> list[Equilibrium]:
    """Returns the Nash equilibria whose follower plan is not credible.

    A plan is not credible when some response in it, on or off the path of
    play, is not the follower's best reply to that leader move.
    """
    return [
        eq
        for eq in self.nash_equilibria()
        if any(
            response != self.best_response(choice)
            for choice, response in eq.follower_plan.items()
        )
    ]


def _unique_argmax(values: Mapping[str, float], who: str) -> str:
  best = max(values.values())
  winners = [option for option, value in values.items() if value == best]
  if len(winners) > 1:
    raise ValueError(f'Tie for the {who}: {winners}.')
  return winners[0]
