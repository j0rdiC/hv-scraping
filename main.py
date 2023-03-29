#!/bin/env python3

from simple_term_menu import TerminalMenu
from src.scrapers.gaviotas import main as exec_gaviotas
from src.scrapers.riu import main as exec_riu


def main():
    options = ['Las Gaviotas', 'Riu Plaza España', 'Salir']
    menu = TerminalMenu(options, title='Seleccione un hotel')
    menu_entry_index = menu.show()
    selection = options[menu_entry_index]
    hotel_name = selection.lower().replace(' ', '_')

    if 'gaviotas' in selection.lower():
        print(f'Executing hotel {selection}')
        exec_gaviotas(hotel_name)

    if 'riu' in selection.lower():
        print(f'Executing hotel {selection}')
        exec_riu(hotel_name)

    if selection == 'Salir':
        print('Saliendo...')
        exit(0)


if __name__ == "__main__":
    main()
