from collections import Counter, defaultdict
import re
from copy import deepcopy
from utils import print_of

chairs = {'W', 'P', 'S', 'C'}
sep_chars = {'\\', '|', '/', '+', '-'}
no_room_chars = {'\\', '|', '/', '+', '-', ' '}

with open('rooms.txt', 'r') as f:
    rooms_string = f.read()

rooms_init = [list([j for j in i.split('\n')][0])
              for i in rooms_string.splitlines()]

dict_pos_chairs = {}
for i, row in enumerate(rooms_init):
    for j, element in enumerate(row):
        if element in chairs:
            dict_pos_chairs[(i, j)] = element

list_pos_chairs = list(dict_pos_chairs.keys())
list_pos_chairs.sort(key=lambda x: (x[0], x[1]))


"""
Data Modification
"""


def remove_chairs(rooms_init, except_chair):
    rooms = deepcopy(rooms_init)
    for pair in list_pos_chairs:
        if pair != except_chair:
            i, j = pair
            rooms[i][j] = ' '
    return rooms


def change_pos(rooms, i, j, new_i, new_j):
    rooms[i][j], rooms[new_i][new_j] = rooms[new_i][new_j], rooms[i][j]
    i, j = new_i, new_j
    return i, j


"""
Vertical check
"""


def is_in_room_same_column(i, j):
    chair = rooms[i][j]
    col = [rooms[k][j] for k in range(len(rooms))]
    col_no_space = list(filter(lambda e: e != ' ', col))
    return col_no_space[col_no_space.index(chair)+1] not in sep_chars or col_no_space[col_no_space.index(chair)-1] not in sep_chars


def find_room_on_same_column(rooms, i, j):
    chair = rooms[i][j]
    col = [rooms[k][j] for k in range(len(rooms))]
    i_up, i_down = i-1, i+1
    # Find a character of the room
    while (col[i_up] in no_room_chars) and (col[i_down] in no_room_chars):
        if col[i_up] not in sep_chars:
            i_up -= 1
        if col[i_down] not in sep_chars:
            i_down += 1
    i_room = i_up if col[i_up] not in no_room_chars else i_down

    # Build the string of the room name
    row_str = ''.join(rooms[i_room])
    # Be in the middle of the name
    if rooms[i_room][j] == '(':
        j += 1
    if rooms[i_room][j] == ')':
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


def is_in_room_same_row(rooms, i, j):
    chair = rooms[i][j]
    row_no_space = list(filter(lambda e: e != ' ', rooms[i]))
    return row_no_space[row_no_space.index(chair)+1] == '(' or row_no_space[row_no_space.index(chair)-1] == ')'


def find_room_on_same_row(rooms, i, j):
    chair = rooms[i][j]
    row = rooms[i]
    j_left, j_right = j-1, j+1
    while row[j_left] != ')' and row[j_right] != '(':
        if row[j_left] not in sep_chars:
            j_left -= 1
        if row[j_right] not in sep_chars:
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


def explore_horizontal_moves(i_start: int, j_start: int, stack_checkpoints: list):
    i, j = i_start, j_start

    # First step: one vertical check at the starting point
    if is_in_room_same_column(i, j):
        return find_room_on_same_column(rooms, i, j), (i, j)

    # Second step: Move horizontally

    # Initialize moving up
    direction = 'up'

    while True:
        open_corners = find_open_corner_horizontal_check(i, j, direction)

        if open_corners != [None, None]:
            update_stack_checkpoints(stack_checkpoints=stack_checkpoints,
                                     new_open_corners=open_corners,
                                     direction_when_found=direction)

        # If the room name is not found in the row, we move vertically
        if not is_in_room_same_row(rooms=rooms, i=i, j=j):
            # If we reached the top of the room ...
            if direction == 'up' and rooms[i-1][j] in sep_chars:
                # ...we set the direction to down for the next step...
                direction = 'down'
                # ...and get back to the initial position
                i, j = change_pos(rooms=rooms, i=i, j=j,
                                  new_i=i_start, new_j=j)

            # If we reached the bottom of the room ...
            if direction == 'down' and rooms[i+1][j] in sep_chars:
                # The research has been unsuccessful
                return 'not found', (i, j)

            # We move up
            if direction == 'up':
                i, j = change_pos(rooms=rooms, i=i, j=j, new_i=i-1, new_j=j)

            # We move down
            elif direction == 'down':
                i, j = change_pos(rooms=rooms, i=i, j=j, new_i=i+1, new_j=j)

        # We found the room name
        else:
            coord = (i, j)
            return find_room_on_same_row(rooms, i, j), (i, j)


