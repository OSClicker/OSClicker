from PyQt5.QtWidgets import QKeySequenceEdit
from PyQt5.QtCore import Qt

class SingleKeySequenceEdit(QKeySequenceEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence_set = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_unknown:
            return

        if self.sequence_set:
            self.clear()
            self.sequence_set = False

        super().keyPressEvent(event)
        self.sequence_set = True
