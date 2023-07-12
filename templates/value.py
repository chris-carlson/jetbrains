from typing import Dict

def convert_value(value: str, substitutions: Dict[str, str]) -> str:
    converted_value: str = value[:]
    for original_fragment, converted_fragment in substitutions.items():
        converted_value = converted_value.replace(original_fragment, converted_fragment)
    return converted_value
