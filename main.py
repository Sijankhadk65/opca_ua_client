import asyncio
import sys
import traceback
import requests

from progress import HIDE_CURSOR, SHOW_CURSOR

from PyQt6.QtCore import (Q_ARG, QMetaObject, QMutex, QMutexLocker, QObject,
                          QRunnable, Qt, QThreadPool, pyqtSignal, pyqtSlot)
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow,
                             QMessageBox, QPlainTextEdit, QPushButton,
                             QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem)

from opc_ua_provider import server_main
from models import NodeTree


class WorkerSignals(QObject):
    finish = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, fn_run, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn_run = fn_run
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.mutex = QMutex()
        self.is_stop = False

    @pyqtSlot()
    def run(self):
        try:
            with QMutexLocker(self.mutex):
                self.is_stop = False
            result = self.fn_run(self, *self.args, **self.kwargs)
        except:
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finish.emit()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_stop = True


class CustomPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CustomPlainTextEdit, self).__init__(parent=parent)
        self.is_progress_bar = False

    def write(self, message):
        # Support for "progress" module
        message = message.strip()
        if message == SHOW_CURSOR:
            self.is_progress_bar = False
            return
        if message:
            if self.is_progress_bar:
                QMetaObject.invokeMethod(self, "replace_last_line", Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(str, message))
            else:
                QMetaObject.invokeMethod(self, "appendPlainText", Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(str, message))
        if message == HIDE_CURSOR:
            self.is_progress_bar = True
            return

    @pyqtSlot(str)
    def replace_last_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.insertPlainText(text)

    def flush(self):
        pass


class MainWindow(QMainWindow):
    # Qt signal when asynchronous processing is interrupted
    stop_worker = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.tree_nodes = []
        self.worker = None
        self.old_stdout = None
        self.start_button = QPushButton("Start!", self)
        self.start_button.clicked.connect(self.on_start)

        self.stop_button = QPushButton("Stop!", self)
        self.stop_button.clicked.connect(self.on_stop)

        self.text_box = CustomPlainTextEdit(self)
        self.text_box.setReadOnly(True)  # Make the text box read-only

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["ID", "Namespace"])

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.text_box)
        layout.addWidget(self.tree)

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Required for asynchronous processing
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

    def closeEvent(self, event):
        # Do not close the application while asynchronous processing is running.
        if self.thread_pool.activeThreadCount() > 0:
            QMessageBox.information(None, "", "Processing is in progress", QMessageBox.StandardButton.Ok)
            event.ignore()
        else:
            event.accept()

    def on_start(self):
        if self.thread_pool.activeThreadCount() < self.thread_pool.maxThreadCount():
            self.old_stdout = sys.stdout
            sys.stdout = self.text_box
            print("Start asynchronous processing")
            self.worker = Worker(self.run_thread, "sample args", sample_kwargs1=1, sample_kwargs2="option")
            self.stop_worker.connect(self.worker.stop)
            self.worker.signals.finish.connect(self.finish_thread)
            self.worker.signals.error.connect(self.error_thread)
            self.worker.signals.result.connect(self.result_thread)
            self.thread_pool.start(self.worker)

    def on_stop(self):
        if self.thread_pool.activeThreadCount() > 0:
            print("Request to suspend processing")
            self.stop_worker.emit()

    def run_thread(self, worker_object, *args, **kwargs):
        # The number and type of arguments can be rewritten.
        # However, the first argument should be fixed to "worker_object".
        # This is necessary to describe the abort process.
        print("Start the main process")
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        url = "https://dummyjson.com/products/1"

        try:
            # response = requests.get(url)
            # response.raise_for_status()
            # data = response.text  # Access the fetched data
            response = asyncio.run(server_main())
            return response  # Return the fetched data
        except Exception as e:
            return f"Error fetching data from {url}"

    def error_thread(self, message):
        print("Outputs error logs that occur in asynchronous processing")
        print(message)

    def result_thread(self, message):
        self.tree_nodes = self.generate_tree_view_struct(message)
        self.tree.insertTopLevelItems(0, [self.tree_nodes])
        print(f"Recieved Node info...")

    def finish_thread(self):
        print("Asynchronous processing is complete")
        # Restore the standard output destination
        sys.stdout = self.old_stdout
        self.thread_pool.waitForDone()

    def generate_tree_view_struct(self, node):
        item = QTreeWidgetItem([str(node.get_id()), str(node.get_ns())])
        if node.get_nodes():
            for child in node.get_nodes():
                item.addChild(self.generate_tree_view_struct(child))
        return item


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create QApplication instance
    main_window = MainWindow()  # Create MainWindow instance
    main_window.show()  # Show the window
    sys.exit(app.exec())  # Start the application and handle events
