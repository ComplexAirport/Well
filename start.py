import decimal

import base_types
import errors
import lexer


def main():
    with open('code.txt', 'r') as f:
        text = f.read()

    execute_command(text)


def check_error(e: errors.ErrorStream):
    if e.is_error:
        print(e.as_string())
        exit()

def execute_command(cmd: str):
    error_stream = errors.ErrorStream()

    namespace = base_types.Namespace()

    code = ''' (PI=10) + (PI=20)'''

    result = lexer.make_tokens(code, '<stdin>', error_stream, namespace)
    if error_stream.is_error:
        print(error_stream.as_string())
    else:
        for i in result:
            print(i)



if __name__ == '__main__':
    main()
