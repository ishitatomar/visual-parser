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

        self.parsing_table = {
            nt: {}
            for nt in self.grammar.non_terminals
        }

        for lhs in self.grammar.productions:

            for rhs in self.grammar.productions[lhs]:

                # Calculate FIRST(rhs)
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

                # Add productions using FIRST(rhs)
                for a in rhs_first:

                    if a != 'epsilon':

                        if a in self.parsing_table[lhs]:

                            if self.parsing_table[lhs][a] != rhs:
                                self.conflicts = True

                                self.conflict_details.append(
                                    f"Conflict in M[{lhs}, {a}]: "
                                    f"{self.parsing_table[lhs][a]} and {rhs}"
                                )

                        self.parsing_table[lhs][a] = rhs

                # If epsilon exists, use FOLLOW(lhs)
                if 'epsilon' in rhs_first:

                    for b in self.follow_sets[lhs]:

                        if b in self.parsing_table[lhs]:

                            if self.parsing_table[lhs][b] != rhs:
                                self.conflicts = True

                                self.conflict_details.append(
                                    f"Conflict in M[{lhs}, {b}]: "
                                    f"{self.parsing_table[lhs][b]} and {rhs}"
                                )

                        self.parsing_table[lhs][b] = rhs

        return (
            self.parsing_table,
            self.conflicts,
            self.conflict_details
        )

    def parse(self, tokens):
        """
        Performs predictive parsing.

        Returns:
        - history
        - tree_nodes
        - error flag
        """

        # Convert lexer tokens into grammar terminals
        input_queue = []

        for t in tokens:

            if (
                t['token'] == 'IDENTIFIER' or
                t['token'] == 'INTEGER' or
                t['token'] == 'FLOAT_CONST'
            ):

                if t['lexeme'] in self.grammar.terminals:
                    input_queue.append(t['lexeme'])

                elif (
                    'id' in self.grammar.terminals and
                    t['token'] == 'IDENTIFIER'
                ):
                    input_queue.append('id')

                elif (
                    'num' in self.grammar.terminals and
                    (
                        t['token'] == 'INTEGER' or
                        t['token'] == 'FLOAT_CONST'
                    )
                ):
                    input_queue.append('num')

                else:
                    input_queue.append(t['lexeme'])

            else:
                input_queue.append(t['lexeme'])

        input_queue.append('$')

        history = []
        node_id_counter = 0

        # Parse tree root
        tree_nodes = [
            {
                "id": node_id_counter,
                "label": self.grammar.start_symbol,
                "children": []
            }
        ]

        stack = [
            ('$', -1),
            (self.grammar.start_symbol, node_id_counter)
        ]

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

            # Accept
            if top_sym == '$' and curr_input == '$':

                step["action"] = "Accept"
                history.append(step)

                stack.pop()
                break

            # Match terminal
            if top_sym == curr_input:

                step["action"] = f"Match {top_sym}"
                history.append(step)

                stack.pop()
                pointer += 1

            # Terminal mismatch
            elif (
                top_sym in self.grammar.terminals or
                top_sym == '$'
            ):

                step["action"] = (
                    f"Error: Expected {top_sym}, "
                    f"found {curr_input}"
                )

                history.append(step)

                error = True
                break

            # Non-terminal expansion
            elif top_sym in self.grammar.non_terminals:

                if curr_input in self.parsing_table[top_sym]:

                    rhs = self.parsing_table[top_sym][curr_input]

                    production_str = (
                        f"{top_sym} -> {' '.join(rhs)}"
                    )

                    step["action"] = production_str
                    history.append(step)

                    stack.pop()

                    if rhs != ['epsilon']:

                        # Push RHS in reverse order
                        for sym in reversed(rhs):

                            tree_nodes.append({
                                "id": node_id_counter,
                                "label": sym,
                                "children": []
                            })

                            # Attach child to parent
                            for node in tree_nodes:

                                if node["id"] == parent_id:
                                    node["children"].insert(
                                        0,
                                        node_id_counter
                                    )
                                    break

                            stack.append(
                                (sym, node_id_counter)
                            )

                            node_id_counter += 1

                    else:
                        # Add epsilon node
                        tree_nodes.append({
                            "id": node_id_counter,
                            "label": "ε",
                            "children": []
                        })

                        for node in tree_nodes:

                            if node["id"] == parent_id:
                                node["children"].append(
                                    node_id_counter
                                )
                                break

                        node_id_counter += 1

                else:

                    step["action"] = (
                        f"Error: No rule for "
                        f"M[{top_sym}, {curr_input}]"
                    )

                    history.append(step)

                    error = True
                    break

            else:

                step["action"] = (
                    f"Error: Unrecognized symbol {top_sym}"
                )

                history.append(step)

                error = True
                break

        return history, tree_nodes, error