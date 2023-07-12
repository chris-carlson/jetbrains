from dataclasses import dataclass
from typing import List

@dataclass
class Template:
    name: str
    description: str
    value: str
    variables: List['Variable']

@dataclass
class Variable:
    name: str
    expression: str
    default_value: str
    always_stop: bool
