######################################
# string_with_arrows
######################################

def string_with_arrows(text, pos_start, pos_end):
    result = ''

    idx_start = text.rfind('\n', 0, pos_start.idx) + 1
    idx_end = text.find('\n', idx_start)
    if idx_end < 0:
        idx_end = len(text)

    line = text[idx_start:idx_end]

    col_start = pos_start.col
    col_end = pos_end.col if pos_start.ln == pos_end.ln else len(line)

    result += line + '\n'
    result += ' ' * col_start + '^' * max(1, col_end - col_start)

    return result.replace('\t', '')


######################################
# CONSTANTS
######################################

DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS_DIGITS = LETTERS + DIGITS


######################################
# ERRORS
######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RunTime error', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}\n'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'   File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos if ctx.parent_entry_pos else pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result

class IndentationError(Error):
    def __init__(self, pos_start, pos_end, indent, exp_indent):
        super().__init__(pos_start, pos_end, 'Indentation Error', f"Expected indentation level {indent}, got {exp_indent}")


######################################
# POSITION
######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


######################################
# TOKENS
######################################

TT_INT          = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING       = 'STRING'
TT_IDENTIFIER   = 'IDENTIFIER'
TT_KEYWORD      = 'KEYWORD'
TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MULT         = 'MULT'
TT_DIV          = 'DIV'
TT_FLOORDIV     = 'FLOORDIV'
TT_MOD          = 'MOD'
TT_POW          = 'POW'
TT_EQ           = 'EQ'
TT_LPAREN       = 'LPAREN'
TT_RPAREN       = 'RPAREN'
TT_LSQPAREN     = 'LsqPAREN'
TT_RSQPAREN     = 'RsqPAREN'
TT_EE           = 'EE'
TT_NE           = 'NE'
TT_LT           = 'LT'
TT_GT           = 'GT'
TT_LTE          = 'LTE'
TT_GTE          = 'GTE'
TT_COMMA        = 'COMMA'
TT_COLON        = 'COLON'
TT_NEWLINE      = 'NEWLINE'
TT_INDENT       = 'INDENT'
TT_EOF          = 'EOF'

KEYWORDS = [
    'and',
    'or',
    'not',
    'True',
    'False',
    'if',
    'then',
    'else',
    'for',
    'to',
    'downto',
    'while',
    'function',
    'do',
    'END',
    'return',
    'Algo',
    'Begin',
    'End'
]

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


######################################
# LEXER
######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    single_char_tokens = {
        '+': TT_PLUS,
        '-': TT_MINUS,
        '/': TT_DIV,
        '(': TT_LPAREN,
        ')': TT_RPAREN,
        '[': TT_LSQPAREN,
        ']': TT_RSQPAREN,
        ',': TT_COMMA,
        ':': TT_COLON,
    }

    def make_tokens(self):
        tokens = []

        indent_lvl, error = self.count_indent_lvl()
        if error: return [], error
        if indent_lvl != 0:
            tokens.append(Token(TT_INDENT, indent_lvl, pos_start=self.pos))

        while self.current_char != None:
            if self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
                indent_lvl, error = self.count_indent_lvl()
                if error: return [], error
                tokens.append(Token(TT_INDENT, indent_lvl, pos_start=self.pos))
            elif self.current_char in ' \t':
                self.advance()
            elif self.current_char == '#':
                while self.current_char != '\n':
                    self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"' or self.current_char == "'":
                token, error = self.make_string(self.current_char)
                if error: return [], error
                tokens.append(token)
            elif self.current_char in self.single_char_tokens:
                tokens.append(Token(self.single_char_tokens[self.current_char], pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(self.make_mult())
            elif self.current_char == '=':
                token, error = self.make_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '<':
                if len(self.text[self.pos.idx:]) >= 3 and self.text[self.pos.idx:self.pos.idx+3] == '<--':
                    tokens.append(Token(TT_EQ, pos_start=self.pos))
                    for _ in range(3):
                        self.advance()
                else:
                    tokens.append(self.make_comparison_token(TT_LT, TT_LTE))
            elif self.current_char == '>':
                tokens.append(self.make_comparison_token(TT_GT, TT_GTE))
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def count_indent_lvl(self):
        count = 0
        pos_start = self.pos.copy()
        while self.current_char in (' ', '\t'):
            count += 1 if self.current_char == '\t' else 1 / 4
            self.advance()

        if not count.is_integer():
            return None, IndentationError(pos_start, self.pos, "Indentation level must be a multiple of 4 spaces or tabs")
        return int(count), None

    def make_number(self):
        numstr = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                numstr += '.'
            else:
                numstr += self.current_char
            self.advance()

        if '.' in numstr:
            return Token(TT_FLOAT, float(numstr), pos_start, self.pos)
        return Token(TT_INT, int(numstr), pos_start, self.pos)

    def make_string(self, end_string_tok):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != end_string_tok or escape_character:
            if self.current_char == '\n' or self.current_char == None :
                return [], ExpectedCharError(pos_start, self.pos, f"String should be closed by {end_string_tok}")
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()

        if string == "Saut-de-ligne":
            string = '\n'

        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos), None

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        if id_str == 'div':
            tok_type = TT_DIV
        elif id_str == 'mod':
            tok_type = TT_MOD
        elif id_str == 'True':
            return Token(TT_KEYWORD, 'true', pos_start, self.pos)
        elif id_str == 'False':
            return Token(TT_KEYWORD, 'false', pos_start, self.pos)
        else:
            tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_mult(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '*':
            self.advance()
            return Token(TT_POW, pos_start=pos_start, pos_end=self.pos)

        return Token(TT_MULT, pos_start=pos_start, pos_end=self.pos)

    def make_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_EE, pos_start=pos_start, pos_end=self.pos), None

        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '=')")

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_comparison_token(self, single_char_tok, equal_char_tok):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(equal_char_tok, pos_start=pos_start, pos_end=self.pos)

        return Token(single_char_tok, pos_start=pos_start, pos_end=self.pos)

