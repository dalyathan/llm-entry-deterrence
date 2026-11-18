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

"""An established cement producer and a possible new rival.

The established firm decides whether to expand its plant before the rival
decides whether to enter. Payoffs are annual profits in millions of dollars and
follow the textbook capacity-commitment game: expanding is costly, but makes
entry unprofitable, so the subgame perfect equilibrium is to expand and for
the rival to stay out. Keeping current capacity and the rival entering anyway
is also a Nash equilibrium, but it rests on the rival's non-credible plan to
enter even after an expansion.
"""

LEADER = 'Mara Lindqvist'
FOLLOWER = 'Tomas Reyes'
PLAYER_PREFAB = 'basic__Entity'

KEEP = 'keep the plant at its current capacity'
EXPAND = 'build a large capacity expansion now'
ENTER = 'build a plant and enter the market'
STAY_OUT = 'stay out of the market'

LEADER_OPTIONS = (KEEP, EXPAND)
FOLLOWER_OPTIONS = (ENTER, STAY_OUT)

# (leader option, follower option): (leader profit, follower profit).
PAYOFFS = {
    (KEEP, ENTER): (2, 1),
    (KEEP, STAY_OUT): (4, 0),
    (EXPAND, ENTER): (1, -1),
    (EXPAND, STAY_OUT): (3, 0),
}

SCENARIO_PREMISE = (
    f'{LEADER} runs Northfield Cement, the only cement producer in the '
    f'Valley region. {FOLLOWER} runs Ridgeway Cement, which is considering '
    'building a plant in the Valley.'
)

RULES = (
    (
        f'{LEADER} decides first whether Northfield will {KEEP} or {EXPAND}. '
        'Construction starts immediately and cannot be undone.'
    ),
    (
        f'{FOLLOWER} will learn what Northfield decided, and then decides'
        f' whether Ridgeway will {ENTER} or {STAY_OUT}.'
    ),
    (
        'Both firms know the following annual profits for every combination of '
        'decisions:'
    ),
)

OUTCOME_TEMPLATE = (
    'If Northfield chooses to {leader_choice} and Ridgeway chooses to '
    '{follower_choice}, Northfield earns {leader_payoff} and Ridgeway earns '
    '{follower_payoff} a year.'
)
PAYOFF_FORMAT = '${} million'

GOALS = {
    LEADER: "Maximize Northfield Cement's annual profit.",
    FOLLOWER: "Maximize Ridgeway Cement's annual profit.",
}

PLAYER_SPECIFIC_MEMORIES = {}

LEADER_Q = 'What does {name} decide for Northfield Cement?'
FOLLOWER_Q = 'What does {name} decide for Ridgeway Cement?'
LEADER_TURN_PREMISE = f"{LEADER} must now decide Northfield Cement's capacity."
LEADER_MOVE_ANNOUNCEMENT = (
    'Northfield Cement has decided to {leader_choice}. {leader} has '
    'committed to this decision and it cannot be changed.'
)
COUNTERFACTUAL_Q = (
    'Suppose that, instead, {leader} had decided that Northfield would '
    '{other_choice}. What would {name} have decided for Ridgeway Cement?'
)

MAX_STEPS_PER_STAGE = 4
