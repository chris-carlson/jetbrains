from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Dict, List, Optional

from cac.io.json.json_reader import JsonReader
from cac.io.xml.xml_element import XmlElement
from cac.io.xml.xml_writer import XmlWriter
from cac.path.directory import Directory
from cac.path.file import File
from ide import IDES, Ide, get_ide_subdirectory, has_ide

@dataclass
class Shortcut:
    code: str
    key1: str = ''
    key2: str = ''
    ide: str = ''

class Modifier(StrEnum):
    META = auto()
    CTRL = auto()

MODIFIERS: List[Modifier] = [Modifier.META, Modifier.CTRL]

SYMBOLS: Dict[str, str] = {'[': 'open_bracket', ']': 'close_bracket', '-': 'minus', '=': 'equals'}

PLATFORMS: Dict[Modifier, str] = {Modifier.META: 'Mac', Modifier.CTRL: 'Windows'}
PARENTS: Dict[Modifier, str] = {Modifier.META: 'Mac OS X 10.5+', Modifier.CTRL: '$default'}

def is_applicable(shortcut: Shortcut, ide: Ide) -> bool:
    return len(shortcut.ide) == 0 or shortcut.ide == ide.value

def create_action(shortcut: Shortcut, modifier: Modifier) -> XmlElement:
    keyboard_shortcut: Optional[XmlElement] = create_keyboard_shortcut(shortcut, modifier)
    keyboard_shortcuts: List[XmlElement] = [keyboard_shortcut] if keyboard_shortcut is not None else []
    return XmlElement('action', {'id': shortcut.code}, keyboard_shortcuts)

def create_keyboard_shortcut(shortcut: Shortcut, modifier: Modifier) -> Optional[XmlElement]:
    if len(shortcut.key1) > 0:
        key1: str = SYMBOLS[shortcut.key1] if shortcut.key1 in SYMBOLS else shortcut.key1.lower()
        keystrokes: Dict[str, str] = {'first-keystroke': '{modifier} {key}'.format(modifier=modifier.value, key=key1)}
        if len(shortcut.key2) > 0:
            key2: str = SYMBOLS[shortcut.key2] if shortcut.key2 in SYMBOLS else shortcut.key2.lower()
            keystrokes['second-keystroke'] = key2
        return XmlElement('keyboard-shortcut', keystrokes)
    return None

def create_keymap(actions: List[XmlElement], modifier: Modifier) -> XmlElement:
    parent: str = PARENTS[modifier]
    return XmlElement('keymap', {'version': '1', 'name': 'CAC', 'parent': parent}, actions)

def get_platform_directory(modifier: Modifier, ide: Ide) -> Directory:
    if modifier == Modifier.CTRL:
        return Directory.get_cwd()
    return get_ide_subdirectory(ide, 'keymaps')

def get_platform_file(directory: Directory, modifier: Modifier, ide: Ide) -> File:
    if modifier == Modifier.META:
        return directory.join_file('CAC.xml')
    return directory.join_file('CAC {ide}.xml'.format(ide=ide))

ides: List[Ide] = [ide for ide in IDES if has_ide(ide)]
reader: JsonReader = JsonReader('shortcuts.json')
# noinspection PyArgumentList
shortcuts: List[Shortcut] = [Shortcut(**shortcut) for shortcut in reader.read_array()]
for ide in ides:
    for key_modifier in MODIFIERS:
        modifier_actions: List[XmlElement] = [create_action(shortcut, key_modifier) for shortcut in shortcuts if
                is_applicable(shortcut, ide)]
        keymap_element: XmlElement = create_keymap(modifier_actions, key_modifier)
        platform_directory: Directory = get_platform_directory(key_modifier, ide)
        platform_file: File = get_platform_file(platform_directory, key_modifier, ide)
        writer: XmlWriter = XmlWriter(platform_file.path)
        writer.write(keymap_element, True)
        writer.close()
