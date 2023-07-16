from dataclasses import dataclass
from typing import Dict, List

from cac.io.xml.xml_element import XmlElement
from cac.io.xml.xml_reader import XmlReader
from cac.path.file import File
from templates.value import convert_value

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

SUBSTITUTIONS: Dict[str, str] = {'&#10;': '\\n', '    ': '\t', '&quot;': '\"', '&amp': '&', '&lt;': '<', '&gt;': '>'}

def parse_templates(file: File) -> List[Template]:
    reader: XmlReader = XmlReader(file.path)
    template_set: XmlElement = reader.read_root()
    return [parse_template(template) for template in template_set.children]

def parse_template(template_element: XmlElement) -> Template:
    name: str = template_element.attributes['name']
    description: str = template_element.attributes['description']
    value: str = template_element.attributes['value']
    converted_value: str = convert_value(value, SUBSTITUTIONS)
    variable_elements: List[XmlElement] = template_element.get_all_by_name('variable')
    variables: List[Variable] = [parse_variable(variable_element) for variable_element in variable_elements]
    return Template(name, description, converted_value, variables)

def parse_variable(variable_element: XmlElement) -> Variable:
    name: str = variable_element.attributes['name']
    expression: str = variable_element.attributes['expression']
    default_value: str = variable_element.attributes['defaultValue']
    always_stop: bool = True if variable_element.attributes['alwaysStopAt'] == 'true' else False
    return Variable(name, expression, default_value, always_stop)
