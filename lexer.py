import decimal

import base_types
from base_types import *
from errors import *
from tokens import *


class Lexer:
    def __init__(self, filename, text, error_stream: ErrorStream = None):
        self.filename = filename
        self.text = text

        self.pos = Position(filename, text)
        self.start_pos = self.pos.copy()

        self.error_stream = error_stream if error_stream else ErrorStream()

        self.tokens = []
        self.tok = ''

    def start(self) -> list:
        is_comment = False
        while self.pos.char is not None:
            self.tok += self.pos.char

            if self.pos.char in ' \r\t\n':
                self.check_for_word()
                self.pos.advance()
                self.set_start_pos()
                continue

            # Append some special characters like =, : immediately
            elif self.pos.char in Triggers.special_chars:
                self.check_for_word()
                self.set_start_pos()
                self.generate_special_char()
                self.set_start_pos()

            # Generate a number token
            elif self.pos.char in Triggers.dot_digits and len(self.tok) == 1:
                self.set_start_pos()
                self.generate_number()
                self.set_start_pos()
                continue  # Continue because while parsing the number the pointer is already on the next character

            # Generate the string token
            elif self.pos.char in ['"', "'"]:
                self.set_start_pos()
                self.generate_string()
                self.set_start_pos()

            # Generate multi-line string token (newlines allowed)
            elif self.pos.char == '`':
                self.set_start_pos()
                self.generate_multiline_string()
                self.set_start_pos()

            elif self.pos.char == Triggers.paren_expr[0]:  # () expression
                self.check_for_word()
                self.set_start_pos()
                self.add_paren_expr()
                self.set_start_pos()

            elif self.pos.char == Triggers.bracket_expr[0]:  # [] expression
                self.check_for_word()
                self.set_start_pos()
                self.add_bracket_expr()
                self.set_start_pos()

            elif self.pos.char == Triggers.brace_expr[0]:  # {} expression
                self.set_start_pos()
                self.add_brace_expr()
                self.set_start_pos()

            elif self.pos.char == Triggers.angle_expr[0]:  # <> expression
                self.check_for_word()
                self.set_start_pos()
                self.add_angle_expr()
                self.set_start_pos()

            if self.error_stream.is_error:
                break

            self.pos.advance()

        self.check_for_word(eof=True)

        return self.tokens

    def set_start_pos(self):  # Set self.start_pos to current position:
        self.tok = ''
        self.start_pos = self.pos.copy()

    def check_for_word(self, eof: bool = False):
        token_before: str = self.get_sliced_token() if not eof else self.tok

        if token_before != '':
            self.tokens.append(WordToken(token_before, self.start_pos, self.pos))

    def get_sliced_token(self, n: int = 1):
        return self.tok[:-n]

    def generate_number(self):
        # 400'hello'
        if self.pos.char == '.':
            dot_count = 1
            number = '0.'
        else:
            dot_count = 0
            number = self.pos.char

        self.pos.advance()

        while self.pos.char is not None and self.pos.char in Triggers.dot_digits + '_':
            if self.pos.char == '.':
                dot_count += 1

            if self.pos.char != '_':
                number += self.pos.char

            self.pos.advance()

        if dot_count > 1:
            self.error_stream.add_error(SyntaxErrorException(
                f'Got too much dots in number ({dot_count})',
                self.start_pos, self.pos, 'while parsing number',
                'Replace to ' + (number[::-1].replace('.', '', number.count('.') - 1))[::-1]
            ))
            return

        if number.endswith('.'):
            number = number[:-1]

        self.tokens.append(NumberToken(number, self.start_pos, self.pos))

    def generate_string(self):
        close_char: str = self.pos.char
        escape: bool = False
        string = ''

        self.pos.advance()

        while self.pos.char is not None:
            if self.pos.char == close_char and not escape:
                break

            elif self.pos.char == '\n':
                self.error_stream.add_error(SyntaxErrorException(
                    'Newline not allowed in a single-line string, use multi-line string instead',
                    self.start_pos, self.pos,
                    'while parsing string',
                    '`' + string + col.Style.RESET_ALL + ' ...'
                ))

            elif self.pos.char == '\\':
                escape = True

            elif escape and self.pos.char != close_char:
                # TODO: add match expr here after new python version

                if self.pos.char == 'n':
                    string += '\n'
                elif self.pos.char == 't':
                    string += '\t'
                elif self.pos.char == 'b':
                    string += '\b'
                elif self.pos.char == 'f':
                    string += '\f'
                elif self.pos.char == 'r':
                    string += '\r'
                elif self.pos.char == '\\':
                    string += '\\'
                else:
                    string += '\\' + self.pos.char

                escape = False

            elif escape and self.pos.char == close_char:
                string += close_char

            else:
                string += self.pos.char

            self.pos.advance()
        else:
            self.error_stream.add_error(SyntaxErrorException(
                'String was never closed',
                self.start_pos, self.pos,
                'while parsing string',
                close_char
            ))
            return

        self.tokens.append(StringToken(string, self.start_pos, self.pos))

    def generate_multiline_string(self):
        close_char = '`'
        close_char = self.pos.char
        escape = False
        string = ''

        self.pos.advance()

        while self.pos.char is not None:
            if self.pos.char == close_char and not escape:
                break

            elif self.pos.char == '\\':
                escape = True

            elif escape:
                if self.pos.char == close_char:
                    string += close_char
                else:
                    string += '\\' + self.pos.char
                escape = False

            else:
                string += self.pos.char

            self.pos.advance()
        else:
            self.error_stream.add_error(SyntaxErrorException(
                'String was never closed',
                self.start_pos, self.pos,
                'while parsing string',
                close_char
            ))
            return

        self.tokens.append(StringToken(string, self.start_pos, self.pos))

    def generate_special_char(self):
        self.tokens.append(WordToken(self.pos.char, self.start_pos, self.pos))

    def get_wrapped_expr(self, open_close):
        open_char, close_char = open_close
        result = ''
        if self.pos.char != open_char:
            return result

        self.pos.advance()

        block_depth: int = 1
        is_string: bool = False
        str_char: str = ''

        while self.pos.char is not None:
            if is_string and self.pos.char == str_char:
                is_string = False
                str_char = ''

            elif not is_string:
                if self.pos.char in ['"', "'", '`']:
                    is_string = True
                    str_char = self.pos.char

                elif self.pos.char == close_char:
                    block_depth -= 1
                    if block_depth == 0:
                        break

                elif self.pos.char == open_char:
                    block_depth += 1

            result += self.pos.char
            self.pos.advance()

        if block_depth != 0:
            self.error_stream.add_error(SyntaxErrorException(
                f'Expected {block_depth} more {close_char}-s, expression not fully closed',
                self.start_pos, self.pos,
                f'while inside {open_char}{close_char} expression (depth: {block_depth})',
                close_char * block_depth
            ))

        return result

    def add_expr_instance(self, cls, open_close):
        inner: str = self.get_wrapped_expr(open_close)
        if inner is not None:
            self.tokens.append(cls(inner, self.start_pos, self.pos))

    def add_paren_expr(self):
        self.add_expr_instance(ParenExprToken, Triggers.paren_expr)

    def add_bracket_expr(self):
        self.add_expr_instance(BracketExprToken, Triggers.bracket_expr)

    def add_brace_expr(self):
        self.add_expr_instance(BraceExprToken, Triggers.brace_expr)

    def add_angle_expr(self):
        self.add_expr_instance(AngleExprToken, Triggers.angle_expr)


