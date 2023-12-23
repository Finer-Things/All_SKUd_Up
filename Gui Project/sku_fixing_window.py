from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,  QCheckBox, QComboBox, QListWidget, QSizePolicy, QGridLayout, QFormLayout
from PyQt6.QtWidgets import QHBoxLayout, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QMainWindow, QSlider, QTextBrowser
from PyQt6.QtCore import pyqtSlot, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
import json




class SkuFixingWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Top: Layout with "File to be fixed" | {filename}
        Find File Button | Combo box with column names
        Fix-skus button that is set disables (?) and then set enambled when there is text in {filename} above. 
        Two more buttons: View Predicted SKUs | View Predicted SKUs in context (either excel or window)
        """
    
        

        self.setWindowTitle("SKU-Fixer")

        # Set Layout
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Get Filenames from Json
        course_profile_filename = "Gui Project/file_name_info.json"
        with open(course_profile_filename, "r") as read_file:
            self.file_name_dictionary = json.load(read_file)
        
        # First Row
        self.file_name_to_fix_textbox = QLineEdit(self)
        self.file_name_to_fix_textbox.setText(self.file_name_dictionary["skus_to_correct"])
        self.layout.addRow("SKUs to be Corrected", self.file_name_to_fix_textbox)




        self.show()