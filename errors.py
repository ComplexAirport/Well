import colorama as col


class Error:
    def __init__(self, error_name: str, details: str, start_pos,
                 end_pos, context: str = None, help_text: str = None):
        self.name = error_name
        self.details = details
        self.start = start_pos
        self.end = end_pos
        self.context = context
        self.help = help_text

    def as_string(self):
        '''
        Error message looks like this:
        With help:

        File: main.well, while parsing string (<- context)
            line: 5, column: 8, index: 26
        print "H
               ~~ String was never closed
        SyntaxError: Expected closing quote ""
        '''

        # Add the file and context
        msg: str = (f'File: {col.Fore.YELLOW}{self.start.loc}{col.Style.RESET_ALL}' +
                    (f', {col.Fore.MAGENTA}{self.context}{col.Style.RESET_ALL}\n' if self.context else '\n'))

        # Add the position information
        msg += f'\tline: {col.Fore.BLUE}{self.start.line}{col.Style.RESET_ALL}'
        msg += f', column: {col.Fore.BLUE}{self.start.col}{col.Style.RESET_ALL}'
        msg += f', index: {col.Fore.BLUE}{self.start.idx}{col.Style.RESET_ALL} to {col.Fore.BLUE}{self.end.idx}{col.Style.RESET_ALL}\n'

        # Add the error line and the underlined error, and help message if it isn't None
        msg += self.start.get_line_text() + '\n'

        msg += ' ' * (self.start.col - 1)
        msg += col.Fore.RED + '~' * (self.end.idx - self.start.idx) + col.Style.RESET_ALL
        msg += col.Fore.MAGENTA + ' ' + self.help + '\n' + col.Style.RESET_ALL if self.help else '\n'

        msg += f'{self.name}: {self.details}'

        return msg


class SyntaxErrorException(Error):
    def __init__(self, details: str, start_pos, end_pos,
                 context: str = None, help_text: str = None):
        super().__init__('Syntax-Error', details, start_pos, end_pos, context, help_text)


class ValueErrorException(Error):
    def __init__(self, details: str, start_pos, end_pos,
                 context: str = None, help_text: str = None):
        super().__init__('Value-Error', details, start_pos, end_pos, context, help_text)


class UndefinedErrorException(Error):
    def __init__(self, details: str, start_pos, end_pos,
                 context: str = None, help_text: str = None):
        super().__init__('Undefined-Error', details, start_pos, end_pos, context, help_text)


class UnsupportedOperationException(Error):
    def __init__(self, details: str, start_pos, end_pos,
                 context: str = None, help_text: str = None):
        super().__init__('Unsupported-Operation', details, start_pos, end_pos, context, help_text)


class ErrorStream:
    def __init__(self, *errors):
        self.__stream: list = errors or []

    def add_error(self, error: Error):
        self.__stream.append(error)

    def as_string(self):
        result = '\n\n'.join([i.as_string() for i in self.__stream])

        return result

    @property
    def is_error(self):
        return len(self.__stream) != 0
