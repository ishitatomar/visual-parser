class ShiftReduceParser:
    def __init__(self, action_table, goto_table, grammar):
        self.action_table = action_table
        self.goto_table = goto_table
        self.grammar = grammar
        
    def parse(self, tokens):
        input_queue = []
        for t in tokens:
            if t['token'] == 'IDENTIFIER' or t['token'] == 'INTEGER' or t['token'] == 'FLOAT_CONST':
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
        
        stack = [0]
        history = []
        pointer = 0
        
        # For parse tree generation
        tree_nodes = []
        node_id_counter = 0
        node_stack = []
        
        while True:
            state = stack[-1]
            curr_input = input_queue[pointer]
            
            step = {
                "stack": [str(s) for s in stack],
                "input": input_queue[pointer:],
                "action": ""
            }
            
            action = self.action_table[state].get(curr_input)
            
            if not action:
                step["action"] = f"Error: No action for state {state} on symbol {curr_input}"
                history.append(step)
                return history, tree_nodes, True
                
            if action.startswith('S'):
                next_state = int(action[1:])
                step["action"] = f"Shift {next_state}"
                history.append(step)
                
                stack.append(curr_input)
                stack.append(next_state)
                
                tree_nodes.append({"id": node_id_counter, "label": curr_input, "children": []})
                node_stack.append(node_id_counter)
                node_id_counter += 1
                
                pointer += 1
                
            elif action.startswith('R'):
                parts = action[2:].split('->')
                lhs = parts[0].strip()
                rhs_str = parts[1].strip()
                rhs = rhs_str.split()
                
                step["action"] = f"Reduce {lhs} -> {rhs_str}"
                history.append(step)
                
                num_symbols = 0 if rhs == ['epsilon'] else len(rhs)
                
                children_ids = []
                for _ in range(num_symbols):
                    stack.pop() # state
                    stack.pop() # symbol
                    children_ids.insert(0, node_stack.pop())
                    
                top_state = stack[-1]
                goto_state = self.goto_table[top_state].get(lhs)
                
                if goto_state is None:
                    step = {
                        "stack": [str(s) for s in stack],
                        "input": input_queue[pointer:],
                        "action": f"Error: No GOTO for state {top_state} on non-terminal {lhs}"
                    }
                    history.append(step)
                    return history, tree_nodes, True
                
                stack.append(lhs)
                stack.append(goto_state)
                
                if rhs == ['epsilon']:
                    # Create epsilon node if reduce by epsilon
                    tree_nodes.append({"id": node_id_counter, "label": "ε", "children": []})
                    children_ids.append(node_id_counter)
                    node_id_counter += 1

                tree_nodes.append({"id": node_id_counter, "label": lhs, "children": children_ids})
                node_stack.append(node_id_counter)
                node_id_counter += 1
                
            elif action == "Accept":
                step["action"] = "Accept"
                history.append(step)
                
                # augmented start symbol reduction completes implicitly
                # the root node is the last node added
                break
                
        return history, tree_nodes, False
