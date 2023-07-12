import dataclasses
from typing import Dict, List

from cac.io.json.json_writer import JsonWriter
from cac.io.xml.xml_element import XmlElement
from cac.io.xml.xml_reader import XmlReader
from cac.path.directory import Directory
from cac.path.file import File
from cac.regex import Regex
from ide import IDES, Ide, get_ide_subdirectory, has_ide
from templates.template import Template, Variable
from templates.value import convert_value

TEMPLATE_FILE_REGEX: Regex = Regex(r'\.xml$')
CONVERTED_TEMPLATE_DIRECTORY: Directory = Directory.get_cwd().join_directory('groups')

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

ides: List[Ide] = [ide for ide in IDES if has_ide(ide)]
original_template_directories: List[Directory] = [get_ide_subdirectory(ide, 'templates') for ide in ides]
for original_template_directory in original_template_directories:
    original_template_files: List[File] = original_template_directory.get_files(regex=TEMPLATE_FILE_REGEX)
    for original_template_file in original_template_files:
        templates: List[Template] = parse_templates(original_template_file)
        serialized_templates: List[Dict[str, str]] = [dataclasses.asdict(template) for template in templates]
        converted_template_file: File = CONVERTED_TEMPLATE_DIRECTORY.join_file(original_template_file.stem, '.json')
        writer: JsonWriter = JsonWriter(converted_template_file.path)
        writer.write(serialized_templates)
        writer.close()