def explore_vertical_moves(i_start: int, j_start: int,  stack_checkpoints: list):
    """TODO To complete
    """
    i, j = i_start, j_start

    # First step: one horizontal check at the starting point
    if is_in_room_same_row(rooms=rooms, i=i, j=j):
        return find_room_on_same_row(i, j), (i, j)

    # Second step: Move horizontally

    # Initialize moving up
    direction = 'left'
    while True:
        open_corners = find_open_corner_vertical_check(i, j, direction)

        if open_corners != [None, None]:
            update_stack_checkpoints(stack_checkpoints=stack_checkpoints,
                                     new_open_corners=open_corners,
                                     direction_when_found=direction)

        # If the room name is not found in the column, we move horizontally
        if not is_in_room_same_column(i, j):

            # If we reached the left side of the room ...
            if direction == 'left' and rooms[i][j-1] in sep_chars:
                # ...we set the direction to down for the next step...
                direction = 'right'
                # ...and get back to the initial position
                i, j = change_pos(rooms=rooms, i=i, j=j,
                                  new_i=i, new_j=j_start)

            # If we reached the right side of the room ...
            if direction == 'right' and rooms[i][j+1] in sep_chars:
                # The research has been unsuccessful
                return 'not found', (i, j)

            # We move left
            if direction == 'left':
                i, j = change_pos(rooms=rooms, i=i, j=j, new_i=i, new_j=j-1)

            # We move right
            elif direction == 'right':
                i, j = change_pos(rooms=rooms, i=i, j=j, new_i=i, new_j=j+1)

        # We found the room name
        else:
            return find_room_on_same_column(rooms, i, j), (i, j)


def find_open_corner_horizontal_check(i, j, direction):
    row = rooms[i]
    j_left, j_right = j-1, j+1
    while not ((row[j_left] in sep_chars) and (row[j_right] in sep_chars)):
        if row[j_left] not in sep_chars:
            j_left -= 1
        if row[j_right] not in sep_chars:
            j_right += 1
    # Possible open corner left and right
    open_corners = [None, None]
    if direction == 'down':
        if row[j_left] == '+' and rooms[i+1][j_left] == ' ':
            open_corners[0] = (i, j_left)
        if row[j_right] == '+' and rooms[i+1][j_right] == ' ':
            open_corners[1] = (i, j_right)

    elif direction == 'up':
        if row[j_left] == '+' and rooms[i-1][j_left] == ' ':
            open_corners[0] = (i, j_left)
        if row[j_right] == '+' and rooms[i-1][j_right] == ' ':
            open_corners[1] = (i, j_right)
    return open_corners


def find_open_corner_vertical_check(i, j, direction):
    col = [rooms[k][j] for k in range(len(rooms))]
    i_up, i_down = i-1, i+1
    while not((col[i_up] in sep_chars) and (col[i_down] in sep_chars)):
        if col[i_up] not in sep_chars:
            i_up -= 1
        if col[i_down] not in sep_chars:
            i_down += 1
    # Possible open corners up and down
    open_corners = [None, None]
    if direction == 'left':
        if col[i_up] == '+' and rooms[i_up][j-1] == ' ':
            open_corners[0] = (i_up, j)
        if col[i_down] == '+' and rooms[i_down][j-1] == ' ':
            open_corners[1] == (i_down, j)
    elif direction == 'right':
        if col[i_up] == '+' and rooms[i_up][j+1] == ' ':
            open_corners[0] = (i_up, j)
        if col[i_down] == '+' and rooms[i_down][j+1] == ' ':
            open_corners[1] == (i_down, j)
    return open_corners


def explore(exp_type, i, j, stack_checkpoints):
    if exp_type == 'h':
        return explore_horizontal_moves(i, j, stack_checkpoints)
    elif exp_type == 'v':
        return explore_vertical_moves(i, j, stack_checkpoints)


def search_room(rooms, coord):
    room_of_chair = 'not found'
    stack_checkpoints = [
        {'coord': coord, 'exp_type': 'h'},
        {'coord': coord, 'exp_type': 'v'}
    ]
    count = 0
    i, j = coord
    while room_of_chair == 'not found' and count < 10:
        print(stack_checkpoints)
        count += 1
        if not stack_checkpoints:
            exp_type = 'h' if exp_type == 'v' else 'v'
            stack_checkpoints.append({'coord': (i, j), 'exp_type': exp_type})
        checkpoint = stack_checkpoints.pop()
        exp_type = checkpoint['exp_type']
        new_i, new_j = checkpoint['coord']
        i, j = change_pos(rooms=rooms, i=i, j=j, new_i=new_i, new_j=new_j)
        room_of_chair, (i, j) = explore(exp_type, i, j, stack_checkpoints)
    return room_of_chair


# print_of(rooms_init)
dict_rooms_chairs = defaultdict(list)
for k, coord in enumerate(list_pos_chairs):
    if k + 1 == 6:
        i, j = coord
        chair = rooms_init[i][j]
        rooms = remove_chairs(rooms_init, except_chair=coord)
        room_of_chair = search_room(rooms, coord)
        # Save it
        dict_rooms_chairs[room_of_chair].append(chair)
print(dict_rooms_chairs)