######################################
# NODES
######################################

class Node:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

class NumberNode(Node):
    def __init__(self, tok):
        super().__init__(tok.pos_start, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f'NumberNode({self.tok})'

class StringNode(Node):
    def __init__(self, tok):
        super().__init__(tok.pos_start, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

class ListNode(Node):
    def __init__(self, element_nodes, pos_start, pos_end):
        super().__init__(pos_start, pos_end)
        self.element_nodes = element_nodes

    def __repr__(self):
        return f'ListNode({self.element_nodes})'

class VarAccessNode(Node):
    def __init__(self, var_name_tok):
        super().__init__(var_name_tok.pos_start, var_name_tok.pos_end)
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f"Var({self.var_name_tok.value})"

class VarAssignNode(Node):
    def __init__(self, var_name_tok, value_node):
        super().__init__(var_name_tok.pos_start, value_node.pos_end)
        self.var_name_tok = var_name_tok
        self.value_node = value_node

    def __repr__(self):
        return f'VarAssignNode({self.var_name_tok}, {self.value_node})'

class BinOpNode(Node):
    def __init__(self, left_node, op_tok, right_node):
        super().__init__(left_node.pos_start, right_node.pos_end)
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'BinOpNode({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode(Node):
    def __init__(self, op_tok, node):
        super().__init__(op_tok.pos_start, node.pos_end)
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

class IfNode(Node):
    def __init__(self, cases, else_case):
        super().__init__(cases[0][0].pos_start, (else_case or cases[len(cases)-1])[0].pos_end)
        self.cases = cases
        self.else_case = else_case

    def __repr__(self):
        cases_repr = " | ".join(f"IF {repr(cond)} THEN {repr(expr)}" for cond, expr, _ in self.cases)
        else_repr = f" ELSE {repr(self.else_case[0])}" if self.else_case else ""
        return f"{cases_repr}{else_repr}"

class ForNode(Node):
    def __init__(self, var_name_tok, start_value_node, end_value_node, body_node, to_downto, should_return_null):
        super().__init__(var_name_tok.pos_start, body_node.pos_end)
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.body_node = body_node
        self.to_downto = to_downto
        self.should_return_null = should_return_null

    def __repr__(self):
        direction = "to" if self.to_downto == 0 else "downto"
        return f"For({self.var_name_tok.value} from {self.start_value_node} {direction} {self.end_value_node}) DO ({self.body_node})"

class WhileNode(Node):
    def __init__(self, condition_node, body_node, should_return_null):
        super().__init__(condition_node.pos_start, body_node.pos_end)
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

    def __repr__(self):
        return f"While({self.condition_node}) DO ({self.body_node})"

class FunctionDefNode(Node):
    def __init__(self, var_name_tok, arg_name_toks, body_node, return_type):
        if var_name_tok:
            pos_start = var_name_tok.pos_start
        elif len(arg_name_toks) > 0:
            pos_start = arg_name_toks[0].pos_start
        else:
            pos_start = body_node.pos_start

        pos_end = body_node.pos_end

        super().__init__(pos_start, pos_end)

        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.return_type = return_type

class CallNode(Node):
    def __init__(self, node_to_call, arg_nodes):
        pos_start = node_to_call.pos_start

        for arg in reversed(arg_nodes):
            if arg is not None and hasattr(arg, 'pos_end'):
                pos_end = arg.pos_end
                break
        else:
            pos_end = node_to_call.pos_end

        super().__init__(pos_start, pos_end)

        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

    def __repr__(self):
        args_repr = ", ".join(repr(arg) for arg in self.arg_nodes)
        return f"Call({repr(self.node_to_call)}, [{args_repr}])"

class ReturnNode(Node):
    def __init__(self, node_to_return, pos_start, pos_end):
        super().__init__(pos_start, pos_end)
        self.node_to_return = node_to_return

class IndexAssignNode(Node):
    def __init__(self, target_node, value_node):
        super().__init__(target_node.pos_start, value_node.pos_end)
        self.target_node = target_node
        self.value_node = value_node

    def __repr__(self):
        return f"IndexAssign({self.target_node}, {self.value_node})"

class IndexAccessNode(Node):
    def __init__(self, target_node, index_nodes):
        super().__init__(target_node.pos_start, (index_nodes[-1].pos_end if index_nodes else target_node.pos_end))
        self.target_node = target_node
        self.index_nodes = index_nodes

    def __repr__(self):
        return f"IndexAccess({self.target_node}, {self.index_nodes})"


######################################
# PARSE RESULT
######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        if isinstance(res, ParseResult):
            self.last_registered_advance_count = res.advance_count
            self.advance_count += res.advance_count
            if res.error:
                self.error = res.error
            return res.node
        return res


    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


######################################
# Parser
######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.indent_lvl = 0
        self.exp_indent_lvl = 0
        self.bns_indent_level = 0
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = ParseResult()
        resList = []

        if self.current_tok.type == TT_IDENTIFIER and self.current_tok.value == "run":
            resList.append(self.run_command())
            return resList

        while not res.error and self.current_tok.type != TT_EOF:
            if self.current_tok.type == TT_KEYWORD and self.current_tok.value not in ['function', 'Algo']:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '-', '*', or '/'"))
            else:
                res = self.algo_expr()
                resList.append(res)

        return resList

    def run_command(self):
        res = ParseResult()

        self.advance()
        if self.current_tok.type == TT_STRING:
            fn_token = self.current_tok
            fn_node = StringNode(fn_token)
            self.advance()
            return res.success(CallNode(VarAccessNode(Token(TT_IDENTIFIER, "run", pos_start=fn_token.pos_start, pos_end=fn_token.pos_end)), [fn_node]))
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected string after 'run'"))

    ######################################

    def algo_expr(self):
        res = ParseResult()

        self.skip_newlines()
        self.check_indent_level()
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'Algo':
            self.exp_indent_lvl += 1
            res.register_advancement()
            self.advance()
        elif self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'function':
            self.exp_indent_lvl += 1
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected Algo"))

        res, _ = self.main_expr()
        return res


    def main_expr(self):
        res = ParseResult()

        self.skip_newlines()

        while self.current_tok.type == TT_IDENTIFIER:
            self.check_indent_level()
            res.register(self.var_declaration()[0])
            if res.error: return res, None
            self.skip_newlines()

        self.exp_indent_lvl -= 1

        self.skip_newlines()
        self.check_indent_level()
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'Begin':
            self.exp_indent_lvl += 1
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected Begin")), None

        self.skip_newlines()

        statements = res.register(self.statements())
        if res.error: return res, None

        self.exp_indent_lvl -= 1

        self.check_indent_level()
        if self.current_tok.type == TT_KEYWORD and self.current_tok.value == 'End':
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected End")), None

        self.skip_newlines()
        return res.success(statements), statements

    def skip_newlines(self):
        res = ParseResult()
        while self.current_tok.type == TT_NEWLINE or self.current_tok.type == TT_INDENT:
            if self.current_tok.type == TT_INDENT:
                self.indent_lvl = self.current_tok.value
            res.register_advancement()
            self.advance()

    def check_indent_level(self, must=False):
        res = ParseResult()
        if self.indent_lvl != self.exp_indent_lvl + self.bns_indent_level :
            if self.bns_indent_level == 0 or must == True:
                return res.failure(IndentationError(self.current_tok.pos_start, self.current_tok.pos_end, self.exp_indent_lvl+self.bns_indent_level, self.indent_lvl)), None
            self.bns_indent_level -= 1

    def var_declaration(self, func=False):
        res = ParseResult()
        var_names = []

        var_names.append(self.current_tok)
        res.register_advancement()
        self.advance()
        while self.current_tok.type == TT_COMMA and func== False:
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier")), None
            var_names.append(self.current_tok)
            res.register_advancement()
            self.advance()

        res = self.expected_token(TT_COLON)
        if res.error: return res, None

        if self.current_tok.matches(TT_IDENTIFIER, 'array'):
            res.register_advancement()
            self.advance()
            if not self.current_tok.matches(TT_IDENTIFIER, 'of'):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'of' after 'array'")), None
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_IDENTIFIER or self.current_tok.value not in ["int", "float", "str", "bool"]:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected a valid type (int, float, str ou bool) after 'of'")), None
            var_type = self.current_tok.value
            res.register_advancement()
            self.advance()
            var_type = f"array<{var_type}>"
        else:
            if self.current_tok.type != TT_IDENTIFIER or self.current_tok.value not in ["int", "float", "str", "bool"]:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'int', 'float', 'str' 'bool' or 'array'")), None
            var_type = self.current_tok.value
            res.register_advancement()
            self.advance()

        for var_name in var_names:
            if global_symbol_table.get(var_name.value):
                return res.failure(InvalidSyntaxError(var_name.pos_start, var_name.pos_end, f"Variable '{var_name.value}' is already declared")), None

            global_symbol_table.set(var_name.value, None, var_type)

        return res.success(None), var_names[0]

    ######################################

    def expected_token(self, tok_type, tok_value=None, display_value=None):
        res = ParseResult()
        if not self.current_tok.matches(tok_type, tok_value):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '{display_value or tok_value or tok_type}'"))
        res.register_advancement()
        self.advance()
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start
        tmp_bns_indent_lvl = self.bns_indent_level
        self.skip_newlines()
        self.check_indent_level()

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        while True:
            self.skip_newlines()
            if self.current_tok.matches(TT_KEYWORD, 'End'): break
            self.check_indent_level()
            if self.bns_indent_level < tmp_bns_indent_lvl: break
            statement = res.register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                break
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_end.copy()))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start

        if self.current_tok.matches(TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_end.copy()))

        expr = res.register(self.expr())
        if res.error: return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, identifier, '+', '-', or '('"))

        return res.success(expr)

    def expr(self):
        res = ParseResult()
        start_tok_idx = self.tok_idx

        if self.current_tok.type == TT_IDENTIFIER:
            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            index_nodes = []
            while self.current_tok.type == TT_LSQPAREN:
                res.register_advancement(); self.advance()
                index_expr = res.register(self.expr())
                if res.error: return res
                res2 = self.expected_token(TT_RSQPAREN, None, "]")
                if res2.error: return res2
                index_nodes.append(index_expr)

            if self.current_tok.type == TT_EQ:
                res.register_advancement(); self.advance()
                value_node = res.register(self.expr())
                if res.error: return res
                if index_nodes:
                    target = IndexAccessNode(VarAccessNode(var_name), index_nodes)
                    return res.success(IndexAssignNode(target, value_node))
                else:
                    return res.success(VarAssignNode(var_name, value_node))

            self.tok_idx = start_tok_idx
            self.update_current_tok()

        node = res.register(self.bin_op(
            self.comp_expr,
            ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))
        ))
        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, identifier, '+', '-', '(', or an expression"))
        return res.success(node)


    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, '+', '-', '(' or 'not'"))
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MULT, TT_DIV, TT_FLOORDIV, TT_MOD))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if isinstance(atom, VarAccessNode) and isinstance(global_symbol_table.get(atom.var_name_tok.value), BuiltInFunction):
            func = global_symbol_table.get(atom.var_name_tok.value)

            if self.current_tok.type == TT_NEWLINE:
                return res.success(CallNode(atom, []))
            elif func.name == 'get':
                arg_nodes = []
                arg_nodes.append(self.current_tok)
                if self.current_tok.value in global_symbol_table.types and global_symbol_table.types.get(self.current_tok.value).startswith("array<"):
                    res.register_advancement()
                    self.advance()
                    while self.current_tok.type == TT_LSQPAREN:
                        res.register_advancement()
                        self.advance()
                        arg_nodes.append(self.current_tok)
                        if res.error: return res
                        res.register_advancement()
                        self.advance()
                        res = self.expected_token(TT_RSQPAREN, None, "]")
                        if res.error: return res
                else:
                    res.register_advancement()
                    self.advance()
                    while self.current_tok.type == TT_COMMA:
                        res.register_advancement()
                        self.advance()
                        arg_nodes.append(self.current_tok)
                        if res.error: return res
                        res.register_advancement()
                        self.advance()
                return res.success(CallNode(atom, arg_nodes))
            elif func.name in ('create_array', 'nombreAleatoire', 'size'):
                res = self.expected_token(TT_LPAREN, None, "(")
                if res.error: return res
                arg_nodes = []
                arg_nodes.append(res.register(self.expr()))
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                res = self.expected_token(TT_RPAREN, None, ")")
                if res.error: return res
                return res.success(CallNode(atom, arg_nodes))
            else:
                arg_nodes = []
                arg_nodes.append(res.register(self.expr()))
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                return res.success(CallNode(atom, arg_nodes))

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')', int, float, identifier, '+', '-', or '('"))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ',' or ')'"))

                res.register_advancement()
                self.advance()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_KEYWORD and tok.value == 'true':
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(Token(TT_INT, 1, tok.pos_start, tok.pos_end)))

        elif tok.type == TT_KEYWORD and tok.value == 'false':
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(Token(TT_INT, 0, tok.pos_start, tok.pos_end)))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            var_name = tok
            res.register_advancement()
            self.advance()

            node = VarAccessNode(var_name)

            index_nodes = []
            while self.current_tok.type == TT_LSQPAREN:
                res.register_advancement()
                self.advance()
                index_expr = res.register(self.expr())
                if res.error: return res
                res = self.expected_token(TT_RSQPAREN, None, "]")
                if res.error: return res
                index_nodes.append(index_expr)

            if index_nodes:
                node = IndexAccessNode(node, index_nodes)

            return res.success(node)

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            res = self.expected_token(TT_RPAREN, None, "')'")
            if res.error: return res
            return res.success(expr)

        elif tok.type == TT_LSQPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            res = self.expected_token(TT_RSQPAREN, None, "']'")
            if res.error: return res
            return res.success(expr)

        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', or '('"))


    def if_expr(self):

        res = ParseResult()
        cases = []
        else_case = None

        res = self.expected_token(TT_KEYWORD, 'if')
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        res = self.expected_token(TT_KEYWORD, 'then')

        if self.current_tok.type == TT_NEWLINE:
            self.bns_indent_level += 1
            self.skip_newlines()
            self.check_indent_level(must=True)

            statements = res.register(self.statements())
            if res.error: return res

            cases.append((condition, statements, True))

            all_cases = res.register(self.if_or_else_expr())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))
            all_cases = res.register(self.if_or_else_expr())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success(IfNode(cases, else_case))

    def if_or_else_expr(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()

            if self.current_tok.matches(TT_KEYWORD, 'if'):
                all_cases = res.register(self.if_expr())
                if res.error: return res
                cases, else_case = all_cases.cases, all_cases.else_case
            else:
                if self.current_tok.type == TT_NEWLINE:
                    self.bns_indent_level += 1

                    self.skip_newlines()
                    self.check_indent_level(must=True)

                    statements = res.register(self.statements())
                    if res.error: return res
                    else_case = (statements, True)

                else:
                    expr = res.register(self.statement())
                    if res.error: return res
                    else_case = (expr, False)

        return res.success((cases, else_case))


    def while_expr(self):
        res = ParseResult()

        res = self.expected_token(TT_KEYWORD, 'while')
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == TT_NEWLINE:
            self.bns_indent_level += 1

            self.skip_newlines()
            self.check_indent_level(must=True)

            body = res.register(self.statements())
            if res.error: return res

            return res.success(WhileNode(condition, body, True))

        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected at least one argument in the while loop"))

    def for_expr(self):
        res = ParseResult()

        res = self.expected_token(TT_KEYWORD, 'for')
        if res.error: return res

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        res = self.expected_token(TT_EQ, display_value = '<--')
        if res.error: return res

        start_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'to'):
            to_downto = 0
            res.register_advancement()
            self.advance()
        elif self.current_tok.matches(TT_KEYWORD, 'downto'):
            to_downto = 1
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'to' or 'downto'"))

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == TT_NEWLINE:
            self.bns_indent_level += 1

            self.skip_newlines()
            self.check_indent_level(must=True)

            body = res.register(self.statements())
            if res.error: return res

            return res.success(ForNode(var_name, start_value, end_value, body, to_downto, True))

        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected at least one argument in the for loop"))

    def func_def(self):
        res = ParseResult()

        res = self.expected_token(TT_KEYWORD, 'function')
        if res.error: return res

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"))

        res = self.expected_token(TT_LPAREN)
        if res.error: return res

        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            tmp, arg_name_tok = self.var_declaration(func=True)
            res.register(tmp)
            arg_name_toks.append(arg_name_tok)

            while self.current_tok.type == TT_COMMA:
                self.advance()
                res.register_advancement()
                tmp, arg_name_tok = self.var_declaration(func=True)
                res.register(tmp)
                arg_name_toks.append(arg_name_tok)

        res = self.expected_token(TT_RPAREN, display_value='identifier or )')
        if res.error: return res

        return_type = None
        if self.current_tok.type == TT_COLON:
            self.advance()
            res.register_advancement()

            if self.current_tok.matches(TT_IDENTIFIER, 'array'):
                res.register_advancement()
                self.advance()
                if not self.current_tok.matches(TT_IDENTIFIER, 'of'):
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'of' after 'array'"))
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER or self.current_tok.value not in ["int", "float", "str", "bool"]:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected a valid type (int, float, str, bool) after 'of'"))
                return_type = f"array<{self.current_tok.value}>"
            else:
                if self.current_tok.type != TT_IDENTIFIER or self.current_tok.value not in ["int", "float", "str", "bool"]:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected return type (int, float, str, bool)"))
                return_type = self.current_tok.value
            res.register_advancement()
            self.advance()

        res = self.expected_token(TT_NEWLINE)
        if res.error: return res

        self.exp_indent_lvl += 1
        res, body = self.main_expr()
        if res.error: return res
        self.exp_indent_lvl -= 1

        return res.success(FunctionDefNode(var_name_tok, arg_name_toks, body, return_type))

    ######################################

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)


