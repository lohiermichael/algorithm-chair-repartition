def console_print_of(apartment) -> None:
    list_of_strings = list(map(''.join, apartment))
    print('\n'.join(list_of_strings))
