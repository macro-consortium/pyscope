import importlib
import sys

from pyscope.drivers import abstract
from pyscope.drivers import _ascom
# from .observatory import ObservatoryException

def _import_driver(driver_name, device, ascom=False):
    '''Imports a driver'''
    if driver_name is None: return None

    if ascom:
        device_class = getattr(_ascom, device)
        return device_class(driver_name)
    else:
        try: 
            device_module = importlib.import_module('pyscope.drivers.%s' % driver_name)
            device_class = getattr(device_module, device)
        except:
            try: 
                spec = importlib.util.spec_from_file_location(driver_name, device)
                device_class = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = device_class
                spec.loader.exec_module(device_class)
            except: 
                return None

    _check_class_inheritance(device_class, device)

    return device_class()

def _check_class_inheritance(device_class, device):
    if not getattr(abstract, device) in device_class.__bases__:
            raise ObservatoryException('Driver %s does not inherit from the required abstract classes' % driver_name)

class ObservatoryException(Exception):
    pass