class Parser:
    def __init__(self, tokens: list, error_stream: ErrorStream, namespace: base_types.Namespace):
        self.tokens = tokens
        self.phases: list = [
            ProOperatorPhase,
            BaseTypeConverterPhase,
            FunctionCallPhase,
            VariablePlacerPhase,
            OperatorPhase,
            VarDeclarationPhase,
            VariablePlacerPhase
        ]

        self.error_stream = error_stream
        self.namespace = namespace

        self.current_result = self.tokens.copy()

    def start(self):
        for phase in self.phases:
            parser = phase(self.current_result, self.error_stream, self.namespace)
            result = parser.start()
            if self.error_stream.is_error:
                break
            else:
                self.current_result = result

        return self.current_result


class ParsingPhase:
    def __init__(self, tokens, error_stream: ErrorStream, namespace: base_types.Namespace):
        self.tokens = tokens
        self.error_stream = error_stream
        self.namespace = namespace

        self.idx = -1
        self.token = None
        self.result = []
        self.advance()

    def start(self):
        pass

    def advance(self, n=1):
        if self.idx + n >= len(self.tokens):
            self.token = None
            return
        else:
            self.idx += 1
            self.token = self.tokens[self.idx]

    def get_next(self, n=1):
        k = self.idx + n
        if k < len(self.tokens):
            return self.tokens[k]
        else:
            return None


class ProOperatorPhase(ParsingPhase):  # Phase where expressions inside parentheses are executed
    def start(self):
        while self.token is not None:
            if isinstance(self.token, ParenExprToken):
                tokens_inside = make_tokens(self.token.value, self.token.start.loc, self.error_stream, self.namespace)

                if self.error_stream.is_error:
                    return
                else:
                    for tok in tokens_inside:
                        self.result.append(tok)
            else:
                self.result.append(self.token)

            self.advance()

        return self.result


