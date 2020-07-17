import re
import sys

from collections import Counter, defaultdict
from copy import deepcopy

# Used for debugging
# from utils import console_print_of
import special_characters as sc


"""
Data Modification
"""


def remove_chairs(apartment_init, list_pos_chairs, except_chair):
    apartment = deepcopy(apartment_init)
    for pair in list_pos_chairs:
        if pair != except_chair:
            i, j = pair
            apartment[i][j] = ' '
    return apartment


def change_pos(apartment, i, j, new_i, new_j):
    apartment[i][j], apartment[new_i][new_j] = apartment[new_i][new_j], apartment[i][j]
    i, j = new_i, new_j
    return i, j


"""
Vertical check
"""


def is_room_on_same_column(apartment, i, j):
    chair = apartment[i][j]
    col = [apartment[k][j] for k in range(len(apartment))]
    col_no_space = list(filter(lambda e: e != ' ', col))
    return col_no_space[col_no_space.index(chair)+1] not in sc.sep_chars or col_no_space[col_no_space.index(chair)-1] not in sc.sep_chars


def find_room_on_same_column(apartment, i, j):
    col = [apartment[k][j] for k in range(len(apartment))]
    i_up, i_down = i-1, i+1
    # Find a character of the room
    while (col[i_up] in sc.no_room_chars) and (col[i_down] in sc.no_room_chars):
        if col[i_up] not in sc.sep_chars:
            i_up -= 1
        if col[i_down] not in sc.sep_chars:
            i_down += 1
    i_room = i_up if col[i_up] not in sc.no_room_chars else i_down

    # Build the string of the room name
    row_str = ''.join(apartment[i_room])
    # Be in the middle of the name
    if apartment[i_room][j] == '(':
        j += 1
    if apartment[i_room][j] == ')':
        j -= 1
    # Initialize as a simple letter
    room_of_chair = row_str[j]
    j_left, j_right = j-1, j+1
    while (row_str[j_left] != '(') or (row_str[j_right] != ')'):
        if row_str[j_left] != '(':
            room_of_chair = row_str[j_left] + room_of_chair
            j_left -= 1
        if row_str[j_right] != ')':
            room_of_chair = room_of_chair + row_str[j_right]
            j_right += 1
    return room_of_chair


"""
Horizontal check
"""


def is_room_on_same_row(apartment, i, j):
    chair = apartment[i][j]
    row_no_space = list(filter(lambda e: e != ' ', apartment[i]))
    return row_no_space[row_no_space.index(chair)+1] == '(' or row_no_space[row_no_space.index(chair)-1] == ')'


def find_room_on_same_row(apartment, i, j):
    row = apartment[i]
    j_left, j_right = j-1, j+1
    while row[j_left] != ')' and row[j_right] != '(':
        if row[j_left] not in sc.sep_chars:
            j_left -= 1
        if row[j_right] not in sc.sep_chars:
            j_right += 1
    side = 'right' if row[j_right] == '(' else 'left'
    if side == 'right':
        j_word = j_right + 1
        room_of_chair = ''
        while row[j_word] != ')':
            room_of_chair = room_of_chair + row[j_word]
            j_word += 1
    elif side == 'left':
        j_word = j_left - 1
        room_of_chair = ''
        while row[j_word] != '(':
            room_of_chair = row[j_word] + room_of_chair
            j_word -= 1
    return room_of_chair


"""
Move strategies
"""


def update_stack_checkpoints(stack_checkpoints, new_open_corners, direction_when_found):
    for open_corner in new_open_corners:
        if open_corner:  # Not None
            i, j = open_corner
            if direction_when_found == 'down':
                stack_checkpoints.append({'coord': (i+1, j), 'exp_type': 'h'})
                stack_checkpoints.append({'coord': (i+1, j), 'exp_type': 'v'})
            elif direction_when_found == 'up':
                stack_checkpoints.append({'coord': (i-1, j), 'exp_type': 'h'})
                stack_checkpoints.append({'coord': (i-1, j), 'exp_type': 'v'})
            if direction_when_found == 'left':
                stack_checkpoints.append({'coord': (i, j-1), 'exp_type': 'v'})
                stack_checkpoints.append({'coord': (i, j-1), 'exp_type': 'h'})
            if direction_when_found == 'right':
                stack_checkpoints.append({'coord': (i, j+1), 'exp_type': 'v'})
                stack_checkpoints.append({'coord': (i, j+1), 'exp_type': 'h'})


