from enum import StrEnum
from typing import List

from cac.path.directory import Directory
from cac.regex import Regex
from cac.sorter import ListSorter

class Ide(StrEnum):
    INTELLIJ = 'IdeaIC'
    WEBSTORM = 'WebStorm'
    PYCHARM = 'PyCharm'

IDES: List[Ide] = [Ide.INTELLIJ, Ide.WEBSTORM, Ide.PYCHARM]

def has_ide(ide: Ide) -> bool:
    ide_directories: List[Directory] = get_ide_directories(ide)
    return len(ide_directories) > 0

def get_ide_subdirectory(ide: Ide, subdirectory_name: str) -> Directory:
    ide_directories: List[Directory] = get_ide_directories(ide)
    sorted_ide_directories: List[Directory] = ListSorter.sort(ide_directories, lambda directory: directory.name)
    latest_ide_directory: Directory = sorted_ide_directories[-1]
    return latest_ide_directory.join_directory(subdirectory_name)

def get_ide_directories(ide: Ide) -> List[Directory]:
    jetbrains_directory: Directory = Directory.get_home().join_directories(
        ['Library', 'Application Support', 'JetBrains'])
    ide_regex: Regex = Regex(r'^{ide}'.format(ide=ide.value))
    return jetbrains_directory.find_directories(regex=ide_regex)
