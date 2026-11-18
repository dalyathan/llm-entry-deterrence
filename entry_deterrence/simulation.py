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

"""A two-move sequential game played by Concordia entities.

A leader chooses first; its choice is announced to the follower, who then
chooses. Both players know the full payoff table from the start. After play,
the follower is also asked what it would have done had the leader chosen
differently (the "strategy method"), using a copy of its memories so that the
question cannot affect play. Comparing the follower's full plan with the
subgame perfect equilibrium shows whether simulated players believe threats
that a rational follower would never carry out.

The game is played in two stages, each run by a fresh game master with a single
choice scene, so the follower cannot act before the leader's move is fixed.
"""

from collections.abc import Callable, Mapping, Sequence
import copy
import dataclasses
from typing import Any

from concordia.associative_memory import basic_associative_memory as associative_memory
from concordia.components.agent import memory as memory_lib
from concordia.components.game_master import payoff_matrix as payoff_matrix_lib
from concordia.language_model import language_model
from concordia.prefabs import entity as entity_prefabs
from concordia.prefabs import game_master as game_master_prefabs
from concordia.prefabs.entity import puppet
from concordia.prefabs.simulation import generic as simulation_lib
from concordia.typing import entity as entity_lib
from concordia.typing import entity_component
from concordia.typing import prefab as prefab_lib
from concordia.typing import scene as scene_lib
from concordia.utils import helper_functions

from entry_deterrence import game as game_lib

_GM_PREFAB = 'dialogic_and_dramaturgic__GameMaster'
_OWN_MODEL_PREFAB = 'own_model__Entity'
_PROBE_MEMORY_LINES = 40


@dataclasses.dataclass
class OwnModelEntity(prefab_lib.Prefab):
  """Builds another entity prefab with a language model of its own.

  Lets each player run on a different language model. Params: `inner_prefab`
  (the prefab to build), `language_model` (the model for this entity; the
  simulation's model is used when it is None), and any params for the inner
  prefab.
  """

  description = 'Builds another entity prefab with its own language model.'

  def build(
      self,
      model: language_model.LanguageModel,
      memory_bank: associative_memory.AssociativeMemoryBank,
  ) -> entity_component.EntityWithComponents:
    params = dict(self.params)
    inner = copy.deepcopy(params.pop('inner_prefab'))
    own_model = params.pop('language_model', None) or model
    inner.params = params
    return inner.build(model=own_model, memory_bank=memory_bank)


class ChoiceRecorder:
  """Records the options chosen in each stage, for the payoff component."""

  def __init__(self, options_by_player: Mapping[str, Sequence[str]]):
    self._options = {name: list(o) for name, o in options_by_player.items()}
    self._choices: dict[str, str] = {}

  @property
  def choices(self) -> dict[str, str]:
    """The valid choices made so far, keyed by player name."""
    return dict(self._choices)

  def action_to_scores(
      self, joint_action: Mapping[str, str]
  ) -> Mapping[str, float]:
    """Records valid choices; the payoff is computed once the game ends."""
    for name, choice in joint_action.items():
      if choice in self._options.get(name, ()):
        self._choices[name] = choice
    return {name: 0.0 for name in joint_action}

  def scores_to_observation(
      self, scores: Mapping[str, float]
  ) -> Mapping[str, str]:
    """Players are told outcomes directly between stages, not here."""
    del scores
    return {}


def make_game(config: Any) -> game_lib.SequentialGame:
  """Returns the payoff table of a scenario as a game."""
  return game_lib.SequentialGame(
      leader=config.LEADER,
      follower=config.FOLLOWER,
      leader_options=tuple(config.LEADER_OPTIONS),
      follower_options=tuple(config.FOLLOWER_OPTIONS),
      payoffs=dict(config.PAYOFFS),
  )


def describe_payoffs(config: Any) -> list[str]:
  """Returns one sentence per outcome, generated from the payoff table.

  Generating the rules from the table keeps what players are told and what
  they are scored on from drifting apart.
  """
  lines = []
  for (leader_choice, follower_choice), (lp, fp) in config.PAYOFFS.items():
    lines.append(
        config.OUTCOME_TEMPLATE.format(
            leader=config.LEADER,
            follower=config.FOLLOWER,
            leader_choice=leader_choice,
            follower_choice=follower_choice,
            leader_payoff=_format_payoff(config, lp),
            follower_payoff=_format_payoff(config, fp),
        )
    )
  return lines


