from PySide6.QtWidgets import QApplication, QSpinBox, QVBoxLayout, QPushButton, QLineEdit, QWidget, QGraphicsView, QTreeWidgetItem, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QTreeWidget
from PySide6.QtGui import QPen, QColor, QFontMetrics
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal, QObject
from PySide6 import QtCore, QtGui
import logging
from datetime import datetime

# Only needed for access to command line arguments
import sys
import os

from numpy import save, uint16

sys.path.append("/Users/rennekef/Documents/Programming/xyzflow/public/xyzflow")
from xyzflow import Flow, flow, Parameter, get_flow_parameter, Task
from xyzflow.Flow import load_parameters, save_parameters
from xyzflow.xyzflow import load_flow_from_file

root = os.path.dirname(__file__)

from ParametersWidget import populate_tree
from QStageWidget import QRowWidget, QTaskWidget, QTaskMatrix

import resource


logger = logging.getLogger('xyzflow')

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
            
            loader = QUiLoader()
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
        
        
class XYZFlowGUI(QObject): 
    redraw_flowchart = Signal(Task, str)
    
    def __init__(self) -> None:                                 
        super(XYZFlowGUI, self).__init__()  
        loader = QUiLoader()
        ui_file = os.path.join(root, "Window.ui")
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        
        Task.add_callback(self.task_callback) 
        self.redraw_flowchart.connect(self.redraw_flowchart_slot) 
        
        # Setup a logger
        self.ui.tabWidget_logger.clear()        
        
        logger.setLevel(logging.DEBUG)        
        qlogger = QLogger(self.ui.tabWidget_logger)
        logger.addHandler(qlogger)
        
        self.scene = QGraphicsScene()
        self.ui.flowchart_graphicsView.setScene(self.scene)
        
        self.ui.actionRun.triggered.connect(self.run_flow)

        self.matrix = QTaskMatrix(self.scene)
        self.matrix.clear_matrix()
        self.matrix.refresh_scene()
            
        self.ui.tabWidget_logger.tabCloseRequested.connect(self.close_log_handler)

    def run_flow(self):
        print("Running flow")
        logger.info("Start running the flow")
        logger.info(str(self.flow.main()()))

    def refresh_flow_parameter(self):        
        populate_tree(self.ui.parameter_treeWidget, self.flow)
       
    def close_log_handler(self, index):
        page = self.ui.tabWidget_logger.findChild(QWidget, self.ui.tabWidget_logger.tabText(index))
        page.deleteLater()
        self.ui.tabWidget_logger.removeTab(index)

    def redraw_flowchart_slot(self, task, event):
        logger.info(event)
        if event=="start":
            self.matrix.add_task(task, task.step)
        self.matrix.refresh_scene()
    
    def task_callback(self, task, event, **kwargs):
        self.redraw_flowchart.emit(task, event)
        
        
    def open_flow_from_file(self, path:str):
        self.flow = load_flow_from_file(path)
        
        self.path_para = path+".json"
        # First try to load
        print(f"Trying to load parameters from path: {self.path_para}")
        if not load_parameters(self.path_para):
            print(f"{self.path_para} cannot be loaded.")
            self.path_para = os.path.basename(self.path_para)
            print(f"Looking locally at: {self.path_para}")
            if not load_parameters(self.path_para):
                print(f"Need to retrieve parameters by executing it as much as necessary. Results are saved here: {self.path_para}")
                save_parameters(self.flow, self.path_para)
                print(f"Saving to {self.path_para}. Deliver this file with your task module to speed up execution on the users side.")
                load_parameters(self.path_para) # Read it again to populate the global space correctly
                       
        self.refresh_flow_parameter()
        
    def show(self):
        self.ui.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    gui = XYZFlowGUI() 
    gui.open_flow_from_file("../../tests/flowC.py")     
    gui.show()
    sys.exit(app.exec())