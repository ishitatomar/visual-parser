def compute_first(grammar):
    first = {nt: set() for nt in grammar.non_terminals}
    for t in grammar.terminals:
        first[t] = {t}
    first['epsilon'] = {'epsilon'}
    
    changed = True
    while changed:
        changed = False
        for lhs in grammar.productions:
            for rhs in grammar.productions[lhs]:
                for symbol in rhs:
                    before_add = len(first[lhs])
                    # Add everything from the FIRST set of symbol, excluding epsilon
                    for s in first.get(symbol, set()):
                        if s != 'epsilon':
                            first[lhs].add(s)
                            
                    if before_add != len(first[lhs]):
                        changed = True
                    
                    if 'epsilon' not in first.get(symbol, set()):
                        break
                else:
                    # If all symbols in rhs can derive epsilon
                    if 'epsilon' not in first[lhs]:
                        first[lhs].add('epsilon')
                        changed = True
                        
    return first

def compute_follow(grammar, first_sets):
    follow = {nt: set() for nt in grammar.non_terminals}
    
    # Rule 1: Place $ in FOLLOW(Start_Symbol)
    follow[grammar.start_symbol].add('$')
    
    changed = True
    while changed:
        changed = False
        for lhs in grammar.productions:
            for rhs in grammar.productions[lhs]:
                for i in range(len(rhs)):
                    symbol = rhs[i]
                    if symbol in grammar.non_terminals:
                        before_add = len(follow[symbol])
                        
                        # Calculate FIRST of string following symbol
                        next_first = set()
                        all_derive_epsilon = True
                        for j in range(i + 1, len(rhs)):
                            next_sym = rhs[j]
                            sym_first = first_sets.get(next_sym, set())
                            for f in sym_first:
                                if f != 'epsilon':
                                    next_first.add(f)
                            if 'epsilon' not in sym_first:
                                all_derive_epsilon = False
                                break
                                
                        for f in next_first:
                            if f not in follow[symbol]:
                                follow[symbol].add(f)
                                changed = True
                                
                        # Rule 3: If symbol is at end of production or everything following derives epsilon
                        if all_derive_epsilon or i == len(rhs) - 1:
                            for f in follow[lhs]:
                                if f not in follow[symbol]:
                                    follow[symbol].add(f)
                                    changed = True
                                    
    return follow

def first_follow_to_dict(first, follow):
    first_dict = {k: list(v) for k, v in first.items() if k != 'epsilon' and k not in first[k]}
    # Clean up first_dict terminal to terminal mapping if returned
    cleaned_first = {k: list(v) for k, v in first.items() if k in follow} 
    follow_dict = {k: list(v) for k, v in follow.items()}
    return {
        "first": cleaned_first,
        "follow": follow_dict
    }
