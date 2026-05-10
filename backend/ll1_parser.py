class LL1Parser:
    def __init__(self, grammar, first_sets, follow_sets):
        self.grammar = grammar
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.parsing_table = {}
        self.conflicts = False
        self.conflict_details = []

    def build_table(self):
        """
        Constructs the LL(1) parsing table M[A, a].
        """
        self.parsing_table = {nt: {} for nt in self.grammar.non_terminals}
        
        for lhs in self.grammar.productions:
            for rhs in self.grammar.productions[lhs]:
<<<<<<< HEAD
                # Calculate FIRST(rhs)
=======
           
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                rhs_first = set()
                all_derive_epsilon = True
                
                for symbol in rhs:
                    sym_first = self.first_sets.get(symbol, set())
                    for f in sym_first:
                        if f != 'epsilon':
                            rhs_first.add(f)
                    if 'epsilon' not in sym_first:
                        all_derive_epsilon = False
                        break
                        
                if all_derive_epsilon:
                    rhs_first.add('epsilon')
                
<<<<<<< HEAD
                # Rule 1: For each terminal a in FIRST(rhs), add A -> rhs to M[A, a]
=======

>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                for a in rhs_first:
                    if a != 'epsilon':
                        if a in self.parsing_table[lhs]:
                            if self.parsing_table[lhs][a] != rhs:
                                self.conflicts = True
                                self.conflict_details.append(f"Conflict in M[{lhs}, {a}]: {self.parsing_table[lhs][a]} and {rhs}")
                        self.parsing_table[lhs][a] = rhs
                        
<<<<<<< HEAD
                # Rule 2: If epsilon is in FIRST(rhs), for each b in FOLLOW(lhs), add A -> rhs to M[A, b]
=======
          
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                if 'epsilon' in rhs_first:
                    for b in self.follow_sets[lhs]:
                        if b in self.parsing_table[lhs]:
                            if self.parsing_table[lhs][b] != rhs:
                                self.conflicts = True
                                self.conflict_details.append(f"Conflict in M[{lhs}, {b}]: {self.parsing_table[lhs][b]} and {rhs}")
                        self.parsing_table[lhs][b] = rhs
                        
        return self.parsing_table, self.conflicts, self.conflict_details

    def parse(self, tokens):
<<<<<<< HEAD
        """
        Performs predictive parsing. tokens is a list of token dicts form lexer.
        Returns a history of the parsing steps for visualization.
        """
        # Append end marker to tokens and map them to grammar terminals
        input_queue = []
        for t in tokens:
            if t['token'] == 'IDENTIFIER' or t['token'] == 'INTEGER' or t['token'] == 'FLOAT_CONST':
                # Simplified matching: if grammar uses 'id', map IDENTIFIER to 'id'
                # To be generic, let's use the lexeme if it's a terminal, otherwise token name
=======
        
     
        input_queue = []
        for t in tokens:
            if t['token'] == 'IDENTIFIER' or t['token'] == 'INTEGER' or t['token'] == 'FLOAT_CONST':
                
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                if t['lexeme'] in self.grammar.terminals:
                    input_queue.append(t['lexeme'])
                elif 'id' in self.grammar.terminals and t['token'] == 'IDENTIFIER':
                    input_queue.append('id')
                elif 'num' in self.grammar.terminals and (t['token'] == 'INTEGER' or t['token'] == 'FLOAT_CONST'):
                    input_queue.append('num')
                else:
                    input_queue.append(t['lexeme'])
            else:
                input_queue.append(t['lexeme'])
                
        input_queue.append('$')
        
        stack = ['$', self.grammar.start_symbol]
        
        history = []
        node_id_counter = 0
        
<<<<<<< HEAD
        # We need to build a parse tree during simulation
        # Stack elements will be tuples (symbol, node_id)
=======
       
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
        tree_nodes = [{"id": node_id_counter, "label": self.grammar.start_symbol, "children": []}]
        stack = [('$', -1), (self.grammar.start_symbol, node_id_counter)]
        node_id_counter += 1
        
        pointer = 0
        error = False
        
        while stack:
            top_sym, parent_id = stack[-1]
            curr_input = input_queue[pointer]
            
            step = {
                "stack": [s[0] for s in stack],
                "input": input_queue[pointer:],
                "action": ""
            }
            
            if top_sym == '$' and curr_input == '$':
                step["action"] = "Accept"
                history.append(step)
                stack.pop()
                break
            
            if top_sym == curr_input:
                step["action"] = f"Match {top_sym}"
                history.append(step)
                stack.pop()
                pointer += 1
            elif top_sym in self.grammar.terminals or top_sym == '$':
                step["action"] = f"Error: Expected {top_sym}, found {curr_input}"
                history.append(step)
                error = True
                break
            elif top_sym in self.grammar.non_terminals:
<<<<<<< HEAD
                # Need to consult parsing table
=======
          
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                if curr_input in self.parsing_table[top_sym]:
                    rhs = self.parsing_table[top_sym][curr_input]
                    production_str = f"{top_sym} -> {' '.join(rhs)}"
                    step["action"] = production_str
                    history.append(step)
                    stack.pop()
                    
                    if rhs != ['epsilon']:
<<<<<<< HEAD
                        # Push in reverse order
                        for sym in reversed(rhs):
                            # Create tree node
                            tree_nodes.append({"id": node_id_counter, "label": sym, "children": []})
                            # Find parent and add child
                            for node in tree_nodes:
                                if node["id"] == parent_id:
                                    # Insert at beginning because we are iterating in reverse
=======
       
                        for sym in reversed(rhs):
           
                            tree_nodes.append({"id": node_id_counter, "label": sym, "children": []})
           
                            for node in tree_nodes:
                                if node["id"] == parent_id:
                                  
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                                    node["children"].insert(0, node_id_counter)
                                    break
                            
                            stack.append((sym, node_id_counter))
                            node_id_counter += 1
                    else:
<<<<<<< HEAD
                        # Add epsilon node
=======
          
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                        tree_nodes.append({"id": node_id_counter, "label": "ε", "children": []})
                        for node in tree_nodes:
                            if node["id"] == parent_id:
                                node["children"].append(node_id_counter)
                                break
                        node_id_counter += 1
                else:
                    step["action"] = f"Error: No rule for M[{top_sym}, {curr_input}]"
                    history.append(step)
                    error = True
                    break
            else:
                 step["action"] = f"Error: Unrecognized symbol {top_sym}"
                 history.append(step)
                 error = True
                 break
                 
        return history, tree_nodes, error
