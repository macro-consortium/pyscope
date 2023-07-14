import importlib
import sys

from .. import drivers, logger

def import_driver(device, driver_name=None, ascom=False, filepath=None, kwargs={}):
    '''Imports a driver'''
    if driver_name is None and not ascom: return None

    if ascom: return getattr(drivers.ascom, device)(driver_name)
    else:
        try: 
            logger.info('Attempting to importing driver %s for device %s from known custom drivers' % (driver_name, device))
            device_class = getattr(drivers, driver_name)
        except:
            logger.info('Driver %s for device %s not found in known custom drivers, attempting to import from file' % (driver_name, device))
            try: 
                module_name = filepath.split('/')[-1].split('.')[0]
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                device_class = getattr(module, driver_name)
            except: 
                logger.error('Could not import driver %s for device %s' % (driver_name, device))
                return None

    _check_class_inheritance(device_class, device)

    return device_class(**kwargs)

def _check_class_inheritance(device_class, device):
    if not getattr(drivers.abstract, device) in device_class.__bases__:
            raise DriverException('Driver %s does not inherit from the required _abstract classes' % driver_name)
    else: logger.debug('Driver %s inherits from the required _abstract classes' % driver_name)

class DriverException(Exception):
    '''Exception for driver errors'''