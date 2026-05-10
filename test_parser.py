import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from grammar import Grammar
from first_follow import compute_first, compute_follow, first_follow_to_dict
from lr1_items import canonical_collection
from lalr_states import compute_lalr_states
from parse_table import build_lalr_table
from ll1_parser import LL1Parser

def main():
    grammar_str = """E = E + T
E = T
T = id"""
    
    import sys
    with open('test_out.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        g = Grammar()
        g.parse_from_string(grammar_str)
        print("Grammar:")
        print(json.dumps(g.to_dict(), indent=2))
        
        first = compute_first(g)
        follow = compute_follow(g, first)
        print("\nFIRST and FOLLOW:")
        print(json.dumps(first_follow_to_dict(first, follow), indent=2))
        
        ll1 = LL1Parser(g, first, follow)
        table, conflicts, _ = ll1.build_table()
        print("\nLL(1) Table:")
        print(json.dumps(table, indent=2))
        
        aug_g = g.get_augmented_grammar()
        aug_first = compute_first(aug_g)
        lr1_states, lr1_transitions = canonical_collection(aug_g, aug_first)
        
        lalr_states, lalr_transitions, mapping = compute_lalr_states(lr1_states, lr1_transitions)
        lalr_action, lalr_goto, conflicts, conflict_details = build_lalr_table(aug_g, lalr_states, lalr_transitions)
        
        print("\nLALR Conflicts:", conflicts)
        if conflicts:
            print(conflict_details)
            
        print("\nLALR Action Table:")
        print(json.dumps(lalr_action, indent=2))
        
        print("\nLALR Goto Table:")
        print(json.dumps(lalr_goto, indent=2))
        
        from lexer import tokenize
        from shift_reduce_parser import ShiftReduceParser
        
        input_str = "id + id"
        tokens = tokenize(input_str)
        print("\nTokens:", tokens)
        
        print("\nLL1 Parsing:")
        ll1_hist, ll1_tree, ll1_err = ll1.parse(tokens)
        print("History:")
        for h in ll1_hist:
            print(h)
        print("Error:", ll1_err)
        
        print("\nLALR Parsing:")
        sr = ShiftReduceParser(lalr_action, lalr_goto, g)
        sr_hist, sr_tree, sr_err = sr.parse(tokens)
        print("History:")
        for h in sr_hist:
            print(h)
        print("Error:", sr_err)

if __name__ == '__main__':
    main()