def _format_payoff(config: Any, value: float) -> str:
  """Formats a payoff with the scenario's units, e.g. '-$1 million'."""
  text = config.PAYOFF_FORMAT.format(f'{abs(value):g}')
  return f'-{text}' if value < 0 else text


def _choice_scene(
    name: str,
    game_master_name: str,
    player: str,
    question: str,
    options: Sequence[str],
    premise: str,
) -> scene_lib.SceneSpec:
  return scene_lib.SceneSpec(
      scene_type=scene_lib.SceneTypeSpec(
          name=name,
          game_master_name=game_master_name,
          action_spec=entity_lib.choice_action_spec(
              call_to_action=question, options=list(options)
          ),
      ),
      participants=[player],
      num_rounds=1,
      premise={player: [premise]},
  )


def _memories(entity: Any) -> list[str]:
  memory = entity.get_component(memory_lib.DEFAULT_MEMORY_COMPONENT_KEY)
  return list(memory.get_all_memories_as_text())


def ask_counterfactual(
    model: language_model.LanguageModel,
    player: Any,
    question: str,
    options: Sequence[str],
) -> str:
  """Asks a question about a player using a copy of its memories.

  Nothing is written to the player's memory, so asking cannot change play.
  """
  recent = _memories(player)[-_PROBE_MEMORY_LINES:]
  prompt = (
      f'Memories of {player.name}:\n'
      + '\n'.join(recent)
      + f'\n\nQuestion: {question}'
  )
  _, answer, _ = model.sample_choice(prompt, list(options))
  return answer