class BaseTypeConverterPhase(ParsingPhase):
    def start(self):
        while self.token is not None:
            converted = self.token_to_type(self.token)

            if self.error_stream.is_error:
                return

            self.result.append(converted)
            self.advance()
        return self.result

    def token_to_type(self, token: Token):
        next_tok = self.get_next()

        if isinstance(token, WordToken):
            if token.value in base_types.bool_values:
                return base_types.Bool(True if token.value == base_types.bool_true else False, token.start,
                                       token.end)

            elif token.value == 'ref' and isinstance(next_tok, WordToken):
                self.idx += 1
                return base_types.ReferenceType(next_tok.value, token.start, next_tok.end)

            elif token.value == 'null':
                return base_types.Null(token.start, token.end)

            else:
                return token

        elif isinstance(token, NumberToken):
            dec = decimal.Decimal(token.value)
            return base_types.Number(dec, token.start, token.end)

        elif isinstance(token, StringToken):
            return base_types.String(token.value, token.start, token.end)

        # Generate an array
        elif isinstance(token, BracketExprToken):
            arr_tokens = make_tokens(token.value, token.start.loc, self.error_stream, self.namespace)
            if arr_tokens is not None:
                return base_types.Array(arr_tokens, token.start, token.end)

        else:
            return token


class FunctionCallPhase(ParsingPhase):  # Phase where all function calls are executed
    def start(self):
        while self.token is not None:
            next_tok = self.get_next()

            if isinstance(self.token, WordToken) and isinstance(next_tok, ParenExprToken):
                get_func = self.namespace.search_func_by_name(self.token.value)
                if not get_func:
                    self.error_stream.add_error(UndefinedErrorException(
                        f'Name \'{self.token.value}\' is not defined',
                        self.token.start, next_tok.end, 'when function call was found'
                    ))
                else:
                    self.idx += 1  # TODO: function is called here, the code should be executed

            else:
                self.result.append(self.token)

            if self.error_stream.is_error:
                break

            self.advance()
        return self.result


class VariablePlacerPhase(ParsingPhase):
    def start(self):
        while self.token is not None:

            if isinstance(self.token, WordToken) and (var := self.namespace.search_not_func(self.token.value)):
                self.result.append(var.value)
            else:
                self.result.append(self.token)

            self.advance()

        return self.result


class OperatorPhase(ParsingPhase):  # Phase where expressions with operators like 1 + 1 are executed
    def start(self):
        while self.token is not None:
            next1: Token = self.get_next(1)
            next2: base_types.Any = self.get_next(2)

            # Apply the overloaded operators like +, -, /, *, ^, %
            if self.can_apply_operator(self.token, next1, next2):
                op = next1.value

                if op == '+':
                    self.apply_operator(self.token, next1, next2, self.token.operator_add)
                elif op == '-':
                    self.apply_operator(self.token, next1, next2, self.token.operator_sub)
                elif op == '*':
                    self.apply_operator(self.token, next1, next2, self.token.operator_mul)
                elif op == '/':
                    self.apply_operator(self.token, next1, next2, self.token.operator_div)
                elif op == '%':
                    self.apply_operator(self.token, next1, next2, self.token.operator_mod)
                elif op == '^':
                    self.apply_operator(self.token, next1, next2, self.token.operator_pow)
                elif op == '>':
                    self.apply_operator(self.token, next1, next2, self.token.operator_bigger)
                elif op == '<':
                    self.apply_operator(self.token, next1, next2, self.token.operator_smaller)
                elif op == 'is':
                    self.apply_operator(self.token, next1, next2, self.token.operator_equal)
                elif op == 'and':
                    self.apply_operator(self.token, next1, next2, self.token.operator_and)
                elif op == 'or':
                    self.apply_operator(self.token, next1, next2, self.token.operator_or)

                self.idx += 2

            else:
                self.result.append(self.token)

            if self.error_stream.is_error:
                return

            self.advance()

        return self.result

    def can_apply_operator(self, left, operator: Token, right):
        return (
                isinstance(left, base_types.Any) and
                isinstance(operator, WordToken) and
                operator.value in base_types.operators and
                isinstance(right, base_types.Any)
        )

    def apply_operator(self, left, operator, right, func):
        result = func(right)

        if isinstance(result, Error):
            self.error_stream.add_error(result)

        elif not result:
            self.error_stream.add_error(UnsupportedOperationException(
                f'Unsupported operation {operator.value} between types {left.type_name} and {right.type_name}',
                left.start_pos, right.end_pos
            ))

        else:
            self.result.append(result)


