from typing import(
    TypedDict,
    Callable,
    Any,
    TypeAlias,
    Literal
)

Asserts: TypeAlias = Literal[
    "equal",
    "notequal",
    "in",
    "notin"
]

class testeType(TypedDict):
    nome      : str
    teste     : Callable
    parametros: dict[str]
    res       : Any
    _assert   : Asserts