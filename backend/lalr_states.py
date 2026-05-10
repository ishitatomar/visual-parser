def get_core(state):
    """
    Returns a set of core item representations from a state.
    Ignores lookaheads.
    """
    cores = set()
    for item in state:
        cores.add(item.core_hash())
    return frozenset(cores)

def compute_lalr_states(lr1_states, lr1_transitions):
    """
    Merges LR(1) item sets that share the same core to form LALR item sets.
    Returns:
    - lalr_states: List of merged states (each state is a list of LR1Item)
    - lalr_transitions: Dictionary of LALR transitions
    - mapping: Dictionary mapping old LR(1) state indices to new LALR indices
    """
    core_map = {} # Maps a core_hash to a list of original LR(1) state indices
    
    for i, state in enumerate(lr1_states):
        core = get_core(state)
        if core not in core_map:
            core_map[core] = []
        core_map[core].append(i)
        
    lalr_states = []
    mapping = {} # old_id -> new_id
    
    # Merge states with same cores
    for new_id, core in enumerate(core_map):
        old_ids = core_map[core]
        
        # Merge all items
        merged_items = []
        for old_id in old_ids:
            mapping[old_id] = new_id
            for item in lr1_states[old_id]:
                # Check if item with same core is already in merged_items
                found = False
                for existing in merged_items:
                    if existing.core_eq(item):
                        existing.lookaheads.update(item.lookaheads)
                        found = True
                        break
                if not found:
                    from lr1_items import LR1Item
                    # Create a deep copy
                    new_item = LR1Item(item.lhs, item.rhs, item.dot_pos, set(item.lookaheads))
                    merged_items.append(new_item)
                    
        lalr_states.append(merged_items)
        
    # Build LALR transitions
    lalr_transitions = {new_id: {} for new_id in range(len(lalr_states))}
    
    for old_from, trans in lr1_transitions.items():
        new_from = mapping[old_from]
        for symbol, old_to in trans.items():
            new_to = mapping[old_to]
            lalr_transitions[new_from][symbol] = new_to
            
    return lalr_states, lalr_transitions, mapping
