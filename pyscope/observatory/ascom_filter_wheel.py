from .filter_wheel import FilterWheel

class ASCOMFilterWheel(FilterWheel):
    def Choose(self, FilterWheelID):
        self._com_object.Choose(FilterWheelID)

    @property
    def FocusOffsets(self):
        return self._com_object.FocusOffsets

    @property
    def Names(self):
        return self._com_object.Names

    @property
    def Position(self):
        return self._com_object.Position
    @Position.setter
    def Position(self, value):
        self._com_object.Position = value