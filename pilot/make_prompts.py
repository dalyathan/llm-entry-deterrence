import json, random, sys
sys.path.insert(0, '..')
from entry_deterrence import simulation as s
from entry_deterrence.configs import market, market_reversed_order, market_costly_expansion, abstract, security
CONDS = {'market': market, 'reversed': market_reversed_order, 'costly': market_costly_expansion, 'abstract': abstract, 'security': security}
rng = random.Random(7)
TEMPLATE = """You are role-playing {name} in a simulation. Answer as {name} would, using only the information below. Do not use any tools and do not ask questions.

{name}'s goal: {goal}

What {name} knows:
{memories}

Question: {question}
{options}

Reply with 2-3 sentences of {name}'s reasoning, then a final line that is exactly "ANSWER: a" or "ANSWER: b"."""

def prompt(c, name, extra, question, options):
    opts = list(options); rng.shuffle(opts)
    payoff_lines = s.describe_payoffs(c); rng.shuffle(payoff_lines)
    mem = [c.SCENARIO_PREMISE, *c.RULES, *payoff_lines, *extra]
    return TEMPLATE.format(name=name, goal=c.GOALS[name], memories='\n'.join('- '+m for m in mem),
        question=question.format(name=name), options='\n'.join(f'({k}) {o}' for k, o in zip('ab', opts))), dict(zip('ab', opts))

def leader_prompts():
    out = {}
    for k, c in CONDS.items():
        out[k] = prompt(c, c.LEADER, [c.LEADER_TURN_PREMISE], c.LEADER_Q, c.LEADER_OPTIONS)
    return out

def follower_prompts(leader_choices, cheap_talk=False):
    out = {}
    for k, choice in leader_choices.items():
        c = CONDS[k]
        ann = c.LEADER_MOVE_ANNOUNCEMENT.format(leader=c.LEADER, leader_choice=choice)
        out[k] = prompt(c, c.FOLLOWER, [ann], c.FOLLOWER_Q, c.FOLLOWER_OPTIONS)
    return out

THREAT = ('{leader} tells {follower} directly: "If Ridgeway builds a plant here, we will flood the Valley '
          'with cheap cement and make sure you lose money. You should stay out."')
def cheap_talk_prompt():
    c = market
    ann = c.LEADER_MOVE_ANNOUNCEMENT.format(leader=c.LEADER, leader_choice=c.KEEP)
    return prompt(c, c.FOLLOWER, [ann, THREAT.format(leader=c.LEADER, follower=c.FOLLOWER)], c.FOLLOWER_Q, c.FOLLOWER_OPTIONS)

def counterfactual_prompt(k, actual, own_choice):
    c = CONDS[k]
    other = [o for o in c.LEADER_OPTIONS if o != actual][0]
    ann = c.LEADER_MOVE_ANNOUNCEMENT.format(leader=c.LEADER, leader_choice=actual)
    return prompt(c, c.FOLLOWER, [ann, f'{c.FOLLOWER} decided to {own_choice}.'],
                  c.COUNTERFACTUAL_Q.replace('{name}', c.FOLLOWER).replace('{leader}', c.LEADER).replace('{other_choice}', other), c.FOLLOWER_OPTIONS) + (other,)

if __name__ == '__main__':
    lp = leader_prompts()
    json.dump({k: {'prompt': p, 'map': m} for k, (p, m) in lp.items()}, open('/home/claude/pilot/leader_prompts.json', 'w'), indent=1)
    print(lp['market'][0]); print(lp['market'][1])
