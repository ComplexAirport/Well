import string


class Position:
    def __init__(self, location: str, text: str, idx=-1, col=-1, line=1):
        self.loc = location
        self.text = text
        self.idx = idx
        self.col = col
        self.line = line
        self.char = None
        self.advance()

    def __repr__(self):
        return f'Position({self.loc} {self.line}:{self.col})'

    def advance(self, n: int = 1):
        if self.idx + n >= len(self.text):
            self.char = None
            return

        self.idx += n
        self.char = self.text[self.idx]

        if self.char == '\n':
            self.col = 0
            self.line += 1
        else:
            self.col += 1

    def next_char(self, n=1):
        return None if self.idx + n >= len(self.text) else self.text[self.idx + n]

    def get_line_text(self):
        return self.text.split('\n')[self.line - 1]

    def copy(self):
        return Position(self.loc, self.text, self.idx, self.col, self.line)

    @staticmethod
    def null_pos(location='', text=''): # TODO: remove
        return Position(location, text)


class Token:
    def __init__(self, token_type: str, token_value: str, start_pos: Position, end_pos: Position):
        self.type = token_type
        self.value = token_value
        self.start = start_pos
        self.end = end_pos

    def __repr__(self):
        return f'{self.type}: {self.value}'


class TokenTypes:
    number = 'number'
    string = 'string'
    word = 'word'

    brace_expr = 'brace-expr'
    paren_expr = 'paren-expr'
    bracket_expr = 'bracket-expr'
    angle_expr = 'angle-expr'


class StringToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.string, value, start_pos, end_pos)


class NumberToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.number, value, start_pos, end_pos)


class WordToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.word, value, start_pos, end_pos)


class ParenExprToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.paren_expr, value, start_pos, end_pos)


class BraceExprToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.brace_expr, value, start_pos, end_pos)


class BracketExprToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.bracket_expr, value, start_pos, end_pos)


class AngleExprToken(Token):
    def __init__(self, value: str, start_pos: Position, end_pos: Position):
        super().__init__(TokenTypes.angle_expr, value, start_pos, end_pos)


class Triggers:
    bracket_expr = '[', ']'
    brace_expr = '{', '}'
    paren_expr = '(', ')'
    angle_expr = '<', '>'

    dot_digits = '.' + string.digits
    comment_char = '#'

    special_chars = [
        '=', ':', '@', '$', '.',
        '+', '-', '/', '*', '^', '%', '&'
    ]
