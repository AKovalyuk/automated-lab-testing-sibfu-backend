from dataclasses import dataclass


@dataclass
class Language:
    id: int
    name: str
    judge0id: int


LANGUAGES = {
    1: Language(id=1, name="Python 3.8", judge0id=71),
    2: Language(id=2, name="Bash 5.0", judge0id=46),
}
ARCHIVED = {}
