from PySide6.QtCore import QObject, Signal

class Model(QObject):
    # 推論結果

    def __init__(self):
        super().__init__()
        self.lock_out_detection_people_cnt = 0
        self.inference_results = ObservableList()
    lock_out_detection_people_cnt_changed = Signal(int)

    @property 
    def lock_out_detection_people_cnt(self):
        return self._lock_out_detection_people_cnt

    @lock_out_detection_people_cnt.setter
    def lock_out_detection_people_cnt(self, value: int):
        self._lock_out_detection_people_cnt = value
        self.lock_out_detection_people_cnt_changed.emit(value)


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