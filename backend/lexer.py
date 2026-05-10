import ply.lex as lex

# Reserved keywords
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'return': 'RETURN',
    'int': 'INT',
    'float': 'FLOAT',
    'void': 'VOID'
}

# List of token names
tokens = [
    'IDENTIFIER',
    'INTEGER',
    'FLOAT_CONST',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ASSIGN_OP',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'SEMICOLON',
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LE',
    'GE',
] + list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_ASSIGN_OP = r'='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_COMMA     = r','
t_SEMICOLON = r';'
t_EQ        = r'=='
t_NEQ       = r'!='
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'

def t_FLOAT_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore spaces and tabs
t_ignore = ' \t'

def t_error(t):
    result = {
        'lexeme': str(t.value[0]),
        'token': 'ERROR',
        'line': t.lexer.lineno,
        'position': t.lexpos
    }

    if not hasattr(t.lexer, 'errors'):
        t.lexer.errors = []

    t.lexer.errors.append(result)
    t.lexer.skip(1)

# Build lexer
lexer = lex.lex()

def tokenize(input_string):
    """
    Tokenizes the input string and returns token information.
    """

    lexer.errors = []
    lexer.lineno = 1
    lexer.input(input_string)

    tokens_list = []

    while True:
        tok = lexer.token()

        if not tok:
            break

        tokens_list.append({
            'lexeme': str(tok.value),
            'token': tok.type,
            'line': tok.lineno,
            'position': tok.lexpos
        })

    tokens_list.extend(lexer.errors)
    tokens_list.sort(key=lambda x: x['position'])

    return tokens_list


if __name__ == '__main__':

    data = '''
    int x = 10;
    float y = 20.5;

    if (x < y) {
        return x + y;
    }
    '''

    result = tokenize(data)

    for t in result:
        print(f"{t['lexeme']:<15} | {t['token']}")