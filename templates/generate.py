from typing import Dict, List

from dacite import from_dict

from cac.collections.multi_dict import MultiDict
from cac.io.json.json_reader import JsonReader
from cac.io.xml.xml_element import XmlElement
from cac.io.xml.xml_writer import XmlWriter
from cac.path.directory import Directory
from cac.path.file import File
from ide import IDES, Ide, get_ide_subdirectory, has_ide
from templates.template import Template, Variable

CONVERTED_TEMPLATE_DIRECTORY: Directory = Directory.get_cwd().join_directory('templates')
IDE_GROUPS: MultiDict[Ide, str] = MultiDict[Ide, str](
    [(Ide.INTELLIJ, 'java'), (Ide.INTELLIJ, 'json'), (Ide.INTELLIJ, 'xml'), (Ide.WEBSTORM, 'html'),
            (Ide.WEBSTORM, 'json'), (Ide.WEBSTORM, 'sass'), (Ide.WEBSTORM, 'typescript'), (Ide.WEBSTORM, 'xml'),
            (Ide.PYCHARM, 'json'), (Ide.PYCHARM, 'python'), (Ide.PYCHARM, 'xml')])

TAB_SPACES: Dict[str, int] = {'html': 2, 'java': 4, 'json': 2, 'python': 4, 'sass': 2, 'typescript': 2, 'xml': 2}
CONTEXTS: Dict[str, str] = {'html': 'HTML', 'json': 'JSON', 'python': 'Python', 'sass': 'CSS',
        'typescript': 'TypeScript'}

def parse_template(template: Template, group: str) -> XmlElement:
    option: XmlElement = XmlElement('option', {'name': CONTEXTS[group], 'value': 'true'})
    context: XmlElement = XmlElement('context', children=[option])
    generated_variables: List[XmlElement] = [parse_variable(converted_variable) for converted_variable in
            template.variables]
    tab_length: int = TAB_SPACES[group]
    converted_value: str = template.value.replace('\t', ' ' * tab_length)
    return XmlElement('template',
        {'name': template.name, 'value': converted_value, 'description': template.description, 'toReformat': 'false',
                'toShortenFQNames': 'true'}, generated_variables + [context])

def parse_variable(variable: Variable) -> XmlElement:
    return XmlElement('variable',
        {'name': variable.name, 'expression': variable.expression, 'defaultValue': variable.default_value,
                'alwaysStopAt': str(variable.always_stop)})

ides: List[Ide] = [ide for ide in IDES if has_ide(ide)]
for ide in ides:
    template_groups: List[str] = IDE_GROUPS[ide]
    for template_group in template_groups:
        converted_template_file_name: str = '{group}.json'.format(group=template_group)
        if not CONVERTED_TEMPLATE_DIRECTORY.has_file(converted_template_file_name):
            continue
        converted_template_file: File = CONVERTED_TEMPLATE_DIRECTORY.get_file(converted_template_file_name)
        reader: JsonReader = JsonReader(converted_template_file.path)
        # noinspection PyTypeChecker
        converted_templates: List[Template] = [from_dict(Template, template) for template in reader.read_array()]
        generated_templates: List[XmlElement] = [parse_template(template, template_group) for template in
                converted_templates]
        template_set: XmlElement = XmlElement('templateSet', {'group': template_group}, generated_templates)
        templates_directory: Directory = get_ide_subdirectory(ide, 'templates')
        generated_template_file: File = templates_directory.join_file(template_group, '.xml')
        writer: XmlWriter = XmlWriter(generated_template_file.path)
        writer.write(template_set, True)
        writer.close()
