from PySide6.QtWidgets import QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem
from PySide6.QtGui import QPen, QColor, QFontMetrics
from PySide6 import QtCore

# Only needed for access to command line arguments
import sys

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
    
    def __init__(self, row, stage, name="task1", state=1):
        self.width = 100
        self.height = 50
        self.margin = 10
        self.name = name
        self.state = state
        self.stage = stage
        self.row = row
        self.clicked = False
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.hover = False
        
        self.setToolTip(name)
        
    def hoverEnterEvent(self, evt):
        self.hover = True
        super().hoverEnterEvent(evt)
        
    def hoverLeaveEvent(self, evt):
        self.hover = False
        super().hoverLeaveEvent(evt)
        
    def mousePressEvent(self, evt):
        self.clicked = True
        evt.accept()
        self.update()
        
    def mouseReleaseEvent(self, evt):
        self.clicked = False
        super().mouseReleaseEvent(evt)
        self.update()
        
    @property
    def x0(self):
        return self.stage*(self.width+self.margin)
        
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
        
        painter.drawRoundedRect(self.boundingRect(), 3, 3)
        
        fm = QFontMetrics(painter.font())
        tw = fm.boundingRect(self.name).width()
        th = fm.boundingRect(self.name).height()
        self.width = tw+100
        painter.drawText(self.x0+self.width/2-tw/2, self.y0+self.height/2+th/2, self.name)
    
class QRowWidget(QGraphicsItem):
    def __init__(self, row):
        super().__init__()
        
        self.height = 50
        self.row = row
        
        self.x0 = 0
        self.y0 = self.row*self.height
        self.y1 = (self.row+1)*self.height
        
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

# Subclass QMainWindow to customize your application's main window
class QStageWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        scene = QGraphicsScene()
        self.setScene(scene)
  
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
  
        pen = QPen(QtCore.Qt.green)

  
  
  
if __name__ == "__main__":     
    app = QApplication(sys.argv)
    window = QStageWidget()
    window.show() 
    app.exec()
