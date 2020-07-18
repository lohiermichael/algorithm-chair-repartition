from pathlib import Path


def get_project_root() -> Path:
    """Returns project root folder."""
    return '' + str(Path(__file__).parent.parent)


def notebook_print_of(file_path) -> list:
    """Display a room in a notebook"""
    # rooms.txt (i.e the apartment)
    with open(file_path, 'r') as f:
        apartment_string = f.read()
    apartment_init = [list([j for j in i.split('\n')][0])
                      for i in apartment_string.splitlines()]
    return list(map(lambda L: ''.join(L), apartment_init))


if __name__ == "__main__":
    print(get_project_root())
