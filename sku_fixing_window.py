from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,  QCheckBox, QComboBox, QListWidget, QSizePolicy, QGridLayout, QFormLayout
from PyQt6.QtWidgets import QHBoxLayout, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QMainWindow, QSlider, QTextBrowser
from PyQt6.QtCore import pyqtSlot, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
from sku_finding_utilies import SKUOperator
import json
import os.path
import pandas as pd




class SkuFixingWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Top: Layout with "File to be fixed" | {filename}
        Find File Button | Combo box with column names
        Fix-skus button that is set disables (?) and then set enambled when there is text in {filename} above. 
        Two more buttons: View Predicted SKUs | View Predicted SKUs in context (either excel or window)
        """
        self.sku_records_filename = "filename_info.json"
        

        self.setWindowTitle("SKU-Fixer")

        # Set Layout
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Get Filenames from Json
        
        with open(self.sku_records_filename, "r") as read_file:
            self.file_info_dictionary = json.load(read_file)
        
        # Top: Choosing the file with SKUs to be fixed
        # self.layout.addRow("Please verify/update the Master SKU Info Below.", QLineEdit(""))
        self.filename_of_skus_to_fix_textbox = QLineEdit(self)
        self.filename_of_skus_to_fix_textbox.setText(self.file_info_dictionary["messed_up_skus_filename"])
        self.filename_of_skus_to_fix_textbox.textChanged.connect(self.update_file_of_skus_to_fix_column_names)
        self.layout.addRow("Messed Up SKUs File:", self.filename_of_skus_to_fix_textbox)

        self.change_filename_of_skus_to_fix_button = QPushButton(self)
        self.change_filename_of_skus_to_fix_button.setText("Change File")
        self.change_filename_of_skus_to_fix_button.clicked.connect(self.change_filename_of_skus_to_fix)
        self.file_of_skus_to_fix_column_names = QComboBox(self)
        self.layout.addRow(self.change_filename_of_skus_to_fix_button, self.file_of_skus_to_fix_column_names)
        self.update_file_of_skus_to_fix_column_names()
        self.file_of_skus_to_fix_column_names.currentIndexChanged.connect(self.save_skus_to_fix_column_name)
        
        

        #Bottom:
        self.done_button_for_selecting_filename_of_skus_to_fix = QPushButton(self)
        self.done_button_for_selecting_filename_of_skus_to_fix.setText("SKU's me, I'm done.")
        self.done_button_for_selecting_filename_of_skus_to_fix.clicked.connect(self.done_selecting_filename_of_skus_to_fix)
        self.layout.addRow(self.done_button_for_selecting_filename_of_skus_to_fix)


        self.show()

    @pyqtSlot()
    def change_filename_of_skus_to_fix(self):
        new_filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "data/",
            "Comma Separated Value (*.csv)",
        )
        self.filename_of_skus_to_fix_textbox.setText(new_filename)
    
    @pyqtSlot()
    def update_file_of_skus_to_fix_column_names(self):
        filename = self.filename_of_skus_to_fix_textbox.text()
        self.file_of_skus_to_fix_column_names.clear()
        if os.path.exists(filename):
            _, file_extension = os.path.splitext(filename)
            if file_extension in (".csv", ".xlsx"):
                if file_extension == ".csv":
                    df = pd.read_csv(filename)
                else:
                    df = pd.read_excel(filename)

                self.qcombo = self.file_of_skus_to_fix_column_names
                self.qcombo.addItems(df.columns)
                # In the lookup dict below (qcombo_index_lookup_dict), the range is indexed backwards so that 
                #  the firstindex is returned in the case of repeated column names. 
                self.qcombo_index_lookup_dict = {self.qcombo.itemText(i): i for i in range(self.qcombo.count(),-1,-1)}
                stored_column_name = self.file_info_dictionary["messed_up_skus_column_name"]
                if stored_column_name in self.qcombo_index_lookup_dict.keys() and stored_column_name:
                    scn_index = self.qcombo_index_lookup_dict[stored_column_name]
                    self.qcombo.setCurrentIndex(scn_index)
                elif self.qcombo.count() > 0:
                    self.qcombo.setCurrentIndex(0)
                
                ##### Still left to do: find the right place to save the selected dropdown item in the QComboBox.
                    # This will require its own method and it needs to be triggered on qcb.changeItem (or some method like that)

    @pyqtSlot()
    def save_skus_to_fix_column_name(self):
        self.file_info_dictionary["messed_up_skus_column_name"] = self.file_of_skus_to_fix_column_names.currentText()
        
        with open(self.sku_records_filename, "w") as write_file:
            json.dump(self.file_info_dictionary, write_file, indent=4)
        
    @pyqtSlot()
    def done_selecting_filename_of_skus_to_fix(self):
        self.analyze_skus_button = QPushButton(self)
        self.analyze_skus_button.setText("Analyze SKUs")
        self.analyze_skus_button.clicked.connect(self.analyze_skus)
        
        self.analysis_info_text_browser = QTextBrowser()
        self.analysis_info_text_browser.setReadOnly(True)
        self.analysis_info_text_browser.append(f"Unrecognized SKUs:   \nSKUs that need to be checked:  ")
        self.layout.addRow(self.analyze_skus_button, self.analysis_info_text_browser)

        self.done_button_for_selecting_filename_of_skus_to_fix.setEnabled(False)
        self.filename_of_skus_to_fix_textbox.setEnabled(False)
        self.change_filename_of_skus_to_fix_button.setEnabled(False)
        self.file_of_skus_to_fix_column_names.setEnabled(False)

    @pyqtSlot()
    def analyze_skus(self):
        for file_info_piece in self.file_info_dictionary.keys():
            setattr(self, file_info_piece, self.file_info_dictionary[file_info_piece])

        sku_operator = SKUOperator()
        sku_operator.get_master_skus_list(self.master_skus_filename, 
                                                                  self.master_skus_column_name
                                                                  )
        sku_operator.get_corrected_skus_dict(self.corrected_skus_filename, 
                                                                        self.incorrect_skus_column_name, 
                                                                        self.correct_skus_column_name
                                                                        )
        self.make_sku_dict()

            
            
            