class VarDeclarationPhase(ParsingPhase):
    def start(self):
        while self.token is not None:
            # Check for constant declaration
            next_tok = self.get_next()
            if isinstance(self.token, WordToken) and self.token.value == 'const':
                self.declare_const()

            elif isinstance(next_tok, WordToken) and next_tok.value == '=':
                self.declare_var()

            else:
                self.result.append(self.token)

            if self.error_stream.is_error:
                return

            self.advance()

        return self.result

    def declare_const(self):
        var_name = self.get_next()

        self.check_declaration(var_name, is_const=True)

        if self.error_stream.is_error:
            return

        # Now parse the value
        equal_sign = self.get_next(2)
        if not isinstance(equal_sign, WordToken) or equal_sign.value != '=':
            self.namespace.add_const(base_types.Constant(
                var_name.value, base_types.Null(self.token.start, var_name.end)
            ))
            self.result.append(Null(self.token.start, var_name.end))
            self.advance()
            return

        var_value = self.get_next(3)

        self.check_var_value(var_value, var_name, equal_sign)
        if self.error_stream.is_error:
            return

        self.namespace.remove_by_name(var_name.value)

        self.namespace.add_const(Constant(var_name.value, var_value))
        self.result.append(var_value)

        for _ in range(3):
            self.advance()

    def declare_var(self):
        self.check_declaration(self.token)
        if self.error_stream.is_error:
            return

        equal_sign = self.get_next()
        var_value = self.get_next(2)
        self.check_var_value(var_value, self.token, equal_sign)
        if self.error_stream.is_error:
            return

        self.namespace.add_var(Variable(self.token.value, var_value))
        self.result.append(var_value)

        for _ in range(2):
            self.advance()

    def check_declaration(self, var, is_const=False):
        # If there is nothing next to const keyword
        if is_const and not var:
            self.error_stream.add_error(SyntaxErrorException(
                'Expected some name after const keyword',
                self.token.start, self.token.end,
                'when constant declaration was found',
                f'foo = '
            ))
            return

        # If var is not a word, for example it is string or number
        elif not isinstance(var, WordToken):
            if isinstance(var, Token):
                type_name = var.type
                start_pos = var.start
                end_pos = var.end
            else:
                type_name = var.type_name
                start_pos = var.start_pos
                end_pos = var.end_pos
            # TODO: add array unpacking here
            if isinstance(var, base_types.String):
                hint = var.value
            elif isinstance(var, base_types.Number):
                hint = f'foo_{var.value}'
            else:
                hint = 'foo'

            self.error_stream.add_error(SyntaxErrorException(
                'Constant' if is_const else 'Variable' + f' name should be a word, not {type_name}',
                start_pos, end_pos,
                'when declaration was found',
                hint
            ))
            return

        # Check variable name to be valid
        elif not self.check_var_name(var.value):
            self.error_stream.add_error(SyntaxErrorException(
                f'Name {var.value} is not valid for a constant or variable',
                var.start, var.end,
                'while parsing declaration name'
            ))
            return

        # Check value to be in special variables
        elif var.value in base_types.special_vars:
            self.error_stream.add_error(SyntaxErrorException(
                f'Cannot assign to literal ({var.value})',
                var.start, var.end,
                'while parsing declaration name'
            ))
            return

        # Check if name is already a constant
        elif self.namespace.search_const_by_name(var.value):
            self.error_stream.add_error(ValueErrorException(
                f'Name {var.value} is already taken by a constant',
                var.start, var.end, 'when declaring ' + 'constant' if is_const else 'variable'
            ))

    def check_var_value(self, var_value, var_name, equal_sign):
        if not isinstance(var_value, Any) or var_value is None:
            self.error_stream.add_error(SyntaxErrorException(
                'Expected some value after = sign',
                var_name.start, equal_sign.end,
                'while assigning value to constant',
                '= null'
            ))

    def check_var_name(self, name: str):
        if name[0] in string.digits:
            return False
        for char in name:
            if char not in string.digits + string.ascii_letters + '$_':
                return False
        return True


def make_tokens(text: str, file_name: str, error_stream: ErrorStream, namespace: base_types.Namespace):
    lex = Lexer(file_name, text, error_stream)
    tokens = lex.start()

    if error_stream.is_error:
        return

    parser = Parser(tokens, error_stream, namespace)
    result = parser.start()

    return None if error_stream.is_error else result
