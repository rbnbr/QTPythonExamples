from typing import Dict, Any

import PySide6
from PySide6.QtCore import Slot, Signal

from PySide6.QtCharts import QLineSeries, QScatterSeries

from qtpex.qt_objects.configurable_xy_series import StaticConfigurableXYSeries


class ConfigurableLineSeries(QLineSeries):
    """
        A QLineSeries which keeps a second scatter series to keep track of point ids.
        It overrides the set configuration methods for the points to keep the same configurations even if points
            are deleted, or replaced, or intermediately inserted.
        """
    swapped_signal = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        StaticConfigurableXYSeries.set_up_init(self)

    def block_qt_configuration_updates(self, block: bool):
        """
        sets the blocking state up configuration updates.
        usefull for adding and removing lot's of points at once where we don't need the GUI to keep up with our
            updates.

        Note that after a series of blocked updates, there should be a final call to unblock this and update manually.
        :param self:
        :param block:
        :return:
        """
        return StaticConfigurableXYSeries.block_qt_configuration_updates(self, block)

    def swap(self, idx1: int, idx2: int):
        """
        Swaps the index of two points and keeps their configuration.
        Triggers the swap signal.
        Does not trigger other signals.
        :param idx1:
        :param idx2:
        :return:
        """
        return StaticConfigurableXYSeries.swap(self, idx1, idx2)

    def setPointConfiguration(self, index: int,
                              configuration: Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]) -> None:
        return StaticConfigurableXYSeries.setPointConfiguration(self, index, configuration)

    def setPointConfigurationKeyVal(self, index: int, key, val):
        """
        Sets only key and value of for the point at given index.
        Does not adjust the other values.
        :param index:
        :param key:
        :param val:
        :return:
        """
        return StaticConfigurableXYSeries.setPointConfigurationKeyVal(self, index, key, val)

    def setPointsConfiguration(self, pointsConfiguration: Dict[
        int, Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]]) -> None:
        """
        Sets the configuration for multiple points at once.
        If it is an empty dict, deletes all configurations.
        :param pointsConfiguration:
        :return:
        """
        return StaticConfigurableXYSeries.setPointsConfiguration(self, pointsConfiguration)

    def clearPointConfiguration(self, index: int, key=None) -> None:
        return StaticConfigurableXYSeries.clearPointConfiguration(self, index, key)

    def clearPointsConfiguration(self, key=None) -> None:
        return StaticConfigurableXYSeries.clearPointsConfiguration(self, key)

    def get_id_of_point_idx(self, idx: int):
        """
        Returns the id of the point idx.
        :param idx:
        :return:
        """
        return StaticConfigurableXYSeries.get_id_of_point_idx(self, idx)

    def get_idx_of_point_id(self, point_id: int):
        """
        Returns the current index of the point with given id.
        Returns -1 if not found.
        :param point_id:
        :return:
        """
        return StaticConfigurableXYSeries.get_idx_of_point_id(self, point_id)

    def set_id_configuration_for_point_at_idx(self, idx: int, conf: dict):
        """
        Sets the configuration for the point at idx based on its id.
        :param conf:
        :param idx:
        :return:
        """
        return StaticConfigurableXYSeries.set_id_configuration_for_point_at_idx(self, idx, conf)

    def get_configuration_for_point_at_idx(self, idx: int):
        return StaticConfigurableXYSeries.get_configuration_for_point_at_idx(self, idx)

    @staticmethod
    def get_qt_point_configuration_keys():
        return StaticConfigurableXYSeries.get_qt_point_configuration_keys()

    def as_json_compatible_list(self):
        return StaticConfigurableXYSeries.as_json_compatible_list(self)

    @staticmethod
    def json_compatible_list_to_regular_point_list(points: list):
        return StaticConfigurableXYSeries.json_compatible_list_to_regular_point_list(points)

    def get_points_configuration_with_limited_keys(self, conf: dict):
        return StaticConfigurableXYSeries.get_points_configuration_with_limited_keys(self, conf)

    def update_points_configuration(self, indices=None):
        """
        Updates the configuration of scatterseries with the current points_id_configuration.
        :param indices: The indices to be updated. If not specified, updates all indices.
        :return:
        """
        return StaticConfigurableXYSeries.update_points_configuration(self, indices)

    def get_points_id_configuration(self):
        """
        Returns the current points_id_configuration for all point of scatterseries.
        The id's are the point's id's from point_id_series.
        :return:
        """
        return StaticConfigurableXYSeries.get_points_id_configuration(self)

    def set_points_id_configuration(self, conf: dict):
        return StaticConfigurableXYSeries.set_points_id_configuration(self, conf)

    @Slot(int)
    def id_series_added(self, idx: int):
        return StaticConfigurableXYSeries.id_series_added(self, idx)

    @Slot(int)
    def id_series_removed(self, idx: int):
        return StaticConfigurableXYSeries.id_series_removed(self, idx)

    @Slot(int)
    def id_series_replaced(self, idx: int):
        return StaticConfigurableXYSeries.id_series_replaced(self, idx)

    @Slot(int, int)
    def id_series_swapped(self, idx1: int, idx2: int):
        """
        Swappes the id_series points.
        :param idx1:
        :param idx2:
        :return:
        """
        return StaticConfigurableXYSeries.id_series_swapped(self, idx1, idx2)