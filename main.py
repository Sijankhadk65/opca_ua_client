import asyncio

import requests
import sys
from PyQt5.QtCore import QAbstractListModel, QStringListModel, QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QVBoxLayout, QLabel, QListView
from opc_ua_provider import server_main

nodes_list = []


class MyApplication(QWidget):
    def __init__(self):
        super().__init__()
        # Set up the main window
        self.init_ui()

    def init_ui(self):
        # Create a button
        button = QPushButton('Click me!', self)
        button.clicked.connect(self.show_response)

        # Create labels to display JSON data
        self.response_label = QLabel(self)
        self.response_label.setWordWrap(True)  # Allow multiline text

        self.list_view = QListView(self)
        self.list_model = QStringListModel()

        self.list_model.setStringList(nodes_list)

        self.list_view.setModel(self.list_model)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(button)
        layout.addWidget(self.response_label)
        layout.addWidget(self.list_view)

        # Set window properties
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('PyQt5 Example')

        # Show the window
        self.show()

    def show_response(self):
        nodes_tree = asyncio.run(server_main())
        print(nodes_tree)

    def add_list_item(self):
        nodes_list.append("item")
        self.list_model.setStringList(nodes_list)


def main():
    app = QApplication(sys.argv)
    window = MyApplication()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
