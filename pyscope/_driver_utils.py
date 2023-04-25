import importlib
import sys

from drivers import abstract
from . import ObservatoryException

def _import_driver(driver_name, device, ascom=False):
    '''Imports a driver'''
    if driver_name is None: return None

    if ascom:
        device_class = importlib.import_module('drivers._ascom.%s' % device)
        return device_class(driver_name)
    else:
        try: 
            device_class = importlib.import_module('drivers.%s' % driver_name)
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