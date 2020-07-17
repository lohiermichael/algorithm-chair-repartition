# Names of the chairs
# We save it as a list because we would like to print out the final result in this order of chairs
# as in the task_en.txt
chairs = ['W', 'P', 'S', 'C']
# Characters that delimit the apartment
sep_chars = {'\\', '|', '/', '+', '-'}

# Characters that are not in a room name: '(', ')' or and small letter
# The chair letters aside (because removed at each iteration), this is what we have left
no_room_chars = {'\\', '|', '/', '+', '-', ' '}
