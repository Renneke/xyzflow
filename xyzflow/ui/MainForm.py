from PySide6.QtWidgets import QApplication, QSpinBox, QVBoxLayout, QPushButton, QLineEdit, QWidget, QGraphicsView, QTreeWidgetItem, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QTreeWidget
from PySide6.QtGui import QPen, QColor, QFontMetrics
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6 import QtCore, QtGui


# Only needed for access to command line arguments
import sys
import os

from numpy import uint16

sys.path.append("/Users/rennekef/Documents/Programming/xyzflow/public/xyzflow")
from xyzflow import Flow, flow, Parameter, get_flow_parameter
from xyzflow.Flow import load_parameters

root = os.path.dirname(__file__)
ui_file = os.path.join(root, "Window.ui")

from ParametersWidget import populate_tree
from QStageWidget import QRowWidget, QTaskWidget


sys.path.append("/Users/rennekef/Documents/Programming/xyzflow/public/xyzflow")
from xyzflow import Flow, flow, Parameter, get_flow_parameter
from xyzflow.Flow import load_parameters

class FlowA(Flow):
    def main(self):
        a = Parameter.create(name="a", value="hello")        
        b = Parameter.create(name="b", value="world")        
        return a+b

class FlowB(Flow):
    def main(self):
        x = Parameter.create(name="x", value="some")        
        y = Parameter.create(name="y", value="thing") 
        
        z = flow(FlowA, "hallo", a=x)       
        return x+y+z
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui_file = QFile(ui_file)
    ui_file.open(QFile.ReadOnly)

    loader = QUiLoader()
    ui = loader.load(ui_file)
           
    
    populate_tree(ui.parameter_treeWidget, FlowB)
    
    
    ui.flowchart_graphicsView.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    scene = QGraphicsScene()
    ui.flowchart_graphicsView.setScene(scene)

    for i in range(0,20):
        row = QRowWidget(i)
        scene.addItem(row)
    
    task1 = QTaskWidget(0,0, state=0)
    scene.addItem(task1)
    task1 = QTaskWidget(2,0, state=2)
    scene.addItem(task1)
    
    task1 = QTaskWidget(0,1, state=3, name="cached")
    scene.addItem(task1)
    
    task1 = QTaskWidget(1,1)
    scene.addItem(task1)
    
    
    
    ui.show()
    sys.exit(app.exec())