from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer import tokenize
from grammar import Grammar
from first_follow import compute_first, compute_follow, first_follow_to_dict
from ll1_parser import LL1Parser
from lr1_items import canonical_collection
from lalr_states import compute_lalr_states
from parse_table import build_lalr_table
from shift_reduce_parser import ShiftReduceParser
from parse_tree import build_hierarchical_tree

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/parse', methods=['POST'])
def parse_endpoint():
    data = request.json
    grammar_str = data.get('grammar', '')
    input_str = data.get('input', '')

    response = {}

    try:
        # 1. Lexical Analysis
        tokens = tokenize(input_str)
        response['tokens'] = tokens

        # Check for lexer errors
        lexer_errors = [t for t in tokens if t['token'] == 'ERROR']
        if lexer_errors:
            response['error'] = f"Lexical error: unrecognized character {lexer_errors[0]['lexeme']}"
            return jsonify(response)

        # 2. Grammar Parsing
        g = Grammar()
        g.parse_from_string(grammar_str)

        if not g.start_symbol:
            response['error'] = "Invalid grammar format. Missing start symbol."
            return jsonify(response)

        response['grammar'] = g.to_dict()

        # 3. FIRST and FOLLOW
        first_sets = compute_first(g)
        follow_sets = compute_follow(g, first_sets)
        response['sets'] = first_follow_to_dict(first_sets, follow_sets)

        # 4. LL(1) Parsing
        ll1 = LL1Parser(g, first_sets, follow_sets)
        ll1_table, ll1_conflicts, ll1_conflict_details = ll1.build_table()

        response['ll1'] = {
            'table': ll1_table,
            'conflicts': ll1_conflicts,
            'conflict_details': ll1_conflict_details
        }

        if not ll1_conflicts:
            ll1_history, ll1_nodes, ll1_error = ll1.parse(tokens)
            response['ll1']['history'] = ll1_history
            response['ll1']['tree'] = build_hierarchical_tree(ll1_nodes)
            response['ll1']['error'] = ll1_error
        else:
            response['ll1']['history'] = []
            response['ll1']['tree'] = {}
            response['ll1']['error'] = True

        # 5. LALR Parsing
        aug_g = g.get_augmented_grammar()
        aug_first_sets = compute_first(aug_g)

        lr1_states, lr1_transitions = canonical_collection(
            aug_g,
            aug_first_sets
        )

        response['lr1_collection'] = []

        for i, state in enumerate(lr1_states):
            state_items = [str(item) for item in state]

            response['lr1_collection'].append({
                'id': i,
                'items': state_items
            })

        lalr_states, lalr_transitions, mapping = compute_lalr_states(
            lr1_states,
            lr1_transitions
        )

        response['lalr_states'] = []

        for i, state in enumerate(lalr_states):
            state_items = [str(item) for item in state]

            # Find which LR1 states were merged
            merged_from = [
                old_id for old_id, new_id in mapping.items()
                if new_id == i
            ]

            response['lalr_states'].append({
                'id': i,
                'items': state_items,
                'merged_from': merged_from
            })

        lalr_action, lalr_goto, lalr_conflicts, lalr_conflict_details = build_lalr_table(
            aug_g,
            lalr_states,
            lalr_transitions
        )

        response['lalr'] = {
            'action_table': lalr_action,
            'goto_table': lalr_goto,
            'conflicts': lalr_conflicts,
            'conflict_details': lalr_conflict_details
        }

        if not lalr_conflicts:
            sr_parser = ShiftReduceParser(lalr_action, lalr_goto, g)

            sr_history, sr_nodes, sr_error = sr_parser.parse(tokens)

            response['lalr']['history'] = sr_history
            response['lalr']['tree'] = build_hierarchical_tree(sr_nodes)
            response['lalr']['error'] = sr_error
        else:
            response['lalr']['history'] = []
            response['lalr']['tree'] = {}
            response['lalr']['error'] = True

    except Exception as e:
        import traceback
        traceback.print_exc()
        response['error'] = str(e)

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)