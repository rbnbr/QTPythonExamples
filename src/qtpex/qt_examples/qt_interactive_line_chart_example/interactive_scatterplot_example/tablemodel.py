from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QIntList, Signal
from PySide6.QtGui import QColor


class CustomTableModel(QAbstractTableModel):
    data_changed = Signal(int, int, float, float)  # new data changed signal with row, column, old value, new value

    def __init__(self, data=None):
        QAbstractTableModel.__init__(self)
        self.load_data(data)

    def load_data(self, data):
        self.input_dates = data[0].values
        self.input_magnitudes = data[1].values

        self.column_count = 2
        self.row_count = len(self.input_magnitudes)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Date", "Magnitude")[section]
        else:
            return f"{section}"

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            if column == 0:
                date = self.input_dates[row].toPython()
                return str(date)[:-3]

            elif column == 1:
                magnitude = self.input_magnitudes[row]
                return f"{magnitude:.2f}"

        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight

        return None

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return super().flags(index)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                old_magnitude = self.input_magnitudes[index.row()]
                self.input_magnitudes[index.row()] = float(value)
                self.dataChanged.emit(index, index, QIntList([role]))
                self.data_changed.emit(index.row(), index.column(), old_magnitude, self.input_magnitudes[index.row()])
                return True
            except ValueError:
                return False



