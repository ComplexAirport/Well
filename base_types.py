import copy
from decimal import Decimal

from errors import UnsupportedOperationException

operators = [
    '+', '-', '/', '*', '^', '%',
    '>', '<', 'is', 'or', 'and'
]

bool_values = 'true', 'false'
bool_true = 'true'
bool_false = 'false'
null_value = 'null'
special_vars = bool_true, bool_false, null_value


class Any:
    def __init__(self, type_name: str, value, start_pos, end_pos):
        self.type_name = type_name
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return f'{self.type_name}:{self.value}'

    def copy(self):
        return Any(self.type_name, copy.copy(self.value), self.start_pos.copy(), self.end_pos.copy())

    # Base Operators
    def operator_add(self, other): ...

    def operator_sub(self, other): ...

    def operator_mul(self, other): ...

    def operator_div(self, other): ...

    def operator_mod(self, other): ...

    def operator_pow(self, other): ...

    # Boolean operators
    def operator_bigger(self, other): ...

    def operator_smaller(self, other): ...

    def operator_equal(self, other): ...

    def operator_or(self, other): ...

    def operator_and(self, other): ...


class Number(Any):
    def __init__(self, value: Decimal, start_pos, end_pos):
        super().__init__(TypeNames.number_t, value, start_pos, end_pos)

    def operator_add(self, other):
        if isinstance(other, Number):
            return Number(
                self.value + other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_sub(self, other):
        if isinstance(other, Number):
            return Number(
                self.value - other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_mul(self, other):
        if isinstance(other, Number):
            return Number(
                self.value * other.value, self.start_pos, other.end_pos
            )
        # If number is multiplied by string
        elif isinstance(other, String):
            return String(
                int(self.value) * other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_div(self, other):
        if isinstance(other, Number):
            return Number(
                self.value / other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_mod(self, other):
        if isinstance(other, Number):
            return Number(
                self.value % other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_pow(self, other):
        if isinstance(other, Number):
            return Number(
                self.value ** other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_bigger(self, other):
        if isinstance(other, Number):
            return Bool(
                self.value > other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_smaller(self, other):
        if isinstance(other, Number):
            return Bool(
                self.value < other.value, self.start_pos, other.end_pos
            )
        else:
            return UnsupportedOperationException(
                f'Unsupported operation + between {self.type_name} and {other.type_name}',
                self.start_pos, other.end_pos, 'when adding two objects'
            )

    def operator_equal(self, other):
        if isinstance(other, Number):
            return Bool(
                self.value == other.value, self.start_pos, other.end_pos
            )
        else:
            return Bool(False, self.start_pos, other.end_pos)

    def operator_and(self, other):
        if isinstance(other, Any):
            return Bool(bool(self.value) and bool(other.value), self.start_pos, other.end_pos)
        else:
            return None

    def operator_or(self, other):
        if isinstance(other, Any):
            return Bool(bool(self.value) or bool(other.value), self.start_pos, other.end_pos)
        else:
            return None


class String(Any):
    def __init__(self, value: str, start_pos, end_pos):
        super().__init__(TypeNames.string_t, value, start_pos, end_pos)


class ReferenceType(Any):
    def __init__(self, name: str, start_pos, end_pos):
        self.name = name
        super().__init__(TypeNames.ref_t, name, start_pos, end_pos)


class Null(Any):
    def __init__(self, start_pos, end_pos):
        super().__init__(TypeNames.null_t, None, start_pos, end_pos)

    def __repr__(self):
        return null_value


class Bool(Any):
    def __init__(self, value: bool, start_pos, end_pos):
        super().__init__(TypeNames.bool_t, value, start_pos, end_pos)

    def __repr__(self):
        return bool_true if self.value else bool_false


class Array(Any):
    def __init__(self, value: list, start_pos, end_pos):
        self.__list = value
        super().__init__(TypeNames.array_t, value, start_pos, end_pos)

    def __repr__(self):
        return f'[{", ".join([i.__repr__() for i in self.__list])}]'


class TypeNames:
    number_t = 'number'
    string_t = 'string'
    ref_t = 'reference'
    func_t = 'function'
    bool_t = 'bool'
    array_t = 'array'
    null_t = 'null'


# Other

class Variable:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class Constant:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.__value = value

    @property
    def value(self):
        return self.__value.copy()


class Function:
    def __init__(self, name: str, code: Any):
        self.name = name
        self.code = code


class Namespace:
    def __init__(self, variables: list[Variable] = None, constants: list[Constant] = None,
                 functions: list[Function] = None):
        self.variables = variables or []
        self.constants = constants or []
        self.functions = functions or []

    def __search_by_name(self, name: str, search_in):
        for item in search_in:
            if item.name == name:
                return item
        return None

    def search_var_by_name(self, name: str):
        return self.__search_by_name(name, self.variables)

    def search_const_by_name(self, name: str):
        return self.__search_by_name(name, self.constants)

    def search_func_by_name(self, name: str):
        return self.__search_by_name(name, self.functions)

    def search_by_name(self, name: str):
        return (
                self.search_var_by_name(name) or self.search_const_by_name(name) or self.search_func_by_name(name)
        )

    def search_not_func(self, name: str):
        return self.search_var_by_name(name) or self.search_const_by_name(name)

    def exists(self, name: str):
        return True if self.search_by_name(name) else False

    def remove_by_name(self, name: str):
        pass

    def add_var(self, var: Variable):
        if isinstance(var, Variable):
            self.variables.append(var)
        else:
            raise Exception

    def add_const(self, const: Constant):
        if isinstance(const, Constant):
            self.constants.append(const)
        else:
            raise Exception
