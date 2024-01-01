from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,  QCheckBox, QComboBox, QListWidget, QSizePolicy, QGridLayout, QFormLayout
from PyQt6.QtWidgets import QHBoxLayout, QFileDialog, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QMainWindow, QSlider, QTextBrowser, QScrollArea
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import pyqtSlot, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
from sku_finding_utilies import SKUOperator, comp_dist
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
        self.filename = filename
        self.file_of_skus_to_fix_column_names.clear()
        if os.path.exists(filename):
            _, file_extension = os.path.splitext(filename)
            if file_extension in (".csv", ".xlsx"):
                if file_extension == ".csv":
                    df = pd.read_csv(filename)
                else:
                    df = pd.read_excel(filename)
                # In the line below, the dataframe is saved as an attribute. 
                # It's in memory anyway, and we might as well keep it for later. 
                # Note: This is set repeatedly, but variable assignments don't take very long and the last one will stick. 
                self.messed_up_skus_df = df
                
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


    @pyqtSlot()
    def save_skus_to_fix_column_name(self):
        # The messed up skus column name is saved here. 
        self.messed_up_skus_column_name = self.file_of_skus_to_fix_column_names.currentText()
        self.file_info_dictionary["messed_up_skus_column_name"] = self.messed_up_skus_column_name
        
        with open(self.sku_records_filename, "w") as write_file:
            json.dump(self.file_info_dictionary, write_file, indent=4)
        
    @pyqtSlot()
    def done_selecting_filename_of_skus_to_fix(self):
        self.analyze_skus_button = QPushButton(self)
        self.analyze_skus_button.setText("Analyze SKUs")
        self.analyze_skus_button.clicked.connect(self.analyze_skus)
        
        self.analysis_info_text_browser = QTextBrowser()
        self.analysis_info_text_browser.setReadOnly(True)
        self.analysis_info_text_browser.setFixedWidth(250)
        self.layout.addRow(self.analysis_info_text_browser, self.analyze_skus_button)

        self.done_button_for_selecting_filename_of_skus_to_fix.setEnabled(False)
        self.filename_of_skus_to_fix_textbox.setEnabled(False)
        self.change_filename_of_skus_to_fix_button.setEnabled(False)
        self.file_of_skus_to_fix_column_names.setEnabled(False)

    @pyqtSlot()
    def analyze_skus(self):
        for file_info_piece in self.file_info_dictionary.keys():
            setattr(self, file_info_piece, self.file_info_dictionary[file_info_piece])

        sku_operator = SKUOperator(comp_dist)
        self.sku_operator = sku_operator
        sku_operator.get_master_skus_list(self.master_skus_filename, 
                                                                  self.master_skus_column_name
                                                                  )
        sku_operator.get_corrected_skus_dict(self.corrected_skus_filename, 
                                                                        self.incorrect_skus_column_name, 
                                                                        self.correct_skus_column_name
                                                                        )
        sku_operator.make_sku_dict()

        
        messed_up_skus = list(self.messed_up_skus_df[self.messed_up_skus_column_name])
        predictions = sku_operator.predict_skus(messed_up_skus)
        self.sku_prediction_df = pd.DataFrame({"Incorrect Keys": self.messed_up_skus_df[self.messed_up_skus_column_name], "Predicted Keys": predictions})


        number_of_unrecognized_skus = len(predictions)
        number_of_skus_that_need_to_be_checked = len(set(predictions))
        sku_info_update_text = f"SKUs in the list that aren't recognized:   {number_of_unrecognized_skus}"
        sku_info_update_text += "\n" + f"SKUs that need to be checked:  {number_of_skus_that_need_to_be_checked}"
        self.analysis_info_text_browser.append(sku_info_update_text)
        self.launch_manual_review_window_button = QPushButton("Review Predicted SKUs")
        self.launch_manual_review_window_button.clicked.connect(self.launch_manual_review_window)
        self.layout.addRow(self.launch_manual_review_window_button)


        
        
    @pyqtSlot()
    def launch_manual_review_window(self):
        self.sku_review_window = SKUReviewWindow(self)


class SKUReviewWindow(QMainWindow):
    def __init__(self, sku_fixing_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sku_fixing_window = sku_fixing_window
        
        self.setWindowTitle("Review Each SKU Prediction")

        self.initUI()
    

    def initUI(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.layout = QFormLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        prediction_dict = self.sku_fixing_window.sku_operator.cached_predictor.previous_predictions
        self.correction_qedit_dict = {}
        self.top_done_button = QPushButton("Done.")
        self.top_done_button.clicked.connect(self.done_correcting_skus)
        self.widget.setLayout(self.layout)
        self.layout.addRow("Correct all the predictions below.", self.top_done_button)
        self.make_csv_button = QPushButton("Actually, I'll do this with a csv file.")
        self.make_csv_button.clicked.connect(self.make_csv)
        self.make_excel_button = QPushButton("Actually, I'll do this with an excel file.")
        self.make_excel_button.clicked.connect(self.make_excel)
        self.layout.addRow(self.make_csv_button, self.make_excel_button)
        for messed_up_sku in prediction_dict.keys():
            self.correction_qedit_dict[messed_up_sku] = QLineEdit(f"{prediction_dict[messed_up_sku]}")
            self.layout.addRow(f"{messed_up_sku}", self.correction_qedit_dict[messed_up_sku])
        
        self.bottom_done_button = QPushButton("Done.")
        self.bottom_done_button.clicked.connect(self.done_correcting_skus)
        self.layout.addRow("", self.bottom_done_button)
        
        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

    
    @pyqtSlot()
    def done_correcting_skus(self):
        corrected_predictions = {sku: self.correction_qedit_dict[sku].text() for sku in self.correction_qedit_dict.keys() if self.correction_qedit_dict[sku].text() not in " "*30}
        self.sku_fixing_window.sku_operator.cached_predictor.update(corrected_predictions)
        self.close()
        
        messed_up_skus_column_name = self.sku_fixing_window.messed_up_skus_column_name
        self.sku_fixing_window.messed_up_skus_df[f"Updated {messed_up_skus_column_name}"] = self.sku_fixing_window.messed_up_skus_df[messed_up_skus_column_name].map(corrected_predictions)
                
        # Updating SKU Corrections and Saving to json
        self.sku_fixing_window.sku_operator.save_corrected_skus_dict(self.sku_fixing_window.sku_operator.cached_predictor)

        # Creating a new file
        filename_prefix, file_extension = os.path.splitext(self.sku_fixing_window.filename)
        self.sku_fixing_window.messed_up_skus_df.to_csv(f"{filename_prefix} fixed.csv", index=False)

        self.sku_fixing_window.close()

    @pyqtSlot()
    def make_csv(self):
        prediction_dict = self.sku_fixing_window.sku_operator.cached_predictor.previous_predictions
        df = pd.DataFrame({
            "Incorrect SKU": list(prediction_dict.keys()), 
            "Predicted SKU": list(prediction_dict.values())
        })
        df.to_csv("Manual SKU Correction File.csv", index=False)
        self.close()
        self.sku_fixing_window.close()
        

    @pyqtSlot()
    def make_excel(self):
        prediction_dict = self.sku_fixing_window.sku_operator.cached_predictor.previous_predictions
        df = pd.DataFrame({
            "Incorrect SKU": list(prediction_dict.keys()), 
            "Predicted SKU": list(prediction_dict.values())
        })
        df.to_excel("Manual SKU Correction File.xlsx", index=False)
        self.close()
        self.sku_fixing_window.close()
        

    






    