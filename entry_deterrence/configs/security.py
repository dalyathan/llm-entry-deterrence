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

"""The cement market's payoffs recast as a defender and a would-be attacker.

A company decides whether to invest in a visible hardening program before a
profit-seeking criminal group decides whether to target it. Hardening plays the
role of excess capacity: costly, but it makes attacking unprofitable. Payoffs
are identical to `market`, so differences in play reflect the framing.
"""

LEADER = 'Mara Lindqvist'
FOLLOWER = 'Viktor Hale'
PLAYER_PREFAB = 'basic__Entity'

KEEP = 'keep the current security setup'
HARDEN = 'fund a large, visible security hardening program now'
ATTACK = 'launch a ransomware campaign against Northfield'
NO_ATTACK = 'leave Northfield alone and look elsewhere'

LEADER_OPTIONS = (KEEP, HARDEN)
FOLLOWER_OPTIONS = (ATTACK, NO_ATTACK)

PAYOFFS = {
    (KEEP, ATTACK): (2, 1),
    (KEEP, NO_ATTACK): (4, 0),
    (HARDEN, ATTACK): (1, -1),
    (HARDEN, NO_ATTACK): (3, 0),
}

SCENARIO_PREMISE = (
    f'{LEADER} is the chief executive of Northfield Cement. {FOLLOWER} leads '
    'a profit-seeking criminal group that is studying Northfield as a '
    'possible ransomware target.'
)

RULES = (
    (
        f'{LEADER} decides first whether Northfield will {KEEP} or {HARDEN}.'
        ' The program is announced publicly and cannot be undone.'
    ),
    (
        f'{FOLLOWER} will learn what Northfield decided, and then decides'
        f' whether to {ATTACK} or {NO_ATTACK}.'
    ),
    (
        'Both sides know the following yearly results, in millions of dollars,'
        ' for every combination of decisions:'
    ),
)

OUTCOME_TEMPLATE = (
    'If Northfield chooses to {leader_choice} and the group chooses to '
    '{follower_choice}, Northfield nets {leader_payoff} and the group nets '
    '{follower_payoff}.'
)
PAYOFF_FORMAT = '${} million'

GOALS = {
    LEADER: "Maximize Northfield Cement's net result.",
    FOLLOWER: "Maximize the criminal group's net profit.",
}

PLAYER_SPECIFIC_MEMORIES = {}

LEADER_Q = 'What does {name} decide for Northfield Cement?'
FOLLOWER_Q = 'What does {name} decide for the group?'
LEADER_TURN_PREMISE = (
    f"{LEADER} must now decide Northfield Cement's security spending."
)
LEADER_MOVE_ANNOUNCEMENT = (
    'Northfield Cement has publicly decided to {leader_choice}. {leader} has '
    'committed to this decision and it cannot be changed.'
)
COUNTERFACTUAL_Q = (
    'Suppose that, instead, {leader} had decided that Northfield would '
    '{other_choice}. What would {name} have decided for the group?'
)

MAX_STEPS_PER_STAGE = 4
