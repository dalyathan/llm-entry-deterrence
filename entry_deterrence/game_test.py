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

"""Tests for the payoff table and game-theoretic benchmark."""

from absl.testing import absltest

from entry_deterrence import game as game_lib

# The capacity-commitment game: monopoly (M) or excess (C) capacity, then enter
# (E) or not (N).
_GAME = game_lib.SequentialGame(
    leader='incumbent',
    follower='entrant',
    leader_options=('M', 'C'),
    follower_options=('E', 'N'),
    payoffs={
        ('M', 'E'): (2, 1),
        ('M', 'N'): (4, 0),
        ('C', 'E'): (1, -1),
        ('C', 'N'): (3, 0),
    },
)


def _reverse(game):
  return game_lib.SequentialGame(
      leader=game.follower,
      follower=game.leader,
      leader_options=game.follower_options,
      follower_options=game.leader_options,
      payoffs={(f, l): (fp, lp) for (l, f), (lp, fp) in game.payoffs.items()},
  )


class SequentialGameTest(absltest.TestCase):

  def test_subgame_perfect_equilibrium_deters_entry(self):
    spe = _GAME.subgame_perfect()
    self.assertEqual(spe.leader_choice, 'C')
    self.assertEqual(dict(spe.follower_plan), {'M': 'E', 'C': 'N'})
    self.assertEqual(dict(spe.payoffs), {'incumbent': 3, 'entrant': 0})

  def test_nash_equilibria_include_the_non_credible_threat(self):
    found = {
        (eq.leader_choice, tuple(sorted(eq.follower_plan.items())))
        for eq in _GAME.nash_equilibria()
    }
    self.assertEqual(
        found,
        {
            ('M', (('C', 'E'), ('M', 'E'))),
            ('C', (('C', 'N'), ('M', 'E'))),
        },
    )

  def test_only_the_always_enter_plan_is_a_non_credible_threat(self):
    (threat,) = _GAME.non_credible_threats()
    self.assertEqual(threat.leader_choice, 'M')
    self.assertEqual(dict(threat.follower_plan), {'M': 'E', 'C': 'E'})

  def test_reversing_the_order_of_moves_removes_deterrence(self):
    spe = _reverse(_GAME).subgame_perfect()
    self.assertEqual(spe.leader_choice, 'E')
    self.assertEqual(dict(spe.follower_plan), {'E': 'M', 'N': 'M'})
    self.assertEqual(dict(spe.payoffs), {'entrant': 1, 'incumbent': 2})

  def test_costly_capacity_flips_the_equilibrium(self):
    costly = game_lib.SequentialGame(
        leader='incumbent',
        follower='entrant',
        leader_options=('M', 'C'),
        follower_options=('E', 'N'),
        payoffs={
            ('M', 'E'): (2, 1),
            ('M', 'N'): (4, 0),
            ('C', 'E'): (0, -1),
            ('C', 'N'): (1, 0),
        },
    )
    self.assertEqual(costly.subgame_perfect().leader_choice, 'M')

  def test_ties_are_rejected(self):
    tied = game_lib.SequentialGame(
        leader='a',
        follower='b',
        leader_options=('x', 'y'),
        follower_options=('p', 'q'),
        payoffs={
            ('x', 'p'): (1, 1),
            ('x', 'q'): (1, 1),
            ('y', 'p'): (0, 0),
            ('y', 'q'): (0, 1),
        },
    )
    with self.assertRaisesRegex(ValueError, 'Tie'):
      tied.subgame_perfect()

  def test_missing_payoffs_are_rejected(self):
    with self.assertRaisesRegex(ValueError, 'every'):
      game_lib.SequentialGame(
          leader='a',
          follower='b',
          leader_options=('x',),
          follower_options=('p', 'q'),
          payoffs={('x', 'p'): (1, 1)},
      )


if __name__ == '__main__':
  absltest.main()
