import glob

from script import *
import pytest

from utils import get_project_root

ROOT = get_project_root()


def find_total_dictionary_with_algorithm(file_path):
    with open(file_path, 'r') as f:
        apartment_string = f.read()
    '''Step 1: Read and transform the txt file'''
    apartment_init = [list([j for j in i.split('\n')][0])
                      for i in apartment_string.splitlines()]

    '''Step 2: Locate the chairs in the apartment'''

    # Dictionary: keys: a chair position, values: its name
    dict_pos_chairs = {}
    for i, row in enumerate(apartment_init):
        for j, element in enumerate(row):
            if element in sc.chairs:
                dict_pos_chairs[(i, j)] = element

    # List of postitions of chairs ordered vertically and horizontally
    list_pos_chairs = list(dict_pos_chairs.keys())
    list_pos_chairs.sort(key=lambda x: (x[0], x[1]))

    '''Step 3: Find the room of each chair'''

    dict_rooms_chairs = defaultdict(list)
    for k, coord in enumerate(list_pos_chairs):
        i, j = coord
        chair = apartment_init[i][j]

        '''Step 3.1: Temporarily remove the other chairs in the apartment'''
        apartment = remove_chairs(
            apartment_init, list_pos_chairs, except_chair=coord)

        '''Step 3.2: Search the room of a chair'''
        room_of_chair = search_room(apartment, coord)

        '''Step 3.3: Save the result'''
        dict_rooms_chairs[room_of_chair].append(chair)

    '''Step 4: Transform the result and display it'''

    grouped_dict_rooms_chairs = group_dict_rooms_chairs(
        dict_rooms_chairs)
    dict_total_chairs = make_total_dict_result(
        grouped_dict_rooms_chairs)

    return dict_total_chairs


def find_total_dict_without_algorithm(file_path):
    with open(file_path, 'r') as f:
        apartment_string = f.read()
    counter_string = Counter(apartment_string)
    total_chairs_from_input = {chair: counter_string[chair]
                               for chair in counter_string if chair in sc.chairs}
    # Add 0s for the chairs that a given room doesn't have
    for chair in sc.chairs:
        if chair not in total_chairs_from_input.keys():
            total_chairs_from_input[chair] = 0
    return total_chairs_from_input


def list_file_paths():
    for file_path in glob.glob(f'{ROOT}/test_rooms/*.txt'):
        yield file_path


@pytest.mark.parametrize('file_path', list_file_paths())
def test_match_total_chairs(file_path):
    assert find_total_dictionary_with_algorithm(
        file_path) == find_total_dict_without_algorithm(file_path)
