import sys
# Here, you might want to set the ``QT_API`` to use.
# Valid values are: 'pyqt5', 'pyqt4' or 'pyside'
# See 
# import os; os.environ['QT_API'] = 'pyside'
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.qt import QtWidgets
from pyqode.core.api.utils import DelayJobRunner, TextHelper
from pyqode.core.panels import LineNumberPanel
from pyqode.core.modes import IndenterMode
from pyqode.core.modes import FileWatcherMode
from pyqode.core.modes import SmartBackSpaceMode
from pyqode.core.modes import SymbolMatcherMode
from pyqode.core.modes import ZoomMode


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # create editor and window
    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"{sys.argv[1]} - {sys.argv[2]}")
    window.resize(680,460)
    
    editor = api.CodeEdit()
    window.setCentralWidget(editor)

    # start the backend as soon as possible
    editor.backend.start('editor_server.py')

    # append some modes and panels
    editor.modes.append(modes.CodeCompletionMode())
    editor.modes.append(FileWatcherMode())
    editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
    editor.modes.append(modes.CaretLineHighlighterMode())
    editor.panels.append(panels.SearchAndReplacePanel(),
                      api.Panel.Position.BOTTOM)
    editor.modes.append(SmartBackSpaceMode())
    editor.modes.append(SymbolMatcherMode())
    print(editor.modes.append(ZoomMode()))
    
    editor.modes.append(IndenterMode())
    editor.panels.append(LineNumberPanel())
    
    
    # open a file
    editor.file.open(sys.argv[1])


    helper = TextHelper(editor)
    helper.goto_line(int(sys.argv[2])-1, move=True)
    # run
    window.show()
    app.exec_()