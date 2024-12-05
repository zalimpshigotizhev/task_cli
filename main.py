from menu import Menu

if __name__ == '__main__':
    menu = Menu()

    while True:
        menu.start()
        selected_choice = str(menu.console.input())
        menu.distribute(selected_choice)