def explore_horizontal_moves(apartment, i_start: int, j_start: int, stack_checkpoints: list):
    i, j = i_start, j_start

    # First step: one vertical check at the starting point
    if is_room_on_same_column(apartment, i, j):
        return find_room_on_same_column(apartment, i, j), (i, j)

    # Second step: Move horizontally

    # Initialize moving up
    direction = 'up'

    while True:
        open_corners = find_open_corner_horizontal_check(
            apartment, i, j, direction)

        if open_corners != [None, None]:
            update_stack_checkpoints(stack_checkpoints=stack_checkpoints,
                                     new_open_corners=open_corners,
                                     direction_when_found=direction)

        # If the room name is not found in the row, we move vertically
        if not is_room_on_same_row(apartment, i=i, j=j):
            # If we reached the top of the room ...
            if direction == 'up' and apartment[i-1][j] in sc.sep_chars:
                # ...we set the direction to down for the next step...
                direction = 'down'
                # ...and get back to the initial position
                i, j = change_pos(apartment, i=i, j=j,
                                  new_i=i_start, new_j=j)

            # If we reached the bottom of the room ...
            if direction == 'down' and apartment[i+1][j] in sc.sep_chars:
                # The research has been unsuccessful
                return 'not found', (i, j)

            # We move up
            if direction == 'up':
                i, j = change_pos(apartment, i=i,
                                  j=j, new_i=i-1, new_j=j)

            # We move down
            elif direction == 'down':
                i, j = change_pos(apartment, i=i,
                                  j=j, new_i=i+1, new_j=j)

        # We found the room name
        else:
            coord = (i, j)
            return find_room_on_same_row(apartment, i, j), (i, j)


def explore_vertical_moves(apartment, i_start: int, j_start: int,  stack_checkpoints: list):
    """TODO To complete
    """
    i, j = i_start, j_start

    # First step: one horizontal check at the starting point
    if is_room_on_same_row(apartment, i=i, j=j):
        return find_room_on_same_row(apartment, i, j), (i, j)

    # Second step: Move horizontally

    # Initialize moving up
    direction = 'left'
    while True:
        open_corners = find_open_corner_vertical_check(
            apartment, i, j, direction)

        if open_corners != [None, None]:
            update_stack_checkpoints(stack_checkpoints=stack_checkpoints,
                                     new_open_corners=open_corners,
                                     direction_when_found=direction)

        # If the room name is not found in the column, we move horizontally
        if not is_room_on_same_column(apartment, i, j):

            # If we reached the left side of the room ...
            if direction == 'left' and apartment[i][j-1] in sc.sep_chars:
                # ...we set the direction to down for the next step...
                direction = 'right'
                # ...and get back to the initial position
                i, j = change_pos(apartment, i=i, j=j,
                                  new_i=i, new_j=j_start)

            # If we reached the right side of the room ...
            if direction == 'right' and apartment[i][j+1] in sc.sep_chars:
                # The research has been unsuccessful
                return 'not found', (i, j)

            # We move left
            if direction == 'left':
                i, j = change_pos(apartment, i=i,
                                  j=j, new_i=i, new_j=j-1)

            # We move right
            elif direction == 'right':
                i, j = change_pos(apartment, i=i,
                                  j=j, new_i=i, new_j=j+1)

        # We found the room name
        else:
            return find_room_on_same_column(apartment, i, j), (i, j)


def find_open_corner_horizontal_check(apartment, i, j, direction):
    row = apartment[i]
    j_left, j_right = j-1, j+1
    while not ((row[j_left] in sc.sep_chars) and (row[j_right] in sc.sep_chars)):
        if row[j_left] not in sc.sep_chars:
            j_left -= 1
        if row[j_right] not in sc.sep_chars:
            j_right += 1
    # Possible open corner left and right
    open_corners = [None, None]
    if direction == 'down':
        if row[j_left] == '+' and apartment[i+1][j_left] == ' ':
            open_corners[0] = (i, j_left)
        if row[j_right] == '+' and apartment[i+1][j_right] == ' ':
            open_corners[1] = (i, j_right)

    elif direction == 'up':
        if row[j_left] == '+' and apartment[i-1][j_left] == ' ':
            open_corners[0] = (i, j_left)
        if row[j_right] == '+' and apartment[i-1][j_right] == ' ':
            open_corners[1] = (i, j_right)
    return open_corners


def find_open_corner_vertical_check(apartment, i, j, direction):
    col = [apartment[k][j] for k in range(len(apartment))]
    i_up, i_down = i-1, i+1
    while not((col[i_up] in sc.sep_chars) and (col[i_down] in sc.sep_chars)):
        if col[i_up] not in sc.sep_chars:
            i_up -= 1
        if col[i_down] not in sc.sep_chars:
            i_down += 1
    # Possible open corners up and down
    open_corners = [None, None]
    if direction == 'left':
        if col[i_up] == '+' and apartment[i_up][j-1] == ' ':
            open_corners[0] = (i_up, j)
        if col[i_down] == '+' and apartment[i_down][j-1] == ' ':
            open_corners[1] == (i_down, j)
    elif direction == 'right':
        if col[i_up] == '+' and apartment[i_up][j+1] == ' ':
            open_corners[0] = (i_up, j)
        if col[i_down] == '+' and apartment[i_down][j+1] == ' ':
            open_corners[1] == (i_down, j)
    return open_corners


