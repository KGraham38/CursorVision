import sys
from PyQt5.QtWidgets import QApplication
from ui.main_menu import UI_MainMenu

def main():
    app = QApplication(sys.argv)
    ui = UI_MainMenu()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()