from pathlib import Path


def console_print_of(apartment) -> None:
    list_of_strings = list(map(''.join, apartment))
    print('\n'.join(list_of_strings))


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent
