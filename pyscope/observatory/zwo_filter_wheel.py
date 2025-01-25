import logging
import time

from zwo_efw import EFW, EFWInformation

from .filter_wheel import FilterWheel

logger = logging.getLogger(__name__)

'''Using https://github.com/mit-kavli-institute/python-zwo-efw-filter-wheel
Also needed to update their code to allow setting unidirectional mode
to true.'''


class ZWOFilterWheel(FilterWheel):
    def __init__(self, device_number=0, serial_number=None, filters=None, filter_focus_offsets=None,):
        """
        Implementation of the FilterWheel abstract base class for ZWO filter wheels.

        Parameters
        ----------
        device_number : `int`, optional
            The device number of the filter wheel. Default is 0.
        serial_number : `str`, optional
            The serial number of the filter wheel. Default is None.
        filters : `list` of `str`, optional
            The names of the filters in the filter wheel, ordered according to the wheel's slot numbers. Default is None.
        filter_focus_offsets : `list` of `int`, optional
            The focus offsets for each filter in the filter wheel, ordered according to the wheel's slot numbers. Default is None.

        Properties
        ----------
        FocusOffsets : `list` of `int`
            Focus offsets for each filter in the wheel. Must be passed in as a keyword argument.
        Names : `list` of `str`
            Name of each filter in the wheel. Must be passed in as a keyword argument.
        Position : `int`
            The current filter wheel position. 0-indexed slot number.
        Wait_for_wheel : `bool`
            If True, the Position property will block until the filter wheel has finished moving.
        """
        logger.debug(f"ZWOFilterWheel.__init__ called with device_number={device_number}")

        self._device = EFW()

        self._device.initialize()

        self._device_number = device_number

        self._info = self._device.filter_wheel_information[0]
        
        self.filter_wheel_name = self._info.Name

        self._number_of_slots = self._info.NumberOfSlots

        if filters is not None:
            if len(filters) != self._number_of_slots:
                raise ValueError(f"Number of filters must match number of slots \n Number of slots: {self._number_of_slots} \n Provided filter list:{filters} \n Number of filters: {len(filters)} ")
            self._filter_names = filters
        else: #if no filter names are provided, use placeholder format from generic FilterWheel class
            self._filter_names = [f"Filter{i+1}" for i in range(self._number_of_slots)]
        
        if filter_focus_offsets is not None:
            if len(filter_focus_offsets) != self._number_of_slots:
                raise ValueError("Number of focus offsets must match number of slots")
            self._filter_focus_offsets = filter_focus_offsets
        else: #if no offsets are provided, default to 0 for all filters
            self._filter_focus_offsets = [0] * self._number_of_slots

        self.connect()
        

    def disconnect(self):
        logger.debug(f"ZWOFilterWheel.disconnect called")
        self._device.close()

    def connect(self):
        """Connect to the filter wheel device."""
        logger.debug(f"ZWOFilterWheel.connect called")
        self._device.initialize()

        self._wait_for_wheel = False

        self.Unidirectional = True

    def reconnect(self):
        """Reconnect to the filter wheel device."""
        logger.debug(f"ZWOFilterWheel.reconnect called")
        self.disconnect()
        self.connect()

    @property
    def EFWInfo(self): # returns the info in the EFWInformation object; for identifying the filter wheel and/or debugging purposes
        logger.debug(f"ZWOFilterWheel.EFWInfo property called")
        return self._info

    @property
    def FocusOffsets(self):
        logger.debug(f"ZWOFilterWheel.FocusOffsets property called")
        return self._filter_focus_offsets
    
    @property
    def is_moving(self):
        logger.debug(f"ZWOFilterWheel.is_moving property called")
        return self._device.is_moving(self._device_number)

    @property
    def Name(self):
        logger.debug(f"ZWOFilterWheel.Name property called")
        return self.filter_wheel_name

    @property
    def Names(self):
        logger.debug(f"ZWOFilterWheel.Names property called")
        return self._filter_names

    @property
    def NumberOfSlots(self):
        logger.debug(f"ZWOFilterWheel.NumberOfSlots property called")
        return self._number_of_slots

    @property
    def Position(self):
        logger.debug(f"ZWOFilterWheel.Position property called")
        if self.is_moving:
            return -1
        # Subtracting 1 from the value to convert from 1-indexed to 0-indexed
        return self._device.get_position(self._device_number) - 1

    @Position.setter
    def Position(self, value):
        # Adding 1 from the value to convert from 1-indexed to 0-indexed
        value += 1
        logger.debug(f"ZWOFilterWheel.Position property set to {value}")
        self._device.set_position(self._device_number, value, wait_until_done=self._wait_for_wheel)
        while self.is_moving:
            time.sleep(0.1)
        # except Exception as e:
            # logger.error(f"Error setting filter wheel position: {e}")
            # logger.error("Asking what position the filter wheel is at")
            # logger.error(f"Filter wheel position is {self.Position}")
            # self._device.set_position(self._device_number, value, wait_until_done=self._wait_for_wheel)
            # logger.error(f"Error setting filter wheel position: {e}")
            # logger.error("Attempting to reconnect to filter wheel")
            # self.reconnect()
            # logger.error("Reconnection run.")
            # try:
            #     self._device.set_position(self._device_number, value, wait_until_done=self._wait_for_wheel)
            # except Exception as e:
            #     logger.error(f"Error setting filter wheel position: {e}")
            #     logger.error(f"Filter wheel position is {self.Position}")
            #     logger.error(f"Retrying to set filter wheel position to {value-1}")
            #     self._device.set_position(self._device_number, value, wait_until_done=self._wait_for_wheel)


    @property
    def Unidirectional(self):
        logger.debug(f"ZWOFilterWheel.Unidirectional property called")
        return self._device.get_direction(self._device_number)
    
    @Unidirectional.setter
    def Unidirectional(self, value):
        logger.debug(f"ZWOFilterWheel.Unidirectional property set to {value}")
        self._device.set_direction(self._device_number, value)

    @property
    def Wait_for_wheel(self):
        logger.debug(f"ZWOFilterWheel.Wait_for_wheel property called")
        return self._wait_for_wheel
    
    @Wait_for_wheel.setter
    def Wait_for_wheel(self, value):
        logger.debug(f"ZWOFilterWheel.Wait_for_wheel property set to {value}")
        self._wait_for_wheel = value
