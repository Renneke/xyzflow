from PySide6.QtWidgets import QApplication, QSpinBox, QPushButton, QLineEdit, QWidget, QGraphicsView, QTreeWidgetItem, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QTreeWidget
from PySide6.QtGui import QPen, QColor, QFontMetrics
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6 import QtCore, QtGui
import logging


logger = logging.getLogger('xyzflow')

# Only needed for access to command line arguments
import sys
import os

from numpy import uint16

root = os.path.dirname(__file__)
ui_file = os.path.join(root, "ParametersWidget.ui")


sys.path.append("/Users/rennekef/Documents/Programming/xyzflow/public/xyzflow")
from xyzflow import Parameter, get_flow_parameter
from xyzflow.Flow import load_parameters

class CustomTreeItem( QTreeWidgetItem ):
    '''
    Custom QTreeWidgetItem with Widgets
    '''
 
    def __init__( self, parent, name, parameter=None ):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''
 
        ## Init super class ( QtGui.QTreeWidgetItem )
        super( CustomTreeItem, self ).__init__( parent )
 
        ## Column 0 - Text:
        self.setText( 0, name )
        self.name = name
        self.parameter = parameter
        
        if parameter is not None:
            ## Column 1 - SpinBox:
            self.valueField = QLineEdit()
            self.valueField.setText( str(parameter.result) )
            self.treeWidget().setItemWidget( self, 1, self.valueField )
            
            self.valueField.editingFinished.connect(self.editing_finished)
 
            ## Column 2 - Button:
            self.setText( 2, str(parameter.result) )
            self.setText( 3, str(parameter.description) )

    def editing_finished(self):
        new_value = self.valueField.text()
        logger.info(f"Changing parameter {self.parameter.name} from {self.parameter.value} to {new_value}.")        
        self.parameter.set(new_value)
        
    
 
 

def populate_tree(treeWidget, flow):
    
        
    def iter_item(root):    
        for i in range(root.childCount()):
            yield root.child(i)
            
    def get_item(root, name:str):    
        for item in iter_item(root):
            if name == item.name:
                return item
        return None
            
    for k, v in Parameter.parameters.items():
        path = k.split(".")[:-1]        
        
        current_item = treeWidget.invisibleRootItem()
        for section in path:
            sec_item = get_item(current_item, section)
            if sec_item is None:
                sec_item = CustomTreeItem(current_item, section)
            current_item = sec_item
        CustomTreeItem(current_item, k.split(".")[-1], v)