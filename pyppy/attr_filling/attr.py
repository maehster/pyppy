"""
TODO
"""


class Attr:
    """
    TODO
    """

    _container = None

    def __init__(self, attr_name):
        self._attr_name = attr_name

    def __get__(self, obj, obj_type=None):
        return getattr(type(self)._container(), self._attr_name)  # pylint: disable=E1102

    def __set__(self, _, value):
        setattr(type(self)._container(), self._attr_name, value)  # pylint: disable=E1102
