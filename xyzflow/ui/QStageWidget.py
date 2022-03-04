import logging
from PySide6.QtWidgets import QApplication,  QWidget, QMenu, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QGraphicsItemGroup
from PySide6.QtGui import QPen, QColor, QFontMetrics, QCursor, QFont
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject, Signal, Slot

# Only needed for access to command line arguments
import sys

from xyzflow import Task

logger = logging.getLogger('xyzflow')
class QTaskWidget(QGraphicsItem):
    FAIL = 0
    NOT_RUN = 1
    OK = 2
    CACHED = 3
    
    COLORS = {
        # State        Pen Color              Brush Color   
        FAIL: (QColor(0xba,0x00,0x0d), QColor(0xf4,0x43,0x36)),
        NOT_RUN: (QColor(0x8a,0xac,0xc8), QColor(0xbb,0xde,0xfb)),
        OK: (QColor(0x6b,0x9b,0x37), QColor(0x9C,0xCC,0x65)),
        CACHED: (QColor(0x9c,0x64,0xa6), QColor(0xce,0x93,0xd8))
    }
    
    
    def __init__(self, row, x0, task):
        
        self.height = 50
        self.margin = 10
        self.name = task.__class__.__name__
        self.state = self.FAIL
        self.row = row
        self.clicked = False
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.hover = False
        self.selected = Signal(Task)
        
        self.x0 = x0
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self.font = QFont("times", 12)
        fm = QFontMetrics(self.font)
        self.tw = fm.boundingRect(self.name).width()
        self.th = fm.boundingRect(self.name).height()
        self.width = self.tw+100
        
        self.setToolTip(self.name)
        
    def contextMenuEvent(self, event) -> None:
        menu = QMenu()
        action = menu.addAction('Run from here')
        action = menu.addAction('Invalidate Cache')
        menu.exec(event.screenPos())
        
        
    def hoverEnterEvent(self, evt):
        self.hover = True
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor));          
        super().hoverEnterEvent(evt)
        
    def hoverLeaveEvent(self, evt):
        self.hover = False
        QApplication.restoreOverrideCursor()
        super().hoverLeaveEvent(evt)
        
    def mousePressEvent(self, evt):
        self.clicked = True
        evt.accept()
        self.update()
        
        logger.info("Task selected")
        
    def mouseReleaseEvent(self, evt):
        self.clicked = False
        super().mouseReleaseEvent(evt)
        self.update()
                
    @property
    def y0(self):
        return self.row*self.height

    def boundingRect(self):
        return QtCore.QRectF(self.x0+2,self.y0+2,self.width-4,self.height-4)
    
    def paint(self, painter, _0, _1): 
        painter.setPen(self.COLORS[self.state][0])
        painter.setBrush(self.COLORS[self.state][1])
        if self.hover:
            painter.setBrush(self.COLORS[self.state][1].lighter(150))
        if self.clicked:
            painter.setBrush(self.COLORS[self.state][1].darker(100))
        
        if self.isSelected():
            painter.setBrush(self.COLORS[self.state][1].darker(200))
        
        painter.drawRoundedRect(self.boundingRect(), 3, 3)
        
        painter.setFont(self.font)        
        painter.drawText(self.x0+self.width/2-self.tw/2, self.y0+self.height/2+self.th/2, self.name)
    
class QRowWidget(QGraphicsItem):
    def __init__(self, row):
        super().__init__()
        
        self.height = 50
        self.row = row
        
        self.x0 = 0
        self.y0 = self.row*self.height
        self.y1 = (self.row)*self.height
        
        
    @property
    def width(self):
        view = self.scene().views()[0]
        return view.width()
            
    def boundingRect(self):
        return QtCore.QRectF(self.x0,self.y0,self.width,self.height)
    
    def paint(self, painter, _0, _1):        
        painter.setPen(QtCore.Qt.NoPen)
        if self.row%2==0:
            painter.setBrush(QColor(0xEE,0xEE,0xEE, 200))
        painter.drawRect(self.boundingRect())
        
        painter.setBrush(QColor(0xDD, 0xDD, 0xDD, 100))
        number_rect = QtCore.QRectF(10, self.y1+10, 30, 30)
        painter.drawRoundedRect(number_rect, 3, 3)
            
        painter.setPen(QColor(0x88, 0x88, 0x88, 255))
        fm = QFontMetrics(painter.font())
        number_str = str(self.row)
        tw = fm.boundingRect(number_str).width()
        th = fm.boundingRect(number_str).height()
        painter.drawText(self.x0+10+15-tw/2, self.y1+10+15+th/2, number_str)
        
class QTaskMatrix:
    def __init__(self, scene) -> None:
        self.clear_matrix()
        self.scene = scene
        
        
    def add_task(self, item, row):
        
        if row not in self.matrix:
            self.matrix[row] = []
        
        self.matrix[row].append(item)
        
    def clear_matrix(self):
        self.matrix = {}
        for i in range(0,10):
            self.matrix[i] = []
        
        
    def refresh_scene(self):
        
        for i in self.matrix.keys():
            row = QRowWidget(i)
            self.scene.addItem(row)
            x0 = 50
            for item in self.matrix[i]:
                task = QTaskWidget(i, x0, item)
                self.scene.addItem(task)
                
                x0 = task.boundingRect().right()+20
                
        
        
