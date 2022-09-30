from typing import Dict, Any

import PySide6
from PySide6.QtCharts import QScatterSeries


class StaticConfigurableXYSeries:
    """
    A static QXYSeries which keeps a second scatter series to keep track of point ids.
    It overrides the set configuration methods for the points to keep the same configurations even if points
        are deleted, or replaced, or intermediately inserted.

    Don't use instances of this class. Derive from QXYSeries or similar and call the functions of this class with 'self'
        as parameter of themselves.

    Be sure to implement the swapped_signal in the derived classes, i.e., add 'swapped_signal = Signal(int, int)' to the
        class.
    """
    @staticmethod
    def set_up_init(self):
        # a scatter series that keeps track of the ids of individual points (their y-values)
        self._point_id_series = QScatterSeries()
        self._next_point_id = 0

        self.pointAdded.connect(self.id_series_added)
        self.pointReplaced.connect(self.id_series_replaced)
        self.pointRemoved.connect(self.id_series_removed)
        self.swapped_signal.connect(self.id_series_swapped)

        # blocks calls to configuration updates
        # usefull for adding and removing lot's of points at once where we don't need the GUI to keep up with our
        # updates
        self._block_qt_configuration_updates = False

        self._points_id_configuration = {}

    @staticmethod
    def block_qt_configuration_updates(self, block: bool = True):
        """
        sets the blocking state up configuration updates.
        usefull for adding and removing lot's of points at once where we don't need the GUI to keep up with our
            updates.

        Note that after a series of blocked updates, there should be a final call to unblock this and update manually.
        :param self:
        :param block:
        :return:
        """
        self._block_qt_configuration_updates = block

    @staticmethod
    def swap(self, idx1: int, idx2: int):
        """
        Swaps the index of two points and keeps their configuration.
        Triggers the swap signal.
        Does not trigger other signals.
        :param idx1:
        :param idx2:
        :return:
        """
        self.blockSignals(True)
        tmp = self.at(idx2)
        self.replace(idx2, self.at(idx1))
        self.replace(idx1, tmp)
        self.blockSignals(False)

        self.swapped_signal.emit(idx1, idx2)

    @staticmethod
    def setPointConfiguration(self, index: int,
                              configuration: Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]) -> None:
        self.set_id_configuration_for_point_at_idx(index, configuration)

    @staticmethod
    def setPointConfigurationKeyVal(self, index: int, key, val):
        """
        Sets only key and value of for the point at given index.
        Does not adjust the other values.
        :param index:
        :param key:
        :param val:
        :return:
        """
        conf = self.get_configuration_for_point_at_idx(idx=index)
        conf[key] = val
        self.set_id_configuration_for_point_at_idx(index, conf)

    @staticmethod
    def setPointsConfiguration(self, pointsConfiguration: Dict[
        int, Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]]) -> None:
        """
        Sets the configuration for multiple points at once.
        If it is an empty dict, deletes all configurations.
        :param pointsConfiguration:
        :return:
        """
        if len(pointsConfiguration) == 0:
            self._points_id_configuration = {}
            self.update_points_configuration()

        for idx in pointsConfiguration:
            self.setPointConfiguration(idx, pointsConfiguration[idx])

    @staticmethod
    def clearPointConfiguration(self, index: int, key=None) -> None:
        if self.get_id_of_point_idx(index) in self._points_id_configuration:
            del self._points_id_configuration[self.get_id_of_point_idx(index)]
        if key is None:
            super(self.__class__, self).clearPointConfiguration(index)
        else:
            super(self.__class__, self).clearPointConfiguration(index, key)

    @staticmethod
    def clearPointsConfiguration(self, key=None) -> None:
        if key is None:
            self._points_id_configuration = dict()
            super(self.__class__, self).clearPointsConfiguration()
        else:
            for idx in self._points_id_configuration:
                if key in self._points_id_configuration[idx]:
                    del self._points_id_configuration[idx][key]
            super(self.__class__, self).clearPointsConfiguration(key)

    @staticmethod
    def get_id_of_point_idx(self, idx: int):
        """
        Returns the id of the point idx.
        :param idx:
        :return:
        """
        return int(self._point_id_series.at(idx).y())

    @staticmethod
    def get_idx_of_point_id(self, point_id: int):
        """
        Returns the current index of the point with given id.
        Returns -1 if not found.
        :param point_id:
        :return:
        """
        for i in range(self.count()):
            if int(point_id) == self.get_id_of_point_idx(i):
                return i
        return -1

    @staticmethod
    def set_id_configuration_for_point_at_idx(self, idx: int, conf: dict):
        """
        Sets the configuration for the point at idx based on its id.
        :param conf:
        :param idx:
        :return:
        """
        if self.get_id_of_point_idx(idx) in self._points_id_configuration:
            self._points_id_configuration[self.get_id_of_point_idx(idx)].update(conf.copy())
        else:
            self._points_id_configuration[self.get_id_of_point_idx(idx)] = conf.copy()
        self.update_points_configuration([idx])

    @staticmethod
    def get_configuration_for_point_at_idx(self, idx: int):
        return self._points_id_configuration[self.get_id_of_point_idx(idx)].copy()

    @staticmethod
    def get_qt_point_configuration_keys():
        return [
            QScatterSeries.PointConfiguration.Color,
            QScatterSeries.PointConfiguration.Size,
            QScatterSeries.PointConfiguration.Visibility,
            QScatterSeries.PointConfiguration.LabelVisibility
        ]

    @staticmethod
    def get_points_configuration_with_limited_keys(self, conf: dict):
        d = dict()
        for k in self.get_qt_point_configuration_keys():
            if k in conf:
                d.update({k: conf[k]})
        return d

    @staticmethod
    def update_points_configuration(self, indices=None):
        """
        Updates the configuration of scatterseries with the current points_id_configuration.
        :param indices: The indices to be updated. If not specified, updates all indices.
        :return:
        """
        if self.block_qt_configuration_updates:
            return

        update_batch = False
        if indices is None:
            update_batch = True
            indices = range(self._point_id_series.count())

        conf = {}

        for i in indices:
            if self.get_id_of_point_idx(i) not in self._points_id_configuration:
                continue

            conf_i = self.get_points_configuration_with_limited_keys(
                self._points_id_configuration[self.get_id_of_point_idx(i)])

            if not update_batch:
                super(self.__class__, self).setPointConfiguration(i, conf_i)
            else:
                conf.update({i: conf_i})

        if update_batch:
            super(self.__class__, self).setPointsConfiguration(conf)

    @staticmethod
    def get_points_id_configuration(self):
        """
        Returns the current points_id_configuration for all point of scatterseries.
        The id's are the point's id's from point_id_series.
        :return:
        """
        return self._points_id_configuration.copy()

    @staticmethod
    def set_points_id_configuration(self, conf: dict):
        self._points_id_configuration = conf.copy()
        self.update_points_configuration()

    @staticmethod
    def id_series_added(self, idx: int):
        p = self.at(idx)
        p.setY(self._next_point_id)

        self._point_id_series.insert(idx, p)

        self._next_point_id += 1
        self.update_points_configuration(range(idx, self._point_id_series.count()))

    @staticmethod
    def id_series_removed(self, idx: int):
        self.clearPointConfiguration(idx)
        self._point_id_series.remove(idx)
        self.update_points_configuration(range(idx, self._point_id_series.count()))

    @staticmethod
    def id_series_replaced(self, idx: int):
        # replacing does not change id, we only change values here.
        # to change id, implement it when replacing
        # self._point_id_series.replace(idx, self._point_id_series.at(idx))
        # self.update_points_configuration()
        pass

    @staticmethod
    def id_series_swapped(self, idx1: int, idx2: int):
        """
        Swappes the id_series points.
        :param idx1:
        :param idx2:
        :return:
        """
        tmp = self._point_id_series.at(idx1)
        self._point_id_series.replace(idx1, self._point_id_series.at(idx2))
        self._point_id_series.replace(idx2, tmp)
        self.update_points_configuration([idx1, idx2])
