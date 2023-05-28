"""
OBSOLETE
v.1.0.0 - Basic release
GUI interface for the composite optimizer. Contains input, optimization and status tabs.
"""

import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QFileDialog,
    QWidget,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QApplication,
    QDialog,
    QTabWidget,
    QLineEdit,
    QFrame,
    QListWidget,
    QGroupBox,
)
from file_manager import FileProcessor

class SharedData:
    """Comprises the shared data between tabs"""
    def __init__(self) -> None:
        self.path_inp = None


class MainWindow(QDialog):
    """
    Main window definition. Contains the three tabs and window layout
    and title definitions 
    """
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.shared_data = SharedData()
        self.input_tab = InputsTab(self.shared_data)
        self.optimization_tab = OptimizationTab(self.shared_data)
        self.status_tab = StatusTab(self.shared_data)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.input_tab, "Inputs")
        self.tab_widget.addTab(self.optimization_tab, "Optimization")
        self.tab_widget.addTab(self.status_tab, "Status")

        main_window_layout = QVBoxLayout()
        main_window_layout.addWidget(self.tab_widget)
        self.setLayout(main_window_layout)
        self.setWindowTitle("optComp v.1.0.0")

        # Size definitions
        min_size = QSize(500, 500)
        self.setMinimumSize(min_size)
    
    def update_optimization_tab(self):
        self.optimization_tab.update_contents_opt()

class InputsTab(QWidget):
    """
    Inputs tab definition. Comprises methods for open file explorer, 
    read this file and call backend functions and use this results to
    update values inside this tab
    """
    def __init__(self, shared_data_input) -> None:
        super().__init__()

        self.shared_data_input = shared_data_input

        # First groupbox definition: comprises the input file manager
        file_groupbox = QGroupBox("File input")

        self.select_file_button = QPushButton("Select file")
        self.select_file_button.clicked.connect(self.select_file)
        self.file_path_line = QLineEdit("Select the input file...")
        self.read_file_button = QPushButton("Read file")
        self.read_file_button.clicked.connect(self.read_file_exec)


        file_input_layout = QHBoxLayout()
        file_input_layout.addWidget(self.select_file_button)
        file_input_layout.addWidget(self.file_path_line)
        file_input_layout.addWidget(self.read_file_button)
        file_groupbox.setLayout(file_input_layout)

        # Second groupbox definition: Regard the orientation cards
        orientation_groupbox = QGroupBox("Orientation")
        self.orientation_list = QListWidget()
        self.orientation_list.itemClicked.connect(self.update_angles)

        self.theta_x = QLabel("Angle \u03B8x")
        self.theta_x_value = QLabel()
        self.theta_x_value.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.theta_y = QLabel("Angle \u03B8y")
        self.theta_y_value = QLabel()
        self.theta_y_value.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.theta_z = QLabel("Angle \u03B8z")
        self.theta_z_value = QLabel()
        self.theta_z_value.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.explanation = QLabel("Angles measured between local and global axis")

        orientation_layout = QGridLayout()
        orientation_layout.addWidget(self.orientation_list, 0, 0, 6, 1)
        orientation_layout.setColumnStretch(0, 4)
        orientation_layout.setColumnStretch(1, 1)
        orientation_layout.setColumnStretch(2, 1)
        orientation_layout.addWidget(self.theta_x, 0, 1)
        orientation_layout.addWidget(self.theta_x_value, 0, 2)
        orientation_layout.addWidget(self.theta_y, 1, 1)
        orientation_layout.addWidget(self.theta_y_value, 1, 2)
        orientation_layout.addWidget(self.theta_z, 2, 1)
        orientation_layout.addWidget(self.theta_z_value, 2, 2)
        orientation_layout.addWidget(self.explanation, 3, 1, 1, 2)
        orientation_groupbox.setLayout(orientation_layout)

        # Third groupbox definition: Element sets
        elements_groupbox = QGroupBox("Element Sets")
        self.elements_list = QListWidget()
        elements_layout = QVBoxLayout()
        elements_layout.addWidget(self.elements_list)
        elements_groupbox.setLayout(elements_layout)

        # Fourth groupbox definition: Node sets
        nodes_groupbox = QGroupBox("Node sets")
        self.nodes_list = QListWidget()
        nodes_layout = QVBoxLayout()
        nodes_layout.addWidget(self.nodes_list)
        nodes_groupbox.setLayout(nodes_layout)

        # Layout definition for the parent tab
        inputs_tab_layout = QGridLayout()
        inputs_tab_layout.addWidget(file_groupbox, 0, 0, 1, 2)
        inputs_tab_layout.addWidget(orientation_groupbox, 1, 0, 1, 2)
        inputs_tab_layout.addWidget(elements_groupbox, 2, 0)
        inputs_tab_layout.addWidget(nodes_groupbox, 2, 1)
        self.setLayout(inputs_tab_layout)

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select File')
        if file_path:
            self.file_path_line.setText(file_path)

    def read_file_exec(self):
        self.shared_data_input.path_inp = self.file_path_line.text()
        instance = FileProcessor()
        instance.read_file(self.shared_data_input.path_inp)
        self.orientation_list_data, self.x_local_list, self.y_local_list, self.z_local_list, \
            self.x_angles, self.y_angles, self.z_angles = instance.search_orientation()
        self.element_names, self.elements_numbers = instance.search_sets("*ELSET")
        self.nodes_names, self.nodes_numbers = instance.search_sets("*NSET")

        self.update_elements()
        self.update_nodes()
        self.update_orientation_list()
        self.window().update_optimization_tab()

    def update_orientation_list(self):
        self.orientation_list.clear()
        self.orientation_list.addItems(self.orientation_list_data)

    def update_angles(self):
        self.theta_x_value.clear()
        index = self.orientation_list.currentRow()
        self.theta_x_value.setText(str(format(self.x_angles[index], ".1f")))
        self.theta_y_value.setText(str(format(self.y_angles[index], ".1f")))
        self.theta_z_value.setText(str(format(self.z_angles[index], ".1f")))

    def update_elements(self):
        self.elements_list.clear()
        list = [str(a) + " - " + str(b) + " elements" for a, b in zip(self.element_names, self.elements_numbers)]
        self.elements_list.addItems(list)

    def update_nodes(self):
        self.nodes_list.clear()
        list = [str(a) + " - " + str(b) + " nodes" for a, b in zip(self.nodes_names, self.nodes_numbers)]
        self.nodes_list.addItems(list)

class OptimizationTab(QWidget):
    """
    Docstring to be defined
    """
    def __init__(self, shared_data_opt) -> None:
        super().__init__()

        self.shared_data_opt = shared_data_opt
        self.file_path_test = QLabel("oi")
        optimization_layout = QHBoxLayout()
        optimization_layout.addWidget(self.file_path_test)
        self.setLayout(optimization_layout)
    
    def update_contents_opt(self):
        self.file_path_test.setText(self.shared_data_opt.path_inp)

class StatusTab(QWidget):
    """
    Docstring to be defined
    """
    def __init__(self, shared_data_status) -> None:
        super().__init__()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())