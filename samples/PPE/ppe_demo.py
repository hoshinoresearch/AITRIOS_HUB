import sys
from PySide6.QtWidgets import QApplication
from models.model import Model
from controllers.controller import Controller
from views.ppe_demo_view import PPEDemoView

class Main(QApplication):
    def __init__(self, argv):
        super(Main, self).__init__(argv)
        self._model = Model()
        self._controller = Controller(self._model)
        self._view = PPEDemoView(self, self._model, self._controller)        
        self._view.showFullScreen()

if __name__ == "__main__":
    app = Main(sys.argv)
    sys.exit(app.exec())