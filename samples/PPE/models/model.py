from PySide6.QtCore import QObject, Signal

from enum import Enum, auto
class PPEDetectonMode(Enum):
    ALL_EQ = auto()         # 全装備着装
    NOT_FULLY_EQ = auto()   # 着装未完全
    NOT_EQ = auto()         # 装備未着装

class Model(QObject):
    # 推論結果

    def __init__(self):
        super().__init__()
        self._ppe_detection_mode = PPEDetectonMode.NOT_EQ

        self.inference_results = ObservableList()

    ppe_detection_mode_changed = Signal(PPEDetectonMode)

    @property 
    def ppe_detection_mode(self):
        return self._ppe_detection_mode

    @ppe_detection_mode.setter
    def ppe_detection_mode(self, value: PPEDetectonMode):
        if self._ppe_detection_mode != value:
            self._ppe_detection_mode = value
            self.ppe_detection_mode_changed.emit(value)


class ObservableList(QObject):
    data_changed = Signal(list)

    def __init__(self, initial_list=None):
        super().__init__()
        self._list = initial_list if initial_list else []

    def append_all(self, items:list):
        self._list.clear()
        for item in items:            
            self._list.append(item)
        self.data_changed.emit(self._list)

    def append(self, item):
        self._list.append(item)
        self.data_changed.emit(self._list)


    def remove(self, item):
        if item in self._list:
            self._list.remove(item)
            self.data_changed.emit(self._list) 


    def clear(self):
        self._list.clear()
        self.data_changed.emit(self._list) 

    def get_list(self):
        return self._list