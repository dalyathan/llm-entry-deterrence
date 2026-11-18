import pygambit as gbt
from entry_deterrence import simulation as s
from entry_deterrence.configs import market, market_reversed_order, market_costly_expansion
for c in (market, market_reversed_order, market_costly_expansion):
    g = gbt.Game.new_tree(players=[c.LEADER, c.FOLLOWER])
    g.append_move(g.root, c.LEADER, list(c.LEADER_OPTIONS))
    for i, lo in enumerate(c.LEADER_OPTIONS):
        node = g.root.children[lo]
        g.append_move(node, c.FOLLOWER, list(c.FOLLOWER_OPTIONS))
        for j, fo in enumerate(c.FOLLOWER_OPTIONS):
            lp, fp = c.PAYOFFS[(lo, fo)]
            g.set_outcome(node.children[fo], g.add_outcome(f"{lo}|{fo}", payoffs=[lp, fp]))
    spe = gbt.nash.logit_solve(g, use_strategic=False).equilibria

    ne = gbt.nash.enumpure_solve(g).equilibria
    ours = s.make_game(c).subgame_perfect()
    def pick(eq, player):
        out = []
        for inf in g.players[player].infosets:
            out.append(max(inf.actions, key=lambda a: eq[a]).label)
        return out
    print(c.__name__.split('.')[-1], '| gambit logit (QRE-limit) eq:', [ (pick(e,c.LEADER), pick(e,c.FOLLOWER)) for e in spe], '| gambit pure NE count:', len(ne), '| ours NE count:', len(s.make_game(c).nash_equilibria()))
    print('   ours SPE:', ours.leader_choice, [ours.follower_plan[o] for o in c.LEADER_OPTIONS])