def explore(apartment, exp_type, i, j, stack_checkpoints):
    if exp_type == 'h':
        return explore_horizontal_moves(apartment, i, j, stack_checkpoints)
    elif exp_type == 'v':
        return explore_vertical_moves(apartment, i, j, stack_checkpoints)


def search_room(apartment, coord, max_iterations=100):
    room_of_chair = 'not found'
    stack_checkpoints = [
        {'coord': coord, 'exp_type': 'h'},
        {'coord': coord, 'exp_type': 'v'}
    ]
    count = 0
    i, j = coord
    while room_of_chair == 'not found':

        # Handle possible errors
        count += 1
        if count > max_iterations:
            raise MiscException('Too many iterations')
        if not stack_checkpoints:
            raise Error(
                'The stack_checkpoints variable is empty and the room name is unfounded')

        checkpoint = stack_checkpoints.pop()
        exp_type = checkpoint['exp_type']
        new_i, new_j = checkpoint['coord']
        i, j = change_pos(apartment, i=i,
                          j=j, new_i=new_i, new_j=new_j)
        room_of_chair, (i, j) = explore(
            apartment, exp_type, i, j, stack_checkpoints)
    return room_of_chair


"""
Final Output generation
"""


def group_dict_apartment_chairs(dict_apartment_chairs):

    grouped_dict_apartment_chairs = {}
    for room_name in dict_apartment_chairs.keys():
        grouped_dict_apartment_chairs[room_name] = dict(
            Counter(dict_apartment_chairs[room_name]))
        # Add 0s for the chairs that a given room doesn't have
        for chair in sc.chairs:
            if chair not in grouped_dict_apartment_chairs[room_name].keys():
                grouped_dict_apartment_chairs[room_name][chair] = 0

    return grouped_dict_apartment_chairs


def make_total_dict_result(grouped_dict_apartment_chairs):
    dict_total_chairs = {chair: 0 for chair in sc.chairs}
    for room_name in grouped_dict_apartment_chairs.keys():
        room_chairs = grouped_dict_apartment_chairs[room_name]
        for chair in room_chairs.keys():
            dict_total_chairs[chair] += room_chairs[chair]
    return dict(dict_total_chairs)


def check_total_chairs(dict_total_chairs, apartment_string):
    total_chairs_from_input = {chair: Counter(apartment_string)[chair]
                               for chair in Counter(apartment_string) if chair in sc.chairs}
    return dict_total_chairs == total_chairs_from_input


def print_element_console(grouped_dict_final_output, element):
    dict_chairs_of_element = grouped_dict_final_output[element]

    print(f'{element}:')
    str_line = ''
    for chair in sc.chairs:
        str_line += f'{chair}: {dict_chairs_of_element[chair]}, '
    # Do not print the final ',' and ' '
    print(str_line[:-2])


def print_output_console(grouped_dict_final_output):
    grouped_dict_final_output = grouped_dict_final_output.copy()

    # We first print the total result
    print_element_console(grouped_dict_final_output, element='total')
    del grouped_dict_final_output['total']

    # We then loop over the apartment names in the alphabetical order

    for room_name in sorted(grouped_dict_final_output.keys()):
        print_element_console(grouped_dict_final_output, element=room_name)


def run_solution(file_path):
    # rooms.txt (i.e the apartment)
    with open('rooms.txt', 'r') as f:
        apartment_string = f.read()
    apartment_init = [list([j for j in i.split('\n')][0])
                      for i in apartment_string.splitlines()]
    # Future useful objects

    # Dictionary: keys: a chair position, values: its name
    dict_pos_chairs = {}
    for i, row in enumerate(apartment_init):
        for j, element in enumerate(row):
            if element in sc.chairs:
                dict_pos_chairs[(i, j)] = element

    # List of postitions of chairs ordered vertically and horizontally
    list_pos_chairs = list(dict_pos_chairs.keys())
    list_pos_chairs.sort(key=lambda x: (x[0], x[1]))

    dict_apartment_chairs = defaultdict(list)
    for k, coord in enumerate(list_pos_chairs):
        i, j = coord
        chair = apartment_init[i][j]
        apartment = remove_chairs(
            apartment_init, list_pos_chairs, except_chair=coord)
        room_of_chair = search_room(apartment, coord)
        # Save it
        dict_apartment_chairs[room_of_chair].append(chair)

    grouped_dict_apartment_chairs = group_dict_apartment_chairs(
        dict_apartment_chairs)
    dict_total_chairs = make_total_dict_result(
        grouped_dict_apartment_chairs)

    grouped_dict_final_output = grouped_dict_apartment_chairs
    grouped_dict_final_output['total'] = dict_total_chairs

    print_output_console(grouped_dict_final_output)


if __name__ == "__main__":
    file_path = sys.argv[1]
    run_solution(file_path=file_path)
