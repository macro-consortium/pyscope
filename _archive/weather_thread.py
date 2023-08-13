# Built-in Python imports
import logging
import threading
import time

# iotalib imports
from . import weather

# Private copy of the latest weather reading
_latest_weather_reading = weather.WeatherReading()

def start(weather_driver):
    """
    Called by the client to kick off the weather monitoring thread
    """

    logging.info("Starting weather thread")

    thread = threading.Thread(target=_thread_loop, args=(weather_driver,))
    thread.daemon = True
    thread.start()

def get_latest_weather():
    """
    Return a reference to the latest weather reading
    """

    return _latest_weather_reading

def _thread_loop(weather_driver):
    """
    Runs in a separate thread, and periodically pulls down new weather data
    """

    global _latest_weather_reading

    logging.info("Monitoring weather using %s", weather_driver)

    while True:
        try:
            logging.info("Refreshing weather data")
            current_reading = weather_driver.get_weather()
            print(current_reading)
            _latest_weather_reading = current_reading
        except Exception as ex:
            logging.exception("Error refreshing weather data")
        
        time.sleep(60)