def run_simulation(
    config: Any,
    model: language_model.LanguageModel,
    embedder: Callable[[str], Any],
    entity_models: Mapping[str, language_model.LanguageModel] | None = None,
    probe_model: language_model.LanguageModel | None = None,
) -> dict[str, Any]:
  """Plays one game and compares it with the subgame perfect equilibrium.

  Args:
    config: The scenario configuration module.
    model: The language model for the game masters, and for any player that
      `entity_models` does not cover.
    embedder: The sentence embedder to use.
    entity_models: Optional language model per player name.
    probe_model: Optional model for the counterfactual question; defaults to
      the follower's model. Use a model that keeps no conversation state.

  Returns:
    A dictionary with the choices, payoffs, the follower's full plan, the
    subgame perfect equilibrium, whether play matched it, and the log.
  """
  c = config
  game = make_game(c)
  entity_models = dict(entity_models or {})
  probe_model = probe_model or entity_models.get(c.FOLLOWER) or model
  fixed_responses = getattr(c, 'FIXED_RESPONSES', {})

  prefabs = {
      **helper_functions.get_package_classes(entity_prefabs),
      **helper_functions.get_package_classes(game_master_prefabs),
  }
  prefabs['puppet__Entity'] = puppet.Entity()
  prefabs[_OWN_MODEL_PREFAB] = OwnModelEntity()

  instances = []
  for name in (c.LEADER, c.FOLLOWER):
    params: dict[str, Any] = {
        'inner_prefab': prefabs[c.PLAYER_PREFAB],
        'language_model': entity_models.get(name),
        'name': name,
        'goal': c.GOALS[name],
    }
    if c.PLAYER_PREFAB == 'puppet__Entity':
      params['fixed_responses'] = {
          call.format(name=name): response
          for call, response in fixed_responses.get(name, {}).items()
      }
    instances.append(
        prefab_lib.InstanceConfig(
            prefab=_OWN_MODEL_PREFAB,
            role=prefab_lib.Role.ENTITY,
            params=params,
        )
    )

  recorder = ChoiceRecorder({
      c.LEADER: c.LEADER_OPTIONS,
      c.FOLLOWER: c.FOLLOWER_OPTIONS,
  })

  def stage_game_master(
      player: str, question: str, options: Sequence[str], premise: str
  ) -> prefab_lib.InstanceConfig:
    gm_name = f'{player} decision rules'
    scene = _choice_scene(
        name=f'{player} decision',
        game_master_name=gm_name,
        player=player,
        question=question,
        options=options,
        premise=premise,
    )
    return prefab_lib.InstanceConfig(
        prefab=_GM_PREFAB,
        role=prefab_lib.Role.GAME_MASTER,
        params={  # pyrefly: ignore[bad-argument-type]
            'name': gm_name,
            'scenes': [scene],
            'allow_llm_fallback': False,
            'extra_components': {
                'payoff_matrix': payoff_matrix_lib.PayoffMatrix(
                    model=model,
                    acting_player_names=[c.LEADER, c.FOLLOWER],
                    action_to_scores=recorder.action_to_scores,
                    scores_to_observation=recorder.scores_to_observation,
                ),
            },
        },
    )

  instances.append(
      stage_game_master(
          c.LEADER, c.LEADER_Q, c.LEADER_OPTIONS, c.LEADER_TURN_PREMISE
      )
  )
  sim = simulation_lib.Simulation(
      config=prefab_lib.Config(
          default_premise=c.SCENARIO_PREMISE,
          default_max_steps=c.MAX_STEPS_PER_STAGE,
          prefabs=prefabs,
          instances=instances,
      ),
      model=model,
      embedder=embedder,
  )
  entities = {e.name: e for e in sim.get_entities()}

  # Both players know the setting and the full payoff table before anyone
  # moves (a game of complete and perfect information).
  shared = [c.SCENARIO_PREMISE, *c.RULES, *describe_payoffs(c)]
  for name, entity in entities.items():
    for memory in [*shared, *c.PLAYER_SPECIFIC_MEMORIES.get(name, [])]:
      entity.observe(memory)

  raw_log: list[Mapping[str, Any]] = []
  structured_log = sim.play(premise='', raw_log=raw_log)
  leader_choice = recorder.choices.get(c.LEADER)

  follower_choice = None
  plan: dict[str, str] = {}
  if leader_choice is not None:
    announcement = c.LEADER_MOVE_ANNOUNCEMENT.format(
        leader=c.LEADER, leader_choice=leader_choice
    )
    for entity in entities.values():
      entity.observe(announcement)
    sim.game_masters.clear()
    sim.game_master_memory_bank = associative_memory.AssociativeMemoryBank(
        sentence_embedder=embedder, allow_duplicates=True
    )
    sim.add_game_master(
        stage_game_master(
            c.FOLLOWER, c.FOLLOWER_Q, c.FOLLOWER_OPTIONS, announcement
        )
    )
    structured_log = sim.play(premise='', raw_log=raw_log)
    follower_choice = recorder.choices.get(c.FOLLOWER)

  payoffs = None
  if leader_choice is not None and follower_choice is not None:
    payoffs = game.score(leader_choice, follower_choice)
    plan[leader_choice] = follower_choice
    for other in c.LEADER_OPTIONS:
      if other == leader_choice:
        continue
      plan[other] = ask_counterfactual(
          probe_model,
          entities[c.FOLLOWER],
          c.COUNTERFACTUAL_Q.format(
              name=c.FOLLOWER, leader=c.LEADER, other_choice=other
          ),
          c.FOLLOWER_OPTIONS,
      )

  spe = game.subgame_perfect()
  complete = follower_choice is not None and len(plan) == len(c.LEADER_OPTIONS)
  return {
      'leader': c.LEADER,
      'follower': c.FOLLOWER,
      'leader_choice': leader_choice,
      'follower_choice': follower_choice,
      'follower_plan': plan,
      'payoffs': payoffs,
      'subgame_perfect': spe,
      'path_matches_spe': (
          complete
          and leader_choice == spe.leader_choice
          and follower_choice == spe.follower_plan[spe.leader_choice]
      ),
      'plan_is_credible': (
          complete
          and all(plan[choice] == game.best_response(choice) for choice in plan)
      ),
      'memories': {name: _memories(e) for name, e in entities.items()},
      'structured_log': structured_log,
  }
