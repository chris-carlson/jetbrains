import dataclasses
from typing import Dict, List

from cac.io.json.json_writer import JsonWriter
from cac.path.directory import Directory
from cac.path.file import File
from cac.regex import Regex
from ide import IDES, Ide, get_ide_subdirectory, has_ide
from templates.template import Template, parse_templates

TEMPLATE_FILE_REGEX: Regex = Regex(r'\.xml$')
CONVERTED_TEMPLATE_DIRECTORY: Directory = Directory.get_cwd().join_directory('groups')

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
