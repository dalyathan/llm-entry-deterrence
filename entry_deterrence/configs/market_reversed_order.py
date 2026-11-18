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

"""The cement market with the order of moves reversed.

The rival decides whether to enter before the established firm decides its
capacity. Payoffs are unchanged, but expansion no longer deters anything, so
the subgame perfect equilibrium is for the rival to enter and for the
established firm to keep its current capacity.
"""

from entry_deterrence.configs import market as _market

LEADER = _market.FOLLOWER
FOLLOWER = _market.LEADER
PLAYER_PREFAB = _market.PLAYER_PREFAB

LEADER_OPTIONS = _market.FOLLOWER_OPTIONS
FOLLOWER_OPTIONS = _market.LEADER_OPTIONS

PAYOFFS = {
    (entrant, incumbent): (entrant_profit, incumbent_profit)
    for (incumbent, entrant), (
        incumbent_profit,
        entrant_profit,
    ) in _market.PAYOFFS.items()
}

SCENARIO_PREMISE = _market.SCENARIO_PREMISE

RULES = (
    (
        f'{LEADER} decides first whether Ridgeway will '
        f'{_market.ENTER} or {_market.STAY_OUT}. The decision cannot be undone.'
    ),
    (
        f'{FOLLOWER} will learn what Ridgeway decided, and then decides whether'
        f' Northfield will {_market.KEEP} or {_market.EXPAND}.'
    ),
    (
        'Both firms know the following annual profits for every combination of '
        'decisions:'
    ),
)

OUTCOME_TEMPLATE = (
    'If Ridgeway chooses to {leader_choice} and Northfield chooses to '
    '{follower_choice}, Ridgeway earns {leader_payoff} and Northfield earns '
    '{follower_payoff} a year.'
)
PAYOFF_FORMAT = _market.PAYOFF_FORMAT

GOALS = _market.GOALS
PLAYER_SPECIFIC_MEMORIES = {}

LEADER_Q = _market.FOLLOWER_Q
FOLLOWER_Q = _market.LEADER_Q
LEADER_TURN_PREMISE = f'{LEADER} must now decide whether Ridgeway enters.'
LEADER_MOVE_ANNOUNCEMENT = (
    'Ridgeway Cement has decided to {leader_choice}. {leader} has committed '
    'to this decision and it cannot be changed.'
)
COUNTERFACTUAL_Q = (
    'Suppose that, instead, {leader} had decided that Ridgeway would '
    '{other_choice}. What would {name} have decided for Northfield Cement?'
)

MAX_STEPS_PER_STAGE = _market.MAX_STEPS_PER_STAGE
