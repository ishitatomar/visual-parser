class LR1Item:
    def __init__(self, lhs, rhs, dot_pos, lookaheads):
        self.lhs = lhs
        self.rhs = tuple(rhs)  # tuple for hashability
        self.dot_pos = dot_pos
        self.lookaheads = set(lookaheads) # set of terminals

    def __eq__(self, other):
        return (self.lhs == other.lhs and 
                self.rhs == other.rhs and 
                self.dot_pos == other.dot_pos and 
                self.lookaheads == other.lookaheads)

    def __hash__(self):
        return hash((self.lhs, self.rhs, self.dot_pos, frozenset(self.lookaheads)))

    def core_eq(self, other):
        """Checks if the LR(0) core is identical"""
        return (self.lhs == other.lhs and 
                self.rhs == other.rhs and 
                self.dot_pos == other.dot_pos)
                
    def core_hash(self):
        return hash((self.lhs, self.rhs, self.dot_pos))

    def __repr__(self):
        rhs_str = list(self.rhs)
        if self.rhs == ('epsilon',):
            rhs_str = []
        rhs_with_dot = rhs_str[:self.dot_pos] + ['•'] + rhs_str[self.dot_pos:]
        lookaheads_str = "/".join(sorted(list(self.lookaheads)))
        return f"{self.lhs} -> {' '.join(rhs_with_dot)} , {lookaheads_str}"

def closure(items, grammar, first_sets):
    """
    Computes the closure of a set of LR(1) items.
    """
    closure_set = list(items)
    added = True
    
    while added:
        added = False
        for item in closure_set:
            # item is A -> alpha • B beta, a
            if item.rhs != ('epsilon',) and item.dot_pos < len(item.rhs):
                B = item.rhs[item.dot_pos]
                if B in grammar.non_terminals:
                    # beta is the rest of the rhs after B
                    beta = item.rhs[item.dot_pos + 1:]
                    
                    # For each b in FIRST(beta a)
                    for a in list(item.lookaheads):
                        # Calculate FIRST(beta a)
                        first_beta_a = set()
                        all_derive_eps = True
                        for sym in beta:
                            sym_first = first_sets.get(sym, set())
                            for f in sym_first:
                                if f != 'epsilon':
                                    first_beta_a.add(f)
                            if 'epsilon' not in sym_first:
                                all_derive_eps = False
                                break
                        
                        if all_derive_eps:
                            first_beta_a.add(a)
                            
                        # For each production B -> gamma
                        for gamma in grammar.productions.get(B, []):
                            gamma_tuple = tuple(gamma) if gamma != ['epsilon'] else ('epsilon',)
                            new_item = LR1Item(B, gamma_tuple, 0, first_beta_a)
                            
                            # Check if new_item is in closure_set (need to merge lookaheads if core exists)
                            found = False
                            for existing in closure_set:
                                if existing.core_eq(new_item):
                                    found = True
                                    # If lookaheads aren't fully contained
                                    if not new_item.lookaheads.issubset(existing.lookaheads):
                                        existing.lookaheads.update(new_item.lookaheads)
                                        added = True
                                    break
                            
                            if not found:
                                closure_set.append(new_item)
                                added = True
                                
    return closure_set

def goto(items, symbol, grammar, first_sets):
    """
    Computes the GOTO set for a given item set and symbol.
    """
    goto_items = []
    for item in items:
        if item.rhs != ('epsilon',) and item.dot_pos < len(item.rhs):
            next_sym = item.rhs[item.dot_pos]
            if next_sym == symbol:
                goto_items.append(LR1Item(item.lhs, item.rhs, item.dot_pos + 1, item.lookaheads))
                
    return closure(goto_items, grammar, first_sets)

def canonical_collection(grammar, first_sets):
    """
    Generates the canonical collection of LR(1) item sets (DFA states).
    """
    start_item = LR1Item(grammar.start_symbol, grammar.productions[grammar.start_symbol][0], 0, {'$'})
    start_set = closure([start_item], grammar, first_sets)
    
    # List of states (each state is a list of LR1Item)
    C = [start_set]
    
    # Store transitions: transitions[state_idx][symbol] = next_state_idx
    transitions = {0: {}}
    
    added = True
    while added:
        added = False
        for i, state in enumerate(C):
            # Find all symbols after the dot
            symbols = set()
            for item in state:
                if item.rhs != ('epsilon',) and item.dot_pos < len(item.rhs):
                    symbols.add(item.rhs[item.dot_pos])
                    
            for sym in symbols:
                next_state = goto(state, sym, grammar, first_sets)
                
                if next_state:
                    # Check if next_state already exists in C
                    found_idx = -1
                    for j, existing_state in enumerate(C):
                        # Proper comparison of sets of items
                        if len(next_state) == len(existing_state):
                            all_match = True
                            for item1 in next_state:
                                match = False
                                for item2 in existing_state:
                                    if item1 == item2:
                                        match = True
                                        break
                                if not match:
                                    all_match = False
                                    break
                            if all_match:
                                found_idx = j
                                break
                                
                    if found_idx == -1:
                        C.append(next_state)
                        found_idx = len(C) - 1
                        transitions[found_idx] = {}
                        added = True
                        
                    transitions[i][sym] = found_idx
                    
    return C, transitions
