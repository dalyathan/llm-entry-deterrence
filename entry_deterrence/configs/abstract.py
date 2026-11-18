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

"""The cement market's payoffs with every story detail removed.

Players are told only the moves and the points they earn. Comparing play here
with `market` and `security` separates the effect of the payoffs from the
effect of the story told around them.
"""

LEADER = 'Avery'
FOLLOWER = 'Blake'
PLAYER_PREFAB = 'basic__Entity'

OPTION_J = 'choose option J'
OPTION_F = 'choose option F'
OPTION_P = 'choose option P'
OPTION_Q = 'choose option Q'

LEADER_OPTIONS = (OPTION_J, OPTION_F)
FOLLOWER_OPTIONS = (OPTION_P, OPTION_Q)

# Same numbers as `market`: J and F mirror keep and expand, P and Q mirror
# enter and stay out.
PAYOFFS = {
    (OPTION_J, OPTION_P): (2, 1),
    (OPTION_J, OPTION_Q): (4, 0),
    (OPTION_F, OPTION_P): (1, -1),
    (OPTION_F, OPTION_Q): (3, 0),
}

SCENARIO_PREMISE = f'{LEADER} and {FOLLOWER} are playing a two-move game.'

RULES = (
    (
        f'{LEADER} moves first and must {OPTION_J} or {OPTION_F}. The move '
        'cannot be undone.'
    ),
    (
        f"{FOLLOWER} will see {LEADER}'s move, and then must {OPTION_P} or "
        f'{OPTION_Q}.'
    ),
    'Both players know the points each earns for every combination of moves:',
)

OUTCOME_TEMPLATE = (
    'If {leader} and {follower} make the moves "{leader_choice}" and '
    '"{follower_choice}", {leader} earns {leader_payoff} and {follower} earns '
    '{follower_payoff}.'
)
PAYOFF_FORMAT = '{} points'

GOALS = {
    LEADER: 'Earn as many points as possible.',
    FOLLOWER: 'Earn as many points as possible.',
}

PLAYER_SPECIFIC_MEMORIES = {}

LEADER_Q = 'Which move does {name} make?'
FOLLOWER_Q = 'Which move does {name} make?'
LEADER_TURN_PREMISE = f"It is {LEADER}'s turn to move."
LEADER_MOVE_ANNOUNCEMENT = (
    '{leader} has made the move "{leader_choice}". It cannot be changed.'
)
COUNTERFACTUAL_Q = (
    'Suppose that, instead, {leader} had made the move "{other_choice}". '
    'Which move would {name} have made?'
)

MAX_STEPS_PER_STAGE = 4
