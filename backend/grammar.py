class Grammar:
    def __init__(self):
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
<<<<<<< HEAD
        self.productions = {}  # dict mapping LHS (str) to list of arrays representing RHS
=======
        self.productions = {}  
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895

    def parse_from_string(self, grammar_str):
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
        self.productions = {}
        
        lines = [line.strip() for line in grammar_str.split('\n') if line.strip()]
        
        for idx, line in enumerate(lines):
<<<<<<< HEAD
            # Support multiple derivation symbols
=======
            
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
            if '->' in line:
                lhs, rhs_part = line.split('->', 1)
            elif '→' in line:
                lhs, rhs_part = line.split('→', 1)
            elif '=' in line:
                lhs, rhs_part = line.split('=', 1)
            else:
                continue
                
            lhs = lhs.strip()
            if not self.start_symbol and idx == 0:
                self.start_symbol = lhs
                
            self.non_terminals.add(lhs)
            
            if lhs not in self.productions:
                self.productions[lhs] = []
                
            import re
            rhs_alternatives = rhs_part.split('|')
            for alt in rhs_alternatives:
<<<<<<< HEAD
                # Add spaces around non-alphanumeric chars (excluding apostrophes)
                alt_spaced = re.sub(r"([^\w\s\'])", r" \1 ", alt)
                symbols = alt_spaced.strip().split()
                # Empty production handling
=======
               
                alt_spaced = re.sub(r"([^\w\s\'])", r" \1 ", alt)
                symbols = alt_spaced.strip().split()
               
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
                if not symbols or symbols[0] in ['epsilon', 'ε', "''", '""', 'e']:
                    self.productions[lhs].append(['epsilon'])
                else:
                    self.productions[lhs].append(symbols)

<<<<<<< HEAD
        # Identify terminals
=======
        
>>>>>>> ca88b4ada4f05acc2afdfa7b85b5625aff502895
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol != 'epsilon' and symbol not in self.non_terminals:
                        self.terminals.add(symbol)
                        
    def get_augmented_grammar(self):
        """Returns a new augmented grammar object for LALR"""
        aug_grammar = Grammar()
        aug_grammar.start_symbol = self.start_symbol + "'"
        while aug_grammar.start_symbol in self.non_terminals:
            aug_grammar.start_symbol += "'"
            
        aug_grammar.non_terminals = set(self.non_terminals)
        aug_grammar.non_terminals.add(aug_grammar.start_symbol)
        aug_grammar.terminals = set(self.terminals)
        
        aug_grammar.productions = {k: [list(v2) for v2 in v] for k, v in self.productions.items()}
        aug_grammar.productions[aug_grammar.start_symbol] = [[self.start_symbol]]
        
        return aug_grammar

    def to_dict(self):
        return {
            "start_symbol": self.start_symbol,
            "non_terminals": list(self.non_terminals),
            "terminals": list(self.terminals),
            "productions": self.productions
        }
