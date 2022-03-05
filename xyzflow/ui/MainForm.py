from PySide6.QtWidgets import QApplication, QSpinBox, QVBoxLayout, QPushButton, QLineEdit, QWidget, QGraphicsView, QTreeWidgetItem, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QTreeWidget
from PySide6.QtGui import QPen, QColor, QFontMetrics
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6 import QtCore, QtGui
import logging
from datetime import datetime

# Only needed for access to command line arguments
import sys
import os

from numpy import save, uint16

sys.path.append("/Users/rennekef/Documents/Programming/xyzflow/public/xyzflow")
from xyzflow import Flow, flow, Parameter, get_flow_parameter
from xyzflow.Flow import load_parameters, save_parameters
from xyzflow.xyzflow import load_flow

root = os.path.dirname(__file__)

from ParametersWidget import populate_tree
from QStageWidget import QRowWidget, QTaskWidget, QTaskMatrix
class QLogger(logging.Handler):
    def __init__(self, tabWidget_logger):
        super().__init__()
        self.tabWidget_logger = tabWidget_logger

    def getTreeWidget(self, log_name):
        page = self.tabWidget_logger.findChild(QWidget, log_name)
        
        if not page:
            ui_file = os.path.join(root, "logPage.ui")
            ui_file = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)
            
            page = loader.load(ui_file)
            page.setObjectName(log_name)
            
            self.tabWidget_logger.addTab(page, log_name)

        return page.findChild(QTreeWidget)            

    def emit(self, record):
        
        treeWidget = self.getTreeWidget(record.name)
        
        item = QTreeWidgetItem(treeWidget)
        item.setText(0, str(datetime.fromtimestamp(record.created)))
        item.setText(1, record.levelname)
        item.setText(2, record.filename)
        item.setText(3, str(record.lineno))
        item.setText(4, record.msg)
        
        
class XYZFlowGUI:
    def __init__(self) -> None:
        loader = QUiLoader()
        ui_file = os.path.join(root, "Window.ui")
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        
        
        # Setup a logger
        self.ui.tabWidget_logger.clear()        
        logger = logging.getLogger('xyzflow')
        logger.setLevel(logging.DEBUG)        
        qlogger = QLogger(self.ui.tabWidget_logger)
        logger.addHandler(qlogger)
        
        self.scene = QGraphicsScene()
        self.ui.flowchart_graphicsView.setScene(self.scene)

        self.matrix = QTaskMatrix(self.scene)
            
        self.ui.tabWidget_logger.tabCloseRequested.connect(self.close_log_handler)

    def refresh_flow_parameter(self):        
        populate_tree(self.ui.parameter_treeWidget, self.flow)
       
    def close_log_handler(self, index):
        page = self.ui.tabWidget_logger.findChild(QWidget, self.ui.tabWidget_logger.tabText(index))
        page.deleteLater()
        self.ui.tabWidget_logger.removeTab(index)

    def refresh_flow_chart(self):
        
        self.matrix.clear_matrix()
        
        self.matrix.add_task("hallo1", 0)
        self.matrix.add_task("hallo2", 0)
        self.matrix.add_task("hallo3", 0)
        
        self.matrix.add_task("hallo5", 1)
        self.matrix.add_task("hallo4", 2)
        
        self.matrix.refresh_scene()
        
    def open_flow_(self, path_or_module:str):
        self.flow = load_flow(path_or_module)
        
        self.path_para = path+".json"
        # First try to load 
        try:
            load_parameters(self.path_para)
        except:        
            load_parameters(self.path_para)
            print("Saving")
            save_parameters(self.flow, self.path_para)
        
        self.refresh_flow_parameter()
        self.refresh_flow_chart()
        
        
    
        
    def show(self):
        self.ui.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    gui = XYZFlowGUI() 
    gui.open_flow("../../tests/flowB.py")     
    gui.show()
    sys.exit(app.exec())