######################################
# RUNTIME RESULT
######################################

class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return self.error or self.func_return_value


######################################
# VALUES
######################################

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def fdivd_by(self, other):
        return None, self.illegal_operation(other)

    def moded_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(self.pos_start, other.pos_end, 'Illegal operation', self.context)

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by 0', self.context)
            return Number(self.value / other.value), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def fdivd_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by 0', self.context)
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def moded_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by 0', self.context)
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(self.value == other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(self.value != other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(self.value < other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(self.value > other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(self.value <= other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(self.value >= other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(self.value and other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(self.value or other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self.pos_start, other.pos_end)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)

class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        return String(self.value + str(other.value)).set_context(self.context), None

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(other.pos_start, other.pos_end, 'Element at this index could not be retrieved from list because index is out of bounds', self.context)
        else:
            return None, Value.illegal_operation(self, other)

    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'{[x for x in self.elements]}'

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()
        if self.name in ("print", "create_array"):
            return res.success(None)
        if len(args) > len(arg_names):
            return res.failure(RTError(self.pos_start, self.pos_end, f"{len(args) - len(arg_names)} too many arguments passed into '{self.name}'\nExpected {len(arg_names)} arguments, got {len(args)}", self.context))
        elif len(args) < len(arg_names):
            return res.failure(RTError(self.pos_start, self.pos_end, f"{len(arg_names) - len(args)} too few arguments passed into '{self.name}'\nExpected {len(arg_names)} arguments, got {len(args)}", self.context))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        if len(arg_names) == 0:
            exec_ctx.symbol_table.set("args", List(args))
        else:
            self.populate_args(arg_names, args, exec_ctx)

        return res.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_name, return_type):
        super().__init__(name)
        self.body_node = body_node
        self.arg_name = arg_name
        self.return_type = return_type

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_name, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res

        return_value = value or res.func_return_value or Number.null

        if self.return_type:
            if self.return_type.startswith('array<'):
                expected_inner_type = self.return_type[6:-1]
                if not isinstance(return_value, List):
                    return res.failure(RTError(self.pos_start, self.pos_end, f"Expected array<{expected_inner_type}> but got {type(return_value).__name__}", exec_ctx))
                for elem in return_value.elements:
                    if expected_inner_type == 'int' and not isinstance(elem, Number):
                        return res.failure(RTError(self.pos_start, self.pos_end, f"Array elements must be int", exec_ctx))
                    elif expected_inner_type == 'float' and not isinstance(elem, Number):
                        return res.failure(RTError(self.pos_start, self.pos_end, f"Array elements must be float", exec_ctx))
                    elif expected_inner_type == 'str' and not isinstance(elem, String):
                        return res.failure(RTError(self.pos_start, self.pos_end, f"Array elements must be str", exec_ctx))
                    elif expected_inner_type == 'bool' and not isinstance(elem, Number):
                        return res.failure(RTError(self.pos_start, self.pos_end, f"Array elements must be bool", exec_ctx))
                return res.success(return_value)
            elif self.return_type == 'int' and isinstance(return_value, Number):
                return_value = Number(int(return_value.value))
            elif self.return_type == 'float' and isinstance(return_value, Number):
                return_value = Number(float(return_value.value))
            elif self.return_type == 'str' and isinstance(return_value, String):
                return_value = String(str(return_value.value))
            elif self.return_type == 'bool' and isinstance(return_value, Number):
                return_value = Number(1 if return_value.value != 0 else 0)
            else:
                return res.failure(RTError(self.pos_start, self.pos_end, f"Cannot convert '{return_value}' to type '{self.return_type}'", exec_ctx))

            return res.success(return_value)
        else:
            if return_value == None:
                return res.success(return_value)
            else:
                return res.failure(RTError(self.pos_start, self.pos_end, f"Return type not specified'", exec_ctx))

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_name, self.return_type)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        if self.name == 'get':
            if len(args) > 1:
                if global_symbol_table.types.get(args[0].var_name_tok.value).startswith("array<"):
                    idx_list = args[1:]
                    idx_list_int = []
                    for idx_node in idx_list:
                        if not isinstance(idx_node, Number):
                            idx_val = exec_ctx.symbol_table.get(idx_node.var_name_tok.value)
                        elif isinstance(idx_node, VarAccessNode):
                            idx_val = exec_ctx.symbol_table.get(idx_node.var_name_tok.value)
                            if not isinstance(idx_val, Number):
                                return res.failure(RTError(self.pos_start, self.pos_end, "The index must be a number", exec_ctx))
                        else:
                            return res.failure(RTError(self.pos_start, self.pos_end, "Invalid array index", exec_ctx))
                        idx_list_int.append(idx_val)
                    exec_ctx.symbol_table.set("var_name", args[0].var_name_tok.value, idx_list=idx_list_int)
                else:
                    return res.failure(RTError(self.pos_start, self.pos_end, f"{len(args)} too many arguments passed into 'get'\nExpected 1 argument, got {len(args)}", exec_ctx))
            if len(args) == 1:
                exec_ctx.symbol_table.set("var_name", args[0].var_name_tok.value)
        else:
            res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
            if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)

    def no_visit_method(self, args, exec_ctx):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    ######################################

    def execute_create_array(self, exec_ctx):
        res = RTResult()
        dimensions = []
        for arg in exec_ctx.symbol_table.get("args").elements:
            if not isinstance(arg, Number):
                return res.failure(RTError(arg.pos_start, arg.pos_end, "La taille doit être un nombre", exec_ctx))
            dimensions.append(int(arg.value))

        array = ['' for _ in range(dimensions[-1])]
        for i in dimensions[:-1][::-1]:
            array = [array]*i

        def create_nested_array(dimensions):
            if len(dimensions) == 1:
                return ['' for _ in range(dimensions[0])]
            else:
                return [create_nested_array(dimensions[1:]) for _ in range(dimensions[0])]

        array = create_nested_array(dimensions)

        return res.success(List(array))
    execute_create_array.arg_names = []

    def execute_print(self, exec_ctx):
        args = exec_ctx.symbol_table.get("args").elements
        print(" ".join(str(arg) for arg in args), end='')
        return RTResult().success(Number.null)
    execute_print.arg_names = []

    def execute_get(self, exec_ctx, idx=None):

        res = RTResult()
        text = input()

        var_name = exec_ctx.symbol_table.get("var_name")
        if var_name:
            idx_list = None
            if "[" in var_name:
                splt = var_name.find("[")
                var_name, idx_list = var_name[:splt], list(map(int, var_name[splt+1:-1].strip('[]').split(',')))

            var_type = exec_ctx.symbol_table.get_type(var_name)
            if not var_type:
                return res.failure(RTError(self.pos_start, self.pos_end, f"Variable '{var_name}' is not declared", exec_ctx))

            if var_type.startswith("array<"):
                var_type = var_type[6:-1]

            try:
                if var_type == 'int':
                    value = Number(int(text))
                elif var_type == 'float':
                    value = Number(float(text))
                elif var_type == 'str':
                    value = String(text)
                else:
                    return res.failure(RTError(self.pos_start, self.pos_end, f"Unknown type for variable '{var_name}'", exec_ctx))
            except:
                value = String(text)

            global_symbol_table.set(var_name, value, idx_list=idx_list, st=True)
            return res.success(value)

        return res.success(String(text))
    execute_get.arg_names = []

    def execute_run(self, exec_ctx):
        fn = exec_ctx.symbol_table.get('fn')

        if not isinstance(fn, String):
            return RTResult().failure(RTError(self.pos_start, self.pos_end, 'Second argument must be string', exec_ctx))

        fn = fn.value

        try:
            with open(fn, 'r', encoding='utf-8') as f:
                script = f.read()
            f.close()
        except Exception as e:
            return RTResult().failure(RTError(self.pos_start, self.pos_end, f"Failed to load script \"{fn}\"\n" + str(e), exec_ctx))

        _, error = run(fn, script)

        if error:
            return RTResult().failure(RTError(self.pos_start, self.pos_end, f"Failed to finish executing script \"{fn}\"\n" + error.as_string(), exec_ctx))
        return RTResult().success(Number.null)
    execute_run.arg_names = ['fn']

    def execute_SQRT(self, exec_ctx):
        number = exec_ctx.symbol_table.get('value')

        if not isinstance(number, Number):
            return RTResult().failure(RTError(self.pos_start, self.pos_end, f"Argument must be a number, got '{type(number).__name__}'", exec_ctx))

        result = number.value ** (1/2)
        return RTResult().success(Number(result))
    execute_SQRT.arg_names = ['value']

    def execute_nombreAleatoire(self, exec_ctx):
        import random
        a = exec_ctx.symbol_table.get('a')
        b = exec_ctx.symbol_table.get('b')

        if not isinstance(a, Number) or not isinstance(b, Number):
            return RTResult().failure(RTError(self.pos_start, self.pos_end, "Arguments must be numbers", exec_ctx))

        result = random.randint(int(a.value), int(b.value))
        return RTResult().success(Number(result))
    execute_nombreAleatoire.arg_names = ['a', 'b']

    def execute_size(self, exec_ctx):
        T = exec_ctx.symbol_table.get('T')

        if not isinstance(T, List):
            return RTResult().failure(RTError(self.pos_start, self.pos_end, "Argument to 'size' must be an array", exec_ctx))

        return RTResult().success(Number(len(T.elements)))
    execute_size.arg_names = ['T']

BuiltInFunction.print = BuiltInFunction('print')
BuiltInFunction.get = BuiltInFunction('get')
BuiltInFunction.run = BuiltInFunction('run')
BuiltInFunction.SQRT = BuiltInFunction('SQRT')
BuiltInFunction.nombreAleatoire = BuiltInFunction('nombreAleatoire')
BuiltInFunction.size = BuiltInFunction('size')


######################################
# CONTEXT
######################################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


######################################
# SYMBOL TABLE
######################################

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.types = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def get_type(self, name):
        var_type = self.types.get(name, None)
        if var_type == None and self.parent:
            return self.parent.get_type(name)
        return var_type

    def set(self, name, value, var_type=None, idx_list=None, st=False):
        if idx_list and st:
            current = self.symbols[name]
            for idx in idx_list[:-1]:
                if isinstance(current, List):
                    current = current.elements[int(idx)]
                elif isinstance(current, list):
                    current = current[int(idx)]
                else:
                    raise Exception(f"Impossible d'accéder à l'index {idx} sur un type non indexable : {type(current).__name__}")

            final_idx = int(idx_list[-1])
            if isinstance(current, List):
                current.elements[final_idx] = value
            elif isinstance(current, list):
                current[final_idx] = value
            else:
                raise Exception(f"Impossible d'affecter une valeur à l'index {final_idx} sur {type(current).__name__}")
        else:
            if idx_list and not st:
                value += str(idx_list)
            self.symbols[name] = value
            if var_type:
                self.types[name] = var_type

    def remove(self, name):
        del self.symbols[name]
        del self.types[name]


######################################
# INTERPRETER
######################################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ######################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_StringNode(self, node, context):
        return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:

            if context.symbol_table.get_type(var_name):
                return res.success(Number.null)
            return res.failure(RTError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value

        if not context.symbol_table.get_type(var_name):
            return res.failure(RTError(node.pos_start, node.pos_end, f"Variable '{var_name}' is not declared", context))

        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        var_type = context.symbol_table.get_type(var_name)
        if var_type == 'int' and not isinstance(value, Number):
            return res.failure(RTError(node.value_node.pos_start, node.value_node.pos_end, f"Variable '{var_name}' is of type 'int', but got '{type(value).__name__}'", context))
        elif var_type == 'float' and not isinstance(value, Number):
            return res.failure(RTError(node.value_node.pos_start, node.value_node.pos_end, f"Variable '{var_name}' is of type 'float', but got '{type(value).__name__}'", context))
        elif var_type == 'str' and not isinstance(value, String):
            return res.failure(RTError(node.value_node.pos_start, node.value_node.pos_end, f"Variable '{var_name}' is of type 'str', but got '{type(value).__name__}'", context))

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_IndexAssignNode(self, node, context):
        res = RTResult()
        target_val = res.register(self.visit(node.target_node.target_node, context))
        if res.should_return(): return res
        indices = []
        for index_node in node.target_node.index_nodes:
            idx_value = res.register(self.visit(index_node, context))
            if res.should_return(): return res
            if not isinstance(idx_value, Number):
                return res.failure(RTError(index_node.pos_start, index_node.pos_end, "The index must be a number", context))
            indices.append(int(idx_value.value))
        new_value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        current = target_val.elements
        try:
            for idx in indices[:-1]:
                current = current[idx].elements if isinstance(current[idx], List) else current[idx]
            current[indices[-1]] = new_value
        except Exception as e:
            return res.failure(RTError(node.pos_start, node.pos_end, "Out-of-bounds index or invalid format", context))

        return res.success(new_value)


    BIN_OP_FUNCTIONS = {
        TT_PLUS: lambda left, right: left.added_to(right),
        TT_MINUS: lambda left, right: left.subbed_by(right),
        TT_MULT: lambda left, right: left.multed_by(right),
        TT_DIV: lambda left, right: left.dived_by(right),
        TT_FLOORDIV: lambda left, right: left.dived_by(right),
        TT_MOD: lambda left, right: left.moded_by(right),
        TT_POW: lambda left, right: left.powed_by(right),
        TT_EE: lambda left, right: left.get_comparison_eq(right),
        TT_NE: lambda left, right: left.get_comparison_ne(right),
        TT_LT: lambda left, right: left.get_comparison_lt(right),
        TT_GT: lambda left, right: left.get_comparison_gt(right),
        TT_LTE: lambda left, right: left.get_comparison_lte(right),
        TT_GTE: lambda left, right: left.get_comparison_gte(right),
    }

    KEYWORD_OP_FUNCTIONS = {
        'and': lambda left, right: left.anded_by(right),
        'or': lambda left, right: left.ored_by(right)
    }

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

        if node.op_tok.type == TT_KEYWORD:
            result, error = self.KEYWORD_OP_FUNCTIONS[node.op_tok.value](left, right)
        else:
            result, error = self.BIN_OP_FUNCTIONS[node.op_tok.type](left, right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'not'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            return res.success(Number.null if should_return_null else else_value)

        return res.success(Number.null)

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true(): break

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.should_return(): return res

        return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return(): return res

        i = start_value.value

        if node.to_downto == 0:
            condition = lambda: i <= end_value.value
            add = 1
        else:
            condition = lambda: i >= end_value.value
            add = -1

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i+=add
            elements.append(res.register(self.visit(node.body_node, context)))
            if res.should_return(): return res

        return res.success(Number.null if node.should_return_null else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_FunctionDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.return_type).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            if isinstance(arg_node, Token) and arg_node.type == TT_IDENTIFIER:
                arg_value = VarAccessNode(arg_node)
            else:
                arg_value = res.register(self.visit(arg_node, context))
                if res.should_return(): return res
            args.append(arg_value)

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null

        return res.success_return(value)

    def visit_IndexAccessNode(self, node, context):
        res = RTResult()
        current = res.register(self.visit(node.target_node, context))
        if res.should_return(): return res

        try:
            for index_node in node.index_nodes:
                index = res.register(self.visit(index_node, context))
                if res.should_return(): return res
                if not isinstance(index, Number):
                    return res.failure(RTError(index_node.pos_start, index_node.pos_end, "The index must be a number", context))
                idx = int(index.value)
                if isinstance(current, List):
                    current = current.elements[idx]
                elif isinstance(current, list):
                    current = current[idx]
                else:
                    return res.failure(RTError(node.pos_start, node.pos_end, f"Non-indexable type: {type(current).__name__}", context))
        except Exception:
            return res.failure(RTError(node.pos_start, node.pos_end, f"Index access error (probably out of bounds)", context))

        return res.success(current)


######################################
# RUN
######################################

def reset_global_symbol_table():
    global global_symbol_table
    global_symbol_table = SymbolTable()
    global_symbol_table.set("NULL", Number.null)
    global_symbol_table.set("false", Number.false)
    global_symbol_table.set("true", Number.true)
    global_symbol_table.set("create_array", BuiltInFunction('create_array'))
    global_symbol_table.set("print", BuiltInFunction.print)
    global_symbol_table.set("get", BuiltInFunction.get)
    global_symbol_table.set("run", BuiltInFunction.run)
    global_symbol_table.set("SQRT", BuiltInFunction.SQRT)
    global_symbol_table.set("nombreAleatoire", BuiltInFunction.nombreAleatoire)
    global_symbol_table.set("size", BuiltInFunction.size)
    global_symbol_table.set("Pi", Number(3.141592653589793))

def run(fn, text):
    reset_global_symbol_table()
    text += "\n"

    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # Generate AST
    parser = Parser(tokens)
    astL = parser.parse()
    for ast in astL:
        if ast.error: return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    for ast in astL:
        result = interpreter.visit(ast.node, context)

    return result.value, result.error


##### main #####

import sys

def repl():
    while True:
        try:
            text = input('DAUPS >>> ')
        except EOFError:
            break
        if not text.strip():
            continue

        result, error = run('<stdin>', text)
        if error:
            print(error.as_string())
        elif result:
            print('\nprog done')

def run_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
    except IOError as e:
        print(f"Error opening file {path}: {e}")
        return

    result, error = run(path, source)
    if error:
        print(error.as_string())

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Tout premier argument est traité comme fichier
            run_file(sys.argv[1])
        else:
            repl()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        sys.exit(1)
    except Exception:
        print("\nAn unknown error has occurred.")
        print("Please check your code. If the error persists, it might be an issue with the compiler.")
        print("You can report it on GitHub: https://github.com/PerseusShade/DAUPS-ext/issues.")
        print("Feel free to contact me if you're experiencing this unexpected issue — I'll do my best to fix it as soon as possible.")
        sys.exit(1)