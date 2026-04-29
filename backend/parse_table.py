def build_lalr_table(grammar, lalr_states, lalr_transitions):
    action = {i: {} for i in range(len(lalr_states))}
    goto = {i: {} for i in range(len(lalr_states))}
    conflicts = False
    conflict_details = []

    for i, state in enumerate(lalr_states):
        for item in state:
            if item.rhs != ('epsilon',) and item.dot_pos < len(item.rhs):
                a = item.rhs[item.dot_pos]
                if a in grammar.terminals:
                    if a in lalr_transitions.get(i, {}):
                        j = lalr_transitions[i][a]
                        action_str = f"S{j}"
                        if a in action[i]:
                            if action[i][a] != action_str:
                                conflicts = True
                                conflict_details.append(f"Shift/Reduce conflict in state {i} on symbol {a}")
                        action[i][a] = action_str
            elif item.rhs == ('epsilon',) or item.dot_pos == len(item.rhs):
                if item.lhs == grammar.start_symbol:
                    for a in item.lookaheads:
                        if a == '$':
                            action[i]['$'] = "Accept"
                else:
                    for a in item.lookaheads:
                        action_str = f"R {item.lhs} -> {' '.join(item.rhs)}"
                        if a in action[i]:
                            if action[i][a] != action_str:
                                conflicts = True
                                conflict_details.append(f"Reduce/Reduce or Shift/Reduce conflict in state {i} on symbol {a}")
                        action[i][a] = action_str

        for A in grammar.non_terminals:
            if A != grammar.start_symbol and A in lalr_transitions.get(i, {}):
                goto[i][A] = lalr_transitions[i][A]

    return action, goto, conflicts, conflict_details
