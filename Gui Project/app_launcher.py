import sys
from PyQt6.QtWidgets import QApplication

from sku_fixing_window import *

app = QApplication(sys.argv)
window = SkuFixingWindow()

sys.exit(app.exec()) 