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

"""Tests that the entry deterrence game plays as designed (no LLM).

Players run on scripted models that record every prompt they receive, so the
tests can check what each player knew when it chose.
"""

import re
import threading

from absl.testing import absltest
from concordia.language_model import language_model
from concordia.language_model import no_language_model
import numpy as np

from entry_deterrence import simulation
from entry_deterrence.configs import market
from entry_deterrence.configs import market_costly_expansion
from entry_deterrence.configs import market_reversed_order
from entry_deterrence.configs import puppet


def _mock_embedder(text: str) -> np.ndarray:
  del text
  return np.ones(3)


class _ScriptedModel(language_model.LanguageModel):
  """Picks the first preferred option offered and records every prompt."""

  def __init__(self, preferences):
    self._preferences = list(preferences)
    self._lock = threading.Lock()
    self.choice_prompts: list[str] = []

  def sample_text(self, prompt, **kwargs):
    del prompt, kwargs
    return ''

  def sample_choice(self, prompt, responses, **kwargs):
    del kwargs
    with self._lock:
      self.choice_prompts.append(prompt)
    # Concordia lists options as "(a) option"; map letters back to options.
    offered = dict(re.findall(r'^\s*\(([a-z])\) (.+)$', prompt, re.M))
    for preferred in self._preferences:
      for key, option in offered.items():
        if option.strip() == preferred and key in responses:
          return responses.index(key), key, {}
      if preferred in responses:
        return responses.index(preferred), preferred, {}
    return 0, responses[0], {}


def _play(config, leader_prefers, follower_prefers, probe_prefers=()):
  models = {
      config.LEADER: _ScriptedModel(leader_prefers),
      config.FOLLOWER: _ScriptedModel(follower_prefers),
  }
  probe = _ScriptedModel(probe_prefers)
  result = simulation.run_simulation(
      config=config,
      model=no_language_model.NoLanguageModel(),
      embedder=_mock_embedder,
      entity_models=models,
      probe_model=probe,
  )
  return result, models, probe


class PuppetTest(absltest.TestCase):

  def test_scripted_rational_players_reach_the_equilibrium(self):
    result = simulation.run_simulation(
        config=puppet,
        model=no_language_model.NoLanguageModel(),
        embedder=_mock_embedder,
        probe_model=_ScriptedModel([market.ENTER]),
    )
    self.assertEqual(result['leader_choice'], market.EXPAND)
    self.assertEqual(result['follower_choice'], market.STAY_OUT)
    self.assertEqual(result['payoffs'], {market.LEADER: 3, market.FOLLOWER: 0})
    self.assertTrue(result['path_matches_spe'])
    self.assertTrue(result['plan_is_credible'])


class InformationTest(absltest.TestCase):

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.result, cls.models, cls.probe = _play(
        market,
        leader_prefers=[market.EXPAND],
        follower_prefers=[market.STAY_OUT],
        probe_prefers=[market.ENTER],
    )

  def test_both_players_know_every_payoff_before_choosing(self):
    for name in (market.LEADER, market.FOLLOWER):
      (prompt,) = self.models[name].choice_prompts
      for line in simulation.describe_payoffs(market):
        self.assertIn(line, prompt)

  def test_follower_sees_the_leader_move_before_choosing(self):
    (prompt,) = self.models[market.FOLLOWER].choice_prompts
    self.assertIn(f'Northfield Cement has decided to {market.EXPAND}', prompt)

  def test_leader_does_not_see_a_follower_move_before_choosing(self):
    (prompt,) = self.models[market.LEADER].choice_prompts
    self.assertNotIn('Ridgeway Cement has decided', prompt)
    self.assertNotIn('Northfield Cement has decided', prompt)

  def test_counterfactual_question_leaves_memory_unchanged(self):
    (probe_prompt,) = self.probe.choice_prompts
    self.assertIn(market.KEEP, probe_prompt)
    for memory in self.result['memories'][market.FOLLOWER]:
      self.assertNotIn('Suppose that, instead', memory)

  def test_follower_plan_covers_every_leader_option(self):
    self.assertEqual(
        self.result['follower_plan'],
        {market.EXPAND: market.STAY_OUT, market.KEEP: market.ENTER},
    )


class BenchmarkTest(absltest.TestCase):

  def test_always_entering_is_flagged_as_not_credible(self):
    result, _, _ = _play(
        market,
        leader_prefers=[market.KEEP],
        follower_prefers=[market.ENTER],
        probe_prefers=[market.ENTER],
    )
    self.assertFalse(result['path_matches_spe'])
    self.assertFalse(result['plan_is_credible'])

  def test_reversed_order_equilibrium_is_entry(self):
    result, _, _ = _play(
        market_reversed_order,
        leader_prefers=[market.ENTER],
        follower_prefers=[market.KEEP],
        probe_prefers=[market.KEEP],
    )
    self.assertTrue(result['path_matches_spe'])
    self.assertTrue(result['plan_is_credible'])

  def test_expanding_is_not_the_equilibrium_when_it_is_costly(self):
    result, _, _ = _play(
        market_costly_expansion,
        leader_prefers=[market.EXPAND],
        follower_prefers=[market.STAY_OUT],
        probe_prefers=[market.ENTER],
    )
    self.assertFalse(result['path_matches_spe'])
    self.assertTrue(result['plan_is_credible'])

  def test_invalid_leader_answer_ends_the_game(self):
    config = puppet
    original = dict(config.FIXED_RESPONSES)
    try:
      config.FIXED_RESPONSES = {
          market.LEADER: {market.LEADER_Q: 'Expand!'},
          market.FOLLOWER: original[market.FOLLOWER],
      }
      result = simulation.run_simulation(
          config=config,
          model=no_language_model.NoLanguageModel(),
          embedder=_mock_embedder,
      )
    finally:
      config.FIXED_RESPONSES = original
    self.assertIsNone(result['leader_choice'])
    self.assertIsNone(result['follower_choice'])
    self.assertIsNone(result['payoffs'])
    self.assertFalse(result['path_matches_spe'])


if __name__ == '__main__':
  absltest.main()
