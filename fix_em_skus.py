import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,  QCheckBox, QComboBox, QListWidget, QFormLayout, QHBoxLayout, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot
import pandas as pd
import json
import glob

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = None

        ## Seting Up Window ##
        # Window Title
        self.setWindowTitle("SKU-Fixer Setup")

        # Setting Layout
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Adding Initial Rows
        """
        Course Name: 
        Quarter: 
        (Done)
        """
        ## Creating Master SKU File Finder Button ##
        # Defining Master SKU File Finder Button
        self.master_sku_file_finder_button = QPushButton(self)
        self.master_sku_file_finder_button.setText("Find it")
        self.master_sku_file_finder_button.clicked.connect(self.open_master_sku_file_finder_dialogue)

        # Add Row with Button
        self.layout.addRow("Where is the Master SKU File?", self.master_sku_file_finder_button)



        
        # show the window
        self.show()


    ### Slot Methods ###
    # Open Master SKU File Finder Dialogue Slot Method
    @pyqtSlot()
    def open_master_sku_file_finder_dialogue(self):
        """
        Opens a dialogue box to find the Master SKU File
        """
        master_sku_file_name_info = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "Master SKU",
            "Comma Separated Value (*.csv)",
        )
        self.master_sku_filename = master_sku_file_name_info[0]
        self.master_sku_df = pd.read_csv(self.master_sku_filename)

        # Add Column Choice and Done Button in next row
        self.master_sku_column_name_box = QComboBox(self)
        self.master_sku_column_name_box.addItems(self.master_sku_df.columns)
        self.done_entering_master_sku_info_button = QPushButton()
        self.done_entering_master_sku_info_button.setText("<-- Yes, this is the Master SKU column")
        self.done_entering_master_sku_info_button.clicked.connect(self.done_entering_master_sku_info)
        
        # Add Master SKU Column Name Box and Done Entering Master SKU Info Button
        self.layout.addRow(self.master_sku_column_name_box, self.done_entering_master_sku_info_button)

        

    # Done-Entering-Master-SKU Slot Method
    @pyqtSlot()
    def done_entering_master_sku_info(self):
        """
        We already have the master sku filename and dataframe: self.master_sku_filename and self.master_sku_df
        But we need to grab the column name.
        """
        ## Storing and Disabling used widgets
        # Extracting Text for Master SKU Column Name
        self.master_sku_column_name = self.master_sku_column_name_box.currentText()

        for widget in [self.master_sku_file_finder_button, self.master_sku_column_name_box, self.done_entering_master_sku_info_button]:
            widget.setEnabled(False)
        
        ## Adding new buttons
        # Defining Master SKU File Finder Button
        self.corrected_sku_file_finder_button = QPushButton(self)
        self.corrected_sku_file_finder_button.setText("Find it")
        self.corrected_sku_file_finder_button.clicked.connect(self.open_corrected_sku_file_finder_dialogue)

        # Add Row with Button
        self.layout.addRow("Where is the Corrected SKU File?", self.corrected_sku_file_finder_button)


    # Open Corrected SKU File Finder Dialogue Slot Method
    @pyqtSlot()
    def open_corrected_sku_file_finder_dialogue(self):
        """
        Opens a dialogue box to find the Corrected SKU File
        """
        corrected_sku_file_name_info = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "Corrected SKU",
            "Comma Separated Value (*.csv)",
        )
        self.corrected_sku_filename = corrected_sku_file_name_info[0]
        self.corrected_sku_df = pd.read_csv(self.corrected_sku_filename)

        ## Add Both Column Choices and Done Button in next row
        # Incorrect SKU Column Name Box
        self.incorrect_sku_column_name_box = QComboBox(self)
        self.incorrect_sku_column_name_box.addItems(self.corrected_sku_df.columns)
        # Correct SKU Column Name Box
        self.correct_sku_column_name_box = QComboBox(self)
        self.correct_sku_column_name_box.addItems(self.corrected_sku_df.columns)
        
        self.done_entering_corrected_sku_info_button = QPushButton()
        self.done_entering_corrected_sku_info_button.setText("Both columns are set.")
        self.done_entering_corrected_sku_info_button.clicked.connect(self.done_entering_corrected_sku_info)
        
        # Add Corrected SKU Column Name Box and Done Entering Corrected SKU Info Button
        self.layout.addRow("Incorrect SKU Column:", self.incorrect_sku_column_name_box)
        self.layout.addRow("Correct SKU Column:", self.correct_sku_column_name_box)
        self.layout.addRow(self.done_entering_corrected_sku_info_button)

    # Done-Entering-Corrected-SKU Slot Method
    @pyqtSlot()
    def done_entering_corrected_sku_info(self):
        """
        We already have the corrected sku filename and dataframe: self.corrected_sku_filename and self.corrected_sku_df
        But we need to grab the column name.
        """
        ## Storing and Disabling used widgets
        # Extracting Text for Corrected SKU Column Name
        self.incorrect_sku_column_name = self.incorrect_sku_column_name_box.currentText()
        self.correct_sku_column_name = self.correct_sku_column_name_box.currentText()

        for widget in [self.corrected_sku_file_finder_button, self.incorrect_sku_column_name_box, self.correct_sku_column_name_box, self.done_entering_corrected_sku_info_button]:
            widget.setEnabled(False)
        
        ### ****Add One More Pair of things like these for the file that needs to have skus replaced. Then Run the fix_skus method**** ###
        

    def fix_skus(self):
        # The line below needs to be updated for this file
        master_sku_list = list(m_df[master_sku_column_name].astype(str).str.strip().unique())        

    



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())




