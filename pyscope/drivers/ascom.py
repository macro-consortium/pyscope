import abstract_hardware as abs_hw

class AscomDriver():
    pass

class Camera(AscomDriver, abs_hw.Camera):
    pass

class CoverCalibrator(AscomDriver, abs_hw.CoverCalibrator):
    pass

class Dome(AscomDriver, abs_hw.Dome):
    pass

class FilterWheel(AscomDriver, abs_hw.FilterWheel):
    pass

class Focuser(AscomDriver, abs_hw.Focuser):
    pass

class ObservingConditions(AscomDriver, abs_hw.ObservingConditions):
    pass

class Telescope(AscomDriver, abs_hw.Telescope):
    pass