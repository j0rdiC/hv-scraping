from simple_term_menu import TerminalMenu
from src.gaviotas import main as exec_gaviotas
from src.riu import main as exec_riu


def main():
    options = ['Las Gaviotas', 'Riu (Plz. Espana)', 'Salir']
    menu = TerminalMenu(options, title='Seleccione un hotel')
    menu_entry_index = menu.show()
    selection = options[menu_entry_index]

    if 'gaviotas' in selection.lower():
        print(f'Executing hotel {selection}')
        exec_gaviotas()

    if 'riu' in selection.lower():
        print(f'Executing hotel {selection}')
        exec_riu()

    if selection == 'Salir':
        print('Saliendo...')
        exit(0)


if __name__ == "__main__":
    main()
