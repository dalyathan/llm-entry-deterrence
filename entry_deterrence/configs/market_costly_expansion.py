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

"""The cement market with an expansion too costly to be worth deterring entry.

Only the cost of expanding changes. Expansion still keeps the rival out, but
it now costs the established firm more than letting the rival in, so the
subgame perfect equilibrium flips: keep current capacity and the rival enters.
Players who expand here are recalling a familiar pattern rather than reasoning
from the payoffs.
"""

from entry_deterrence.configs.market import *  # pylint: disable=wildcard-import,unused-wildcard-import

PAYOFFS = {
    (KEEP, ENTER): (2, 1),
    (KEEP, STAY_OUT): (4, 0),
    (EXPAND, ENTER): (0, -1),
    (EXPAND, STAY_OUT): (1, 0),
}
